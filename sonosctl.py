#!/usr/bin/env python3

import logging
import logging.handlers
import argparse
import sys
import time
import soco
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Defaults
LOG_FILENAME = "/var/log/sonosctl/controller.log"
LOG_LEVEL = logging.DEBUG
SPEAKER_NAME = "Playroom"
READER = SimpleMFRC522()
OLDCARDID = ""

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="RFID Sonos Controller")
parser.add_argument("-f", "--logfile", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-l", "--loglevel", help="log level (DEBUG, ERROR, WARNING, INFO)")
parser.add_argument("-s", "--speaker", help="speaker to be used as output device")

# Eventually override the defaults with command line arguments
args = parser.parse_args()
if args.logfile:
        LOG_FILENAME = args.logfile
if args.loglevel:
	LOG_LEVEL = args.loglevel
if args.speaker:
	SPEAKER_NAME = args.speaker

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout and stderr with logging to file
sys.stdout = MyLogger(logger, logging.INFO)
sys.stderr = MyLogger(logger, logging.ERROR)

try:
	# Set active speaker
	logger.info("Successfully initialized Sonos controller for kids")
	speaker = soco.discovery.by_name(SPEAKER_NAME)
	logger.info("Active speaker set to: " + speaker.player_name + " (" + speaker.ip_address + ")")

	while True:
		# Read card
		id, text = READER.read()
		logger.debug("Found card with id: " + str(id))
		# Remove any spaces from card text
		text = text.strip()
		logger.debug("Card text: " + text)

		# Check if a new card was placed on the reader
		if id != OLDCARDID:
			OLDCARDID = id

			# Stop playlist if STOP card found
			if text == "STOP":
				logger.info("Found STOP")
				speaker.stop()

			# Else get playlist by given item_id and play
			else:
				# Get Sonos playlist by item_id
				logger.info("Getting playlist with item_id: " + text)
				playlist = speaker.get_sonos_playlist_by_attr('item_id', text)
				logger.info("Found corresponding playlist: " + playlist.title)
				logger.info("Clearing queue for " + speaker.player_name)
				# Clear speaker queue
				speaker.clear_queue()
				logger.info("Adding playlist to queue")
				# Add Sonos playlist to speaker queue and play
				speaker.add_to_queue(playlist)
				logger.info("Starting playlist")
				speaker.play()

		# Do nothing if still the same card
		else :
			logger.debug("Still same card with id: " + str(id))
			time.sleep(2)
finally:
	GPIO.cleanup()
