import torch
import mlflow
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTConfig
import torch
from typing import Any, Dict, List, Union

class CompletionOnlyDataCollator(DataCollatorForLanguageModeling):
    def __init__(self, response_template, tokenizer, mlm=False):
        super().__init__(tokenizer=tokenizer, mlm=mlm)
        self.response_template = response_template
        self.response_token_ids = self.tokenizer.encode(self.response_template, add_special_tokens=False)

    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        batch = super().torch_call(examples)
        input_ids = batch["input_ids"]
        labels = batch["labels"].clone()
        
        # Mask padding tokens in labels
        if self.tokenizer.pad_token_id is not None:
            labels[labels == self.tokenizer.pad_token_id] = -100

        for i in range(len(input_ids)):
            # Find the start of the response
            # We look for the sequence of response_token_ids
            response_start_idx = -1
            
            # Simple linear search for the sub-sequence
            len_template = len(self.response_token_ids)
            for j in range(len(input_ids[i]) - len_template + 1):
                if input_ids[i][j:j+len_template].tolist() == self.response_token_ids:
                    response_start_idx = j + len_template # Start of the actual response
                    break
            
            if response_start_idx != -1:
                # Mask everything before the response
                labels[i, :response_start_idx] = -100
            else:
                # If template not found, ignore the whole sample (or maybe just keep it? standard practice is ignore)
                # But to be safe and avoid learning garbage:
                labels[i, :] = -100
                
        batch["labels"] = labels
        return batch

def load_model_and_tokenizer(model_name, use_quantization=False):
    """
    Load model and tokenizer with appropriate configuration.
    MPS/CUDA detection included.
    """
    bnb_config = None
    if use_quantization:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

    # Determine device map
    device_map = "auto"
    
    # MPS workaround: sometimes "auto" is flaky on Mac, but usually fine.
    # We will trust "auto" for now as per transformers >= 4.35
    
    print(f"Loading model: {model_name} (Quantization: {use_quantization})")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map=device_map,
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.padding_side = 'right' # FunctionGemma specific
    
    # Ensure pad_token is set (Gemma uses eos as pad often, but let's check)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    return model, tokenizer

def get_lora_config(r=16, alpha=32, dropout=0.05):
    """
    Get LoRA configuration based on train_unsloth.py settings.
    Targets more modules for better performance.
    """
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ]
    )

def get_data_collator(tokenizer):
    """
    Get DataCollatorForCompletionOnlyLM to correctly mask user prompts.
    This prevents the model from learning to output padding or copying inputs.
    """
    response_template = "<start_of_turn>model\n"
    return CompletionOnlyDataCollator(
        response_template=response_template, 
        tokenizer=tokenizer,
        mlm=False
    )

def get_training_args(output_dir, epochs=3, batch_size=4, learning_rate=2e-4):
    """
    Get stable training arguments.
    Disables fp16 on MPS to prevent NaNs.
    Adds gradient clipping.
    """
    # Check device for bf16/fp16 support
    is_mps = torch.backends.mps.is_available()
    is_cuda = torch.cuda.is_available()
    
    # Use bf16 if available (Apple Silicon M1/M2/M3 supports it)
    # Otherwise fallback to fp32 (no fp16 on MPS due to instability)
    bf16 = False
    fp16 = False
    
    if is_mps or is_cuda:
        # Try to enable bf16
        try:
            # Simple check or just assume newer torch versions on Mac support it
            bf16 = True
        except:
            bf16 = False
            
    # Force fp16=False to avoid the NaN issue we saw earlier
    
    return SFTConfig(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4, # From train_unsloth.py
        learning_rate=learning_rate,
        logging_steps=10,
        save_strategy="steps",
        save_steps=10,
        eval_strategy="no", # We evaluate separately
        
        # Stability settings
        fp16=False,
        bf16=bf16, # Use BFloat16 if possible, else Float32
        max_grad_norm=0.3, # Gradient clipping
        
        report_to=["mlflow"],
        dataset_text_field="text",
        max_length=1024,
        packing=False, # Don't pack for now to keep collator simple
    )
