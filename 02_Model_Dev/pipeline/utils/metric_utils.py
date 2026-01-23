import json
import logging

logger = logging.getLogger(__name__)

class ToolCallMatchMetric:
    @staticmethod
    def match(predicted_text: str, expected_tool_calls: list):
        """
        Matches predicted text (JSON string) against expected tool calls.
        Returns: (is_match: bool, reason: str, parsed_prediction: list|None)
        """
        try:
            # Attempt to parse JSON
            # Sometimes the model might output extra whitespace or newlines
            cleaned_text = predicted_text.strip()
            
            # If empty, it's not a match unless expected is empty (but typically expected is not empty in this dataset)
            if not cleaned_text:
                return False, "empty_output", None
                
            try:
                pred_obj = json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in cleaned_text:
                    try:
                        extracted = cleaned_text.split("```json")[1].split("```")[0].strip()
                        pred_obj = json.loads(extracted)
                    except:
                        return False, "json_parse_error", None
                else:
                    return False, "json_parse_error", None
            
            if not isinstance(pred_obj, list):
                return False, "not_a_list", pred_obj
                
            # Compare length
            if len(pred_obj) != len(expected_tool_calls):
                return False, f"count_mismatch_expected_{len(expected_tool_calls)}_got_{len(pred_obj)}", pred_obj
                
            # Compare each tool call (order matters? usually yes for sequential actions, but let's assume strict equality for now)
            # The previous results suggested strict matching.
            for i, (pred, exp) in enumerate(zip(pred_obj, expected_tool_calls)):
                if not isinstance(pred, dict):
                    return False, f"item_{i}_not_dict", pred_obj
                
                # Check name
                if pred.get("name") != exp.get("name"):
                    return False, f"item_{i}_name_mismatch", pred_obj
                    
                # Check arguments
                pred_args = pred.get("arguments", {})
                exp_args = exp.get("arguments", {})
                
                if pred_args != exp_args:
                    return False, f"item_{i}_args_mismatch", pred_obj
                    
            return True, "match", pred_obj
            
        except Exception as e:
            logger.error(f"Error in ToolCallMatchMetric: {e}")
            return False, f"exception_{str(e)}", None
