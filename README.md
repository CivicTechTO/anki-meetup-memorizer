# Meetup RSVP Memorizer

This is a quick little script for helping Meetup.com event organizers
remember the names of attendees.

![Screenshot of Anki Desktop and AnkiDroid](https://imgur.com/h471IJt.png)

**Meetup.com** is an online platform for finding and organizing
in-person communities of practice.

**Anki** is a popular flashcard tool that helps people memorize things.
It is available on desktop and mobile.

Use this script to generate an Anki flashcard deck for memorizing the
names and faces of your Meetup attendees.

## Usage

To run the script and generate a new APKG file for
[importing](https://ankidroid.org/docs/manual.html#importing):

```
git submodule update --init
pip install -r requirements.txt

# Get your MEETUP_API_KEY here:
# https://secure.meetup.com/meetup_api/key/
export MEETUP_API_KEY=xxxxxxxxx

# Find the <meetup-event-id> in the event URL
./generate_csv.py <meetup-event-id>

# Point this script at the generated CSV
PYTHONPATH=$PWD/anki: ./create_apkg.py <meetup-rsvp-csv>
```
