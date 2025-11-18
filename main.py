import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User as UserSchema
from schemas import Listing as ListingSchema
from schemas import Message as MessageSchema
from schemas import Review as ReviewSchema

app = FastAPI(title="Kitesurf Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class IdResponse(BaseModel):
    id: str


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/")
def read_root():
    return {"message": "Kitesurf Marketplace API Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            response["collections"] = db.list_collection_names()
            response["database"] = "✅ Connected & Working"
    except Exception as e:
        response["database"] = f"⚠️ Error: {str(e)[:80]}"
    return response


# -----------------------------
# Users
# -----------------------------
@app.post("/api/users", response_model=IdResponse)
async def create_user(payload: UserSchema):
    new_id = create_document("user", payload)
    return {"id": new_id}


@app.get("/api/users", response_model=List[dict])
async def list_users():
    users = get_documents("user")
    for u in users:
        u["_id"] = str(u["_id"])  # serialize
    return users


# -----------------------------
# Listings
# -----------------------------
@app.post("/api/listings", response_model=IdResponse)
async def create_listing(payload: ListingSchema):
    # ensure seller exists
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    seller = db["user"].find_one({"_id": to_object_id(payload.seller_id)})
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    new_id = create_document("listing", payload)
    return {"id": new_id}


@app.get("/api/listings", response_model=List[dict])
async def list_listings(gear_type: Optional[str] = None, q: Optional[str] = None):
    filter_dict = {}
    if gear_type:
        filter_dict["gear_type"] = gear_type
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"brand": {"$regex": q, "$options": "i"}},
            {"model": {"$regex": q, "$options": "i"}},
        ]
    listings = get_documents("listing", filter_dict)
    for l in listings:
        l["_id"] = str(l["_id"])  # serialize
    return listings


# -----------------------------
# Messages
# -----------------------------
@app.post("/api/messages", response_model=IdResponse)
async def send_message(payload: MessageSchema):
    # basic existence checks
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    if not db["user"].find_one({"_id": to_object_id(payload.sender_id)}):
        raise HTTPException(status_code=404, detail="Sender not found")
    if not db["user"].find_one({"_id": to_object_id(payload.receiver_id)}):
        raise HTTPException(status_code=404, detail="Receiver not found")
    if not db["listing"].find_one({"_id": to_object_id(payload.listing_id)}):
        raise HTTPException(status_code=404, detail="Listing not found")
    new_id = create_document("message", payload)
    return {"id": new_id}


# -----------------------------
# Reviews
# -----------------------------
@app.post("/api/reviews", response_model=IdResponse)
async def create_review(payload: ReviewSchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    if not db["user"].find_one({"_id": to_object_id(payload.reviewer_id)}):
        raise HTTPException(status_code=404, detail="Reviewer not found")
    if not db["user"].find_one({"_id": to_object_id(payload.reviewee_id)}):
        raise HTTPException(status_code=404, detail="Reviewee not found")
    new_id = create_document("review", payload)
    return {"id": new_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
