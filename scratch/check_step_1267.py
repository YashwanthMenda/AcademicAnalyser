import json

log_path = r"C:\Users\menda\.gemini\antigravity\brain\f6d68905-0182-44ae-8823-13625660e166\.system_generated\logs\transcript.jsonl"

content_1267 = ""

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step_index = data.get("step_index")
        if step_index == 1267:
            content_1267 = data.get("content", "")
            break

lines_1267 = {}
for l in content_1267.split('\n'):
    parts = l.split(': ', 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        lines_1267[int(parts[0].strip())] = parts[1]

print("Total lines in 1267:", len(lines_1267))
print("Min line:", min(lines_1267.keys()) if lines_1267 else None)
print("Max line:", max(lines_1267.keys()) if lines_1267 else None)
missing = [i for i in range(902, 1000) if i not in lines_1267]
print("Missing lines from 902 to 999:", missing)
missing_any = [i for i in range(53, 999) if i not in lines_1267]
print("Number of missing lines overall in 53..998:", len(missing_any))
