#!/usr/bin/env python3

import argparse
import soco

# Defaults
SPEAKER_NAME = "Playroom"
PLAYLIST_NAME = ""

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Get Sonos Playlist ID")
parser.add_argument("-p", "--playlist", help="name of the Sonos playlist to search for")
parser.add_argument("-s", "--speaker", help="speaker to be used as output device")

# Eventually override the defaults with command line arguments
args = parser.parse_args()
if args.playlist:
	PLAYLIST_NAME = args.playlist
if args.speaker:
	SPEAKER_NAME = args.speaker

speaker = soco.discovery.by_name(SPEAKER_NAME)
print("Found speaker: " + speaker.player_name + " (" + speaker.ip_address + ")")

# Get playlist by title
print("Getting ID for Sonos playlist " + PLAYLIST_NAME)
playlist = speaker.get_sonos_playlist_by_attr('title', PLAYLIST_NAME)
print("Sonos playlist " + PLAYLIST_NAME + " has ID " + playlist.item_id)
