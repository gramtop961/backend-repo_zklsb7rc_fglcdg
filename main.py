import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="BloomBox API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    query: Optional[str] = Field(None, description="Free-form search like 'gift for book lover'")
    mood: Optional[str] = Field(None, description="Mood like happy, calm, romantic, stress, self-love")
    relationship: Optional[str] = None
    occasion: Optional[str] = None
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None


class MessageRequest(BaseModel):
    to: Optional[str] = None
    from_name: Optional[str] = None
    mood: Optional[str] = None
    occasion: Optional[str] = None
    style: Optional[str] = Field(
        default="warm",
        description="warm | romantic | playful | grateful | poetic",
    )


@app.get("/")
def read_root():
    return {"message": "BloomBox API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from BloomBox backend!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os

    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# --------- Catalog-like curated data (mock AI + curated) ---------

FEATURED_BOXES = [
    {
        "slug": "joy-box",
        "name": "Joy Box",
        "price": 1899,
        "thumb": "https://images.unsplash.com/photo-1520975682031-6de9d3f7d89c?q=80&w=1200&auto=format&fit=crop",
        "gradient": ["#FFD6E0", "#E8DFF5"],
        "items": [
            "Rose-scented candle",
            "Handwritten note",
            "Almond cookies",
            "Mini dried bouquet",
        ],
        "mood": "happy",
    },
    {
        "slug": "calm-box",
        "name": "Calm Box",
        "price": 2199,
        "thumb": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop",
        "gradient": ["#B9F3E4", "#E8DFF5"],
        "items": ["Lavender mist", "Chamomile tea", "Satin scrunchie", "Journaling pen"],
        "mood": "calm",
    },
    {
        "slug": "love-box",
        "name": "Love Box",
        "price": 2499,
        "thumb": "https://images.unsplash.com/photo-1519682577862-22b62b24e493?q=80&w=1200&auto=format&fit=crop",
        "gradient": ["#FFD6E0", "#F4D9B3"],
        "items": ["Silk ribbon", "Chocolate truffles", "Rose oil", "Polaroid frame"],
        "mood": "romantic",
    },
    {
        "slug": "celebration-box",
        "name": "Celebration Box",
        "price": 2799,
        "thumb": "https://images.unsplash.com/photo-1513151233558-d860c5398176?q=80&w=1200&auto=format&fit=crop",
        "gradient": ["#FFF7E9", "#F4D9B3"],
        "items": ["Confetti popper", "Sparkle topper", "Vanilla cupcake mix", "Note card"],
        "mood": "festive",
    },
]


@app.get("/api/featured-boxes")
def get_featured_boxes():
    return {"boxes": FEATURED_BOXES}


@app.get("/api/categories")
def get_categories():
    return {
        "moods": ["happy", "calm", "romantic", "festive", "sad", "self-love"],
        "relationships": ["for him", "for her", "parents", "friends"],
        "occasions": ["birthday", "anniversary", "graduation", "self-love"],
    }


@app.post("/api/recommend-gifts")
def recommend_gifts(req: RecommendRequest):
    """Simple rule-based recommender that mimics AI output."""
    mood = (req.mood or "").lower()
    occasion = (req.occasion or "").lower()
    relationship = (req.relationship or "").lower()

    pool = {
        "happy": [
            {"title": "Sunshine Candle", "price": 699, "tag": "cheer"},
            {"title": "Berry Truffles", "price": 499, "tag": "treat"},
            {"title": "Mini Bouquet", "price": 799, "tag": "flowers"},
        ],
        "calm": [
            {"title": "Lavender Mist", "price": 749, "tag": "relax"},
            {"title": "Chamomile Tea Set", "price": 549, "tag": "soothe"},
            {"title": "Soft Eye Mask", "price": 399, "tag": "sleep"},
        ],
        "romantic": [
            {"title": "Rose Oil", "price": 999, "tag": "romance"},
            {"title": "Silk Ribbon Wrap", "price": 299, "tag": "wrap"},
            {"title": "Love Notes Set", "price": 399, "tag": "note"},
        ],
        "festive": [
            {"title": "Confetti Popper", "price": 299, "tag": "party"},
            {"title": "Vanilla Cupcake Mix", "price": 499, "tag": "bake"},
            {"title": "Sparkle Topper", "price": 349, "tag": "sparkle"},
        ],
        "sad": [
            {"title": "Warm Hug Mug", "price": 599, "tag": "comfort"},
            {"title": "Kind Notes", "price": 349, "tag": "uplift"},
            {"title": "Self-care Mask", "price": 299, "tag": "care"},
        ],
        "self-love": [
            {"title": "Jade Roller", "price": 899, "tag": "glow"},
            {"title": "Affirmation Cards", "price": 499, "tag": "affirm"},
            {"title": "Bath Salt", "price": 399, "tag": "soak"},
        ],
    }

    suggestions = pool.get(mood or "happy", [])

    # Filter by budget
    if req.min_budget is not None or req.max_budget is not None:
        mn = req.min_budget or 0
        mx = req.max_budget or 10_000_000
        suggestions = [s for s in suggestions if mn <= s["price"] <= mx]

    # Personalize blurb
    context_bits = [b for b in [mood, occasion, relationship] if b]
    context = ", ".join(context_bits) if context_bits else "thoughtful"

    return {
        "context": context,
        "query": req.query,
        "results": suggestions[:5],
    }


@app.post("/api/generate-message")
def generate_message(req: MessageRequest):
    tones = {
        "warm": "Wrapping you in a soft hug and a little sparkle today.",
        "romantic": "My heart chose this just for you—gentle, rosy and full of love.",
        "playful": "A pocketful of confetti and a sprinkle of mischief—just for you!",
        "grateful": "Thank you for being the calm in my chaos and the glow in my days.",
        "poetic": "Like petals on quiet water, may this bring you small, luminous joy.",
    }

    to_line = f"Dear {req.to}," if req.to else "Hey love,"
    style_line = tones.get((req.style or "warm").lower(), tones["warm"]) 
    mood_line = f" For your {req.occasion} I wished for {req.mood} moments." if req.occasion or req.mood else ""
    from_line = f"\n\nWith love,\n{req.from_name}" if req.from_name else "\n\nWith love,\nBloomBox"

    message = f"{to_line}\n{style_line}{mood_line}{from_line}"

    return {"message": message}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
