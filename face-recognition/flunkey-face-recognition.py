import face_recognition
import picamera
import numpy as np
import os
import json
import logging
import signal
import sys
import requests
from datetime import datetime, date, time
from time import sleep

# Logging config
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

# SIGINT HANDLING
def signal_handler(signal, frame):
      sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Get a reference to the Pi Camera.
camera = picamera.PiCamera()
camera.resolution = (480, 320)
output = np.empty((320, 480, 3), dtype=np.uint8)

# Configuration
people_dir = "./known_people"

# Initialize some variables
known_face_encodings = []
known_face_names = []
peoples = {}
face_id = 0

# Init
flunkey_api = "http://localhost:5000"
users = json.loads(requests.get(flunkey_api + "/config/users/").content)
known_face_encodings = []
known_users = {}

logging.info('Getting known users & faces.')
for user in users:
    if users[user]['username'] != "guest":
        for key in users[user]['face_encoding'].keys():
            face_id = key 
        encoding = users[user]['face_encoding'][face_id]['face']
        known_users[face_id] = {}
        known_users[face_id]['username'] = user
        known_face_encodings.insert(int(face_id), encoding)

# Initialize some variables
face_locations = []
face_encodings = []

logging.info('Started image capturing.')
while True:
    #print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format="rgb", use_video_port=True)

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)

    #logging.info("Found {} faces in image.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
        #if True in matches:
            #first_match_index = matches.index(True)
            current_user = known_users[str(best_match_index)]['username']
            logging.info("I see %s %s!", users[current_user]['name'], users[current_user]['surname'])
            patch_current_user = {
                "query": {
                    "_id": "production"
                },
                "payload": 
                {
                    "current_user": current_user
                }
            }
            patch = {
                "query": {
                    "username": current_user
                },
                "payload": 
                {
                    "last_seen_date": datetime.now().strftime('%d.%m.%Y'),
                    "last_seen_time": datetime.now().strftime('%H:%M:%S')

                }
            }
            # Set user as current
            response = requests.patch(flunkey_api + "/config/global", json=patch_current_user)
            # Update user config
            response = requests.patch(flunkey_api + "/config/user/" + current_user, json=patch)
            if response.status_code == 200:
                logging.info('Set last_seen fields in database.')
        else:
            logging.info("Unknown person in front of mirror.")
            patch_current_user = {
                "query": {
                    "_id": "production"
                },
                "payload": 
                {
                    "current_user": "guest"
                }
            }
            # Set user as current
            response = requests.patch(flunkey_api + "/config/global", json=patch_current_user)

            logging.info("Taking a short video of the unknown person...")

            # Setting timestamps
            time = datetime.now().strftime('%H-%M')
            date = datetime.now().strftime('%d-%m-%Y')

            # Starting capturing
            camera.resolution = (480, 320)
            camera.start_recording("/tmp/unknown_person_"+ date + ".h264")
            camera.wait_recording(8)
            camera.stop_recording()

            logging.info("Video captured and saved in /tmp.")            


