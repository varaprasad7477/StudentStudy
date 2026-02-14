# StudentStudy - AI-Powered Study Planner

An intelligent web application that generates personalized study schedules from university syllabus PDFs using Google Gemini AI.

## Features

✨ **AI-Generated Study Plans** - Upload your syllabus PDF and get an intelligent, customized study schedule
📚 **Chapter-by-Chapter Breakdown** - Organized by modules, topics, and learning outcomes
📅 **Smart Scheduling** - Allocates study time based on exam date and topic complexity
🎯 **Priority-Based Planning** - High, Medium, Low priority levels for different learning needs
📊 **Exam Calendar** - Track all your upcoming exams in one place
📱 **Responsive Design** - Works on desktop and mobile devices
🔐 **Free API** - Uses Google Gemini API (completely free, no quota limits)

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Google Generative AI (Gemini)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Processing**: PyPDF2

## Installation

### Prerequisites
- Python 3.8 or higher
- Git
- Google Gemini API Key (free from [AI Studio](https://aistudio.google.com/app/apikey))

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/varaprasad7477/StudentStudy.git
cd StudentStudy/AI-Study-Planner
```

2. **Create virtual environment** (optional but recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**
- Get your free Gemini API key from: https://aistudio.google.com/app/apikey
- Create `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## Usage

1. **Navigate to Home Page** - Fill in your student details
2. **Enter Subject Information** - Subject name and exam date
3. **Upload Syllabus PDF** - Upload your university syllabus
4. **Get AI Study Plan** - Receive a customized study schedule
5. **View Exam Calendar** - Track all your exams

## Project Structure

```
StudentStudy/
├── AI-Study-Planner/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Environment variables (API key)
│   ├── .gitignore            # Git ignore rules
│   ├── templates/             # HTML templates
│   │   ├── index.html         # Home page
│   │   ├── dashboard.html     # Study plan display
│   │   └── calendar.html      # Exam calendar
│   ├── static/                # Frontend assets
│   │   └── style.css          # Styling
│   ├── uploads/               # Uploaded PDF files
│   └── database.db            # SQLite database
```

## Database Models

### Subject
- `id`: Primary key
- `student_name`: Student's name
- `roll_number`: Student's roll number
- `subject_name`: Subject/course name
- `exam_date`: Exam date
- `priority`: Priority level (High/Medium/Low)
- `pdf_file`: Path to uploaded syllabus

### Progress
- `id`: Primary key
- `subject_id`: Foreign key to Subject
- `topic`: Topic name
- `completed`: Completion status (Boolean)

## API Integration

The application uses **Google Generative AI (Gemini 1.5 Pro)** which:
- ✅ Completely FREE
- ✅ No pricing/billing required
- ✅ Unlimited free tier (with fair usage)
- ✅ Fast response times
- ✅ Supports advanced features

## How It Works

1. **PDF Processing**: Extracts text from uploaded syllabus using PyPDF2
2. **AI Analysis**: Sends extracted content to Gemini API
3. **Smart Prompting**: Uses advanced prompts to extract module names, topics, and learning outcomes
4. **Schedule Generation**: Creates personalized study timeline based on exam date
5. **Display**: Renders formatted study plan on dashboard

## Features in Detail

### AI Study Plan Generation
- Extracts exact module/chapter names from syllabus
- Lists all topics under each module
- Assigns study time based on complexity
- Creates week-by-week study schedule
- Includes revision timeline
- Respects high/medium/low priority levels

### Exam Calendar
- Displays all uploaded subjects
- Shows exam dates
- Color-coded priority badges
- Quick subject overview

### Responsive Design
- Works on all devices
- Dark theme for comfortable studying
- Easy navigation
- Clean, professional interface

## Future Enhancements

- [ ] Support for multiple study plan formats
- [ ] Progress tracking with analytics
- [ ] Customizable study preferences
- [ ] Study reminders and notifications
- [ ] Export study plan to PDF/Excel
- [ ] Collaborative study groups
- [ ] Mobile app version

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on [GitHub Issues](https://github.com/varaprasad7477/StudentStudy/issues).

## Author

**Vara Prasad** - [GitHub Profile](https://github.com/varaprasad7477)

## Acknowledgments

- Google Gemini AI for powerful language model capabilities
- Flask for web framework
- PyPDF2 for PDF processing
- All students using StudentStudy to improve their studies

---

**Happy Studying! 📚✨**
