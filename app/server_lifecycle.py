import gc

def on_server_loaded(server_context):
    ''' If present, this function is called when the server first starts. '''
    pass

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    on_session_destroyed(server_context)
    pass
def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''
    pass

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    gc.collect()