#!/usr/bin/env python

import anki
import csv
import sys
import tempfile
import os
import urllib

from anki.exporting import AnkiPackageExporter


script, rsvp_csvfile = sys.argv

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

    deck_id = collection.decks.id("Civic Tech Toronto - RSVPs")
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

    filepath = collection.media._oldcwd + '/' + rsvp_csvfile
    reader = csv.reader(open(filepath))
    for i, row in enumerate(reader):
        if i == 0: continue
        name, url = row
        local_file = retrieveURL(url)

        note = collection.newNote()
        note['person_photo'] = '<img src="{}" />'.format(local_file)
        note['person_name'] = name
        note.guid = i
        collection.addNote(note)

    # Update media database, just in case.
    # Not sure if this is necessary
    collection.media.findChanges()

    output_file = collection.media._oldcwd + '/' + rsvp_csvfile.replace('.csv', '.apkg')

    export = AnkiPackageExporter(collection)
    export.exportInto(output_file)
