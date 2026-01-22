import json
import os
import argparse
import re

def parse_function_gemma_text(text):
    """
    Function Gemma 포맷(<start_of_turn>...)에서 User Prompt와 Model Action을 분리합니다.
    """
    # 1. User Prompt 추출 (user 태그 다음부터 ~ model 태그 앞까지)
    # 보통 Function Gemma 프롬프트에는 System Prompt와 Context가 포함되어 있으므로 통째로 Input으로 씁니다.
    pattern = r"<start_of_turn>user\n(.*?)\n<start_of_turn>model"
    match = re.search(pattern, text, re.DOTALL)
    
    if not match:
        return None, None
        
    user_input = match.group(1).strip()
    
    # 2. Model Action 추출 (model 태그 다음부터 ~ end_of_turn 까지)
    action_pattern = r"<start_of_turn>model\n(.*?)(?:<end_of_turn>|$)"
    action_match = re.search(action_pattern, text, re.DOTALL)
    
    if not action_match:
        return user_input, []
        
    action_json_str = action_match.group(1).strip()
    try:
        expected_actions = json.loads(action_json_str)
    except:
        expected_actions = action_json_str # JSON 파싱 실패 시 원문 유지
        
    return user_input, expected_actions

def convert_dataset(input_path, output_path):
    print(f"Converting {input_path} -> {output_path} ...")
    
    converted_count = 0
    with open(input_path, 'r') as fin, open(output_path, 'w') as fout:
        for idx, line in enumerate(fin):
            try:
                data = json.loads(line)
                full_text = data.get("text", "")
                
                user_input, expected = parse_function_gemma_text(full_text)
                
                if user_input:
                    # Canonical Format (Chatbot Tester)
                    sample = {
                        "id": f"seed_{idx:05d}",
                        "messages": [
                            {"role": "user", "content": user_input}
                        ],
                        "expected": expected,
                        "tags": ["from_seed"],
                        "metadata": {"source": "seed_dataset"}
                    }
                    fout.write(json.dumps(sample) + "\n")
                    converted_count += 1
            except Exception as e:
                print(f"Skipping line {idx}: {e}")
                
    print(f"✅ Success! Converted {converted_count} samples.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to existing finetune.jsonl")
    parser.add_argument("output", help="Path to save canonical.jsonl")
    args = parser.parse_args()
    
    convert_dataset(args.input, args.output)