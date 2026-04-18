import os
from supabase import create_client

def get_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

def get_active_businesses():
    db = get_client()
    result = db.table("businesses").select("*").eq("active", True).execute()
    return result.data

def save_review(business_id, google_review_id, reviewer_name, 
                star_rating, review_text, ai_reply, approval_token):
    db = get_client()
    db.table("reviews").insert({
        "business_id": business_id,
        "google_review_id": google_review_id,
        "reviewer_name": reviewer_name,
        "star_rating": star_rating,
        "review_text": review_text,
        "ai_reply": ai_reply,
        "status": "pending",
        "approval_token": approval_token
    }).execute()

def get_review_by_token(token):
    db = get_client()
    result = db.table("reviews").select("*, businesses(*)") \
               .eq("approval_token", token).single().execute()
    return result.data

def mark_review_posted(token):
    db = get_client()
    db.table("reviews").update({"status": "posted"}) \
      .eq("approval_token", token).execute()

def review_already_exists(google_review_id):
    db = get_client()
    result = db.table("reviews") \
               .select("id").eq("google_review_id", google_review_id).execute()
    return len(result.data) > 0