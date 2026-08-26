"""Execute agentic_workflow.py and recreate both Phase 2 output files.

Usage:
    python run_agentic_workflow.py

Produces:
    agentic_workflow_terminal_output.txt  - the full captured terminal output
    agentic-workflow-output.txt           - only the final synthesized project plan
"""

import os
import subprocess
import sys

WORKFLOW_SCRIPT = "agentic_workflow.py"
TERMINAL_OUTPUT_FILE = "agentic_workflow_terminal_output.txt"
FINAL_OUTPUT_FILE = "agentic-workflow-output.txt"
FINAL_MARKER = "Final output of the workflow"


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    result = subprocess.run(
        [sys.executable, WORKFLOW_SCRIPT],
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    terminal_output = result.stdout
    if result.stderr:
        terminal_output += "\n[stderr]\n" + result.stderr

    # Echo to the console so the run is visible live.
    print(terminal_output)

    # Save the complete terminal output.
    terminal_path = os.path.join(script_dir, TERMINAL_OUTPUT_FILE)
    with open(terminal_path, "w", encoding="utf-8") as f:
        f.write(terminal_output.rstrip() + "\n")

    # Extract the synthesized final plan (everything from the final marker onward).
    marker_index = terminal_output.rfind(FINAL_MARKER)
    if marker_index == -1:
        print(
            f"\nWarning: '{FINAL_MARKER}' not found in output; "
            f"{FINAL_OUTPUT_FILE} was not written."
        )
        return result.returncode

    final_section = terminal_output[marker_index:].strip()
    header, _, body = final_section.partition("\n")
    final_output = f"{header.strip()}\n\n{body.strip()}\n"

    final_path = os.path.join(script_dir, FINAL_OUTPUT_FILE)
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_output)

    print(f"\nWrote {TERMINAL_OUTPUT_FILE} and {FINAL_OUTPUT_FILE}.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
