# Flunkey Utils
Utility Scripts and systemd unit files for the Flunkey Mirror

## Face Recognition
In the folder `face-rognition` you will find the scripts to use flunkeys face recognition. The recognition works with a raspberry pi camera connected via the PI's camera interface. 
The implementation is separated in two parts: Model training and Face Recognition itself. While the model training process the script takes all **.jpg** files in `known_faces` folder and generates numpy arrays with unique face encodings. It is important to give the image files correct names based on the schema `Name.Surname.jpg`. 

The script will take the file name, split it in variables and publish it via **flunkey-api** as a user object with an initial config and the generated **face_encoding** as an attribute in the database. The face_encoding give us the opportunity to compare each other and on match to determine which face in front of the camera.

### Dependencies
All software dependencies are defined in `debian.packages` and `python.packages`. Please install them with apt-get and pip3 and be patient. The dlib will need on a Pi4 about 20-30 Minutes. 

## Unit Files
In `system/unit_files` you will find all unit files for running flunkey. The units require that all the flunkey components are checked out in `/home/pi/flunkey/`. For this purpose you could check out the global **[Flunkey Mirror Repo](https://github.com/tgeci/flunkey)** with all the components as git submodules. 

Then you can copy the unit files from `system/unit_files` to `/etc/systemd/system/`, run the `systemctl daemon-reload` command and start the components in order that flunkey-api starts first. 

Don`t forget to enable them for autostart.

## Autostart of flunkey glass
Copy the the `LXDE-pi/autostart`file to `/home/pi/.config/lxsession/LXDE-pi/autostart` to start flunkey glass automatically. 