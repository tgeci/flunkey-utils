#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority
cd /home/pi/flunkey/flunkey-glass && npm run flunkey
