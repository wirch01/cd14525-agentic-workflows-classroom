"""Run all Phase 1 agent test scripts and print each agent's output,
labeled with the command line used to execute it.

Usage:
    python run_all_agents.py
"""

import subprocess
import sys
import os

# The agent test scripts to execute, in a sensible order.
AGENT_SCRIPTS = [
    "direct_prompt_agent.py",
    "augmented_prompt_agent.py",
    "knowledge_augmented_prompt_agent.py",
    "rag_knowledge_prompt_agent.py",
    "evaluation_agent.py",
    "routing_agent.py",
    "action_planning_agent.py",
]


def run_agent(script_name):
    """Execute a single agent script and return the command and captured output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    command = [sys.executable, script_name]

    result = subprocess.run(
        command,
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # Build a readable command-line string.
    command_line = f"python {script_name}"

    output = result.stdout
    if result.stderr:
        output += "\n[stderr]\n" + result.stderr

    return command_line, output.strip()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "agents_execution_output.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for script in AGENT_SCRIPTS:
            command_line, output = run_agent(script)
            block = (
                "=" * 70 + "\n"
                f"Command: {command_line}\n"
                + "=" * 70 + "\n"
                + (output if output else "(no output)") + "\n\n"
            )
            f.write(block)
            print(block, end="")

    print(f"\nOutput written to {output_path}")


if __name__ == "__main__":
    main()
