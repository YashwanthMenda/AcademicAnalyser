import os

search_terms = ["Extracting text", "No text found with pdfplumber", "Trying alternative method"]
search_dir = "."

for root, dirs, files in os.walk(search_dir):
    if "venv" in root or ".git" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith(".py") or file.endswith(".txt") or file.endswith(".md"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        for term in search_terms:
                            if term.lower() in line.lower():
                                print(f"{path}:{line_num}: {line.strip()}")
            except Exception:
                pass
