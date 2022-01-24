import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os as SYSTEM
import time
import piplates.RELAYplate as RELAY
import pygame

# Pygame for audio
pygame.mixer.init()
pygame.mixer.music.load("Sounds/click.wav")
RELAY.getID(0)

# Relay Key:
# 0,1 Left Speaker Mute
# 0,2 Right Speaker Mute
# 0,3 Auxiliary Devices
# 0,4 Yaesu 7900
# 0,5 Thermal Control
# 0,6 HF-2 7300
# 0,7 ameritron amplifier
# 1,1 12VDC Power Supply
# 1,2 Dual Monitor
# 1,3 Lights
# 1,4 HF -1 Yaesu 101MP
# 1,5 Audio System
# 1,6 unused
# 1,7 unused

# Initalize 12VDC relays off
#RELAY.relayOFF(0, 1)
#RELAY.relayOFF(0, 2)
#RELAY.relayOFF(0, 3)
#RELAY.relayOFF(0, 4)
#RELAY.relayOFF(0, 5)
#RELAY.relayOFF(0, 6)
#RELAY.relayOFF(0, 7)

# Initialize 120VAC relays off
#RELAY.relayOFF(1, 1)
#RELAY.relayOFF(1, 2)
#RELAY.relayOFF(1, 3)
#RELAY.relayOFF(1, 4)
#RELAY.relayOFF(1, 5)
#RELAY.relayOFF(1, 6)
#RELAY.relayOFF(1, 7)

# Turn on lights
RELAY.relayON(1, 3)


class Relay_Control_Window(Gtk.Window):
    """Uber class that contains everything"""

    def __init__(self):
        """Builds the view window and buttons"""
        Gtk.Window.__init__(self, title="KC9WPS Shack Device Controller")
        grid = Gtk.Grid()
        self.add(grid)
        self.fullscreen()

        button100 = Gtk.ToggleButton(label="Normal\nShutdown")
        grid.add(button100)
        button100.connect("toggled", self.on_button_toggled100,"100")

        button110 = Gtk.ToggleButton(label="Auto\nPower\nUp")
        grid.attach_next_to(button110, button100, Gtk.PositionType.RIGHT, 1, 1)
        button110.connect("toggled", self.on_button_toggled110, "110")

        button120 = Gtk.ToggleButton(label="Full\nShut \nDown")
        grid.attach_next_to(button120, button110, Gtk.PositionType.RIGHT, 1, 1)
        button120.connect("toggled", self.on_button_toggled120, "120")

        button130 = Gtk.ToggleButton(label="Mute\nAudio")
        grid.attach_next_to(button130, button120, Gtk.PositionType.RIGHT, 1, 1)
        button130.connect("toggled",self.on_button_toggled130,"130")

        button140 = Gtk.ToggleButton(label="Lights\nOn")
        grid.attach_next_to(button140, button130, Gtk.PositionType.RIGHT, 1, 1)
        button140.connect("toggled", self.on_button_toggled140, "140")

        button150 = Gtk.ToggleButton(label="Audio\nSystem")
        grid.attach_next_to(button150, button140, Gtk.PositionType.RIGHT, 1, 1)
        button150.connect("toggled", self.on_button_toggled150, "150")

        button3 = Gtk.ToggleButton(label="12VDC\nPower")
        grid.attach_next_to(button3, button100, Gtk.PositionType.BOTTOM, 1, 1)
        button3.connect("toggled", self.on_button_toggled3, "3")

        button4 = Gtk.ToggleButton(label="Dual\nMonitor")
        grid.attach_next_to(button4, button3, Gtk.PositionType.RIGHT, 1, 1)
        button4.connect("toggled", self.on_button_toggled4, "4")

        button5 = Gtk.ToggleButton(label="Aux\nDevices")
        grid.attach_next_to(button5, button4, Gtk.PositionType.RIGHT, 1, 1)
        button5.connect("toggled", self.on_button_toggled5, "5")

        button6 = Gtk.ToggleButton(label="Thermal\nControl")
        grid.attach_next_to(button6, button5, Gtk.PositionType.RIGHT, 1, 1)
        button6.connect("toggled", self.on_button_toggled6, "6")

        button7 = Gtk.ToggleButton(label="HF-1\nYaesu\n101MP")
        grid.attach_next_to(button7, button6, Gtk.PositionType.RIGHT, 1, 1)
        button7.connect("toggled", self.on_button_toggled7, "7")

        button8 = Gtk.ToggleButton(label="HF-2\nIcom\n7300")
        grid.attach_next_to(button8, button7, Gtk.PositionType.RIGHT, 1, 1)
        button8.connect("toggled", self.on_button_toggled8, "8")

        button9 = Gtk.ToggleButton(label="VHF-1\nYaesu\n7900")
        grid.attach_next_to(button9, button8, Gtk.PositionType.RIGHT, 1, 1)
        button9.connect("toggled", self.on_button_toggled9, "9")

        button10 = Gtk.ToggleButton(label="Amplifier\nAmeritron\nALS-1300")
        grid.attach_next_to(button10, button3, Gtk.PositionType.BOTTOM, 1, 1)
        button10.connect("toggled", self.on_button_toggled10, "10")

        button11 = Gtk.ToggleButton(label="Unused_1")
        grid.attach_next_to(button11, button10, Gtk.PositionType.RIGHT, 1, 1)
        button11.connect("toggled", self.on_button_toggled11, "11")

        button12 = Gtk.ToggleButton(label="Unused_2")
        grid.attach_next_to(button12, button11, Gtk.PositionType.RIGHT, 1, 1)
        button12.connect("toggled", self.on_button_toggled12, "12")

        button13 = Gtk.ToggleButton(label="Unused_3")
        grid.attach_next_to(button13, button12, Gtk.PositionType.RIGHT, 1, 1)
        button13.connect("toggled", self.on_button_toggled13, "13")

        button14 = Gtk.ToggleButton(label="Unused_4")
        grid.attach_next_to(button14, button13, Gtk.PositionType.RIGHT, 1, 1)
        button14.connect("toggled", self.on_button_toggled14, "14")

        button15 = Gtk.ToggleButton(label="Full\nSystem\nShutdown")
        grid.attach_next_to(button15, button14, Gtk.PositionType.RIGHT, 1, 1)
        button15.connect("toggled", self.on_button_toggled15, "15")

        button16 = Gtk.ToggleButton(label="Exit to OS")
        grid.attach_next_to(button16, button15, Gtk.PositionType.RIGHT, 1, 1)
        button16.connect("toggled", self.on_button_toggled16, "16")

    def on_button_toggled100(self, button100, name):
        """Normal Shutdown - turn off all power relays"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.play()
        pygame.mixer.music.load("Sounds/click.wav")
        if button100.get_active():
            # Relays Off in one second intervals
            RELAY.relayOFF(0, 3)
            time.sleep(0.5)
            RELAY.relayOFF(0, 4)
            time.sleep(0.5)
            RELAY.relayOFF(0, 5)
            time.sleep(0.5)
            RELAY.relayOFF(0, 6)
            time.sleep(0.5)
            RELAY.relayOFF(0, 7)
            RELAY.relayOFF(1, 2)
#           Leave lights on
#           time.sleep(0.5)
#           RELAY.relayOFF(1, 3)
            time.sleep(0.5)
            RELAY.relayOFF(1, 4)
            time.sleep(0.5)
            RELAY.relayOFF(1, 6)
            time.sleep(0.5)
            RELAY.relayOFF(1, 7)
            time.sleep(0.5)
            RELAY.relayOFF(1, 1)
            time.sleep(0.5)
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/completed.wav")
            pygame.mixer.music.play()
            RELAY.relayOFF(0, 1)
            RELAY.relayOFF(0, 2)
            time.sleep(0.5)
            RELAY.relayOFF(1, 5)
        else:
            print("button 100 Off")
        button100.set_active(False)

    def on_button_toggled110(self, button110, name):
        """Auto PowerUp"""
        if button110.get_active():
            RELAY.relayON(1, 5)
            time.sleep(1)
            RELAY.relayON(0, 1)
            time.sleep(1)
            RELAY.relayON(0, 2)
            time.sleep(1)
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
            RELAY.relayON(1, 3)
            time.sleep(1)
            RELAY.relayON(1, 1)
            time.sleep(3)
            RELAY.relayON(1, 2)
            time.sleep(1)
            RELAY.relayON(1, 4)
            time.sleep(1)
            RELAY.relayON(1, 6)
            time.sleep(1)
            RELAY.relayON(1, 7)
#           Icom 7300
#           RELAY.relayON(0, 6)
            time.sleep(1)
            RELAY.relayON(0, 3)
            time.sleep(1)
            RELAY.relayON(0, 4)
            time.sleep(1)
            RELAY.relayON(0, 5)
            time.sleep(1)
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/completed.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
        else:
            time.sleep(1)
        button110.set_active(False)

    def on_button_toggled120(self, button120, name):
        """Full Shutdown - turn off all relays"""
        if button120.get_active():
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
            RELAY.relayOFF(0, 3)
            time.sleep(0.5)
            RELAY.relayOFF(0, 4)
            time.sleep(0.5)
            RELAY.relayOFF(0, 5)
            time.sleep(0.5)
            RELAY.relayOFF(0, 6)
            time.sleep(0.5)
            RELAY.relayOFF(0, 7)
            time.sleep(0.5)
            RELAY.relayOFF(1, 1)
            time.sleep(0.5)
            RELAY.relayOFF(1, 2)
            time.sleep(0.5)
            RELAY.relayOFF(1, 4)
            time.sleep(0.5)
            RELAY.relayOFF(1, 6)
            time.sleep(0.5)
            RELAY.relayOFF(1, 7)
            time.sleep(0.5)
            RELAY.relayOFF(1, 3)
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/completed.wav")
            pygame.mixer.music.play()
            RELAY.relayOFF(0, 1)
            RELAY.relayOFF(0, 2)
            RELAY.relayOFF(1, 5)
        else:
#           Relay.relayOFF(1, 7)
            print("button120")
        button120.set_active(False)

    def on_button_toggled130(self, button130, name):
        """Mute Audio"""
        if button130.get_active():
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
            RELAY.relayOFF(0, 1)
            RELAY.relayOFF(0, 2)
        else:
            RELAY.relayON(0, 1)
            RELAY.relayON(0, 2)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
                continue

    def on_button_toggled140(self, button140, name):
        """Lights"""
        pygame.mixer.music.play()
        if button140.get_active():
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
            RELAY.relayTOGGLE(1, 3)
        else:
            RELAY.relayTOGGLE(1, 3)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled150(self, button150, name):
        """Audio System"""
        if button150.get_active():
            RELAY.relayON(1, 5)
            time.sleep(2)
            RELAY.relayON(0, 1)
            RELAY.relayON(0, 2)
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
        else:
            while pygame.mixer.music.get_busy() == True:
                continue
            pygame.mixer.music.load("Sounds/click.wav")
            pygame.mixer.music.play()
            RELAY.relayOFF(0, 1)
            RELAY.relayOFF(0, 2)
            RELAY.relayOFF(1, 5)
        while pygame.mixer.music.get_busy() == True:
                 continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled3(self, button4, name):
        """12VDC"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button4.get_active():
            RELAY.relayTOGGLE(1, 1)
        else:
            RELAY.relayTOGGLE(1, 1)
        while pygame.mixer.music.get_busy() == True:
            continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled4(self, button4, name):
        """Dual Monitor"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button4.get_active():
            RELAY.relayTOGGLE(1, 2)
        else:
            RELAY.relayTOGGLE(1, 2)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled5(self, button5, name):
        """Palstar HF-Auto Tuner"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button5.get_active():
            RELAY.relayTOGGLE(0, 3)
        else:
            RELAY.relayTOGGLE(0, 3)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled6(self, button6, name):
        """Aux Devices: LP500, MFJ ant switch, bias-T, fans"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button6.get_active():
            RELAY.relayTOGGLE(0, 5)
        else:
            RELAY.relayTOGGLE(0, 5)

        while pygame.mixer.music.get_busy() == True:
            continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled7(self, button7, name):
        """HF-1 Yaesu 101MP"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button7.get_active():
            RELAY.relayTOGGLE(1, 4)
        else:
            RELAY.relayOFF(1, 4)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled8(self, button8, name):
        """HF-2 Icom 7300"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.play()
        pygame.mixer.music.load("Sounds/click.wav")
        if button8.get_active():
            RELAY.relayTOGGLE(0, 6)
        else:
            RELAY.relayTOGGLE(0, 6)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled9(self, button9, name):
        """VHF - UHF Yaesu 7900"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button9.get_active():
            RELAY.relayTOGGLE(0, 4)
        else:
            RELAY.relayTOGGLE(0, 4)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled11(self, button11, name):
        """not used"""
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button11.get_active():
            RELAY.relayTOGGLE(1, 6)
        else:
            RELAY.relayTOGGLE(1, 6)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled10(self, button10, name):
        """Ameritron Amplifier"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button10.get_active():
            RELAY.relayTOGGLE(0, 7)
        else:
            RELAY.relayTOGGLE(0, 7)
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled12(self, button12, name):
        """not used"""
        pygame.mixer.music.play()
        if button12.get_active():
            pygame.mixer.music.play()
            pygame.mixer.music.load("Sounds/click.wav")
#           RELAY.relayON(0, 0)
        else:
#           RELAY.relayOFF(0, 0)
          while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled13(self, button13, name):
        """not used"""
        while pygame.mixer.music.get_busy() == True:
              continue
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        if button13.get_active():
            RELAY.relayTOGGLE(1, 7)
        else:
            RELAY.relayTOGGLE(1, 7)
        while pygame.mixer.music.get_busy() == True:
              continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()

    def on_button_toggled14(self, button14, name):
        """not used"""
        pygame.mixer.music.play()
        if button14.get_active():
            pygame.mixer.music.play()
            pygame.mixer.music.load("Sounds/click.wav")
            RELAY.relayTOGGLE(0, 4)
        else:
            RELAY.relayTOGGLE(0, 4)

    def on_button_toggled15(self, button15, name):
        """Button 15 Full System Shutdown"""
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.play()
        pygame.mixer.music.load("Sounds/click.wav")
        if button15.get_active():
            RELAY.relayOFF(0, 3)
            time.sleep(0.5)
            RELAY.relayOFF(0, 4)
            time.sleep(0.5)
            RELAY.relayOFF(0, 5)
            time.sleep(0.5)
            RELAY.relayOFF(0, 6)
            time.sleep(0.5)
            RELAY.relayOFF(0, 7)
            time.sleep(0.5)
            RELAY.relayOFF(1, 1)
            time.sleep(0.5)
            RELAY.relayOFF(1, 2)
            time.sleep(0.5)
            RELAY.relayOFF(1, 4)
            time.sleep(0.5)
            RELAY.relayOFF(1, 6)
            time.sleep(0.5)
            RELAY.relayOFF(1, 7)
            time.sleep(0.5)
            RELAY.relayOFF(1, 3)
            time.sleep(0.5)
            RELAY.relayOFF(1,5)
            print("Button 15-1")
        else:
            print("Button 15-2")
        while pygame.mixer.music.get_busy() == True:
                continue
        pygame.mixer.music.load("Sounds/completed.wav")
        pygame.mixer.music.play()
        SYSTEM.system("sudo halt")

    def on_button_toggled16(self, button16, state):
        """Button 16 Exit to OS"""
        pygame.mixer.music.load("Sounds/click.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
                continue
        print("exit here to OS")
        quit()


win = Relay_Control_Window()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()