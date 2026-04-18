import os
import requests

def get_fresh_access_token(refresh_token):
    """Use refresh token to get a new access token."""
    response = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    data = response.json()
    return data.get("access_token")

def get_recent_reviews(access_token, account_id, location_id):
    """Fetch reviews for a business location."""
    url = f"https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations/{location_id}/reviews"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get("reviews", [])

def post_reply(access_token, account_id, location_id, review_id, reply_text):
    """Post a reply to a specific review."""
    url = f"https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations/{location_id}/reviews/{review_id}/reply"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {"comment": reply_text}
    response = requests.put(url, headers=headers, json=body)
    return response.status_code == 200