import json
import inspect

cb_info = {
    "disk_add": {"signal_name" : "InterfacesAdded","dbus_interface": None,"bus_name": None, "path": None},
    "disk_remove": {"signal_name" : "InterfacesRemoved","dbus_interface": None,"bus_name": None, "path": None}
}


class CallBack(object):
    """
    Call back class that contains all the callback functions.
    """
    
    def __init__(self, caller):
        self.caller = caller

    def disk_add(self, a , d):
        for e,v in d.iteritems():
            if e.split('.')[-1]== "Block":
                res = {}
                res["name"] = str(a.split('/')[-1])
                res["size"] = str(v.get("Size"))
                res["ReadOnly"] = str(v.get("ReadOnly"))
                res["DeviceNumber"] = str(v.get("DeviceNumber"))
                res["Partitionable"] = str(v.get("HintPartitionable"))
                res["action"] = "Added"
                print res
                #caller = salt.client.Caller()
                self.caller.sminion.functions['event.send'](
                    'disk/add',
                    res
                )

    def disk_remove(self, a, d):
        for e in d:
            if e.split('.')[-1]== "Block":
                res = {}
                res["name"] = str(a.split('/')[-1])
                res["Action"] = "Removed"
                self.caller.sminion.functions['event.send'](
                    'disk/remove',
                    res
                )



def get_enabled_methods(cb):
    f = open("/root/DbusAgent/dbusAgent.json",'r')
    conf = json.loads(f.read())
    enabled_methods = []
    for group, info in conf.iteritems():
        if not conf[group]['enabled']:
            continue
        for method, enabled in conf[group]["methods"].iteritems():
            if enabled:
                enabled_methods.append(str(method))
    
    all_methods = inspect.getmembers(cb)
    em = {}
    for el in all_methods:
        if el[0] in enabled_methods:
            em.update({el[0]:el[1]})
    return em
