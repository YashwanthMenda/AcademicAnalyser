import json

log_path = r"C:\Users\menda\.gemini\antigravity\brain\f6d68905-0182-44ae-8823-13625660e166\.system_generated\logs\transcript.jsonl"

content_1267 = ""
content_1221 = ""

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step_index = data.get("step_index")
        if step_index == 1267:
            content_1267 = data.get("content", "")
        elif step_index == 1221:
            content_1221 = data.get("content", "")

# Parse line number mapping
lines_1267 = {}
for l in content_1267.split('\n'):
    parts = l.split(': ', 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        lines_1267[int(parts[0].strip())] = parts[1]

lines_1221 = {}
for l in content_1221.split('\n'):
    parts = l.split(': ', 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        lines_1221[int(parts[0].strip())] = parts[1]

# Stitch lines from 902 to 1060
stitched = []
for i in range(902, 1061):
    if i in lines_1267:
        stitched.append(lines_1267[i])
    elif i in lines_1221:
        stitched.append(lines_1221[i])
    else:
        stitched.append(f"# MISSING LINE {i}\n")

with open('scratch/reconstructed_manager.py', 'w', encoding='utf-8') as out:
    out.writelines(stitched)

print("Reconstruction complete!")
