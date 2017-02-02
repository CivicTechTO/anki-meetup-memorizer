#!/usr/bin/env python

import csv
import meetup.api
import sys
import os

from datetime import datetime

api_key = os.environ['MEETUP_API_KEY']
script, event_id = sys.argv

client = meetup.api.Client(api_key)

event = client.GetEvent(id=event_id)
date = datetime.fromtimestamp(event.time/1000).strftime('%Y-%m-%d')
filename = 'meetup-rsvps-{}.csv'.format(date)

response = client.GetRsvps(event_id=event_id)

with open(filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'photo_link'])
    for rsvp in response.results:
        if not rsvp.get('member_photo'):
            continue
        writer.writerow([rsvp['member']['name'], rsvp['member_photo']['photo_link']])
