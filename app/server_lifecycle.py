import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


import gc
gc.set_debug(gc.DEBUG_STATS)
import sys
def on_server_loaded(server_context):
    ''' If present, this function is called when the server first starts. '''
    pass

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    #on_session_destroyed(server_context)
    pass
def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''
    pass

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    gc.collect()
    print("garbage----->",gc.garbage)