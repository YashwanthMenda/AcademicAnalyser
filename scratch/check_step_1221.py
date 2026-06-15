import json

log_path = r"C:\Users\menda\.gemini\antigravity\brain\f6d68905-0182-44ae-8823-13625660e166\.system_generated\logs\transcript.jsonl"

content_1221 = ""

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step_index = data.get("step_index")
        if step_index == 1221:
            content_1221 = data.get("content", "")
            break

lines_1221 = {}
for l in content_1221.split('\n'):
    parts = l.split(': ', 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        lines_1221[int(parts[0].strip())] = parts[1]

print("Total lines in 1221:", len(lines_1221))
print("Min line:", min(lines_1221.keys()) if lines_1221 else None)
print("Max line:", max(lines_1221.keys()) if lines_1221 else None)
missing = [i for i in range(885, 1075) if i not in lines_1221]
print("Missing lines from 885 to 1074:", missing)
