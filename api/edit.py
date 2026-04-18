import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from lib.database import get_review_by_token, mark_review_posted
from lib.google_api import get_fresh_access_token, post_reply

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)
        
        token = data.get("token")
        edited_reply = data.get("reply")
        
        review = get_review_by_token(token)
        business = review["businesses"]
        access_token = get_fresh_access_token(business["refresh_token"])
        
        success = post_reply(
            access_token=access_token,
            account_id=business["google_account_id"],
            location_id=business["google_location_id"],
            review_id=review["google_review_id"],
            reply_text=edited_reply
        )
        
        if success:
            mark_review_posted(token)
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"success": success}).encode())