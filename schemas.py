"""
Database Schemas for Kitesurf Marketplace

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the class name.

Example:
- User -> "user"
- Listing -> "listing"
- Message -> "message"
- Review -> "review"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# -----------------------------
# User
# -----------------------------
class User(BaseModel):
    handle: str = Field(..., min_length=2, max_length=32, description="Public username/handle")
    name: Optional[str] = Field(None, description="Full name")
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=280)
    location: Optional[str] = Field(None, description="City / primary spot")
    favorite_brands: Optional[List[str]] = Field(default_factory=list)
    verified: bool = Field(default=False)
    avatar_url: Optional[str] = None

# -----------------------------
# Listing
# -----------------------------
GearType = Literal["kite", "board", "bar", "foil", "harness", "accessory"]
Condition = Literal["new", "like new", "excellent", "good", "fair", "needs repair"]

class Listing(BaseModel):
    seller_id: str = Field(..., description="User ID of seller")
    title: str
    description: Optional[str] = None
    gear_type: GearType
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(None, ge=2000, le=datetime.utcnow().year + 1)
    condition: Condition
    price: float = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    size_m2: Optional[float] = Field(None, ge=0, description="Kite size in m²")
    board_length_cm: Optional[float] = Field(None, ge=0)
    board_width_cm: Optional[float] = Field(None, ge=0)
    line_length_m: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    pickup_available: bool = True
    shipping_available: bool = True
    image_urls: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

# -----------------------------
# Message
# -----------------------------
class Message(BaseModel):
    listing_id: str
    sender_id: str
    receiver_id: str
    body: str = Field(..., min_length=1, max_length=1000)
    attachment_urls: List[str] = Field(default_factory=list)

# -----------------------------
# Review
# -----------------------------
class Review(BaseModel):
    reviewer_id: str
    reviewee_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)
    listing_id: Optional[str] = None
