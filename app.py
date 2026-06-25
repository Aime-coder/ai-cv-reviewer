import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="CV Reviewer — AI Powered",
    page_icon="📄",
    layout="centered"
)

# ── Styling ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0f1117; }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #8b8fa8;
        margin-bottom: 2rem;
    }

    .score-box {
        background: linear-gradient(135deg, #1e2235, #252a40);
        border: 1px solid #2e3450;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .score-number {
        font-size: 3.5rem;
        font-weight: 700;
        color: #6c8fff;
    }
    .score-label {
        font-size: 0.9rem;
        color: #8b8fa8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .section-card {
        background: #1a1e2e;
        border: 1px solid #2a2f45;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .green { color: #4ade80; }
    .red   { color: #f87171; }
    .blue  { color: #60a5fa; }
    .yellow{ color: #fbbf24; }

    .tag {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    .tag-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
    .tag-red    { background: #2d0a0a; color: #f87171; border: 1px solid #991b1b; }
    .tag-blue   { background: #0a1628; color: #60a5fa; border: 1px solid #1d4ed8; }

    textarea {
        font-family: 'Inter', monospace !important;
        font-size: 0.9rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4f63d2, #6c8fff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }

    .stTextArea > label { color: #8b8fa8 !important; font-size: 0.85rem !important; }
    .stSelectbox > label { color: #8b8fa8 !important; font-size: 0.85rem !important; }

    hr { border-color: #2a2f45; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── API Client ───────────────────────────────────────────────
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ── OOP Classes ──────────────────────────────────────────────
class CVReview:
    """Represents a structured CV review result."""

    def __init__(self, score, overall, strengths, weaknesses, improvements, keywords):
        self.score        = score
        self.overall      = overall
        self.strengths    = strengths
        self.weaknesses   = weaknesses
        self.improvements = improvements
        self.keywords     = keywords

    def is_strong(self):
        return self.score >= 7

    def grade(self):
        if self.score >= 9: return "Excellent"
        if self.score >= 7: return "Good"
        if self.score >= 5: return "Average"
        return "Needs Work"

    def __str__(self):
        return f"CVReview(score={self.score}/10, grade={self.grade()})"


class CVReviewer:
    """Handles communication with the AI API to review CVs."""

    def __init__(self, client, job_role="General"):
        self.client   = client
        self.job_role = job_role

    def build_prompt(self, cv_text):
        return f"""You are an expert HR professional and career coach with 15 years of experience reviewing CVs.

Review this CV for a {self.job_role} position and respond ONLY in this exact format — no extra text:

SCORE: [number 1-10]
OVERALL: [2-3 sentence overall impression]
STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]
WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]
IMPROVEMENTS:
- [specific improvement 1]
- [specific improvement 2]
- [specific improvement 3]
- [specific improvement 4]
KEYWORDS: [comma separated list of 6-8 important keywords missing or present]

CV TEXT:
{cv_text}"""

    def review(self, cv_text):
        response = self.client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": self.build_prompt(cv_text)}],
            max_tokens=1000
        )
        raw = response.choices[0].message.content
        return self._parse(raw)

    def _parse(self, raw):
        """Parse AI response into a CVReview object."""
        lines = raw.strip().split("\n")
        score        = 5
        overall      = ""
        strengths    = []
        weaknesses   = []
        improvements = []
        keywords     = []
        current      = None

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip().split()[0])
                except:
                    score = 5
            elif line.startswith("OVERALL:"):
                overall  = line.replace("OVERALL:", "").strip()
                current  = "overall"
            elif line == "STRENGTHS:":
                current = "strengths"
            elif line == "WEAKNESSES:":
                current = "weaknesses"
            elif line == "IMPROVEMENTS:":
                current = "improvements"
            elif line.startswith("KEYWORDS:"):
                kw_raw   = line.replace("KEYWORDS:", "").strip()
                keywords = [k.strip() for k in kw_raw.split(",")]
                current  = None
            elif line.startswith("- ") and current:
                item = line[2:].strip()
                if current == "strengths":    strengths.append(item)
                elif current == "weaknesses": weaknesses.append(item)
                elif current == "improvements": improvements.append(item)
            elif current == "overall" and line and not line.startswith("STRENGTH"):
                overall += " " + line

        return CVReview(score, overall.strip(), strengths, weaknesses, improvements, keywords)


# ── UI ───────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📄 AI CV Reviewer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Paste your CV and get instant, professional feedback powered by AI.</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    job_role = st.selectbox(
        "Target Job Role",
        ["General", "Software Engineer", "Data Scientist", "AI Engineer",
         "Product Manager", "Marketing", "Finance", "Designer"]
    )
    st.markdown("---")
    st.markdown("### 📌 Tips for best results")
    st.markdown("""
- Paste the **full CV text**
- Include your skills, experience, and education
- The more detail, the better the review
    """)
    st.markdown("---")
    st.markdown("**Built by Parfait 🇷🇼**")
    st.markdown("Junior AI Developer")

# Main input
cv_text = st.text_area(
    "Paste your CV text here",
    height=280,
    placeholder="John Doe\nSoftware Engineer\n\nEXPERIENCE\n...\n\nSKILLS\n...\n\nEDUCATION\n..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    review_btn = st.button("🔍 Review My CV")

# ── Run Review ───────────────────────────────────────────────
if review_btn:
    if not cv_text.strip():
        st.warning("Please paste your CV text first.")
    elif len(cv_text.strip()) < 100:
        st.warning("Your CV seems too short. Please paste the full content.")
    else:
        with st.spinner("Analyzing your CV..."):
            reviewer = CVReviewer(client, job_role)
            review   = reviewer.review(cv_text)

        st.markdown("---")
        st.markdown("## 📊 Your Results")

        # Score box
        color = "#4ade80" if review.is_strong() else "#fbbf24" if review.score >= 5 else "#f87171"
        st.markdown(f"""
        <div class="score-box">
            <div class="score-number" style="color:{color}">{review.score}<span style="font-size:1.5rem;color:#8b8fa8">/10</span></div>
            <div class="score-label">{review.grade()} CV</div>
        </div>
        """, unsafe_allow_html=True)

        # Overall
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title blue">💬 Overall Impression</div>
            <p style="color:#cbd5e1;margin:0">{review.overall}</p>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            items = "".join([f'<div class="tag tag-green">✓ {s}</div>' for s in review.strengths])
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title green">✅ Strengths</div>
                {items}
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            items = "".join([f'<div class="tag tag-red">✗ {w}</div>' for w in review.weaknesses])
            st.markdown(f"""
            <div class="section-card">
                <div class="section-title red">⚠️ Weaknesses</div>
                {items}
            </div>
            """, unsafe_allow_html=True)

        # Improvements
        imp_html = "".join([f"<li style='color:#cbd5e1;margin-bottom:0.4rem'>{i}</li>" for i in review.improvements])
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title yellow">🎯 How to Improve</div>
            <ul style="margin:0;padding-left:1.2rem">{imp_html}</ul>
        </div>
        """, unsafe_allow_html=True)

        # Keywords
        kw_html = "".join([f'<span class="tag tag-blue">{k}</span>' for k in review.keywords])
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title blue">🔑 Keywords</div>
            {kw_html}
        </div>
        """, unsafe_allow_html=True)

        st.success(f"Review complete! Your CV scored {review.score}/10 for a {job_role} role.")