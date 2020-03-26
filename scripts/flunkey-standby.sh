#!/bin/bash

# Global config
FLUNKEY_URL="http://flunkey:5000/system/standby"
DISPLAY_ID=7

# Get standby status
STANDBY_STATUS=$(curl -s $FLUNKEY_URL | jq -r '.status.standby')


if [ "$STANDBY_STATUS" = "0" ]
then 
    echo "Monitoring device is offline, turning off the hdmi signal."
    vcgencmd display_power 0 $DISPLAY_ID
else
    echo "Monitoring device is online, turning on the hdmi signal."
    vcgencmd display_power 1 $DISPLAY_ID
fi
