# HamShackRelayController

Name
==============
Ham Shack Relay Controller

Description
==============
Scott's GTK Python program for turning on/off relays for his ham radio shack using a Raspberry Pi and relay hats.

Installation
==============

Linux Packages and Apps
--------------
Requires the following:
- Thonny IDE
- Python 3 for base language
- GTK 3 for GUI
- GI
- Time for timer functions
- Piplates for relays

Making the app autostart
--------------
    sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
    add @python3 /home/pi/Documents/PythonApps/Source/Shack.py

That's it!