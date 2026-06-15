import json

log_path = r"C:\Users\menda\.gemini\antigravity\brain\f6d68905-0182-44ae-8823-13625660e166\.system_generated\logs\transcript.jsonl"

found = []
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        if "def render_js_session_manager" in line:
            data = json.loads(line)
            step_index = data.get("step_index")
            step_type = data.get("type")
            # Check tool calls
            for tc in data.get("tool_calls", []):
                args = tc.get("args", {})
                for k, v in args.items():
                    if isinstance(v, str) and "def render_js_session_manager" in v:
                        found.append((step_index, f"tool_call arg {k}", v))
                    elif isinstance(v, list):
                        # check chunks
                        for item in v:
                            if isinstance(item, dict) and "def render_js_session_manager" in item.get("ReplacementContent", ""):
                                found.append((step_index, f"tool_call chunk ReplacementContent", item["ReplacementContent"]))
            # Check content
            content = data.get("content")
            if content and "def render_js_session_manager" in content:
                found.append((step_index, "content", content))

print(f"Found {len(found)} candidate blocks.")
for idx, (step, source, text) in enumerate(found):
    print(f"--- Option {idx}: Step {step} from {source} (Length: {len(text)}) ---")
    # print first 500 chars and last 500 chars
    print("START:")
    print(text[:500])
    print("...")
    print("END:")
    print(text[-500:])
    print("\n" + "="*80 + "\n")
