from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the text_generation_app.ipynb directory with bokeh server"""
    Popen(["panel", "serve", "text_generation_app.ipynb", "--allow-websocket-origin=*"])