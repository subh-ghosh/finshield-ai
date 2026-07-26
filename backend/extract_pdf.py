import sys
sys.stdout.reconfigure(encoding='utf-8')

from PyPDF2 import PdfReader

r = PdfReader(r'C:\Users\subar\OneDrive\Desktop\SG Hackathon\V2 VISION.pdf')
for i, page in enumerate(r.pages):
    print(f"=== PAGE {i+1} ===")
    print(page.extract_text())
    print()
