# HamShackRelayController

Description
==============
GTK Python program for turning on/off Pi-Plate relays for Scott's ham radio shack.

https://pi-plates.com/product/relayplate/

Installation
==============

Linux Packages and Apps
--------------
Requires the following:
- Python 3 (installed on RPi by default)
- Gtk 3
- gi
- pip
- pygame
- pi-plates

Commands:<br />
apt install gtk3 python3-gi python-pip<br />
(change to script directory)<br />
pip3 install pygame<br />
pip3 install pi-plates

Making the app autostart
--------------
    sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
    add @python3 /home/pi/Documents/PythonApps/HamShackRelayController/ShackController.py

IDE suggestions:
--------------
Python beginners:<br />
Thonny IDE<br />
https://thonny.org/<br />
apt install thonny

VIM<br />
https://www.vim.org/<br />
apt install vim

Visual Studio Code (add python extension from Microsoft)<br />
https://code.visualstudio.com/<br />
https://code.visualstudio.com/docs/setup/linux

How To
==============

View Logs
--------------
Logs are sent to syslog, so on Raspberry Pi OS they'll be in /var/log/messages

To follow it while you're using the app, use the following, but don't leave that open excessively. Ctrl-C to quit.
tail -f /var/log/messages

Change Colors and Sizes
--------------
All visual stuff is done in the main.css file. Because of the way the Gtk Grid works, the main way to affect button size is by changing the font and padding on the button CSS. Other changes are more obvious.

Disable a Button
--------------
In the ControlWindow class, find the block with the button you want to disable. Add the following code to the bottom of that block, changing the generic parts to match the actual button name and "off" method:

    self.devicenameButton.set_sensitive(False)
    self.turn_off_devicename()`

If the device is part of the perform_power_up method, be sure to comment out its lines of code.

Add a New Relay/Device
--------------
- Create a new variable in the arrays section toward the top.
- Create a new button in ControlWindow __init__, using an existing toggle button as an example.
- Create an "if" conditional in on_button_toggled
- Create a turn_on and turn_off method
- Add to power on and shutdown scripts if desired