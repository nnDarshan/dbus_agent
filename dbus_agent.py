#!/usr/bin/env python
import signal
import sys, time
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
    
def update_listener(cb,bus):
    global current_methods
    enabled_methods = callBack.get_enabled_methods(cb)
    poplist = []
    # unregister the signals that are not in the latest config file
    for key, value in current_methods.iteritems():
        if not enabled_methods.has_key(key):
            value.remove()
            poplist.append(key)
    for el in poplist:
        current_methods.pop(el)

    # register the signals that are newly added in the latest config file
    for key,value  in enabled_methods.iteritems():
        if not current_methods.has_key(key):
            signalMatch = bus.add_signal_receiver(
                value,
                signal_name=cb_info[key]['signal_name'],
                dbus_interface = cb_info[key]['dbus_interface'],
                bus_name = cb_info[key]['bus_name'],
                path = cb_info[key]['path']
            )
            current_methods.update({key:signalMatch})

            
def signalHandler(loop,cb,bus):
    # signal handler
    def sighup_handler(signal, frame):
        update_listener(cb,bus)

    def sigterm_handler(signal, frame):
        loop.quit()
        global RUN
        RUN = False

    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    signal.pause()


class MyDaemon(Daemon):
    def run(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        caller = salt.client.Caller()
        cb = callBack.CallBack(caller)
        update_listener(cb,bus)
        loop = glib.MainLoop()
        glib.threads_init()
        t = threading.Thread(target = mainSource, args = (loop,))
        t.start()
        while RUN:
            signalHandler(loop,cb,bus)

            
if __name__ == "__main__":
    # this is just a temp location to be modified later
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
