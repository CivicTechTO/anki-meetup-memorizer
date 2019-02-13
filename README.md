# Meetup RSVP Memorizer

This is a quick little script for helping Meetup.com event organizers
remember the names and faces of attendees, taken from their public profiles.

![Screenshot of Anki Desktop and AnkiDroid](https://imgur.com/h471IJt.png)

**Meetup.com** is an online platform for finding and organizing
in-person communities of practice.

**Anki** is a popular flashcard tool that helps people memorize things.
It is available on desktop and mobile.

Use this script to generate an Anki flashcard deck for memorizing the
names and faces of your Meetup attendees.

## Requirements

* Python 3.6+
* [`pipenv`](https://pipenv.readthedocs.io/en/latest/#install-pipenv-today) (optional)

## Usage

```
# Not yet working. Please use development instructions.
$ pip install git+https://github.com/civictechto/anki-meetup-memorizer
```

## Development

To run the script and generate a new APKG file for
[importing](https://ankidroid.org/docs/manual.html#importing):

```
# Install dependencies
git submodule update --init
pipenv install

# For usage instructions
pipenv run anki-meetup-memorizer --help

# You can set config via a dot-env file
cp sample.env .env

# To generate an APKG import file
pipenv run anki-meetup-memorizer <meetup-event-url>
```

Your generated APKG file will now be in the `outputs/` directory.

## Notes

* Each meetup event gets it's own card deck.
* We include attendees who RSVP'd both Yes and No, as both forms of
  action are indicative of an active community member.
* Members without photos are obviously not included in the deck.
