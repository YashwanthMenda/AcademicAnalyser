import json

log_path = r"C:\Users\menda\.gemini\antigravity\brain\f6d68905-0182-44ae-8823-13625660e166\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        if "def render_js_session_manager" in line:
            data = json.loads(line)
            step_index = data.get("step_index")
            # We want to look for a tool call to write_to_file or replace_file_content
            # where the script was modified.
            tool_calls = data.get("tool_calls", [])
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args", {})
                if name in ["write_to_file", "replace_file_content", "multi_replace_file_content"]:
                    # check if the replacement content contains the function
                    chunks = args.get("ReplacementChunks", [])
                    if isinstance(chunks, str):
                        try:
                            chunks = json.loads(chunks)
                        except:
                            continue
                    
                    if not isinstance(chunks, list):
                        chunks = [args] # treat single edit tool call args as a chunk if it has the keys
                    
                    for chunk in chunks:
                        target = chunk.get("TargetContent", "")
                        repl = chunk.get("ReplacementContent", "")
                        code = chunk.get("CodeContent", "")
                        for val in [target, repl, code]:
                            if val and "def render_js_session_manager" in val and "truncated" not in val:
                                print(f"=== STEP {step_index} ({name}) ===")
                                print(val)
                                print("="*40)
                                break
