# dbus_agent
A linux daemon that listens to dbus signals and pushes them to salt's(Saltstack) event bus

Install
-------

1. Edit dbus_agent.service file to assign the following variables: ExecStart, ExecStop, ExecReload the location of dbus_agent.py
Eg:

ExecStart=/root/DbusAgent/dbus_agent.py start
ExecStop=/root/DbusAgent/dbus_agent.py stop
ExecReload=/root/DbusAgent/dbus_agent.py reload

2. Copy the edited script to location: /usr/lib/systemd/system/

3. Edit the dbusAgent.json (config file) to filter the events.

4. Start the daemon:

service dbus_agent start