import os
import requests

def send_approval_email(owner_email, owner_name, business_name,
                         reviewer_name, star_rating, review_text,
                         ai_reply, approval_token):
    
    base_url = os.environ.get("BASE_URL")
    approve_url = f"{base_url}/api/approve?token={approval_token}"
    edit_url = f"{base_url}/edit?token={approval_token}"
    
    stars = "⭐" * star_rating
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        
        <div style="background: #ff4444; color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="margin:0">⚠️ New {star_rating}-Star Review on Your Google Listing</h2>
        </div>
        
        <p>Hi {owner_name},</p>
        <p>A new review just came in for <strong>{business_name}</strong>. Here's what they said:</p>
        
        <div style="background: #f5f5f5; border-left: 4px solid #ff4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <p style="margin:0; font-size: 13px; color: #666;">{stars} — {reviewer_name}</p>
            <p style="margin: 10px 0 0 0; font-style: italic;">"{review_text}"</p>
        </div>
        
        <p>Here's your suggested reply:</p>
        
        <div style="background: #f0fff0; border-left: 4px solid #22c55e; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <p style="margin:0;">"{ai_reply}"</p>
        </div>
        
        <div style="margin: 30px 0;">
            <a href="{approve_url}" 
               style="background: #22c55e; color: white; padding: 14px 28px; 
                      text-decoration: none; border-radius: 6px; font-weight: bold;
                      display: inline-block; margin-right: 10px;">
                ✅ Post This Reply
            </a>
            <a href="{edit_url}" 
               style="background: #3b82f6; color: white; padding: 14px 28px; 
                      text-decoration: none; border-radius: 6px; font-weight: bold;
                      display: inline-block;">
                ✏️ Edit First
            </a>
        </div>
        
        <p style="color: #888; font-size: 12px;">
            Posting a reply takes under 30 seconds and shows other customers you care.
            Businesses that reply to reviews rank higher on Google Maps.
        </p>
        
    </div>
    """
    
    resend_key = os.environ.get("RESEND_API_KEY")
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {resend_key}", 
                 "Content-Type": "application/json"},
        json={
            "from": "ReviewReply <alerts@yourdomain.com>",
            "to": owner_email,
            "subject": f"⚠️ New {star_rating}-star review needs your reply — {business_name}",
            "html": html
        }
    )
    return response.status_code == 200