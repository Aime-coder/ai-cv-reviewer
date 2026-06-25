# 📄 AI CV Reviewer

An AI-powered CV/Resume reviewer built with Python OOP + Streamlit + OpenRouter API.

## 🚀 Live App
[Open the Live App](ai-cv-reviewer-ngr9jvvkrg6cyhwe5eern6.streamlit.app)

## ✨ Features
- Paste any CV and get instant AI feedback
- Score out of 10
- Strengths, weaknesses, and specific improvements
- Filter by job role (Software Engineer, Data Scientist, etc.)
- Clean dark UI

## 🧠 OOP Concepts Used
| Concept | How it's used |
|---|---|
| Classes | `CVReview`, `CVReviewer` |
| Encapsulation | Review data stored inside `CVReview` object |
| Methods | `review()`, `_parse()`, `is_strong()`, `grade()` |
| `__str__` | String representation of a review |

## 🛠️ Tech Stack
- Python
- Streamlit
- OpenRouter API (Mistral 7B)
- python-dotenv

## ⚙️ Run Locally
```bash
git clone https://github.com/Aime-coder/ai-cv-reviewer
cd ai-cv-reviewer
pip install -r requirements.txt
# create .env file with: OPENROUTER_API_KEY=your-key
streamlit run app.py
```

## 👨‍💻 Built by
**Ndacyayisenga Parfait** 🇷🇼 — Junior AI Developer  
University of Lodz, Poland