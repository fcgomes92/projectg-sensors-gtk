#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'gomes'

from gi.repository import Gtk, GObject, GLib
import threading
import subprocess


class Sensors:
    def __init__(self):
        self.time_value = 0

        builder = Gtk.Builder()
        builder.add_from_file("./sensors.glade")

        self.spin_time = builder.get_object("spin_time")

        self.lbl_time = builder.get_object("lbl_time")
        self.lbl_time.set_text("Time: {}".format(self.time_value))

        self.bt_update_time = builder.get_object("bt_update_time")
        self.bt_update_time.connect("released", self.bt_update_time_clicked)

        self.data = builder.get_object("data")
        self.data.set_editable(False)

        self.win = builder.get_object("sensors_window")
        self.win.connect("delete-event", Gtk.main_quit)

        self.data_thread = threading.Thread(target=self.update_by_time)
        self.data_thread_stop = threading.Event()

    def bt_update_time_clicked(self, button):
        self.time_value = self.spin_time.get_value()
        self.update_lbl_time(self.time_value)
        if self.data_thread.isAlive():
            self.data_thread = threading.Thread(target=self.update_by_time)
            self.data_thread_stop = threading.Event()
        self.data_thread.daemon = True
        self.data_thread.start()
        pass

    def update_by_time(self):
        while not self.data_thread_stop.is_set():
            decoding = "utf-8"
            command = subprocess.Popen(['sensors'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = command.communicate()
            # print(err.decode(decoding))
            text = out.decode(decoding)
            GLib.idle_add(self.update_data_text, text)
            self.data_thread_stop.wait(self.time_value)

    def update_lbl_time(self, new_value):
        self.lbl_time.set_text("Time: {} s".format(new_value))

    def update_data_text(self, value):
        self.data.get_buffer().set_text(value)
        return False


if __name__ == '__main__':
    GObject.threads_init()
    win = Sensors()
    win.win.show_all()
    Gtk.main()
