import json
import random

def evaluate_samples():
    filename = 'driver_assist_finetune.jsonl'
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        print(f"Total lines: {total_lines}")
        
        if total_lines == 0:
            print("File is empty.")
            return

        # Select 20 random indices
        indices = random.sample(range(total_lines), min(20, total_lines))
        
        print(f"Selected {len(indices)} samples for evaluation:\n")
        
        for i, idx in enumerate(indices):
            line = lines[idx]
            try:
                data = json.loads(line)
                text = data.get('text', '')
                
                print(f"--- Sample {i+1} (Line {idx+1}) ---")
                # We can print the raw text, or parse it to be nicer. 
                # The user asked to check for "strange content like ...", so printing raw text part might be safer to spot artifacts,
                # but formatted is easier to read logic. Let's print the relevant parts extracted from the prompt text.
                
                # Simple extraction for readability
                start_context = text.find("Input context is structured sensor state")
                end_context = text.find("User prompt:")
                context_str = text[start_context:end_context].strip()
                
                start_prompt = text.find("User prompt:")
                end_prompt = text.find("Return ONLY a JSON array")
                prompt_str = text[start_prompt:end_prompt].strip()
                
                start_model = text.find("<start_of_turn>model")
                model_str = text[start_model:].strip()
                
                print(f"[Context Parsing]\n{context_str[:200]} ... (truncated context for brevity if long)\n") 
                # Actually, let's print the parsed JSON context to check values
                # Re-extract JSON from text
                import re
                context_match = re.search(r'Input context is structured sensor state \(do not invent fields\):\n(\{.*?\})\n\nUser prompt:', text, re.DOTALL)
                if context_match:
                    context_json = json.loads(context_match.group(1))
                    print(f"[Input Context]: {json.dumps(context_json, indent=2)}")
                else:
                    print("[Input Context]: Could not extract JSON")

                prompt_match = re.search(r'User prompt:\n(.*?)\n\nReturn ONLY', text, re.DOTALL)
                if prompt_match:
                     print(f"[User Prompt]: {prompt_match.group(1)}")
                else:
                     print(f"[User Prompt]: Not found")

                model_match = re.search(r'<start_of_turn>model\n(\[.*?\])<end_of_turn>', text, re.DOTALL)
                if model_match:
                    model_json = json.loads(model_match.group(1))
                    print(f"[Model Action]: {json.dumps(model_json, indent=2)}")
                else:
                    print(f"[Model Action]: Could not extract JSON. Raw: {model_str}")
                
                print("\n")
                
            except json.JSONDecodeError:
                print(f"--- Sample {i+1} (Line {idx+1}) ---")
                print("FAILED TO PARSE JSON LINE")
                print(line[:200])
                print("\n")

    except FileNotFoundError:
        print(f"File {filename} not found.")

if __name__ == "__main__":
    evaluate_samples()
