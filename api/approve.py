import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from lib.database import get_review_by_token, mark_review_posted
from lib.google_api import get_fresh_access_token, post_reply

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        token = params.get("token", [None])[0]
        
        if not token:
            self._respond_html("<h2>Invalid link.</h2>")
            return
        
        review = get_review_by_token(token)
        
        if not review:
            self._respond_html("<h2>Review not found or already processed.</h2>")
            return
        
        if review["status"] == "posted":
            self._respond_html("<h2>✅ This reply has already been posted!</h2>")
            return
        
        business = review["businesses"]
        access_token = get_fresh_access_token(business["refresh_token"])
        
        success = post_reply(
            access_token=access_token,
            account_id=business["google_account_id"],
            location_id=business["google_location_id"],
            review_id=review["google_review_id"],
            reply_text=review["ai_reply"]
        )
        
        if success:
            mark_review_posted(token)
            self._respond_html("""
                <div style='font-family:Arial;text-align:center;padding:60px;'>
                    <h1 style='color:#22c55e;'>✅ Reply Posted!</h1>
                    <p>Your reply has been posted to Google.</p>
                    <p style='color:#666;'>Customers can now see that you care about their feedback.</p>
                </div>
            """)
        else:
            self._respond_html("""
                <div style='font-family:Arial;text-align:center;padding:60px;'>
                    <h1 style='color:#ef4444;'>Something went wrong.</h1>
                    <p>Please try again or contact support.</p>
                </div>
            """)
    
    def _respond_html(self, body):
        html = f"<html><body>{body}</body></html>"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())