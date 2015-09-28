#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'gomes'

from gi.repository import Gtk, GObject, GLib
import threading
import subprocess


class Sensors:
    '''

    '''
    def __init__(self):
        '''
        Sensors constructor.
        Get the sensors.glade file on the same folder as this file.
        :return: None
        '''
        # Update time
        self.time_value = 0

        builder = Gtk.Builder()
        # Build the template from glade
        builder.add_from_file("./sensors.glade")

        # Loads the spinner
        self.spin_time = builder.get_object("spin_time")

        # Loads the label to indicate time
        self.lbl_time = builder.get_object("lbl_time")
        self.lbl_time.set_text("Time: {}".format(self.time_value))

        # Loads the button to start the thread
        self.bt_update_time = builder.get_object("bt_update_time")
        self.bt_update_time.connect("released", self.bt_update_time_clicked)

        # Loads the textview
        self.data = builder.get_object("data")
        self.data.set_editable(False)

        # Loads the window
        self.win = builder.get_object("sensors_window")
        self.win.connect("delete-event", Gtk.main_quit)

        # Creates the thread
        self.data_thread = threading.Thread(target=self.update_by_time)

        # Creates an event to stop the thread
        self.data_thread_stop = threading.Event()

    def bt_update_time_clicked(self, button= None):
        '''
        Method to connect to the released event of the update button.
        :param button: Button that sent the msg
        :return: None
        '''
        self.time_value = self.spin_time.get_value()
        self.update_lbl_time(self.time_value)
        if self.data_thread.isAlive():
            self.data_thread = threading.Thread(target=self.update_by_time)
            self.data_thread_stop = threading.Event()
        self.data_thread.daemon = True
        self.data_thread.start()

    def update_by_time(self):
        '''
        Thread method.
        :return: None
        '''
        while not self.data_thread_stop.is_set():
            decoding = "utf-8"
            # Loads the sensors command
            command = subprocess.Popen(['sensors'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Retrieve the output and any given errs
            out, err = command.communicate()
            # print(err.decode(decoding))
            text = out.decode(decoding)
            # GTK gets aware of the thread to update the textview
            GLib.idle_add(self.update_data_text, text)
            # Makes the thread sleep
            self.data_thread_stop.wait(self.time_value)

    def update_lbl_time(self, new_value):
        '''
        Method to update the time shown on the time label.
        :param new_value: Time value for the label.
        :return:
        '''
        self.lbl_time.set_text("Time: {} s".format(new_value))

    def update_data_text(self, value):
        '''
        Method to update the textView data.
        :param value: String value to be printed.
        :return:
        '''
        self.data.get_buffer().set_text(str(value))
        return False


if __name__ == '__main__':
    GObject.threads_init()
    win = Sensors()
    win.win.show_all()
    Gtk.main()
