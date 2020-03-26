#!/usr/bin/python3

import face_recognition
import os, json, logging, signal, sys, requests, time
from datetime import datetime, date, time
from time import sleep
from pymongo import MongoClient

# Configuration
people_dir = "./known_people"
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
mongo = MongoClient('mongodb://192.168.178.80:27017')

# Initialize some variables
env = "production"
flunkey_api = "http://flunkey:5000"
known_face_encodings = []
known_face_names = []
peoples = {}
face_id = 0
formatted_date = datetime.now().strftime('%d.%m.%Y')
db = mongo.flunkey

logging.info('Training model...')
# Load a sample pictures and learn how to recognize it.
for file in os.listdir(people_dir):
    if file.endswith(".jpg"):
       
        name = file.split(".")[0]
        surname = file.split(".")[1]
        username = name[:1].lower() + surname.lower()
        image = face_recognition.load_image_file(people_dir + "/" + file)
        face = face_recognition.face_encodings(image)[0]

        # Search for user in DB
        result = db.users.find_one({"username": username})
        if result:
            patch = {
                "query": {
                    "username": username
                },
                "payload": 
                {
                    "face_encoding": 
                    { 
                        face_id: 
                        { "face": list(face) }
                    },
                    "image": file,

                }
            }
            response = requests.patch(flunkey_api + "/config/user/" + username, json=patch)
            if response.status_code == 200:
                logging.info('Training model for %s updated.', username)
        else:
            logging.info('User %s is not in database.', username)
            logging.info('Initializing user %s.', username)
            create_user = {
                "_id": username,
                "config": {
                    "calendars": {
                    "05 - Schulferien NRW": {
                        "display_name": "Schulferien",
                        "entries": 2,
                        "url": "http://i.cal.to/ical/77/nrw/ferien/8959432e.0d42e438-6e549464.ics"
                    }
                    },
                    "feeds": {
                    "Spiegel": {
                        "url": "https://www.spiegel.de/schlagzeilen/tops/index.rss"
                    }
                    },
                    "greetings": {
                    "0": "Hallo "+ name +"!",
                    "1": "Gut siehst du aus",
                    "2": "Willkommen in der Nerd-Wohnung",
                    "3": "Lach doch mal..."
                    }
                },
                "email": username + "@flunkey.de",
                "name": name,
                "surname": surname,
                "username": username,
                "face_encoding": 
                { 
                    face_id: 
                    { "face_encoding": list(face) }
                },
                "image": file
            }
            response = requests.post(flunkey_api + "/config/user/" + username, json=create_user)
            if response.status_code == 200:
                logging.info('Training model for %s updated.', username)
            else:
               print(response)
        face_id += 1
logging.info('Training model completed.')


