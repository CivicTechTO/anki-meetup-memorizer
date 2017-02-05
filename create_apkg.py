#!/usr/bin/env python

# See: https://superuser.com/questions/698902/can-i-create-an-anki-deck-from-a-csv-file

import anki
import csv
import meetup.api
import sys
import tempfile
import os
import urllib

from anki.exporting import AnkiPackageExporter
from datetime import datetime


api_key = os.environ['MEETUP_API_KEY']
script, event_id = sys.argv

client = meetup.api.Client(api_key)

event = client.GetEvent(id=event_id)

date = datetime.fromtimestamp(event.time/1000).strftime('%Y-%m-%d')
filename = 'meetup-rsvps-{}-{}.apkg'.format(event.group['urlname'], date)


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
        showWarning(_("An error occurred while opening %s") % e)
        return
    path = urllib.parse.unquote(url)
    return collection.media.writeData(path, filecontents)


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
            continue
        name = rsvp['member']['name']
        url = rsvp['member_photo']['photo_link']
        local_file = retrieveURL(url)

        note = collection.newNote()
        note['person_photo'] = '<img src="{}" />'.format(local_file)
        note['person_name'] = name
        note.guid = rsvp['member']['member_id']
        collection.addNote(note)

    # Update media database, just in case.
    # Not sure if this is necessary
    collection.media.findChanges()

    output_file = collection.media._oldcwd + '/' + filename

    export = AnkiPackageExporter(collection)
    export.exportInto(output_file)
