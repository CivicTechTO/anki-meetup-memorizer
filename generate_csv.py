import csv
import meetup.api
import os

api_key = os.environ['MEETUP_API_KEY']
client = meetup.api.Client(api_key)

response = client.GetRsvps(event_id='237172947')

with open('rsvps.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'photo_link'])
    for rsvp in response.results:
        if not rsvp.get('member_photo'):
            continue
        writer.writerow([rsvp['member']['name'], rsvp['member_photo']['photo_link']])
