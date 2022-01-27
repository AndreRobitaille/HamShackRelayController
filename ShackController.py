import sys
import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import pygame
#import piplates.RELAYplate as RELAY
import threading
import syslog

# Logging goes to /var/log/messages
# Change level as necessary: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Anything below DEBUG needs to edit /etc/rsyslog.d/50-default.conf
# and uncomment the debug section, then restart the syslog service:
#   sudo service rsyslog restart

syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))


# Initalize the pygame mixer for sounds. Doing it in this
# order supposedly shortens the delay before the sound plays.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
clickSound = pygame.mixer.Sound("Sounds/click.wav")
completedSound = pygame.mixer.Sound("Sounds/completed.wav")
syslog.syslog(syslog.LOG_INFO, "Pygame initialized and sounds loaded")

global suppressSounds
suppressSounds = False  # Avoids playing UI sounds when true.


# Relay Arrays
leftSpeakerMute = 0, 1
rightSpeakerMute = 0, 2
auxDevices = 0, 3
yaesu7900 = 0, 4
thermalControl = 0, 5
icom7300 = 0, 6
ameritron = 0, 7
powerSupply = 1, 1
dualMonitor = 1, 2
lights = 1, 3
yaesu101 = 1, 4
audioSystem = 1, 5
# 1,6 unused
# 1,7 unused


# Plate addresses
plate12vdc = 0
plate120vac = 1
allPlates = 2   # Not really 2. This must be manually translated in the method.


# Check that relay plates are working or fail.
#if RELAY.getADDR(plate12vdc) != plate12vdc:
#    syslog.syslog(syslog.LOG_ERROR, "12vcd relay plate not responding.")
#    sys.exit()
#if RELAY.getADDR(plate120vac) != plate120vac:
#    syslog.syslog(syslog.LOG_ERROR, "120vac relay plate not responding.")
#    sys.exit()


class RelayShim: 
    """Class to extend Pi-Plates relay functionality"""

    def immediate_shutoff(self, plate):
        """Something is wrong or we want to initalize plates."""
        if plate < 2:
            RELAY.RESET(plate)
        elif plate == 2:
            RELAY.RESET(plate12vdc)
            RELAY.RESET(plate120vac)
        else:                           #Must be emergency. Kill everything.
            RELAY.RESET(plate12vdc)
            RELAY.RESET(plate120vac)
            quit()


class ControlWindow(Gtk.Window):
    """Main class that creates the controller window."""

    def __init__(self):
        """Builds the window and buttons for the view."""
        super().__init__(title="Shack System Controller")

        self.apply_css()
        
        self.set_border_width(10)

        grid = Gtk.Grid()
        
        # Button creation.
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

        self.lightsButton = Gtk.ToggleButton(label="Lights")
        self.lightsButton.connect("toggled", self.on_button_toggled, "lights")
        grid.attach_next_to(self.lightsButton, self.muteAudioButton,
                            Gtk.PositionType.RIGHT, 1, 1)

        self.audioSystemButton = Gtk.ToggleButton(label="Audio\nSystem")
        self.audioSystemButton.connect("toggled", self.on_button_toggled, 
                                       "audioSystem")
        grid.attach_next_to(self.audioSystemButton, self.lightsButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.powerSupplyButton = Gtk.ToggleButton(label="12VDC\nPower")
        self.powerSupplyButton.connect("toggled", self.on_button_toggled, 
                                       "powerSupply")
        grid.attach_next_to(self.powerSupplyButton, normalShutdownButton, 
                            Gtk.PositionType.BOTTOM, 1, 1)

        self.dualMonitorButton = Gtk.ToggleButton(label="Dual\nMonitor")
        self.dualMonitorButton.connect("toggled", self.on_button_toggled, 
                                       "dualMonitor")
        grid.attach_next_to(self.dualMonitorButton, self.powerSupplyButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.auxDevicesButton = Gtk.ToggleButton(label="Aux\nDevices")
        self.auxDevicesButton.connect("toggled", self.on_button_toggled, 
                                      "auxDevices")
        grid.attach_next_to(self.auxDevicesButton, self.dualMonitorButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.thermalControlButton = Gtk.ToggleButton(label="Thermal\nControl")
        self.thermalControlButton.connect("toggled", self.on_button_toggled, 
                                          "thermalControl")
        grid.attach_next_to(self.thermalControlButton, self.auxDevicesButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.yaesu101Button = Gtk.ToggleButton(label="HF-1\nYaesu\n101MP")
        self.yaesu101Button.connect("toggled", self.on_button_toggled, 
                                    "yaesu101")
        grid.attach_next_to(self.yaesu101Button, self.thermalControlButton, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.icom7300Button = Gtk.ToggleButton(label="HF-2\nIcom\n7300")
        self.icom7300Button.connect("toggled", self.on_button_toggled, 
                                    "icom7300")
        grid.attach_next_to(self.icom7300Button, self.yaesu101Button, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.yaesu7900Button = Gtk.ToggleButton(label="VHF\nYaesu\n7900")
        self.yaesu7900Button.connect("toggled", self.on_button_toggled, 
                                     "yaesu7900")
        grid.attach_next_to(self.yaesu7900Button, self.icom7300Button, 
                            Gtk.PositionType.RIGHT, 1, 1)

        self.ameritronButton = Gtk.ToggleButton(label="Amplifier\nAmeritron\nALS-1300")
        self.ameritronButton.connect("toggled", self.on_button_toggled, 
                                     "ameritron")
        grid.attach_next_to(self.ameritronButton, self.powerSupplyButton, 
                            Gtk.PositionType.BOTTOM, 1, 1)

        # Extra buttons to fit the original layout.
        extraRelay1Button = Gtk.Button()
        grid.attach_next_to(extraRelay1Button, self.ameritronButton, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay2Button = Gtk.Button()
        grid.attach_next_to(extraRelay2Button, extraRelay1Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay3Button = Gtk.Button()
        grid.attach_next_to(extraRelay3Button, extraRelay2Button, 
                            Gtk.PositionType.RIGHT, 1, 1)
        extraRelay4Button = Gtk.Button()
        grid.attach_next_to(extraRelay4Button, extraRelay3Button, 
                            Gtk.PositionType.RIGHT, 1, 1)


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

    def on_button_toggled(self, button, buttonName):
        """Button was toggled. Figure out which button and do something."""
        if suppressSounds != True:
            time.sleep(0.6) #Wait for the click sound to be ready to play.
            self.play_sound(clickSound)
        if button.get_active():
#            RELAY.relayON(relayName)
            state = "on"
        else:
#            RELAY.relayOFF(relayName)
            state = "off"
        
#        if isinstance(relayName, str):
        if buttonName == "muteAudio":
            if button.get_active():
                self.mute_audio()
            else:
                self.unmute_audio()

        #self.play_sound(completedSound) #This should play after doing something, 
                                         #not after button press.
        print("Button", buttonName, "was turned", state)

    def on_button_clicked(self, button, buttonName):
        """Standard button was pressed. Probably starts toggling other buttons."""
        if suppressSounds != True:
            time.sleep(0.6) #Wait for the click sound to be ready to play.
            self.play_sound(clickSound)
        if buttonName == "normalShutdown":
            self.perform_normal_shutdown()
        if buttonName == "autoPowerUp":
            buttonThread = threading.Thread(target=self.perform_power_up, args=())
            buttonThread.start()
        if buttonName == "exitToOs":
            sys.exit()

    def perform_normal_shutdown(self):
        """Normal Shutdown - turn off all power relays with time delay."""
        #shutoff relays here
        print("Completed normal shutdown")

    def perform_power_up(self):
        """Power up all the normal systems."""
        global suppressSounds
        suppressSounds = True #Supress sounds; we're about to press buttons.
        time.sleep(.4)        #Wait for sound to finish before pushing buttons.

        #turn on relays here
        #1,5 audio - button down
        self.audioSystemButton.set_active(True)
        time.sleep(1)

        #unmute audio
        #0,1 left speaker mute - mute button up
        #0,2 right speaker mute - see above
        self.muteAudioButton.set_active(False)
        time.sleep(1)
        
        #lights on
        #1,3 lights - button down
        self.lightsButton.set_active(True)
        time.sleep(1)
        
        #power supply on
        #1,1 power supply - button down
        self.powerSupplyButton.set_active(True)
        time.sleep(1)
        
        #dual monitor on
        #1,2 dual monitor - button down
        self.dualMonitorButton.set_active(True)
        time.sleep(1)
        
        #101mp on
        #1,4 101mp - button down
        self.yaesu101Button.set_active(True)
        time.sleep(1)
        
        #leave off
        #1,6 nothing ???
        #1,7 nothing ???
        
        #7300 commented out
        #0,6 7300 - commented out
        #self.icom7300Button.set_active(True)
        #time.sleep(1)
        
        # aux on
        #0,3 aux - button down
        self.auxDevicesButton.set_active(True)
        time.sleep(1)
        
        # 7900 on
        #0,4 7900 - button down
        self.yaesu7900Button.set_active(True)
        time.sleep(1)
        
        # thermal on
        #0,5 thermal - button down
        self.thermalControlButton.set_active(True)
        
        #RELAY.relayON(*)
       
        suppressSounds = False #Play sounds again now that we're done pressing buttons.
        self.play_sound(completedSound)
        print("Completed auto power up")

    def mute_audio(self):
        """Mute audio on left and right channels. Relays off."""
        #shutoff relays here
        # off 0,1
        # off 0,2
    
    def unmute_audio(self):
        """Unmute audio on left and right channels. Relays on."""
        #turn on relays here
        # on 0,1
        # on 0,2

    def play_sound(self, sound):
        """Plays a sound using pygame but don't wait before moving on."""
        global suppressSounds
        if suppressSounds:
            return #We've said somewhere to not play audio at this time. 
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
            print(f"Applied CSS.")
        except GLib.Error as e:
            print(f"Error in theme: {e} ")


win = ControlWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

