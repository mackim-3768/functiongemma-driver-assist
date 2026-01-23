import sys
import os
sys.path.append(os.getcwd())

print("Testing imports...")
try:
    from pipeline.utils.finetune_utils import (
        load_model_and_tokenizer,
        get_lora_config,
        get_data_collator,
        get_training_args
    )
    print("Imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

print("Testing DataCollator instantiation...")
try:
    from transformers import AutoTokenizer
    # Mock tokenizer
    class MockTokenizer:
        def __init__(self):
            self.pad_token = None
            self.eos_token = "</s>"
        def encode(self, text, add_special_tokens=False):
            return [1, 2, 3]
    
    tokenizer = MockTokenizer()
    collator = get_data_collator(tokenizer)
    print(f"Collator created: {type(collator)}")
except Exception as e:
    print(f"Collator creation failed: {e}")
    import traceback
    traceback.print_exc()
