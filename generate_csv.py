#!/usr/bin/env python

import csv
import meetup.api
import sys
import os

api_key = os.environ['MEETUP_API_KEY']
script, event_id = sys.argv

client = meetup.api.Client(api_key)

response = client.GetRsvps(event_id=event_id)

filename = 'meetup-rsvps-{}.csv'.format(event_id)
with open(filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'photo_link'])
    for rsvp in response.results:
        if not rsvp.get('member_photo'):
            continue
        writer.writerow([rsvp['member']['name'], rsvp['member_photo']['photo_link']])
