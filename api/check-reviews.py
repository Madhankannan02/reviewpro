import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import uuid
from http.server import BaseHTTPRequestHandler
from lib.database import (get_active_businesses, save_review, 
                          review_already_exists)
from lib.google_api import get_fresh_access_token, get_recent_reviews
from lib.gemini import generate_reply
from lib.email_sender import send_approval_email

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        results = []
        
        businesses = get_active_businesses()
        
        for business in businesses:
            try:
                # Get fresh Google access token
                access_token = get_fresh_access_token(business["refresh_token"])
                
                # Fetch their recent reviews
                reviews = get_recent_reviews(
                    access_token,
                    business["google_account_id"],
                    business["google_location_id"]
                )
                
                for review in reviews:
                    # Only process 1, 2, or 3 star reviews
                    star_rating = review.get("starRating", "FIVE")
                    rating_map = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
                    stars = rating_map.get(star_rating, 5)
                    
                    if stars > 3:
                        continue
                    
                    review_id = review.get("reviewId")
                    
                    # Skip if already processed
                    if review_already_exists(review_id):
                        continue
                    
                    # Skip if already has a reply
                    if review.get("reviewReply"):
                        continue
                    
                    review_text = review.get("comment", "No comment left")
                    reviewer_name = review.get("reviewer", {}).get("displayName", "A customer")
                    
                    # Generate AI reply
                    ai_reply = generate_reply(
                        business_name=business["name"],
                        business_type="local business",
                        reviewer_name=reviewer_name,
                        star_rating=stars,
                        review_text=review_text
                    )
                    
                    # Create unique approval token
                    approval_token = str(uuid.uuid4())
                    
                    # Save to database
                    save_review(
                        business_id=business["id"],
                        google_review_id=review_id,
                        reviewer_name=reviewer_name,
                        star_rating=stars,
                        review_text=review_text,
                        ai_reply=ai_reply,
                        approval_token=approval_token
                    )
                    
                    # Send email to owner
                    send_approval_email(
                        owner_email=business["owner_email"],
                        owner_name=business["name"],
                        business_name=business["name"],
                        reviewer_name=reviewer_name,
                        star_rating=stars,
                        review_text=review_text,
                        ai_reply=ai_reply,
                        approval_token=approval_token
                    )
                    
                    results.append(f"Processed review for {business['name']}")
                    
            except Exception as e:
                results.append(f"Error for {business['name']}: {str(e)}")
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"processed": results}).encode())