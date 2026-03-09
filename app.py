"""
StyleSense - Generative AI Fashion Recommendation System
Flask Backend Application
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import os
import json
import re
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "stylesense-secret-key-2024")

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_db():
    """Get a database connection."""
    db = sqlite3.connect("stylesense.db")
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database with required tables."""
    db = get_db()
    cursor = db.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            style_profile TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Recommendations history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            result TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Saved outfits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_outfits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()
    db.close()
    print("✅ Database initialized.")

# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def validate_email(email):
    """Basic email validation."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None

# ─────────────────────────────────────────────
# AI RECOMMENDATION ENGINE (Rule-based + Template)
# ─────────────────────────────────────────────

STYLE_TEMPLATES = {
    "casual": {
        "outfits": [
            {"name": "Weekend Relaxed", "items": ["White oversized tee", "High-waist mom jeans", "White sneakers", "Mini crossbody bag"], "colors": ["White", "Light Blue", "Beige"]},
            {"name": "Coffee Run Chic", "items": ["Striped long-sleeve top", "Linen joggers", "Loafers", "Canvas tote"], "colors": ["Navy", "White", "Tan"]},
            {"name": "Effortless Day Out", "items": ["Flowy midi dress", "Denim jacket", "Block heel sandals", "Straw hat"], "colors": ["Sage Green", "Denim Blue", "Caramel"]},
        ],
        "tips": ["Layer textures for depth", "Invest in quality basics", "Neutral palette is your best friend"],
    },
    "formal": {
        "outfits": [
            {"name": "Power Meeting", "items": ["Tailored blazer", "Wide-leg trousers", "Silk blouse", "Pointed-toe heels"], "colors": ["Charcoal", "Ivory", "Black"]},
            {"name": "Corporate Elegance", "items": ["Sheath dress", "Structured blazer", "Kitten heels", "Leather portfolio"], "colors": ["Navy", "White", "Gold"]},
            {"name": "Executive Presence", "items": ["Pantsuit", "Fitted turtleneck", "Oxford shoes", "Minimalist watch"], "colors": ["Camel", "Cream", "Black"]},
        ],
        "tips": ["Fit is everything — tailor your clothes", "Quality over quantity", "Classic pieces transcend trends"],
    },
    "evening": {
        "outfits": [
            {"name": "Dinner Date Glam", "items": ["Slip dress", "Strappy heels", "Clutch bag", "Statement earrings"], "colors": ["Champagne", "Black", "Gold"]},
            {"name": "Cocktail Hour", "items": ["Wrap dress", "Block heels", "Structured mini bag", "Delicate necklace"], "colors": ["Emerald", "Black", "Silver"]},
            {"name": "Night Out Bold", "items": ["Sequin top", "Straight-leg trousers", "Platform heels", "Chain belt"], "colors": ["Silver", "Black", "Red"]},
        ],
        "tips": ["Accessories elevate any look", "Balance volume — fitted top + wide pants", "One statement piece per outfit"],
    },
    "streetwear": {
        "outfits": [
            {"name": "Urban Edge", "items": ["Graphic hoodie", "Cargo pants", "Chunky sneakers", "Beanie"], "colors": ["Black", "Olive", "Off-white"]},
            {"name": "Hypebeast Casual", "items": ["Oversized bomber", "Joggers", "High-top sneakers", "Crossbody bag"], "colors": ["Burgundy", "Black", "White"]},
            {"name": "Street Minimal", "items": ["Fitted turtleneck", "Wide-leg jeans", "Clean sneakers", "Cap"], "colors": ["Grey", "Indigo", "White"]},
        ],
        "tips": ["Proportions are key in streetwear", "Limited-edition pieces add uniqueness", "Mix luxury with high-street"],
    },
    "bohemian": {
        "outfits": [
            {"name": "Free Spirit", "items": ["Flowy maxi skirt", "Embroidered top", "Leather sandals", "Layered necklaces"], "colors": ["Terracotta", "Cream", "Rust"]},
            {"name": "Festival Boho", "items": ["Crochet top", "Flared jeans", "Ankle boots", "Fringe bag"], "colors": ["Mustard", "Brown", "Teal"]},
            {"name": "Desert Wanderer", "items": ["Linen shirt dress", "Woven belt", "Espadrille wedges", "Wide-brim hat"], "colors": ["Sand", "Camel", "Copper"]},
        ],
        "tips": ["Layer different textures and patterns", "Natural fabrics breathe better", "Embrace imperfection — it's the boho way"],
    },
}

TREND_DATA = [
    {"trend": "Quiet Luxury", "description": "Understated elegance with premium fabrics and minimal branding", "season": "2024", "popularity": 95},
    {"trend": "Y2K Revival", "description": "Low-rise silhouettes, metallic fabrics, and nostalgic accessories", "season": "2024", "popularity": 88},
    {"trend": "Coastal Grandmother", "description": "Linen, flowing fabrics, and relaxed nautical-inspired palette", "season": "2024", "popularity": 82},
    {"trend": "Dopamine Dressing", "description": "Bold colors and playful prints to boost mood through fashion", "season": "2024", "popularity": 79},
    {"trend": "Gorpcore", "description": "Outdoorsy, technical fabrics merged with urban street style", "season": "2024", "popularity": 74},
    {"trend": "Coquette Aesthetic", "description": "Feminine, delicate pieces with bows, lace, and soft pink tones", "season": "2024", "popularity": 71},
]

def generate_recommendation(prompt, style_type="casual", body_type=None, occasion=None):
    """
    Generate fashion recommendation based on inputs.
    In production, this would call Gemini/Groq/HuggingFace APIs.
    """
    prompt_lower = prompt.lower()

    # Detect style from prompt
    detected_style = "casual"
    if any(w in prompt_lower for w in ["formal", "work", "office", "business", "professional"]):
        detected_style = "formal"
    elif any(w in prompt_lower for w in ["evening", "party", "dinner", "date", "night", "gala"]):
        detected_style = "evening"
    elif any(w in prompt_lower for w in ["street", "urban", "hype", "skate"]):
        detected_style = "streetwear"
    elif any(w in prompt_lower for w in ["boho", "bohemian", "festival", "hippie"]):
        detected_style = "bohemian"
    elif style_type in STYLE_TEMPLATES:
        detected_style = style_type

    template = STYLE_TEMPLATES.get(detected_style, STYLE_TEMPLATES["casual"])
    outfit = template["outfits"][datetime.now().second % len(template["outfits"])]

    # Build response
    response = {
        "style_category": detected_style.capitalize(),
        "outfit": outfit,
        "styling_tips": template["tips"],
        "color_palette": outfit["colors"],
        "occasion": occasion or "General Wear",
        "ai_note": f"Based on your request '{prompt[:60]}...', here's a curated {detected_style} look for you.",
        "confidence_score": 87 + (datetime.now().second % 10),
    }

    return response

def get_trend_insights(season=None):
    """Return current fashion trend insights."""
    return {
        "trends": TREND_DATA,
        "season": "Spring/Summer 2024",
        "key_colors": ["Peach Fuzz", "Warm Coral", "Sage Green", "Butter Yellow", "Electric Blue"],
        "key_fabrics": ["Linen", "Satin", "Leather", "Sheer Organza", "Recycled Denim"],
    }

# ─────────────────────────────────────────────
# PAGE ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="login")

@app.route("/signup")
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="signup")

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    recent = db.execute(
        "SELECT * FROM recommendations WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (session["user_id"],)
    ).fetchall()
    saved_count = db.execute(
        "SELECT COUNT(*) as cnt FROM saved_outfits WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()["cnt"]
    rec_count = db.execute(
        "SELECT COUNT(*) as cnt FROM recommendations WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()["cnt"]
    db.close()
    return render_template("dashboard.html", user=user, recent=recent, saved_count=saved_count, rec_count=rec_count)

@app.route("/recommend")
@login_required
def recommend_page():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    db.close()
    return render_template("recommend.html", user=user)

@app.route("/trends")
@login_required
def trends_page():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    db.close()
    return render_template("trends.html", user=user)

@app.route("/profile")
@login_required
def profile_page():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    history = db.execute(
        "SELECT * FROM recommendations WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (session["user_id"],)
    ).fetchall()
    saved = db.execute(
        "SELECT * FROM saved_outfits WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    db.close()
    return render_template("profile.html", user=user, history=history, saved=saved)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validation
    if not name or len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    if not validate_email(email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({"error": "An account with this email already exists"}), 409

    hashed = hash_password(password)
    cursor = db.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed)
    )
    db.commit()
    user_id = cursor.lastrowid
    db.close()

    session["user_id"] = user_id
    session["user_name"] = name
    return jsonify({"success": True, "redirect": "/dashboard"}), 201

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"success": True, "redirect": "/dashboard"})

@app.route("/api/recommend", methods=["POST"])
@login_required
def api_recommend():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    style_type = data.get("style_type", "casual")
    occasion = data.get("occasion", "")
    body_type = data.get("body_type", "")

    if not prompt or len(prompt) < 3:
        return jsonify({"error": "Please describe what you're looking for"}), 400

    result = generate_recommendation(prompt, style_type, body_type, occasion)

    # Save to history
    db = get_db()
    db.execute(
        "INSERT INTO recommendations (user_id, prompt, result, category) VALUES (?, ?, ?, ?)",
        (session["user_id"], prompt, json.dumps(result), style_type)
    )
    db.commit()
    db.close()

    return jsonify({"success": True, "recommendation": result})

@app.route("/api/trends", methods=["GET"])
@login_required
def api_trends():
    insights = get_trend_insights()
    return jsonify({"success": True, "data": insights})

@app.route("/api/save-outfit", methods=["POST"])
@login_required
def api_save_outfit():
    data = request.get_json()
    title = data.get("title", "").strip()
    description = data.get("description", "")
    tags = data.get("tags", [])

    if not title:
        return jsonify({"error": "Outfit title is required"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO saved_outfits (user_id, title, description, tags) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, description, json.dumps(tags))
    )
    db.commit()
    db.close()

    return jsonify({"success": True, "message": "Outfit saved!"})

@app.route("/api/update-profile", methods=["POST"])
@login_required
def api_update_profile():
    data = request.get_json()
    name = data.get("name", "").strip()
    style_profile = data.get("style_profile", {})

    if not name or len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400

    db = get_db()
    db.execute(
        "UPDATE users SET name = ?, style_profile = ? WHERE id = ?",
        (name, json.dumps(style_profile), session["user_id"])
    )
    db.commit()
    db.close()
    session["user_name"] = name
    return jsonify({"success": True, "message": "Profile updated!"})

@app.route("/api/history", methods=["GET"])
@login_required
def api_history():
    db = get_db()
    history = db.execute(
        "SELECT * FROM recommendations WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()
    db.close()
    return jsonify({
        "success": True,
        "history": [{"id": r["id"], "prompt": r["prompt"], "category": r["category"], "created_at": r["created_at"]} for r in history]
    })

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("🌟 StyleSense is running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
