import sys
import os

print(f"Python executable: {sys.executable}")
print(f"sys.path: {sys.path}")

try:
    import chatbot_tester
    print(f"chatbot_tester version: {chatbot_tester.__version__}")
    print(f"chatbot_tester file: {chatbot_tester.__file__}")
    
    from chatbot_tester.evaluator.metrics.tool_call import ToolCallMatchMetric
    print("Successfully imported ToolCallMatchMetric")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
