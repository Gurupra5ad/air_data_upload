import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

APP_KEY = "shlhxvxutvjtqhw"
APP_SECRET = "wvdmikm3bik6m8u"
REDIRECT_URI = "http://localhost:8080"

# Start browser auth
auth_url = (
    f"https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}"
    f"&redirect_uri={REDIRECT_URI}&response_type=code&token_access_type=offline"
)
print(f"Opening: {auth_url}")
webbrowser.open(auth_url)

# Create simple server to capture the code
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("code")
        if code:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful. You may close this window.</h1>")
            print(f"\nAuthorization Code: {code[0]}")

            # Exchange code for tokens
            response = requests.post("https://api.dropboxapi.com/oauth2/token", data={
                "code": code[0],
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI
            })
            print("\n== Dropbox Token Response ==")
            print(response.json())
            exit(0)

print("Waiting for Dropbox redirect...")
httpd = HTTPServer(("localhost", 8080), Handler)
httpd.handle_request()
