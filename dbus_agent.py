#!/usr/bin/env python
import signal
import sys
import time
from daemon import Daemon
import threading
import time
import dbus
import glib
from dbus.mainloop.glib import DBusGMainLoop
import callBack
from callBack import cb_info
import salt.client

RUN = True
current_methods = {}


def mainSource(loop):
    loop.run()


def update_listener(cb, bus):
    global current_methods
    enabled_methods = callBack.get_enabled_methods(cb)
    poplist = []
    # unregister the signals that are not in the latest config file
    for key, value in current_methods.iteritems():
        if key not in enabled_methods:
            value.remove()
            poplist.append(key)
    for el in poplist:
        current_methods.pop(el)

    # register the signals that are newly added in the latest config file
    for key, value in enabled_methods.iteritems():
        if key not in current_methods:
            signalMatch = bus.add_signal_receiver(
                value,
                signal_name=cb_info[key]['signal_name'],
                dbus_interface=cb_info[key]['dbus_interface'],
                bus_name=cb_info[key]['bus_name'],
                path=cb_info[key]['path'],
                path_keyword='path'
            )
            current_methods.update({key: signalMatch})


def signalHandler(loop, cb, bus):
    """
    signal handler to handle sighup and sigterm signals
    """
    def sighup_handler(signal, frame):
        update_listener(cb, bus)

    def sigterm_handler(signal, frame):
        loop.quit()
        global RUN
        RUN = False

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    signal.pause()


class MyDaemon(Daemon):
    """
    this is a class derived from daemon class, and here
    we are overriding the run method to suit this daemon
    """
    def run(self):
        # Using Dbus-python's default mainloop to listen to the events
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()

        # creating a salt caller object, this is used to push events using
        # salt's eventing framework
        caller = salt.client.Caller()

        cb = callBack.CallBack(caller)

        # this initializes/updates the interested signals
        # (read from config file) to be listened brom the bus
        update_listener(cb, bus)

        loop = glib.MainLoop()
        glib.threads_init()

        # create a thread to run the main loop which will listen to the dbus
        # and push the events to salt-master
        t = threading.Thread(target=mainSource, args=(loop,))
        t.start()

        # this will continue and listent to external signals (sighup,sigterm)
        # if sighup, the signals to be listened is reread from the config file
        # if sigterm, the daemon will be terminated
        while RUN:
            signalHandler(loop, cb, bus)


if __name__ == "__main__":
    # /tmp/fbus-agent.pid is just a temporary location to be modified later
    daemon = MyDaemon('/tmp/dbus-agent.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        elif 'reload' == sys.argv[1]:
            daemon.reload()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status|reload" % sys.argv[0]
        sys.exit(2)
