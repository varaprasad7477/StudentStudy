# 📚 AI Study Planner - Setup & Usage Guide

## 🎯 What's New

Your AI Study Planner has been completely upgraded with:

✅ **Smart PDF Reading** - Automatically detects chapters, sections, and topics from your syllabus PDF
✅ **Intelligent Study Plans** - Generates customized weekly/daily schedules based on exam date and priority
✅ **Beautiful Dashboard** - Clean, modern interface showing:
   - Syllabus structure with all chapters and topics
   - Weekly breakdown with time estimates
   - Study tips and revision strategies
✅ **No API Limits** - Works offline without rate limits
✅ **Proper Error Handling** - Clear messages if PDF can't be read

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "c:\Users\vara prasad\Desktop\Study-Planner\AI-Study-Planner"
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

You'll see:
```
 * Running on http://127.0.0.1:5000
```

Open this URL in your browser.

### 3. Upload Your Syllabus

1. Enter student name & roll number
2. Enter subject name
3. **Select exam date** (important for study plan timing!)
4. Choose priority (High/Medium/Low)
5. **Upload your syllabus PDF** (text-based, not scanned images)
6. Click "Generate AI Study Plan"

---

## 📊 What the Study Plan Includes

### Syllabus Structure
- All chapters/sections extracted from PDF
- Number of topics in each chapter
- Difficulty level (based on topic count)
- Complete topic list

### Weekly Schedule
- **Number of weeks calculated** based on days until exam
- **Chapters distributed** across available weeks
- **Time estimates** for each chapter (2-3 hours per day)
- **Daily topic breakdown** (how many topics per day)

### Final Revision Week
- Comprehensive revision activities
- Mock test recommendations
- Weak area focus strategies

### Study Tips
- Reading strategies
- Time management
- Practice methods
- Pre-exam preparation

---

## 📝 PDF Requirements

✅ **What Works:**
- Text-based PDFs (created from documents)
- PDFs with clear chapter/section headings
- PDFs with table of contents

❌ **What Doesn't Work:**
- Scanned images (PDFs from photographs)
- Black & white low-quality scans

**Tip:** If your PDF is a scan, use OCR tools like:
- Google Docs (upload PDF → convert)
- Adobe Acrobat's OCR feature
- Free online OCR tools

---

## 🎨 How It Works

### Step 1: PDF Parsing
The system reads your PDF and extracts:
- Chapter names (Chapter 1, Unit 2, Module 3, etc.)
- Topics under each chapter
- Content structure

### Step 2: Plan Generation
Based on:
- Number of chapters found
- Number of topics per chapter
- Exam date (calculates available days)
- Priority level

The system creates:
- Weekly breakdown
- Daily study recommendations (2-3 hours/day)
- Revision schedule
- Study tips

### Step 3: Display
Beautiful formatted plan showing everything needed to study effectively

---

## 🔧 Optional: Google Gemini API Integration

If you want AI-powered plan enhancement in future:

1. Get API key: https://aistudio.google.com/app/apikey
2. Create `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```
3. Uncomment in `app.py` when ready

Note: The current version works perfectly WITHOUT API key!

---

## 📱 Test Route

View a sample plan without uploading PDF:
```
http://127.0.0.1:5000/test-plan
```

---

## 🆘 Troubleshooting

### "Could not extract text from PDF"
→ Your PDF might be scanned. Try converting with OCR first

### "Could not detect syllabus structure"
→ PDF doesn't have clear chapter headings. Try adding them or reformat

### Plan shows generic topics
→ Check if PDF has chapter names like "Chapter 1", "Unit 2", etc.

### Studies plan seems short
→ Exam date is too close. System spread topics across available days

---

## 📚 Features

| Feature | Status |
|---------|--------|
| PDF Upload & Parsing | ✅ Working |
| Chapter Detection | ✅ Optimized |
| Study Schedule Generation | ✅ Improved |
| Weekly Plans | ✅ Dynamic |
| Study Tips | ✅ Included |
| Calendar View | ✅ Available |
| Database Storage | ✅ SQLite |
| Responsive Design | ✅ Mobile-friendly |

---

## 📂 Project Structure

```
AI-Study-Planner/
├── app.py                 # Main Flask app (improved)
├── requirements.txt       # Dependencies (updated)
├── .env.example          # Configuration template
├── instance/             # Database storage
├── static/
│   └── style.css        # Styling (redesigned)
├── templates/
│   ├── index.html       # Upload form
│   ├── dashboard.html   # Study plan display (new design)
│   └── calendar.html    # Calendar view
└── uploads/             # Uploaded PDFs
```

---

## 🎓 Best Practices

1. **Upload complete syllabus** - Include all chapters
2. **Use text-based PDFs** - Not scanned images
3. **Include clear headings** - Chapter names help detection
4. **Set realistic exam date** - Affects study plan timing
5. **Follow the weekly plan** - Adjust as needed for your pace

---

## ✨ What Changed

### Before ❌
- API rate limit errors (429)
- Generic templates
- No real PDF parsing
- Errors displayed to users
- No proper syllabus structure

### After ✅
- No API limitations
- Smart PDF parsing
- Proper chapter/topic extraction
- Clean error handling
- Beautiful structured plans
- Works offline
- Responsive design

---

## 📞 Support

If you encounter issues:
1. Check PDF is text-based (not scanned)
2. Ensure clear chapter headings in PDF
3. Verify exam date is set correctly
4. Check browser console for errors (F12)

---

**Happy Studying! 📖✨**
