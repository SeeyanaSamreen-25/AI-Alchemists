# ✦ StyleSense — AI Fashion Recommendation System

A production-ready, full-stack web application for AI-powered personalized fashion recommendations. Built with Flask, SQLite3, and a beautiful dark editorial UI.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
stylesense/
├── app.py                  # Flask backend — routes, API, AI engine
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── stylesense.db           # SQLite database (auto-created)
├── templates/
│   ├── base.html           # Base layout
│   ├── index.html          # Landing page
│   ├── auth.html           # Login / Signup
│   ├── dashboard.html      # Main dashboard
│   ├── recommend.html      # AI outfit builder
│   ├── trends.html         # Fashion trends
│   └── profile.html        # User profile & history
└── static/
    ├── css/main.css        # Complete design system
    └── js/main.js          # Frontend utilities
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Auth System** | Login/Signup with SHA-256 password hashing |
| **AI Outfit Builder** | Prompt-based outfit generation with style analysis |
| **Trend Insights** | Season's top trending aesthetics with popularity metrics |
| **Style Profiles** | Personalized style preferences per user |
| **History** | Track all generated recommendations |
| **Save Outfits** | Bookmark favorite looks |
| **Responsive UI** | Works beautifully on desktop and mobile |

---

## 🔌 Extending with Real AI

To connect Gemini, Groq, or HuggingFace, replace `generate_recommendation()` in `app.py`:

```python
# Example: Gemini
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

def generate_recommendation(prompt, ...):
    response = model.generate_content(f"Fashion stylist: {prompt}")
    # Parse and return structured result
```

---

## 🗃️ Database

SQLite3 database with 3 tables:
- **users** — accounts, preferences, style profiles
- **recommendations** — full recommendation history
- **saved_outfits** — bookmarked looks

---

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Cormorant Garamond + DM Sans
- **Auth**: Session-based with hashed passwords

---

Made with ✦ by StyleSense
