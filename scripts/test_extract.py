from app import read_pdf, extract_chapters_and_topics
import os

UP_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
UP_DIR = os.path.abspath(UP_DIR)

if not os.path.exists(UP_DIR):
    print('uploads folder not found:', UP_DIR)
    raise SystemExit(1)

files = [f for f in os.listdir(UP_DIR) if f.lower().endswith('.pdf')][:8]
print('Found', len(files), 'pdf(s) in uploads (showing up to 8):')
for f in files:
    path = os.path.join(UP_DIR, f)
    print('\n---')
    print('FILE:', f)
    try:
        txt = read_pdf(path)
        ch = extract_chapters_and_topics(txt)
        print('Detected units/chapters:', len(ch))
        for i, c in enumerate(ch, 1):
            name = c.get('name')
            topics = c.get('topics', [])
            hours = c.get('hours')
            print(f"  {i}. {name[:100]}  | topics={len(topics)}  | hours={hours}")
    except Exception as e:
        print('Error processing file:', e)
