# dependency_agent.py

import os
import sys
import google.generativeai as genai
from agent_logic import DependencyAgent

AGENT_CONFIG = {
    "REQUIREMENTS_FILE": "generated-requirements.txt",
    "PRIMARY_REQUIREMENTS_FILE": "primary_requirements.txt", # We'll use an empty one
    "METRICS_OUTPUT_FILE": "metrics_output.txt",
    "MAX_LLM_BACKTRACK_ATTEMPTS": 3,
    "MAX_RUN_PASSES": 5, 
    "ACCEPTABLE_FAILURE_THRESHOLD": 5,
    "VALIDATION_CONFIG": {
        "type": "pytest_with_smoke_test",
        "target": "matplotlib",
        "smoke_test_script": "validation_smoke.py"
    }
}

# The rest of this file is IDENTICAL to your requests experiment version
if __name__ == "__main__":
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        sys.exit("Error: GEMINI_API_KEY environment variable not set.")
    
    genai.configure(api_key=GEMINI_API_KEY)
    llm_client = genai.GenerativeModel('gemini-1.5-flash-latest')

    agent = DependencyAgent(config=AGENT_CONFIG, llm_client=llm_client)
    agent.run()