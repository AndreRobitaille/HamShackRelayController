import os           # for shutdown
import sys          # lots of things
import time         # time.sleep delay between relays
import threading    # separate the relay changes from UI
import syslog       # logging to /var/log/messages
import gi           # GTK interface
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import pygame                       # Audio file playback
import piplates.RELAYplate as RELAY # Relay Rasberry Pi hats


# Logging goes to /var/log/messages
# Change level as necessary: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Anything below DEBUG needs to edit /etc/rsyslog.d/50-default.conf
# and uncomment the debug section, then restart the syslog service:
#   sudo service rsyslog restart
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))

# Initalize the pygame mixer for sounds. Doing it in this
# order supposedly shortens the delay before the sound plays
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()

# UI sounds we'll use repeatedly
clickSound = pygame.mixer.Sound("Sounds/click.wav")
completedSound = pygame.mixer.Sound("Sounds/completed.wav")
syslog.syslog(syslog.LOG_INFO, "Pygame initialized and sounds loaded")

# Occasionally need to mute redundant interface clicks and completed sounds
global suppressSounds
suppressSounds = True  # Start quietly

# Create arrays for each relay (plate address, relay address)
leftSpeakerMuteRelay = 0, 1
rightSpeakerMuteRelay = 0, 2
auxDevicesRelay = 0, 3
yaesu7900Relay = 0, 4
thermalControlRelay = 0, 5
icom7300Relay = 0, 6
ameritronRelay = 0, 7
powerSupplyRelay = 1, 1
dualMonitorRelay = 1, 2
lightsRelay = 1, 3
yaesu101Relay = 1, 4
audioSystemRelay = 1, 5
# 1,6 unused
# 1,7 unused

# Plate addresses
plate12vdc = 0
plate120vac = 1
allPlates = 2   # Not really 2. This must be manually translated in the method


class RelayShim: 
    """Class to extend Pi-Plates relay functionality."""

    def get_relay_state(relayAddress, relayPosition):
        """Retreive and return the state of a specific relay."""

        # Convert the 7 bit number to binary string and reverse the string
        entirePlateState = f'{RELAY.relaySTATE(relayAddress):07b}'[::-1]
        relayPositionString = entirePlateState[relayPosition - 1]
        if relayPositionString == "0":
            relayPositionBoolean = False
        elif relayPositionString == "1":
            relayPositionBoolean = True

        syslog.syslog(syslog.LOG_DEBUG, f"Relay state polled. {entirePlateState}")
        return relayPositionBoolean

    def immediate_shutoff(self, plate):
        """Something is wrong or we want to initalize plates."""
        if plate < 2:                   # Not both plates
            RELAY.RESET(plate)
            syslog.syslog(syslog.LOG_DEBUG, f"Plate {plate} relays shut off")

        elif plate == 2:                # Both plates
            RELAY.RESET(plate12vdc)
            RELAY.RESET(plate120vac)
            syslog.syslog(syslog.LOG_DEBUG, f"Relays on both plates shut off")

        else:                           # Not used, but could be an emergency
                                        # kill everything and quit button
            RELAY.RESET(plate12vdc)
            RELAY.RESET(plate120vac)
            syslog.syslog(syslog.LOG_DEBUG, f"Relays on both plates shut off and quit application")
            sys.exit()


class TerminationWindow(Gtk.Window):
    """Popup window if we have to force the application to quit."""
    def __init__(self):
        """Initalize the termination window."""
        super().__init__(title="Application Error")

    def create_error_window(self, errorMessage):
        """Create an error window and display the message passed as an argument."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Program Must Terminate",
        )
        dialog.format_secondary_text(errorMessage)
        dialog.run()
        dialog.destroy()


class ControlWindow(Gtk.Window):
    """Creates the controller main window and buttons."""

    def __init__(self):
        """Builds the window and buttons for the view."""
        super().__init__(title="Shack System Controller")

        self.apply_css()
        self.set_border_width(10)

        # Grid creation and button placement
        # Check state of relays and make toggle buttons match
        grid = Gtk.Grid()
        
        normalShutdownButton = Gtk.Button(label="Normal\nShutdown")
        normalShutdownButton.connect("clicked", self.on_button_clicked, 
                                     "normalShutdown")
        grid.add(normalShutdownButton)
        
        autoPowerUpButton = Gtk.Button(label="Auto\nPower\nUp")
        autoPowerUpButton.connect("clicked", self.on_button_clicked, 
                                  "autoPowerUp")
        grid.attach_next_to(autoPowerUpButton, normalShutdownButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        fullShutdownButton = Gtk.Button(label="Full\nShut\nDown")
        fullShutdownButton.connect("clicked", self.on_button_clicked, 
                                   "fullShutdown")
        grid.attach_next_to(fullShutdownButton, autoPowerUpButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.muteAudioButton = Gtk.ToggleButton(label="Mute\nAudio")
        self.muteAudioButton.connect("toggled", self.on_button_toggled, 
                                     "muteAudio")
        grid.attach_next_to(self.muteAudioButton, fullShutdownButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        # Setting state for mute is weird becuase there are two relays
        # and the state is the opposite of what you'd expect.
        # Extra method added in case the relays don't match.
        relayState = RelayShim.get_relay_state(*leftSpeakerMuteRelay)
        relayState2 = RelayShim.get_relay_state(*rightSpeakerMuteRelay)
        if relayState == False or relayState2 == False:
            self.muteAudioButton.set_active(True)
            self.mute_audio()
        else:
            self.muteAudioButton.set_active(False)
            self.unmute_audio()

        self.lightsButton = Gtk.ToggleButton(label="Lights")
        self.lightsButton.connect("toggled", self.on_button_toggled, "lights")
        grid.attach_next_to(self.lightsButton, self.muteAudioButton,
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*lightsRelay)
        self.lightsButton.set_active(relayState)

        self.audioSystemButton = Gtk.ToggleButton(label="Audio\nSystem")
        self.audioSystemButton.connect("toggled", self.on_button_toggled, 
                                       "audioSystem")
        grid.attach_next_to(self.audioSystemButton, self.lightsButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*audioSystemRelay)
        self.audioSystemButton.set_active(relayState)

        self.powerSupplyButton = Gtk.ToggleButton(label="12VDC\nPower")
        self.powerSupplyButton.connect("toggled", self.on_button_toggled, 
                                       "powerSupply")
        grid.attach_next_to(self.powerSupplyButton, normalShutdownButton, 
                            Gtk.PositionType.BOTTOM, 1, 1)
        relayState = RelayShim.get_relay_state(*powerSupplyRelay)
        self.powerSupplyButton.set_active(relayState)

        self.dualMonitorButton = Gtk.ToggleButton(label="Dual\nMonitor")
        self.dualMonitorButton.connect("toggled", self.on_button_toggled, 
                                       "dualMonitor")
        grid.attach_next_to(self.dualMonitorButton, self.powerSupplyButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*dualMonitorRelay)
        self.dualMonitorButton.set_active(relayState)

        self.auxDevicesButton = Gtk.ToggleButton(label="Aux\nDevices")
        self.auxDevicesButton.connect("toggled", self.on_button_toggled, 
                                      "auxDevices")
        grid.attach_next_to(self.auxDevicesButton, self.dualMonitorButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*auxDevicesRelay)
        self.auxDevicesButton.set_active(relayState)

        self.thermalControlButton = Gtk.ToggleButton(label="Thermal\nControl")
        self.thermalControlButton.connect("toggled", self.on_button_toggled, 
                                          "thermalControl")
        grid.attach_next_to(self.thermalControlButton, self.auxDevicesButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*thermalControlRelay)
        self.thermalControlButton.set_active(relayState)

        self.yaesu101Button = Gtk.ToggleButton(label="HF-1\nYaesu\n101MP")
        self.yaesu101Button.connect("toggled", self.on_button_toggled, 
                                    "yaesu101")
        grid.attach_next_to(self.yaesu101Button, self.thermalControlButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*yaesu101Relay)
        self.yaesu101Button.set_active(relayState)

        self.icom7300Button = Gtk.ToggleButton(label="HF-2\nIcom\n7300")
        self.icom7300Button.connect("toggled", self.on_button_toggled, 
                                    "icom7300")
        grid.attach_next_to(self.icom7300Button, self.yaesu101Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*icom7300Relay)
        self.icom7300Button.set_active(relayState)
        self.icom7300Button.set_sensitive(False) # Disable icom 7300 button
        self.turn_off_icom_7300()                # Turn off icom 7300 relay

        self.yaesu7900Button = Gtk.ToggleButton(label="VHF\nYaesu\n7900")
        self.yaesu7900Button.connect("toggled", self.on_button_toggled, 
                                     "yaesu7900")
        grid.attach_next_to(self.yaesu7900Button, self.icom7300Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        relayState = RelayShim.get_relay_state(*yaesu7900Relay)
        self.yaesu7900Button.set_active(relayState)

        self.ameritronButton = Gtk.ToggleButton(label="Amplifier\nAmeritron\nALS-1300")
        self.ameritronButton.connect("toggled", self.on_button_toggled, 
                                     "ameritron")
        grid.attach_next_to(self.ameritronButton, self.powerSupplyButton, 
                            Gtk.PositionType.BOTTOM, 1, 1)
        relayState = RelayShim.get_relay_state(*ameritronRelay)
        self.ameritronButton.set_active(relayState)

        # Extra buttons to fit the original layout.
        extraRelay1Button = Gtk.Button()
        grid.attach_next_to(extraRelay1Button, self.ameritronButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay1Button.set_sensitive(False)
        extraRelay2Button = Gtk.Button()
        grid.attach_next_to(extraRelay2Button, extraRelay1Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay2Button.set_sensitive(False)
        extraRelay3Button = Gtk.Button()
        grid.attach_next_to(extraRelay3Button, extraRelay2Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay3Button.set_sensitive(False)
        extraRelay4Button = Gtk.Button()
        grid.attach_next_to(extraRelay4Button, extraRelay3Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay4Button.set_sensitive(False)

        fullSystemShutdownButton = Gtk.Button(label="Full\nSystem\nShutdown")
        fullSystemShutdownButton.connect("clicked", self.on_button_clicked, 
                                         "fullSystemShutdown")
        grid.attach_next_to(fullSystemShutdownButton, extraRelay4Button, 
                            Gtk.PositionType.RIGHT, 1, 1)

        exitToOsButton = Gtk.Button(label="Exit to OS")
        exitToOsButton.connect("clicked", self.on_button_clicked, "exitToOs")
        grid.attach_next_to(exitToOsButton, fullSystemShutdownButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.add(grid)
        self.fullscreen()
        syslog.syslog(syslog.LOG_DEBUG, "Grid and buttons created")

        self.lightsButton.set_active(True) # Turn on the lights
        
        global suppressSounds
        suppressSounds = False # Turn audio back on now that the UI is built

        self.connect("realize", self.on_realize)
        GLib.timeout_add(interval=5000, function=self.reset_cursor)

    def on_realize(self, widget):
        # Step 1: Get the Gdk.Display for the toplevel for this widget.
        display = widget.get_display()

        # Step 2: Create a new Cursor of type BLANK_CURSOR
        cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)

        # Step 3: Get the widget’s Gdk.Window and set the new Cursor
        widget.get_window().set_cursor(cursor)

    def reset_cursor(self):
        cursor = Gdk.Cursor.new_from_name(self.get_display(), 'default')
        self.get_window().set_cursor(cursor)

    def on_button_toggled(self, button, buttonName):
        """Button was toggled. Figure out which button and do something."""
        if suppressSounds != True:
            time.sleep(0.6) # Wait for the click sound to be ready to play
            self.play_sound(clickSound)
        
        if buttonName == "lights":
            if button.get_active():
                self.turn_on_lights()
            else:
                self.turn_off_lights()

        if buttonName == "muteAudio":
            if button.get_active():
                self.mute_audio()
            else:
                self.unmute_audio()

        if buttonName == "audioSystem":
            if button.get_active():
                self.turn_on_audio_system()
            else:
                self.turn_off_audio_system()

        if buttonName == "powerSupply":
            if button.get_active():
                self.turn_on_power_supply()
            else:
                self.turn_off_power_supply()

        if buttonName == "dualMonitor":
            if button.get_active():
                self.turn_on_dual_monitor()
            else:
                self.turn_off_dual_monitor()

        if buttonName == "auxDevices":
            if button.get_active():
                self.turn_on_aux_devices()
            else:
                self.turn_off_aux_devices()

        if buttonName == "thermalControl":
            if button.get_active():
                self.turn_on_thermal_control()
            else:
                self.turn_off_thermal_control()

        if buttonName == "yaesu101":
            if button.get_active():
                self.turn_on_yaesu_101()
            else:
                self.turn_off_yaesu_101()

        if buttonName == "icom7300":
            if button.get_active():
                self.turn_on_icom_7300()
            else:
                self.turn_off_icom_7300()

        if buttonName == "yaesu7900":
            if button.get_active():
                self.turn_on_yaesu_7900()
            else:
                self.turn_off_yaesu_7900()

        if buttonName == "ameritron":
            if button.get_active():
                self.turn_on_ameritron()
            else:
                self.turn_off_ameritron()

        # Only used for debug logging
        if button.get_active():
            state = "on"
        else:
            state = "off"
        syslog.syslog(syslog.LOG_DEBUG, f"Button {buttonName} was turned {state}")

    def on_button_clicked(self, button, buttonName):
        """Standard button was pressed. Probably starts toggling other buttons."""
        if suppressSounds != True:
            time.sleep(0.6) # Wait for the click sound to be ready to play
            self.play_sound(clickSound)
        
        # Use threads or the UI won't update until after everything is done
        if buttonName == "normalShutdown":
            buttonThread = threading.Thread(target=self.perform_normal_shutdown, args=())
            buttonThread.start()
        if buttonName == "autoPowerUp":
            buttonThread = threading.Thread(target=self.perform_power_up, args=())
            buttonThread.start()
        if buttonName == "fullShutdown":
            buttonThread = threading.Thread(target=self.perform_full_shutdown, args=())
            buttonThread.start()
        if buttonName == "fullSystemShutdown":
            buttonThread = threading.Thread(target=self.perform_full_system_shutdown, args=())
            buttonThread.start()
        if buttonName == "exitToOs":
            self.exit_to_os()

    def turn_on_lights(self):
        """Turn on the lights."""
        RELAY.relayON(*lightsRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Lights were turned on")

    def turn_off_lights(self):
        """Turn off the lights."""
        RELAY.relayOFF(*lightsRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Lights were turned off")

    def turn_on_audio_system(self):
        """Turn on the audio system."""
        RELAY.relayON(*audioSystemRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Audio system was turned on")

    def turn_off_audio_system(self):
        """Turn off the audio system."""
        RELAY.relayOFF(*audioSystemRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Audio system was turned off")

    def turn_on_power_supply(self):
        """Turn on the 12VDC power supply."""
        RELAY.relayON(*powerSupplyRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "12VDC power supply was turned on")

    def turn_off_power_supply(self):
        """Turn off the 12VDC power supply."""
        RELAY.relayOFF(*powerSupplyRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "12VDC power supply was turned off")

    def turn_on_dual_monitor(self):
        """Turn on the dual monitor."""
        RELAY.relayON(*dualMonitorRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Dual monitor was turned on")

    def turn_off_dual_monitor(self):
        """Turn off the dual monitor."""
        RELAY.relayOFF(*dualMonitorRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Dual monitor was turned off")

    def mute_audio(self):
        """Mute audio on left and right channels. Relays off."""
        RELAY.relayOFF(*leftSpeakerMuteRelay)
        RELAY.relayOFF(*rightSpeakerMuteRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Left and right audio was muted")
    
    def unmute_audio(self):
        """Unmute audio on left and right channels. Relays on."""
        RELAY.relayON(*leftSpeakerMuteRelay)
        RELAY.relayON(*rightSpeakerMuteRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Left and right audio was unmuted")

    def turn_on_ameritron(self):
        """Turn on the Ameritron amplifier."""
        RELAY.relayON(*ameritronRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Ameritron amplifier was turned on")

    def turn_off_ameritron(self):
        """Turn off the Ameritron amplifier."""
        RELAY.relayOFF(*ameritronRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Ameritron amplifier was turned off")

    def turn_on_aux_devices(self):
        """Turn on the auxilary devices."""
        RELAY.relayON(*auxDevicesRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Auxilary devices were turned on")

    def turn_off_aux_devices(self):
        """Turn off the auxilary devices."""
        RELAY.relayOFF(*auxDevicesRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Auxilary devices were turned off")

    def turn_on_thermal_control(self):
        """Turn on the thermal control."""
        RELAY.relayON(*thermalControlRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Thermal control was turned on")

    def turn_off_thermal_control(self):
        """Turn off the thermal control."""
        RELAY.relayOFF(*thermalControlRelay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Thermal control was turned off")

    def turn_on_yaesu_101(self):
        """Turn on the Yaesu 101."""
        RELAY.relayON(*yaesu101Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Yaesu 101 was turned on")

    def turn_off_yaesu_101(self):
        """Turn off the Yaesu 101."""
        RELAY.relayOFF(*yaesu101Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Yaesu 101 was turned off")

    def turn_on_icom_7300(self):
        """Turn on the Icom 7300."""
        RELAY.relayON(*icom7300Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Icom 7300 was turned on")

    def turn_off_icom_7300(self):
        """Turn off the Icom 7300."""
        RELAY.relayOFF(*icom7300Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Icom 7300 was turned off")

    def turn_on_yaesu_7900(self):
        """Turn on the Yaesu 7900."""
        RELAY.relayON(*yaesu7900Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Yaesu 7900 was turned on")

    def turn_off_yaesu_7900(self):
        """Turn off the Yaesu 7900."""
        RELAY.relayOFF(*yaesu7900Relay)
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Yaesu 7900 was turned off")

    def perform_power_up(self):
        """Power up all the normal systems."""
        global suppressSounds
        suppressSounds = True # Supress sounds; we're about to press buttons
        while pygame.mixer.get_busy():  # Click sound needs to finish
            continue

        if not self.audioSystemButton.get_active():
            self.audioSystemButton.set_active(True)
            time.sleep(1)
        if self.muteAudioButton.get_active():
            self.muteAudioButton.set_active(False)
            time.sleep(1)
        if not self.lightsButton.get_active():
            self.lightsButton.set_active(True)
            time.sleep(1)
        if not self.powerSupplyButton.get_active():
            self.powerSupplyButton.set_active(True)
            time.sleep(3)
        if not self.dualMonitorButton.get_active():
            self.dualMonitorButton.set_active(True)
            time.sleep(1)
        if not self.yaesu101Button.get_active():
            self.yaesu101Button.set_active(True)
            time.sleep(1)
        
        # 7300 commented out
        #if not self.icom7300Button.get_active():
            #self.icom7300Button.set_active(True)
            #time.sleep(1)
        
        if not self.auxDevicesButton.get_active():
            self.auxDevicesButton.set_active(True)
            time.sleep(1)
        if not self.yaesu7900Button.get_active():
            self.yaesu7900Button.set_active(True)
            time.sleep(1)
        if not self.thermalControlButton.get_active():
            self.thermalControlButton.set_active(True)
        
        suppressSounds = False # Play sounds again now that we're done pressing buttons
        self.play_sound(completedSound)
        syslog.syslog(syslog.LOG_DEBUG, "Completed auto power up")

    def perform_normal_shutdown(self):
        """Normal Shutdown - turn off all power relays with time delay."""
        global suppressSounds
        suppressSounds = True # Supress sounds; we're about to press buttons
        while pygame.mixer.get_busy():  # Click sound needs to finish
            continue

        self.auxDevicesButton.set_active(False)
        time.sleep(0.5)
        self.yaesu7900Button.set_active(False)
        time.sleep(0.5)
        self.thermalControlButton.set_active(False)
        time.sleep(0.5)
        self.icom7300Button.set_active(False)
        time.sleep(0.5)
        self.ameritronButton.set_active(False)
        time.sleep(0.5)
        self.dualMonitorButton.set_active(False)
        time.sleep(0.5)
        
        # Leave lights on
        #self.lightsButton.set_active(False)
        #time.sleep(0.5)

        self.yaesu101Button.set_active(False)
        time.sleep(0.5)
        self.powerSupplyButton.set_active(False)
        time.sleep(0.5)

        # Play completion sound before shutting off audio system
        suppressSounds = False # Play sounds again now that we're done pressing buttons
        self.play_sound(completedSound)
        while pygame.mixer.get_busy():  # Complete sound needs to finish
            continue

        self.muteAudioButton.set_active(True)
        time.sleep(0.5)
        self.audioSystemButton.set_active(False)
        
        syslog.syslog(syslog.LOG_DEBUG, "Completed normal shutdown")

    def perform_full_shutdown(self):
        """Full Shutdown - turn off all power relays with time delay."""
        global suppressSounds
        suppressSounds = True # Supress sounds; we're about to press buttons
        while pygame.mixer.get_busy():  # Click sound needs to finish
            continue

        self.auxDevicesButton.set_active(False)
        time.sleep(0.5)
        self.yaesu7900Button.set_active(False)
        time.sleep(0.5)
        self.thermalControlButton.set_active(False)
        time.sleep(0.5)
        self.icom7300Button.set_active(False)
        time.sleep(0.5)
        self.ameritronButton.set_active(False)
        time.sleep(0.5)
        self.dualMonitorButton.set_active(False)
        time.sleep(0.5)
        self.lightsButton.set_active(False)
        time.sleep(0.5)
        self.yaesu101Button.set_active(False)
        time.sleep(0.5)
        self.powerSupplyButton.set_active(False)
        time.sleep(0.5)

        # Play completion sound before shutting off audio system
        suppressSounds = False # Play sounds again now that we're done pressing buttons
        self.play_sound(completedSound)
        while pygame.mixer.get_busy():  # Complete sound needs to finish
            continue
        
        self.muteAudioButton.set_active(True)
        time.sleep(0.5)
        self.audioSystemButton.set_active(False)
        
        syslog.syslog(syslog.LOG_DEBUG, "Completed full shutdown")

    def perform_full_system_shutdown(self):
        """Full System Shutdown - turn off all power relays with time delay and then computer."""
        global suppressSounds
        suppressSounds = True # Supress sounds; we're about to press buttons
        while pygame.mixer.get_busy():  # Click sound needs to finish
            continue

        self.auxDevicesButton.set_active(False)
        time.sleep(0.5)
        self.yaesu7900Button.set_active(False)
        time.sleep(0.5)
        self.thermalControlButton.set_active(False)
        time.sleep(0.5)
        self.icom7300Button.set_active(False)
        time.sleep(0.5)
        self.ameritronButton.set_active(False)
        time.sleep(0.5)
        self.dualMonitorButton.set_active(False)
        time.sleep(0.5)
        self.lightsButton.set_active(False)
        time.sleep(0.5)
        self.yaesu101Button.set_active(False)
        time.sleep(0.5)
        self.powerSupplyButton.set_active(False)
        time.sleep(0.5)

        # Play completion sound before shutting off audio system
        suppressSounds = False # Play sounds again now that we're done pressing buttons
        self.play_sound(completedSound)
        while pygame.mixer.get_busy():  # Complete sound needs to finish
            continue
        
        self.muteAudioButton.set_active(True)
        time.sleep(0.5)
        self.audioSystemButton.set_active(False)
        
        syslog.syslog(syslog.LOG_DEBUG, "Completed full system shutdown")

        os.system("sudo halt")

    def exit_to_os(self):
        sys.exit()

    def play_sound(self, sound):
        """Play a sound using pygame but don't wait for it to complete."""
        global suppressSounds
        if suppressSounds:
            return  # We've said somewhere to not play audio at this time. 
        while pygame.mixer.get_busy():
            continue
        pygame.mixer.Sound.play(sound)
        
    def apply_css(self):
        """Reads the CSS file so that it can be applied to the view."""
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path('main.css')
            context = Gtk.StyleContext()
            context.add_provider_for_screen(screen, css_provider,
                                            Gtk.STYLE_PROVIDER_PRIORITY_USER)
            syslog.syslog(syslog.LOG_INFO, "CSS applied")
        except GLib.Error as e:
            syslog.syslog(syslog.LOG_ERR, f"CSS application failed {e}")


# Test for relay board fail before doing anything else, and quit if anything fails
if RELAY.getADDR(plate12vdc) != plate12vdc and RELAY.getADDR(plate120vac) != plate120vac:
    errorDialogMessage = ("Can't start application. Neither relay plate is responding.")
    errorWin = TerminationWindow()
    errorWin.create_error_window(errorDialogMessage)
    syslog.syslog(syslog.LOG_ERR, "Neither relay plate is responding - terminating program")
    sys.exit()
elif RELAY.getADDR(plate120vac) != plate120vac:
    errorDialogMessage = ("Can't start application. 120VAC relay plate not responding.")
    errorWin = TerminationWindow()
    errorWin.create_error_window(errorDialogMessage)
    syslog.syslog(syslog.LOG_ERR, "12vcd relay plate not responding - terminating program")
    sys.exit()
elif RELAY.getADDR(plate120vac) != plate120vac:
    errorDialogMessage = ("Can't start application. 12VDC relay plate not responding.")
    errorWin = TerminationWindow()
    errorWin.create_error_window(errorDialogMessage)
    syslog.syslog(syslog.LOG_ERR, "12vcd relay plate not responding - terminating program")
    sys.exit()


win = ControlWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
