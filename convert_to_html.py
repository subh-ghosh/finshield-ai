import re
import base64
import json
import urllib.request
import markdown

with open('Submission_Documentation.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Find all mermaid blocks
pattern = r'```mermaid\n(.*?)\n```'
matches = re.finditer(pattern, md_content, re.DOTALL)

for i, match in enumerate(matches):
    mermaid_code = match.group(1)
    
    # Base64 encode for mermaid.ink
    state = {
        "code": mermaid_code,
        "mermaid": {"theme": "default"}
    }
    encoded_string = base64.urlsafe_b64encode(json.dumps(state).encode('utf-8')).decode('utf-8')
    url = f"https://mermaid.ink/img/{encoded_string}"
    
    # Replace the block with an HTML image tag pointing to the rendered image
    md_content = md_content.replace(match.group(0), f'![Diagram {i}]({url})')

# Convert to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Add some basic CSS for a professional look
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>FinShield AI - Technical Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
        }}
        h1, h2, h3 {{
            color: #111;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow: auto;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

with open('Submission_Final.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Created Submission_Final.html")
