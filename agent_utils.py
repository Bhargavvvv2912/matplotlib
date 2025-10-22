# agent_utils.py

import subprocess
import re
import sys
from pathlib import Path

def start_group(title):
    print(f"\n::group::{title}")

def end_group():
    print("::endgroup::")

def run_command(command, cwd=None):
    # Added more verbose logging to help with debugging
    display_command = ' '.join(command)
    print(f"--> Running command: '{display_command}' in CWD: '{cwd or '.'}'")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    return result.stdout, result.stderr, result.returncode

def parse_pytest_summary(full_output):
    """
    A helper function to parse the rich summary line from a pytest run.
    """
    summary = {
        "passed": "N/A", "failed": "0", "errors": "0",
        "skipped": "N/A", "xfailed": "N/A", "xpassed": "N/A"
    }
    
    # Find the main summary line (it's the last line with '=' signs)
    summary_line = ""
    for line in reversed(full_output.splitlines()):
        if "=" in line and ("passed" in line or "failed" in line or "skipped" in line):
            summary_line = line
            break
            
    if not summary_line:
        return summary # Return defaults if no summary found

    # Use findall to get all number/word pairs
    matches = re.findall(r"(\d+)\s+(passed|failed|skipped|xfailed|xpassed|errors)", summary_line)
    for count, status in matches:
        if status in summary:
            summary[status] = count
            
    return summary


def _run_smoke_test(python_executable, config):
    print("\n--- Running Smoke Test ---")
    
    # This logic assumes the smoke test script is in the root of your experiment repo
    smoke_script_path = str(Path("validation_smoke.py").resolve())
    smoke_test_command = [python_executable, smoke_script_path]
    
    # The command needs to run from the root of the cloned repo (e.g., 'matplotlib')
    project_dir_name = config["VALIDATION_CONFIG"]["target"]
    
    stdout, stderr, returncode = run_command(smoke_test_command, cwd=project_dir_name)

    if returncode != 0:
        print(f"CRITICAL VALIDATION FAILURE: Smoke test failed.", file=sys.stderr)
        if stderr: print(f"SMOKE TEST STDERR:\n{stderr}")
        
        # --- THIS IS THE FIX ---
        # It now correctly returns all three values: (False, reason, output)
        return False, f"Smoke test failed with exit code {returncode}", stdout + stderr
    
    print("Smoke test PASSED.")
    return True, "Smoke test passed.", stdout + stderr

def _run_pytest_suite(python_executable, config):
    print("\n--- Running Full Pytest Suite ---")
    validation_target = config["VALIDATION_CONFIG"]["target"]
    
    command = [python_executable, "-m", "pytest", validation_target]
    stdout, stderr, returncode = run_command(command)
    full_output = stdout + stderr
    # Placeholder for the parsing logic (it's identical to the last answer)
    if returncode > 1: return False, "Critical pytest error", full_output
    summary = parse_pytest_summary(full_output)
    total_failures = int(summary["failed"]) + int(summary["errors"])
    threshold = config.get("ACCEPTABLE_FAILURE_THRESHOLD", 0)
    if total_failures > threshold:
        return False, f"{total_failures} failures exceeded threshold", full_output
    
    metrics = f"Tests Passed: {summary['passed']}" # Simplified for brevity
    return True, metrics, full_output


def validate_changes(python_executable, config, group_title="Running Validation"):
    """
    A general-purpose, config-driven validation dispatcher.
    """
    start_group(group_title)
    
    validation_type = config.get("VALIDATION_CONFIG", {}).get("type", "pytest")
    success = False
    reason = "No validation configured."
    full_output = ""

    if validation_type == "pytest":
        success, reason, full_output = _run_pytest_suite(python_executable, config)
    
    elif validation_type == "script":
        # Note: we are merging the smoke test logic into "script" for simplicity.
        success, reason, full_output = _run_smoke_test(python_executable, config)

    elif validation_type == "pytest_with_smoke_test":
        smoke_success, smoke_reason, smoke_output = _run_smoke_test(python_executable, config)
        if not smoke_success:
            end_group()
            return False, smoke_reason, smoke_output
        
        # If smoke test passes, run the full suite
        success, reason, full_output = _run_pytest_suite(python_executable, config)

    else:
        print(f"WARNING: Unknown validation type '{validation_type}'. Assuming success.", file=sys.stderr)
        success = True # Default to success if no valid config is found
        
    end_group()
    return success, reason, full_output