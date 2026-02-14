# ⚡ Quick Start Guide

## 🚀 Start the Application

```bash
# Navigate to project
cd "c:\Users\vara prasad\Desktop\Study-Planner\AI-Study-Planner"

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the app
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

Open browser: **http://127.0.0.1:5000**

---

## ✅ What's Working Now

### ✓ Upload Syllabus
- No more database errors
- Accepts PDFs with or without clear structure
- Generates plans even if parsing is incomplete

### ✓ View Study Plans
- Beautiful dashboard with:
  - Syllabus structure (all chapters + topics)
  - Weekly schedule with time estimates
  - Daily topic breakdown
  - Study tips

### ✓ Track Exams
- Exam calendar shows:
  - All uploaded subjects
  - Exam dates
  - Days remaining (auto-calculated)
  - Color-coded urgency levels
  - Both card and table views

---

## 📝 How to Use

### Step 1: Upload Syllabus
1. Go to http://127.0.0.1:5000
2. Fill the form:
   - **Student Name**: Your name
   - **Roll Number**: Your ID
   - **Subject Name**: Subject to study
   - **Exam Date**: When your exam is (YYYY-MM-DD format)
   - **Priority**: High/Medium/Low
3. **Upload PDF**: Click browse and select syllabus
4. Click **"Generate AI Study Plan"**

### Step 2: View Generated Plan
You'll see a beautiful dashboard with:
- 📊 Summary stats (chapters, topics, days left)
- 📖 Syllabus breakdown
- 📅 Weekly study schedule
- 💡 Study tips

### Step 3: Track Exams
- Click **"View Calendar"** to see all your exams
- Dates are auto-calculated showing days remaining
- Color coding: 🔴 Urgent | 🟡 Soon | 🟢 Normal

### Step 4: Add More Subjects
- Click **"Add Another Subject"** on dashboard
- OR visit home page
- Repeat upload process

---

## 🧪 Test Routes

### Home Page
```
http://127.0.0.1:5000/
```
Upload form for PDF syllabus

### Exam Calendar
```
http://127.0.0.1:5000/calendar
```
View all upcoming exams with dates

### Test Plan (Sample)
```
http://127.0.0.1:5000/test-plan
```
View a sample study plan without uploading PDF

---

## 🐛 Troubleshooting

### Error: "Address already in use"
Port 5000 is taken by another app
```bash
# Kill the process or use different port
# Or: Restart PowerShell
```

### Error: "ModuleNotFoundError"
Missing dependencies
```bash
pip install -r requirements.txt
```

### PDF not being parsed
Try one of these:
- ✅ Ensure PDF is text-based (not scanned image)
- ✅ Check if PDF has clear chapter headings
- ✅ Use online OCR tool to convert scanned PDF first

### Database error on startup
Already fixed! If you see it:
```bash
# Delete database and restart
Remove-Item -Path "instance\database.db" -Force
python app.py
```

---

## 📊 Features

| Feature | Status |
|---------|--------|
| PDF Upload | ✅ Working |
| PDF Parsing | ✅ Improved |
| Study Plan Generation | ✅ Working |
| Automatic Scheduling | ✅ Works |
| Exam Calendar | ✅ Fixed |
| Days Remaining Calculation | ✅ Dynamic |
| Database | ✅ Fixed |
| No API Key Needed | ✅ Works Offline |
| Mobile Responsive | ✅ Yes |
| Error Handling | ✅ Graceful |

---

## 📁 Project Structure

```
AI-Study-Planner/
├── app.py                 # Main Flask app (UPDATED)
├── requirements.txt       # Dependencies (TESTED)
├── SETUP_GUIDE.md        # Detailed setup
├── FIXES_LOG.md          # What was fixed
├── instance/             # Database folder
│   └── database.db       # SQLite database (auto-created)
├── static/
│   └── style.css         # Styling (redesigned)
├── templates/
│   ├── index.html        # Upload form
│   ├── dashboard.html    # Study plan display
│   └── calendar.html     # Exam calendar (REDESIGNED)
└── uploads/              # Uploaded PDFs
```

---

## 🎯 Next Steps

1. **Start the app**: `python app.py`
2. **Visit homepage**: http://127.0.0.1:5000
3. **Upload a PDF**: Any text-based syllabus
4. **View the plan**: Beautiful dashboard
5. **Check calendar**: Track all exams

---

## 💡 Tips

- **Exam date matters**: Closer dates = more compressed schedule
- **PDF quality**: Text-based PDFs work best
- **Chapter headings**: Help with accurate parsing
- **Priority level**: Affects time allocation
- **Study plan**: Adjust to your pace

---

## 🆘 Need Help?

Check these files:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- [FIXES_LOG.md](FIXES_LOG.md) - What was fixed and how
- [app.py](app.py) - Check console for detailed error messages

---

**Ready to study smart! 📚✨**
