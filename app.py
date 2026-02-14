import os
from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import PyPDF2
from dotenv import load_dotenv
import re
from math import ceil

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
# Disable debug routes by default; set environment variable ENABLE_DEBUG_ROUTES=1 to enable
app.config['ENABLE_DEBUG_ROUTES'] = os.getenv('ENABLE_DEBUG_ROUTES', '0') == '1'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    subjects = db.relationship('Subject', backref='owner', lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_name = db.Column(db.String(120))
    roll_number = db.Column(db.String(80))
    subject_name = db.Column(db.String(200))
    exam_date = db.Column(db.String(20))
    priority = db.Column(db.String(20))
    pdf_file = db.Column(db.String(400))


class StudyPlan(db.Model):
    __tablename__ = 'study_plan'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    plan_data = db.Column(db.Text)

    def __repr__(self):
        return f"<StudyPlan subject_id={self.subject_id}>"
@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader. Returns None if `User` model is not yet defined or not found."""
    try:
        User = globals().get('User')
        if User is None:
            return None
        # Prefer SQLAlchemy 2.0 style get if available
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return User.query.get(int(user_id))
    except Exception:
        return None
def extract_chapters_and_topics(pdf_text: str):
    """Extract unit/chapter headings, their hours and topic lists from PDF text.

    This function uses heuristics to find lines that look like 'Unit 1', 'UNIT I',
    'Chapter 1' etc., segments text between headers, and extracts bulleted/numbered
    topics. It returns a list of chapters each with 'name', 'topics' and optional 'hours'.
    """
    chapters = []

    if not pdf_text:
        return chapters

    # Normalize text and remove common page markers
    try:
        pdf_text = re.sub(r'-{2,}\s*Page\s*\d+\s*-{2,}', ' ', pdf_text, flags=re.IGNORECASE)
    except Exception:
        pass

    # Normalize line endings and split into non-empty lines
    lines = [ln.strip() for ln in re.split(r'\r?\n', pdf_text) if ln and ln.strip()]

    # Heuristic patterns for headers
    header_patterns = [
        re.compile(r'^(Unit|UNIT|UNIT\b).*', re.IGNORECASE),
        re.compile(r'^(Chapter|CHAPTER|CHAP\.)\b', re.IGNORECASE),
        re.compile(r'^Module\b', re.IGNORECASE),
        re.compile(r'^\bUnit\s+\d+\b', re.IGNORECASE)
    ]

    header_indices = []
    for i, ln in enumerate(lines):
        for pat in header_patterns:
            if pat.search(ln):
                header_indices.append((i, ln))
                break

    # Fallback searches for common header variants
    if not header_indices:
        for i, ln in enumerate(lines):
            if re.search(r'\bUNIT\s+\d+\b', ln, re.IGNORECASE) or re.search(r'\bUnit\s+\d+[:\-]?', ln):
                header_indices.append((i, ln))

    if not header_indices:
        for i, ln in enumerate(lines):
            if re.match(r'^(Chapter|CHAPTER)\b', ln):
                header_indices.append((i, ln))

    # Segment text between headers
    segments = []
    if header_indices:
        for idx, (pos, hdr) in enumerate(header_indices):
            start = pos
            end = header_indices[idx + 1][0] if idx + 1 < len(header_indices) else len(lines)
            segments.append((hdr, lines[start + 1:end]))
    else:
        segments.append(('Course Content', lines))

    # Parse each segment into a chapter/unit
    for hdr, seg in segments:
        name = re.sub(r'^(Unit|UNIT|Chapter|CHAPTER|Module)[:\.\-\s]*', '', hdr, flags=re.IGNORECASE).strip()
        if not name:
            name = hdr.strip()

        # Try to find hours in header or first lines of segment
        hours = None
        head_block = hdr + ' ' + ' '.join(seg[:3])
        m = re.search(r'(\d{1,2})\s*(?:hours|hrs|Hrs|Hours)', head_block, re.IGNORECASE)
        if m:
            hours = f"{m.group(1)} hours"

        topics = []
        capture = False
        for ln in seg:
            # Start capture after explicit 'Topics' or 'Syllabus' markers
            if re.match(r'^(Topics|Syllabus|Course Content|Contents)[:\-]?', ln, re.IGNORECASE):
                capture = True
                parts = re.split(r'[:\-]\s*', ln, maxsplit=1)
                if len(parts) > 1 and len(parts[1].strip()) > 3:
                    extra = parts[1].strip()
                    for p in re.split(r';|,\s(?=[A-Z])', extra):
                        p = p.strip()
                        if len(p) > 3:
                            topics.append(p)
                continue

            if capture:
                if re.match(r'^(Unit|UNIT|Chapter|CHAPTER|Module)\b', ln, re.IGNORECASE):
                    break
                if re.match(r'^[•\-\*\+→]\s+(.+)', ln) or re.match(r'^\d+[\.\)]\s+(.+)', ln) or re.match(r'^[a-zA-Z]\)\s+(.+)', ln):
                    t = re.sub(r'^[•\-\*\+→\d\.\)\s]+', '', ln).strip()
                    if len(t) > 2:
                        topics.append(t)
                    continue
                if 5 < len(ln) < 160 and any(k in ln.lower() for k in ['introduction', 'overview', 'objective', 'learning', 'apply', 'practice', 'exercise', 'concept', 'topic', 'unit']):
                    topics.append(ln)
                    continue

            else:
                if re.match(r'^[•\-\*\+→]\s+(.+)', ln) or re.match(r'^\d+[\.\)]\s+(.+)', ln):
                    t = re.sub(r'^[•\-\*\+→\d\.\)\s]+', '', ln).strip()
                    if len(t) > 3:
                        topics.append(t)

        # Fallback: take first substantive lines if no explicit topics
        if not topics:
            for ln in seg:
                if len(ln) > 12 and not re.match(r'^(Reference|Textbook|Books|CO-PO|Assessment|Outcome)', ln, re.IGNORECASE):
                    topics.append(ln)
                if len(topics) >= 12:
                    break

        # Clean duplicates preserving order
        seen = set()
        clean_topics = []
        for t in topics:
            t2 = re.sub(r'\s+', ' ', t).strip().rstrip('.,;:')
            if t2 and t2.lower() not in seen:
                clean_topics.append(t2)
                seen.add(t2.lower())

        chapter = {'name': name, 'topics': clean_topics}
        if hours:
            chapter['hours'] = hours

        if chapter['topics'] or chapter.get('hours'):
            chapters.append(chapter)

    # Limit to reasonable number of chapters
    if len(chapters) > 10:
        chapters = chapters[:10]

    return chapters

def read_pdf(filepath, max_pages=50):
    """Read text from a PDF file using PyPDF2, with per-page error handling."""
    text_parts = []
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = min(len(reader.pages), max_pages)
            for i in range(num_pages):
                try:
                    page = reader.pages[i]
                    page_text = page.extract_text() or ''
                    text_parts.append(page_text)
                except Exception:
                    # skip problematic pages but continue
                    continue
    except Exception:
        return ''

    return '\n'.join(p for p in text_parts if p)

def calculate_days_until_exam(exam_date_str):
    """Calculate days remaining until exam."""
    try:
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = (exam_date - today).days
        return max(1, delta)
    except:
        return 30

def generate_weekly_plan(chapters, exam_date, priority):
    """Generate a day-wise or weekly study plan based on exam date and chapters."""
    
    days_remaining = calculate_days_until_exam(exam_date)
    weeks_remaining = max(1, days_remaining // 7)
    
    plan = {
        'total_chapters': len(chapters),
        'total_topics': sum(len(ch['topics']) for ch in chapters),
        'days_remaining': days_remaining,
        'weeks_remaining': weeks_remaining,
        'priority': priority,
        'weekly_schedule': []
    }
    
    # Distribute chapters across weeks
    chapters_per_week = max(1, ceil(len(chapters) / max(1, weeks_remaining)))
    
    week_num = 1
    chapter_idx = 0
    
    for week in range(min(weeks_remaining, 12)):
        week_data = {
            'week': week_num,
            'chapters': [],
            'revision_focus': []
        }
        
        # Assign chapters to this week
        weeks_chapters = 0
        while weeks_chapters < chapters_per_week and chapter_idx < len(chapters):
            chapter = chapters[chapter_idx]
            
            # Calculate topics per day for this chapter
            num_topics = len(chapter['topics'])
            days_for_chapter = max(2, min(4, ceil(num_topics / 4)))
            
            week_data['chapters'].append({
                'name': chapter['name'],
                'topics': chapter['topics'][:12],  # Limit to 12 topics display
                'all_topics_count': num_topics,
                'study_days': days_for_chapter,
                'daily_topics': ceil(num_topics / days_for_chapter) if days_for_chapter > 0 else 1,
                'estimated_hours': days_for_chapter * 2
            })
            
            chapter_idx += 1
            weeks_chapters += 1
        
        # Add revision focus from previous weeks
        if week_num > 1 and week_data['chapters']:
            week_data['revision_focus'] = [ch['name'] for ch in week_data['chapters'][:1]]
        
        if week_data['chapters']:  # Only add week if it has chapters
            plan['weekly_schedule'].append(week_data)
        
        week_num += 1
    
    # Add final revision week
    plan['final_revision'] = {
        'focus': 'Comprehensive Revision & Mock Tests',
        'activities': [
            f"Complete revision of all {len(chapters)} chapters",
            "Practice with previous year papers",
            "Identify and focus on weak areas",
            "Full mock test (under exam conditions)",
            "Quick review 1 day before exam",
            "Get 8+ hours sleep before exam day"
        ]
    }
    
    return plan

def format_study_plan_html(chapters, study_plan):
    """Format the study plan as polished HTML."""
    
    html = f"""
    <div class="study-plan-container">
        <div class="plan-summary">
            <h3>📊 Study Plan Overview</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">Total Chapters</span>
                    <span class="value">{study_plan['total_chapters']}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Total Topics</span>
                    <span class="value">{study_plan['total_topics']}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Days Until Exam</span>
                    <span class="value">{study_plan['days_remaining']}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Priority</span>
                    <span class="value">{study_plan['priority']}</span>
                </div>
            </div>
            <p class="recommendation">📚 <strong>Recommended Study Time:</strong> 2-3 hours daily</p>
        </div>

        <div class="syllabus-structure">
            <h3>📖 Syllabus Structure</h3>
            <div class="chapters-container">
    """
    
    for idx, chapter in enumerate(chapters, 1):
        num_topics = len(chapter['topics'])
        difficulty = "Hard" if num_topics > 15 else "Medium" if num_topics > 8 else "Easy"
        
        html += f"""
                <div class="chapter-card">
                    <div class="chapter-header">
                        <h4>Chapter {idx}: {chapter['name']}</h4>
                        <span class="difficulty-badge difficulty-{difficulty.lower()}">{difficulty}</span>
                    </div>
                    <p class="topic-count">📚 {num_topics} Topics</p>
                    <div class="topics-list">
                        <ul>
        """
        
        # Show all topics
        for topic in chapter['topics']:
            # Limit topic text to reasonable length
            topic_text = topic[:80] + "..." if len(topic) > 80 else topic
            html += f"<li>{topic_text}</li>"
        
        html += """
                        </ul>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>

        <div class="weekly-plan">
            <h3>📅 Weekly Study Schedule</h3>
            <div class="weeks-container">
    """
    
    for week_data in study_plan['weekly_schedule']:
        html += f"""
                <div class="week-card">
                    <h4>📍 Week {week_data['week']}</h4>
        """
        
        for chapter in week_data['chapters']:
            html += f"""
                    <div class="chapter-study-week">
                        <h5>{chapter['name']}</h5>
                        <div class="study-details">
                            <span class="detail-item">⏱️ {chapter['study_days']} days</span>
                            <span class="detail-item">⏰ {chapter['estimated_hours']} hours total</span>
                            <span class="detail-item">📝 {chapter['daily_topics']} topics/day</span>
                        </div>
                        <div class="topics-preview">
                            <p><strong>Topics to Cover:</strong></p>
                            <ul>
            """
            
            # Show all topics in week view
            for topic in chapter['topics']:
                topic_text = topic[:70] + "..." if len(topic) > 70 else topic
                html += f"<li>{topic_text}</li>"
            
            if chapter['all_topics_count'] > len(chapter['topics']):
                html += f"<li><em class='additional'>... and {chapter['all_topics_count'] - len(chapter['topics'])} more topics</em></li>"
            
            html += """
                            </ul>
                        </div>
                    </div>
            """
        
        html += """
                </div>
        """
    
    # Final revision
    html += f"""
            </div>

            <div class="final-revision-card">
                <h4>🎯 Final Revision Week</h4>
                <p><strong>{study_plan['final_revision']['focus']}</strong></p>
                <ul class="revision-activities">
    """
    
    for activity in study_plan['final_revision']['activities']:
        html += f"<li>✓ {activity}</li>"
    
    html += """
                </ul>
            </div>
        </div>

        <div class="study-tips-section">
            <h3>💡 Study Tips for Success</h3>
            <div class="tips-grid">
                <div class="tip-card">
                    <h5>📚 Reading Strategy</h5>
                    <ul>
                        <li>Read chapter overview first</li>
                        <li>Focus on key topics listed</li>
                        <li>Make summary notes</li>
                        <li>Highlight important concepts</li>
                    </ul>
                </div>
                <div class="tip-card">
                    <h5>⏱️ Time Management</h5>
                    <ul>
                        <li>Study 2-3 hours daily</li>
                        <li>Take 45-min focused sessions</li>
                        <li>10-minute breaks between sessions</li>
                        <li>Follow the weekly schedule</li>
                    </ul>
                </div>
                <div class="tip-card">
                    <h5>✍️ Practice & Review</h5>
                    <ul>
                        <li>Solve practice problems</li>
                        <li>Use previous year papers</li>
                        <li>Create formula/concept cards</li>
                        <li>Revise daily for 15 min</li>
                    </ul>
                </div>
                <div class="tip-card">
                    <h5>🧠 Before Exam</h5>
                    <ul>
                        <li>Complete 3-4 mock tests</li>
                        <li>Focus on weak topics</li>
                        <li>Sleep 7-8 hours before exam</li>
                        <li>Light review morning of exam</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

# ============== ROUTES ==============

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_home'))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            
            # Validation
            if not username or not email or not password:
                return jsonify({'error': 'All fields are required'}), 400
            
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('dashboard_home'))
        
        except Exception as e:
            print(f"Register Error: {e}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            # Find user
            user = User.query.filter_by(username=username).first()
            
            if user is None or not user.check_password(password):
                return jsonify({'error': 'Invalid username or password'}), 401
            
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard_home'))
        
        except Exception as e:
            print(f"Login Error: {e}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard_home():
    """Show user's subjects and quick actions."""
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard_home.html", subjects=subjects, user=current_user)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    
    try:
        # Get form data
        student_name = request.form.get("student_name", "Student")
        roll_number = request.form.get("roll_number", "")
        subject_name = request.form.get("subject_name", "Subject")
        exam_date = request.form.get("exam_date", "")
        priority = request.form.get("priority", "Medium")
        
        # Validate required fields
        if not exam_date:
            return jsonify({'error': 'Exam date is required'}), 400
        
        pdf = request.files.get("pdf_file")
        if not pdf or pdf.filename == '':
            return jsonify({'error': 'PDF file is required'}), 400
        
        # Save PDF
        filename = f"{current_user.id}_{pdf.filename.replace(' ', '_')}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf.save(filepath)
        
        # Save to database (linked to current user)
        subject = Subject(
            user_id=current_user.id,
            student_name=student_name,
            roll_number=roll_number,
            subject_name=subject_name,
            exam_date=exam_date,
            priority=priority,
            pdf_file=filepath
        )
        db.session.add(subject)
        db.session.commit()
        
        # Extract text from PDF
        pdf_text = read_pdf(filepath)
        
        if not pdf_text or len(pdf_text.strip()) < 30:
            # Even if PDF is mostly empty, create a basic plan
            print(f"Warning: PDF text extraction minimal, using fallback")
            chapters = [{
                'name': 'Study Material',
                'topics': [
                    'Introduction and Overview',
                    'Core Concepts and Principles',
                    'Key Topics and Content',
                    'Practical Applications',
                    'Review and Assessment'
                ]
            }]
        else:
            # Extract chapters and topics
            chapters = extract_chapters_and_topics(pdf_text)
            
            # If extraction failed, use fallback
            if not chapters or len(chapters) == 0:
                chapters = [{
                    'name': 'Extracted Content',
                    'topics': [line for line in pdf_text.split('\n') if 10 < len(line) < 150][:15]
                }]
        
        # Generate study plan
        study_plan = generate_weekly_plan(chapters, exam_date, priority)
        
        # Format as HTML
        plan_html = format_study_plan_html(chapters, study_plan)
        
        # Save plan to database
        study_plan_record = StudyPlan(
            subject_id=subject.id,
            plan_data=plan_html
        )
        db.session.add(study_plan_record)
        db.session.commit()
        
        return render_template("dashboard.html",
                             student_name=student_name,
                             subject_name=subject_name,
                             exam_date=exam_date,
                             plan=plan_html)
    
    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route("/calendar")
@login_required
def calendar():
    # Only show current user's subjects
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template("calendar.html", subjects=subjects)

@app.route("/subject/<int:subject_id>")
@login_required
def view_subject(subject_id):
    """View specific subject's study plan."""
    subject = Subject.query.get_or_404(subject_id)
    
    # Ensure user owns this subject
    if subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    study_plan = StudyPlan.query.filter_by(subject_id=subject_id).first()
    plan_html = study_plan.plan_data if study_plan else "<p>No study plan generated yet.</p>"
    
    return render_template("dashboard.html",
                         student_name=subject.student_name,
                         subject_name=subject.subject_name,
                         exam_date=subject.exam_date,
                         plan=plan_html)

@app.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id):
    """Delete a subject (only if user owns it)."""
    subject = Subject.query.get_or_404(subject_id)
    
    # Ensure user owns this subject
    if subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Delete PDF file
        if os.path.exists(subject.pdf_file):
            os.remove(subject.pdf_file)
        
        # Delete from database
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        print(f"Delete Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/test-plan")
@login_required
def test_plan():
    """Test route to generate a sample plan without PDF (for testing)."""
    
    sample_chapters = [
        {
            'name': 'Chapter 1: Introduction & Fundamentals',
            'topics': ['Definition and scope of subject', 'Historical background and evolution', 'Key terminologies', 'Importance and applications', 'Learning objectives', 'Overview of chapters']
        },
        {
            'name': 'Chapter 2: Core Concepts & Theory',
            'topics': ['Fundamental principles', 'Theoretical framework', 'Mathematical foundations', 'Key formulas and equations', 'Derivations', 'Examples and applications', 'Case studies']
        },
        {
            'name': 'Chapter 3: Advanced Topics',
            'topics': ['Complex concepts', 'Advanced applications', 'Real-world scenarios', 'Problem-solving methods', 'Integration with other topics', 'Research methods', 'Current trends']
        },
        {
            'name': 'Chapter 4: Practical Implementation',
            'topics': ['Laboratory procedures', 'Practical exercises', 'Project-based learning', 'Hands-on practice', 'Safety considerations', 'Tools and equipment']
        }
    ]
    
    # Use a default exam date 30 days from now
    exam_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    study_plan = generate_weekly_plan(sample_chapters, exam_date, "Medium")
    plan_html = format_study_plan_html(sample_chapters, study_plan)
    
    return render_template("dashboard.html",
                         student_name="Test Student",
                         subject_name="Sample Subject",
                         exam_date=exam_date,
                         plan=plan_html)


@app.route('/_parse_test')
def _parse_test():
    """Debug route: parse PDFs in uploads/ and return detected units/topics."""
    if not app.config.get('ENABLE_DEBUG_ROUTES'):
        return jsonify({'success': False, 'error': 'Not Found'}), 404

    try:
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith('.pdf')][:10]
        results = []
        for f in files:
            path = os.path.join(app.config['UPLOAD_FOLDER'], f)
            txt = read_pdf(path)
            ch = extract_chapters_and_topics(txt)
            units = []
            for c in ch:
                units.append({'name': c.get('name'), 'topics': len(c.get('topics', [])), 'hours': c.get('hours')})
            results.append({'file': f, 'units': units})
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/status')
def status():
    """Return simple server/process status helpful for troubleshooting connectivity."""
    import subprocess, os, time
    pid = os.getpid()
    # Run netstat to show listeners for port 5000 (Windows)
    try:
        netout = subprocess.check_output('netstat -ano | findstr ":5000"', shell=True, text=True)
        net_lines = [ln for ln in netout.splitlines() if ln.strip()]
    except Exception as e:
        net_lines = [f"netstat error: {e}"]

    uploads_ok = os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads'))
    pdf_count = 0
    try:
        pdf_count = len([f for f in os.listdir(app.config.get('UPLOAD_FOLDER', 'uploads')) if f.lower().endswith('.pdf')])
    except Exception:
        pdf_count = 0

    if not app.config.get('ENABLE_DEBUG_ROUTES'):
        return jsonify({'success': False, 'error': 'Not Found'}), 404

    return jsonify({
        'running': True,
        'pid': pid,
        'netstat': net_lines,
        'host': request.host,
        'uploads_folder_exists': uploads_ok,
        'pdf_count': pdf_count,
        'recommended_access_urls': ['http://127.0.0.1:5000', 'http://localhost:5000']
    })


@app.route('/create_test_user')
def create_test_user():
    """Temporary: create a test user (username: testuser, password: Test1234!) if it doesn't exist.

    Remove this endpoint in production.
    """
    username = 'testuser'
    email = 'test@example.com'
    password = 'Test1234!'
    if not app.config.get('ENABLE_DEBUG_ROUTES'):
        return jsonify({'created': False, 'error': 'Not available'}), 404

    try:
        with app.app_context():
            existing = User.query.filter_by(username=username).first()
            if existing:
                return jsonify({'created': False, 'reason': 'already exists', 'username': username})
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'created': True, 'username': username, 'password': password})
    except Exception as e:
        return jsonify({'created': False, 'error': str(e)})

if __name__ == "__main__":
    print("Starting Flask app on http://127.0.0.1:5000 (or http://localhost:5000). If you cannot connect, try host='0.0.0.0' or check Windows firewall.")
    # Ensure database tables exist
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print('Warning: db.create_all() failed:', e)
    app.run(debug=True, host='0.0.0.0', port=5000)
