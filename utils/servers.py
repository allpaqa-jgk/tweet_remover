from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import states.setup_state as setup_state


def start_and_wait() -> None:
    server = start_server()
    wait_for_callback(server)


def start_server() -> HTTPServer:
    # Start local server to receive callback

    return HTTPServer(("localhost", 8080), OAuthCallbackHandler)


def wait_for_callback(server: HTTPServer) -> None:
    print("Waiting for OAuth2 callback...")
    server.handle_request()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from X API."""

    def log_message(self, format, *args) -> None:
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        global auth_code

        """Handle GET request from OAuth redirect."""
        query = parse_qs(urlparse(self.path).query)

        if "code" in query:
            if "state" not in query or query["state"][0] != setup_state.state:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Invalid state parameter</h1></body></html>"
                )
                return
            setup_state.auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication successful!</h1><p>You can close this window.</p></body></html>"
            )
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication failed</h1></body></html>"
            )
