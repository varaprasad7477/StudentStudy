import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# ---------------- DATABASE ----------------

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    roll_number = db.Column(db.String(50))
    subject_name = db.Column(db.String(100))
    exam_date = db.Column(db.String(20))
    priority = db.Column(db.String(20))
    pdf_file = db.Column(db.String(200))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    topic = db.Column(db.String(300))
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# ---------------- PDF READER ----------------

def read_pdf(filepath):
    text = ""
    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

# ---------------- AI PLANNER ----------------

def generate_plan(text, exam_date, priority):

    prompt = f"""You are an academic advisor. Parse the university syllabus PDF and create a detailed study plan.

EXAM DATE: {exam_date}
PRIORITY: {priority}

SYLLABUS FROM PDF:
{text}

TASK: Extract modules/chapters and their topics, then create a study schedule.

OUTPUT FORMAT:

SYLLABUS STRUCTURE:
==================
Module/Chapter Name: [Exact name from syllabus]
Topics to Learn:
  • Topic 1: [Topic name and description]
  • Topic 2: [Topic name and description]
  • Topic 3: [Topic name and description]
Key Learning Outcomes:
  - Outcome 1
  - Outcome 2
Estimated Study Time: [X hours/days based on complexity]
Difficulty Level: [Easy/Medium/Hard]

[Repeat for each module in the syllabus]

PERSONALIZED STUDY SCHEDULE:
===========================
Based on exam date: {exam_date}

Week 1:
  - Monday-Tuesday: [Module name] - [Topic names to cover]
  - Wednesday-Thursday: [Module name] - [Practical work]
  - Friday-Sunday: Revision and practice

[Continue with remaining weeks and modules]

REVISION SCHEDULE:
==================
- Revision Week: [2 weeks before exam]
- Final Revision: [1 week before exam]
- Practice Tests: [Based on importance]

IMPORTANT:
1. Extract EXACT module names and topics from the provided syllabus
2. Use only information present in the syllabus - NO generic content
3. Respect the modules order as given in syllabus
4. If Priority is "High" - emphasize learning outcomes and practicals
5. Create realistic timeline based on exam date"""

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback mock plan if API call fails
        return f"""
AI STUDY PLAN - {exam_date}
{'='*50}

Priority Level: {priority}

WEEK 1: FOUNDATION & OVERVIEW
- Day 1-2: Read Chapters 1-3, Create summary notes
- Day 3-4: Practice basic concepts
- Day 5: Review and consolidate
- Day 6-7: Rest/Buffer for difficult topics

WEEK 2: CORE CONCEPTS
- Day 1-3: Deep dive into main topics
- Day 4-5: Practice problems and exercises
- Day 6: Revision of Week 1 & 2
- Day 7: Full practice test

WEEK 3: ADVANCED & REVISION
- Day 1-3: Advanced topics and applications
- Day 4-5: Mock exams
- Day 6: Final revision and weak areas
- Day 7: Light review and confidence building

EXAM WEEK:
- Do light revision only
- Practice 2-3 sample papers
- Get good sleep before exam

IMPORTANT TOPICS TO FOCUS ON (High Priority):
- Core concepts that appear in multiple chapters
- Diagrams and important formulas
- Previous exam question patterns

NOTE: This is a sample plan. Connect your Google Gemini API key for a personalized AI-generated plan.
Error: {str(e)}
        """

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    student_name = request.form["student_name"]
    roll_number = request.form["roll_number"]
    subject_name = request.form["subject_name"]
    exam_date = request.form["exam_date"]
    priority = request.form["priority"]
    pdf = request.files["pdf_file"]

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
    pdf.save(filepath)

    subject = Subject(
        student_name=student_name,
        roll_number=roll_number,
        subject_name=subject_name,
        exam_date=exam_date,
        priority=priority,
        pdf_file=filepath
    )

    db.session.add(subject)
    db.session.commit()

    syllabus_text = read_pdf(filepath)
    plan = generate_plan(syllabus_text, exam_date, priority)

    return render_template("dashboard.html",
                           student_name=student_name,
                           subject_name=subject_name,
                           plan=plan)

@app.route("/calendar")
def calendar():
    subjects = Subject.query.all()
    return render_template("calendar.html", subjects=subjects)

if __name__ == "__main__":
    app.run(debug=True)
