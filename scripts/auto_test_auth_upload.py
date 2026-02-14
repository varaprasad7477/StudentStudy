import requests
import os
import sys

BASE = 'http://127.0.0.1:5000'
USERNAME = 'testuser'
PASSWORD = 'Test1234!'

uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
if not os.path.exists(uploads_dir):
    print('uploads directory not found:', uploads_dir)
    sys.exit(1)

pdfs = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.pdf')]
if not pdfs:
    print('No PDFs found in uploads:', uploads_dir)
    sys.exit(1)

pdf_path = os.path.join(uploads_dir, pdfs[0])
print('Using PDF:', pdfs[0])

s = requests.Session()
# Login
login_resp = s.post(f'{BASE}/login', data={'username': USERNAME, 'password': PASSWORD})
print('Login status code:', login_resp.status_code)

# Confirm dashboard access
dash = s.get(f'{BASE}/dashboard')
print('Dashboard GET status:', dash.status_code)
if 'Please log in' in dash.text or dash.status_code != 200:
    print('Login may have failed; dashboard response length:', len(dash.text))

# Prepare upload
data = {
    'student_name': 'Auto Tester',
    'roll_number': '000',
    'subject_name': 'Auto Subject',
    'exam_date': '2026-03-15',
    'priority': 'Medium'
}
files = {
    'pdf_file': (os.path.basename(pdf_path), open(pdf_path, 'rb'), 'application/pdf')
}
print('Uploading PDF...')
up = s.post(f'{BASE}/upload', data=data, files=files)
print('Upload status:', up.status_code)
print('Upload response length:', len(up.text))

# Save returned HTML to file for inspection
out_file = os.path.join(os.path.dirname(__file__), 'upload_result.html')
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(up.text)
print('Saved upload result to', out_file)
