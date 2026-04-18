import os
import requests

def generate_reply(business_name, business_type, reviewer_name, 
                   star_rating, review_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    prompt = f"""You are a professional reputation manager for Indian small businesses.
Write a reply from the business owner to this Google review.

STRICT RULES:
- Under 80 words
- Warm and human, not corporate
- Acknowledge the specific issue they mentioned
- Apologize sincerely without admitting legal fault
- Offer to resolve offline: ask them to call or WhatsApp
- End positively
- Do NOT use phrases like "We value your feedback" or "Dear Customer"
- Write as if you are the owner personally

Business name: {business_name}
Business type: {business_type}
Reviewer name: {reviewer_name}
Star rating: {star_rating}/5
Review: {review_text}

Reply:"""

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 200, "temperature": 0.7}
    }
    
    response = requests.post(url, json=body)
    data = response.json()
    
    reply = data["candidates"][0]["content"]["parts"][0]["text"]
    return reply.strip()