# The Empirical Lens — Fake News Detection System

**CSE439 Capstone Project | B.Tech CSE | Lovely Professional University**
**January – May 2026 | Supervisor: Mr. Akshay Kumar**

A full-stack fake news detection web application that uses a 4-signal ensemble to analyze news text and deliver a transparent, explainable verdict.

---

## Team

| Name | Reg. No | Role |
|---|---|---|
| Lakshya Kumar Pandey | 12215715 | Backend & API |
| Justin Mathew Francis | 12217882 | ML Model |
| Ajay Singh Patel | 12217954 | Frontend |
| Nitin Kumar | 12210055 | Frontend |
| Varun Narsana | 12216943 | Ensemble / Signal Pipeline |

---

## How It Works

The system runs 4 independent signals on the input text and combines them with weighted averaging:

| Signal | Weight | Description |
|---|---|---|
| ML Classifier | 35% | TF-IDF + Logistic Regression trained on Kaggle Fake/Real News dataset |
| Wikipedia | 30% | Extracts claim from text, cross-references Wikipedia article |
| Google Fact Check API | 25% | Queries Google's fact-check database for matching claims |
| Knowledge Base | 10% | Local `facts_kb.json` with curated verifiable facts |

If a signal finds no result, its weight is redistributed proportionally to the active signals.

---

## Tech Stack

- **Backend:** Python, Flask, Flask-JWT-Extended, SQLAlchemy, Alembic
- **Database:** MySQL
- **ML:** scikit-learn (Logistic Regression + TF-IDF)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (served by Flask)
- **Auth:** JWT with token versioning

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your DB credentials, JWT secret, and Google API key
```

### 4. Set up the database
```bash
flask db upgrade
```

### 5. Run the app
```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## Project Structure

```
├── app.py                  # Flask entry point
├── db.py                   # SQLAlchemy instance
├── facts_kb.json           # Local knowledge base
├── fake_news_model.pkl     # Trained Logistic Regression model
├── vectorizer.pkl          # TF-IDF vectorizer
├── requirements.txt
├── .env.example
├── controller/             # Flask Blueprints (auth, user, analyze)
├── Service/                # Business logic & signal services
├── Models/                 # SQLAlchemy models (Users, Predictions)
├── migrations/             # Alembic migration files
└── frontend/               # HTML, CSS, JS (single-page app)
```

---

## Notes

- `.env` is excluded from version control — never commit real credentials
- `fake_news_distilroberta/` (old transformer model) is excluded — project uses sklearn pkl
