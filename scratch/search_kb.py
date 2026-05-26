import re
import sys

# Reconfigure stdout to utf-8 to avoid encoding issues on Windows console
sys.stdout.reconfigure(encoding='utf-8')

kb_path = r"c:\Users\xiong\AIcode\AIbook1\knowledge_base\hot_books_kb.md"
with open(kb_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find occurrences of words like 综艺, 节目, 直播, 娃综
keywords = ["综艺", "节目", "直播", "真人秀"]
matches = []

lines = content.split('\n')
for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            # Get a context of 5 lines before and after
            start = max(0, i - 3)
            end = min(len(lines), i + 4)
            context = "\n".join(f"{idx+1}: {lines[idx]}" for idx in range(start, end))
            matches.append((kw, i+1, context))
            break

print(f"Total matches: {len(matches)}")
for kw, line_num, ctx in matches[:15]:
    print(f"\n--- Keyword: '{kw}' at line {line_num} ---")
    print(ctx)
