import json

log_path = r"C:\Users\xiong\.gemini\antigravity\brain\5cbfddf1-dbd1-4733-b3a2-d6d825c8fd96\.system_generated\logs\transcript.jsonl"
out_path = r"c:\Users\xiong\AIcode\AIbook1\scratch\transcript_decoded.txt"

with open(log_path, 'r', encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as out:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            out.write(f"Step {data.get('step_index')}:\n")
            out.write(data.get('content') + "\n")
            out.write("-" * 40 + "\n")
print("Done writing transcript decoded file.")
