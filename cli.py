import sys
sys.path.append('./anki')

# See: https://superuser.com/questions/698902/can-i-create-an-anki-deck-from-a-csv-file

import anki
import click
import csv
import errno
import functools
import hashlib
import json
import meetup.api
import tempfile
import textwrap
import os
import urllib
import anki.sched

from anki.exporting import AnkiPackageExporter
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


CONTEXT_SETTINGS = dict(help_option_names=['--help', '-h'])
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/drive']

def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_path(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def retrieveURL(url):
    "Download file into media folder and return local filename or None."
    # urllib doesn't understand percent-escaped utf8, but requires things like
    # '#' to be escaped. we don't try to unquote the incoming URL, because
    # we should only be receiving file:// urls from url mime, which is unquoted
    if url.lower().startswith("file://"):
        url = url.replace("%", "%25")
        url = url.replace("#", "%23")
    # fetch it into a temporary folder
    try:
        req = urllib.request.Request(url, None, {
            'User-Agent': 'Mozilla/5.0 (compatible; Anki)'})
        filecontents = urllib.request.urlopen(req).read()
    except urllib.error.URLError as e:
        click.echo("An error occurred while opening %s".format(e), err=True)
        return
    path = urllib.parse.unquote(url)
    return (path, filecontents)

def common_params(func):
    @click.option('--yes', '-y',
                  help='Skip confirmation prompts',
                  is_flag=True)
    @click.option('--verbose', '-v',
                  help='Show output for each action',
                  is_flag=True)
    @click.option('--debug', '-d',
                  is_flag=True,
                  help='Show full debug output',
                  default=False)
    @click.option('--noop',
                  help='Skip API calls that change/destroy data',
                  is_flag=True)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('meetup-event-url', nargs=1)
@click.option('--meetup-api-key',
              required=True,
              help='API key for any unprivileged site user',
              envvar='ANKI_MEETUP_API_KEY',
              metavar='<string>')
@common_params
def create_apkg(meetup_event_url, meetup_api_key, yes, verbose, debug, noop):
    parse_result = urllib.parse.urlparse(meetup_event_url)
    urlname, _, event_id = parse_result.path.split('/')[1:4]
    client = meetup.api.Client(meetup_api_key)

    event = client.GetEvent(id=event_id, urlname=urlname)

    date = datetime.fromtimestamp(event.time/1000).strftime('%Y-%m-%d')
    filename = 'meetup-rsvps-{}-{}.apkg'.format(urlname, date)

    ### Output confirmation to user

    if verbose or not yes:
        confirmation_details = """\
            We are using the following configuration:
              * Meetup Group: {group}
              * Event Name:   {name}
                    * Date:   {date}
                    * RSVPs:  {rsvps}"""
        confirmation_details = confirmation_details.format(group=urlname, name=event.name, date=date, rsvps=event.yes_rsvp_count)
        click.echo(textwrap.dedent(confirmation_details), err=True)

    if not yes:
        click.confirm('Do you want to continue?', abort=True)

    create_path('outputs')

    with tempfile.TemporaryDirectory() as tmpdir:
        collection = anki.Collection(os.path.join(tmpdir, 'collection.anki2'))

        deck_id = collection.decks.id('Meetup: {}'.format(event.name))
        deck = collection.decks.get(deck_id)

        model = collection.models.new("meetup_model")
        model['did'] = deck_id
        model['css'] = ''
        collection.models.addField(model, collection.models.newField('person_photo'))
        collection.models.addField(model, collection.models.newField('person_name'))

        tmpl = collection.models.newTemplate('meetup attendee')
        tmpl['qfmt'] = '{{person_photo}}'
        tmpl['afmt'] = '{{FrontSide}}\n\n<hr>\n\n{{person_name}}'
        collection.models.addTemplate(model, tmpl)

        model['id'] = 123456789
        collection.models.update(model)
        collection.models.setCurrent(model)
        collection.models.save(model)

        note = anki.notes.Note(collection, model)
        note['person_photo'] = ''
        note['person_name'] = ''
        note.guid = 0
        collection.addNote(note)

        response = client.GetRsvps(event_id=event_id)
        for rsvp in response.results:
            if not rsvp.get('member_photo'):
                if verbose: click.echo('Skipping {} (no photo)'.format(rsvp['member']['name']), err=True)
                continue
            if verbose: click.echo('Fetching ' + rsvp['member']['name'], err=True)
            name = rsvp['member']['name']
            url = rsvp['member_photo']['photo_link']
            path, contents = retrieveURL(url)
            local_file = collection.media.writeData(path, contents)

            note = collection.newNote()
            note['person_photo'] = '<img src="{}" />'.format(local_file)
            note['person_name'] = name
            note.guid = rsvp['rsvp_id']
            collection.addNote(note)

        # Update media database, just in case.
        # Not sure if this is necessary
        collection.media.findChanges()

        output_filepath = collection.media._oldcwd + '/outputs/' + filename

        export = AnkiPackageExporter(collection)
        export.exportInto(output_filepath)
        click.echo('output_filepath: '+output_filepath)


def echo_config(dict, fields):
    for k, v in dict.items():
        if k in fields:
            click.echo('{}: {}'.format(k, v))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file')
@click.option('--gdrive-folder', '-f',
              required=True,
              help='Google Drive folder to upload file into. (URL or folder ID)',
              envvar='ANKI_GDRIVE_FOLDER',
              metavar='<url/id>')
@click.option('--google-creds', '-c',
              type=click.File('rb'),
              required=True,
              help='',
              envvar='ANKI_GOOGLE_CREDS',
              metavar='<file>')
@common_params
def upload(file, gdrive_folder, google_creds, yes, verbose, debug, noop):
    folder_id = gdrive_folder
    json_bytes = b''
    while True:
        chunk = google_creds.read(1024)
        if not chunk:
            break
        json_bytes = json_bytes + chunk
    keyfile_dict = json.loads(json_bytes)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, GOOGLE_SCOPES)
    if debug: click.echo('>>> Service account email: ' + creds.service_account_email, err=True)
    gauth = GoogleAuth()
    gauth.credentials = creds
    gdrive = GoogleDrive(gauth)
    query = "'{}' in parents".format(folder_id)
    file_list = gdrive.ListFile({'q': query}).GetList()
    filename = file.split('/')[-1]
    match = [f for f in file_list if f['title'] == filename]
    match = match.pop() if match else None
    if match:
        if match['md5Checksum'] == get_md5(file):
            click.echo('File exists already. Skipping...', err=True)
        else:
            click.echo('File exists and differs. Overriding...', err=True)
            match.SetContentFile(file)
            match.Upload()

        myfile = match
    else:
        click.echo('Adding file to folder...', err=True)
        new_file = gdrive.CreateFile({'title': filename})
        new_file.SetContentFile(file)
        new_file.Upload()
        new_file.auth.service.parents().insert(fileId=new_file['id'], body={'id': folder_id}).execute()
        new_file.FetchMetadata(fields='permissions')
        # NOTE: We can't change the owner of a non-Drive file with a service account.
        myfile = new_file

    echo_config(myfile.metadata, ['webContentLink', 'title'])

if __name__ == '__main__':
    cli(auto_envvar_prefix='ANKI')
