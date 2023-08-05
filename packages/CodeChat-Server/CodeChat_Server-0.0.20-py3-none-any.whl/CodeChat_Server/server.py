# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#   This file is part of the CodeChat system.
#
#   The CodeChat system is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   The CodeChat system is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the CodeChat system.  If not, see
#   <http://www.gnu.org/licenses/>.
#
# *******************************
# |docname| - The CodeChat server
# *******************************
# The CodeChat server receives requests from the editor/IDE, renders these, then displays them in the CodeChat client; likewise, it listens for CodeChat client requests, processes them, and forwards the results to the editor/IDE.
#
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import signal
import socket
import sys
import threading
from typing import Union
import webbrowser

# Third-party imports
# -------------------
from flask import (
    Flask,
    Response,
    make_response,
    render_template,
    send_file,
    abort,
)
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol


# Local application imports
# -------------------------
from . import renderer
from .gen_py.CodeChat_Services import EditorPlugin
from .gen_py.CodeChat_Services.ttypes import (
    RenderClientReturn,
    CodeChatClientLocation,
)


# Constants
# =========
# The port used for and HTTP connection from the CodeChat Client to the CodeChat Server.
HTTP_PORT = 5000
# .. _CodeChat service port:
#
# The port used for the Thrift connection between text editor/IDE extensions/plugins and the CodeChat Server. All editor/IDE plugins must use this port to access CodeChat services.
THRIFT_PORT = 9090

UNKNOWN_CLIENT = "Unknown client id {}."


# Service provider
# ================
# This class implements the EditorPlugin service.
class CodeChatHandler:
    def __init__(self):
        self.render_manager: renderer.RenderManager

    # _`get_client`: Return the HTML for a web client.
    def get_client(self, codeChat_client_location: int) -> RenderClientReturn:
        try:
            location_name = CodeChatClientLocation._VALUES_TO_NAMES[
                codeChat_client_location
            ]
        except KeyError:
            location_name = "invalid location"
        print("get_client({})".format(location_name))
        id = self.render_manager.threadsafe_create_client()
        # Get the next ID.
        if id is None:
            ret = RenderClientReturn("", -1, "Duplicate id {}".format(id))
            print("  => {}".format(ret))
            return ret
        if id < 0:
            ret = RenderClientReturn("", -1, "Server is shutting down.")
            print("  => {}".format(ret))
            return ret

        # Return what's requested.
        url = "http://127.0.0.1:{}/client?id={}".format(HTTP_PORT, id)
        if codeChat_client_location == CodeChatClientLocation.url:
            # Just return the URL.
            ret_str = url
        elif codeChat_client_location == CodeChatClientLocation.html:
            # Redirect to the webserver.
            ret_str = """
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body style="margin: 0px; padding: 0px; overflow: hidden">
        <iframe src="{}" style="width: 100%; height: 100vh; border: none"></iframe>
    </body>
</html>""".format(
                url
            )
        elif codeChat_client_location == CodeChatClientLocation.browser:
            # Open in an external browser.
            webbrowser.open(url, 1)
            ret_str = ""
        else:
            ret = RenderClientReturn(
                "", -1, "Invalid location {}".format(codeChat_client_location)
            )
            print("  => {}".format(ret))
            return ret

        ret = RenderClientReturn(ret_str, id, "")
        print("  => {}".format(ret))
        return ret

    # Render the provided text to HTML, then enqueue it for the web view.
    def start_render(self, text: str, path: str, id: int, is_dirty: bool) -> str:
        print(
            "start_render(path={}, id={}, is_dirty={}, html=\n{}...)\n".format(
                path, id, is_dirty, text[:80]
            )
        )
        if self.render_manager.threadsafe_start_render(text, path, id, is_dirty):
            # Indicate success.
            print(" => (empty string)")
            return ""
        else:
            ret = UNKNOWN_CLIENT.format(id)
            print(" => {}".format(ret))
            return ret

    # _`Shut down an editor client`. The sequence is:
    #
    # #.    _`Client stop`: send a message to the web client, informing it of the shutdown. While the editor shouldn't make any more ``start_render`` or ``stop_client`` calls, doing so won't cause the server to misbehave.
    # #.    _`Client deletion`: when the web client receives the shutdown message, tell the renderer to delete its ClientState. Since the ClientState contains the queue with the shutdown message, it shouldn't be deleted until the message is sent.
    #
    # This method performs the first step; ``get_result`` performs the second.
    def stop_client(self, id: int) -> str:
        print("stop_client(id={})".format(id))
        ok = self.render_manager.threadsafe_shutdown_client(id)
        if not ok:
            ret = UNKNOWN_CLIENT.format(id)
            print("  => {}".format(ret))
            return ret
        # Indicate success.
        print("  => (empty string)")
        return ""

    # Shut down the server.
    def shutdown_server(self) -> str:
        print("shutdown_server")
        shutdown_event.set()
        return ""


# Instantiate this class, which will be used by both servers.
handler = CodeChatHandler()


# Servers
# =======
#
# Server for the CodeChat editor plugin
# -------------------------------------
def editor_plugin_server() -> None:
    transport = TSocket.TServerSocket(host="127.0.0.1", port=THRIFT_PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    processor = EditorPlugin.Processor(handler)

    # Spawns up to 10 threads by default, then uses those. Mark these threads as daemon, so they will be terminated on program exit.
    server = TServer.TThreadPoolServer(
        processor, transport, tfactory, pfactory, daemon=True
    )
    # Other options for the server:
    #
    # This server spawns a thread per connection.
    ## server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)  # noqa: E266
    # A simpler server:
    ## server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)  # noqa: E266

    server.serve()


# Server for the CodeChat client
# ------------------------------
client_app = Flask(
    __name__,
    # Serve CodeChat client files statically.
    static_url_path="/static",
    static_folder="CodeChat_Client/static",
    # Serve the CodeChat client HTML as a template.
    template_folder="CodeChat_Client/templates",
)


# The endpoint to get the HTML for the CodeChat client.
@client_app.route("/client")
def client_html() -> str:
    return render_template(
        "CodeChat_client.html", WEBSOCKET_PORT=renderer.WEBSOCKET_PORT
    )


# The endpoint for files requested by a specific client, including rendered source files.
@client_app.route("/client/<int:id>/<path:url_path>")
def client_data(id: int, url_path: str) -> Union[str, Response]:
    # See if we rendered this file.
    html = handler.render_manager.threadsafe_get_render_results(id, url_path)

    # If we have rendered HTML, return it.
    if type(html) == str:
        assert isinstance(html, str)
        response = make_response(html)
    else:
        # The file is on disk. Send it or a 404 if nothing was found.
        try:
            # Don't allow Flask to cache files on disk, since they may change with each edit.
            response = make_response(send_file(url_path, cache_timeout=0))  # type: ignore
        except (FileNotFoundError, PermissionError):
            abort(404)

    # Don't allow the browser to cache files. See the `Flask docs <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Request.cache_control>`_ and `MDN docs <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#Directives>`_.
    response.cache_control.no_store = True
    return response


# Main code
# =========
# When this event is ``set``, ``run_servers`` will shut down the servers and return.
shutdown_event = threading.Event()


# Handle signals by setting the shutdown event.
def signal_handler(signum, frame):
    shutdown_event.set()


# Handle exceptions in the same way.
def excepthook(type, value, traceback):
    shutdown_event.set()
    sys.__excepthook__(type, value, traceback)


# Run both servers. This does not (usually) return.
def run_servers() -> int:
    # See if the required ports are in use, probably by another instance of this server.
    if (
        is_port_in_use(HTTP_PORT)
        or is_port_in_use(renderer.WEBSOCKET_PORT)
        or is_port_in_use(THRIFT_PORT)
    ):
        print(
            f"Error: ports {HTTP_PORT}, {renderer.WEBSOCKET_PORT}, and/or {THRIFT_PORT} are already in use. Exiting."
        )
        return 1

    # Shut down if any unhandled exception occurs.
    sys.excepthook = excepthook

    # Both servers block when run, so place them in a thread. Mark the Thrift server as a daemon, so it will be killed when the program shuts down.
    editor_plugin_thread = threading.Thread(
        target=editor_plugin_server, name="Editor plugin server", daemon=True
    )
    editor_plugin_thread.start()

    # Taken from https://stackoverflow.com/a/45017691.
    flask_server_thread = threading.Thread(
        target=client_app.run, kwargs=dict(port=HTTP_PORT), name="Flask", daemon=True
    )
    flask_server_thread.start()

    # Start the render loop in another thread.
    render_manager = renderer.RenderManager()
    handler.render_manager = render_manager
    render_manager_thread = threading.Thread(target=render_manager.run, name="asyncio")
    render_manager_thread.start()

    # On a signal, shut down gracefully.
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run the servers in threads until a user-requested shutdown occurs.
    while True:
        # Ctrl+C is ignored while waiting, so use a 1 second poll.
        if shutdown_event.wait(1):
            # If the event is received, exit the loop in order to shut down. First, clear the event so the next invocation of this function will work correctly.
            shutdown_event.clear()
            break

    print("Shutting down...")
    # This will prevent future editor or web requests from being serviced.
    render_manager.threadsafe_shutdown()
    # When this is done, the Flask server and editor plugin sever can be shut down, since they're idle. Since they're daemons, they'll be shut down by exiting main.
    render_manager_thread.join()
    return 0


# Inspired by Stack Overflow. The original post used ``connect_ex``, which is very slow (~2 seconds).
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
        except OSError:
            return True
        return False
