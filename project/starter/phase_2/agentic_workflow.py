# agentic_workflow.py

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module
from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import io
import logging
import os
import sys
import time

from dotenv import load_dotenv

# Force UTF-8 output. When stdout/stderr are redirected on Windows (e.g.
# `python agentic_workflow.py > output.txt`), Python defaults to the legacy
# 'charmap' codec, which cannot encode characters such as the check mark emoji
# printed by the evaluation agents and crashes the evaluation loop.
for _stream in (sys.stdout, sys.stderr):
    if isinstance(_stream, io.TextIOWrapper):
        _stream.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agentic_workflow")

# TODO: 2 - Load the OpenAI key into a variable called openai_api_key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Add it to your environment or a local .env file."
    )

# Steering flag for the final synthesis step (default: False).
# When True, a final synthesis step merges all validated outputs into one
# consistent project plan (final_project_plan); when False, the workflow ends
# with the last completed step as output. Toggle it here or via the
# SYNTHESIS_STEP_NEEDED environment variable ("true"/"false") to compare the
# workflow output with and without synthesis.
synthesis_step_needed = os.getenv("SYNTHESIS_STEP_NEEDED", "true").strip().lower() in (
    "1", "true", "yes",
)

# load the product spec
# TODO: 3 - Load the product spec document Product-Spec-Email-Router.txt into a variable called product_spec
product_spec_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "Product-Spec-Email-Router.txt"
)
try:
    with open(product_spec_path, "r", encoding="utf-8") as spec_file:
        product_spec = spec_file.read()
except OSError as error:
    raise FileNotFoundError(
        f"Could not read the product spec file at {product_spec_path}: {error}"
    ) from error

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components. \n"
    "Creating a development plan always consists of exactly these three "
    "high-level workflow steps, in this order:\n"
    "1. Product Manager: identify the user personas and define the user stories "
    "for the product based on the product spec.\n"
    "2. Program Manager: group the user stories into product features.\n"
    "3. Development Engineer: define the engineering tasks required to "
    "implement the user stories.\n"
    "Return only these workflow steps as short instructions to be executed by "
    "other agents, keeping the responsible role name at the start of each step. "
    "Never write the actual user stories, features, or tasks yourself, and "
    "never return more than these three steps."
)
# TODO: 4 - Instantiate an action_planning_agent using the 'knowledge_action_planning'
action_planning_agent = ActionPlanningAgent(
    openai_api_key=openai_api_key,
    knowledge=knowledge_action_planning,
)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = (
    "You are a Product Manager. You are solely responsible for defining user "
    "stories for a product. You identify the different user personas and, for "
    "each persona, write user stories that capture the action they want to take "
    "and the value they expect. You do NOT group user stories into features "
    "(that is the Program Manager's responsibility) and you do NOT define "
    "engineering or development tasks (that is the Development Engineer's "
    "responsibility)."
)
knowledge_product_manager = (
    "A user story is a single sentence that combines a persona, an action, and a "
    "desired outcome, and always starts with: As a "
    "The exact structure is: 'As a [type of user], I want [an action or feature] "
    "so that [benefit/value].' "
    "Write several user stories for the product spec below, where the personas "
    "are the different users of the product. "
    "Do not group stories into features and do not define development tasks. "
    # TODO: 5 - Complete this knowledge string by appending the product_spec loaded in TODO 3
    "\n\nProduct Spec:\n" + product_spec
)
# TODO: 6 - Instantiate a product_manager_knowledge_agent using 'persona_product_manager' and the completed 'knowledge_product_manager'
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    knowledge=knowledge_product_manager,
)

# Product Manager - Evaluation Agent
# TODO: 7 - Define the persona and evaluation criteria for a Product Manager evaluation agent and instantiate it as product_manager_evaluation_agent. This agent will evaluate the product_manager_knowledge_agent.
# The evaluation_criteria should specify the expected structure for user stories (e.g., "As a [type of user], I want [an action or feature] so that [benefit/value].").
# persona_product_manager_eval = (
#     "You are an evaluation agent that checks whether the Product Manager's "
#     "answers are valid user stories. You only judge user-story quality and "
#     "structure; you do not evaluate features or development tasks."
# )
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_product_manager = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=evaluation_criteria_product_manager,
    worker_agent=product_manager_knowledge_agent,
    max_interactions=10,
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = (
    "You are a Program Manager. You are solely responsible for defining product "
    "features. A feature is a cohesive group of related user stories. You take "
    "existing user stories and organize the similar ones into named feature "
    "groups. You do NOT write user stories (that is the Product Manager's "
    "responsibility) and you do NOT define engineering or development tasks "
    "(that is the Development Engineer's responsibility)."
)
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into "
    "cohesive groups. Each feature has a name, a description of what it does and "
    "its purpose, its key functionality, and the user benefit it delivers. "
    "Features describe grouped capabilities, not individual user stories and not "
    "engineering implementation tasks. "
    "Group the user stories provided in the prompt's shared workflow context; "
    "every single user story from that context must be assigned to at least one "
    "feature, and each feature must map to a capability described in the product "
    "spec below. List the user stories each feature groups. "
    "\n\nProduct Spec:\n" + product_spec
)
# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager,
)

# Program Manager - Evaluation Agent
# persona_program_manager_eval = (
#     "You are an evaluation agent that checks whether the Program Manager's "
#     "answers are valid product features. You only judge feature quality and "
#     "structure; you do not evaluate user stories or development tasks."
# )
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

# TODO: 8 - Instantiate a program_manager_evaluation_agent using 'persona_program_manager_eval' and the evaluation criteria below.
#                      "The answer should be product features that follow the following structure: " \
#                      "Feature Name: A clear, concise title that identifies the capability\n" \
#                      "Description: A brief explanation of what the feature does and its purpose\n" \
#                      "Key Functionality: The specific capabilities or actions the feature provides\n" \
#                      "User Benefit: How this feature creates value for the user"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user\n"
    "Coverage: every user story from the shared workflow context must be grouped "
    "into at least one feature, and every feature must correspond to a "
    "capability described in the product spec."
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=evaluation_criteria_program_manager,
    worker_agent=program_manager_knowledge_agent,
    max_interactions=10,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = (
    "You are a Development Engineer. You are solely responsible for defining the "
    "technical development tasks required to implement user stories. You describe "
    "the concrete engineering work needed to build the product. You do NOT write "
    "user stories (that is the Product Manager's responsibility) and you do NOT "
    "group user stories into features (that is the Program Manager's "
    "responsibility)."
)
knowledge_dev_engineer = (
    "Development tasks are defined by identifying the concrete engineering work "
    "needed to implement each user story. Each task describes what needs to be "
    "built, including the technical work required, acceptance criteria, an effort "
    "estimate, and dependencies. Tasks are implementation-level work items, not "
    "user stories and not feature groupings. "
    "Define tasks for the user stories provided in the prompt's shared workflow "
    "context, referencing those stories. Work through the stories one by one: "
    "every user story and every feature in that context must receive at least "
    "one task, and no story or feature may be left without tasks. Each task must "
    "implement a capability described in the product spec below. "
    "\n\nProduct Spec:\n" + product_spec
)
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer,
)

# Development Engineer - Evaluation Agent
# persona_dev_engineer_eval = (
#     "You are an evaluation agent that checks whether the Development Engineer's "
#     "answers are valid development tasks. You only judge development-task quality "
#     "and structure; you do not evaluate user stories or features."
# )
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."

# TODO: 9 - Instantiate a development_engineer_evaluation_agent using 'persona_dev_engineer_eval' and the evaluation criteria below.
#                      "The answer should be tasks following this exact structure: " \
#                      "Task ID: A unique identifier for tracking purposes\n" \
#                      "Task Title: Brief description of the specific development work\n" \
#                      "Related User Story: Reference to the parent user story\n" \
#                      "Description: Detailed explanation of the technical work required\n" \
#                      "Acceptance Criteria: Specific requirements that must be met for completion\n" \
#                      "Estimated Effort: Time or complexity estimation\n" \
#                      "Dependencies: Any tasks that must be completed first"
# For the 'agent_to_evaluate' parameter, refer to the provided solution code's pattern.
evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first\n"
    "Coverage: every user story and every feature from the shared workflow "
    "context must be referenced by at least one task, and every task must "
    "implement a capability described in the product spec. Tasks that all "
    "reference the same single user story do not meet the criteria."
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev_engineer,
    worker_agent=development_engineer_knowledge_agent,
    max_interactions=10,
)

# Project Plan Synthesis - Knowledge Augmented Prompt Agent
# Runs as a fixed final step (not routed by embedding similarity) and merges all
# validated outputs from the shared workflow state into one coherent project plan.
persona_synthesis = (
    "You are a Project Plan Synthesizer. You are solely responsible for merging "
    "already validated user stories, product features, and engineering tasks into "
    "one coherent, internally consistent and complete project plan document. You "
    "consolidate, deduplicate, and cross-reference the material you are given. "
    "You do NOT invent new user stories or features, and you only add an "
    "engineering task when a user story or feature would otherwise have none, "
    "deriving it from the product spec."
)
knowledge_synthesis = (
    "A complete project plan document for a product contains three consistent, "
    "cross-referenced sections:\n"
    "1. User Stories: numbered stories (US-1, US-2, ...) in the form 'As a [type "
    "of user], I want [an action or feature] so that [benefit/value].'\n"
    "2. Product Features: every feature is written as plain labelled lines, each "
    "line starting with the exact label followed by a colon, in this order:\n"
    "Feature Name: <a clear, concise title that identifies the capability>\n"
    "Description: <a brief explanation of what the feature does and its purpose>\n"
    "Key Functionality: <the specific capabilities or actions the feature provides>\n"
    "User Benefit: <how this feature creates value for the user>\n"
    "Related User Stories: <the story IDs from section 1 that the feature groups>\n"
    "3. Engineering Tasks: every task is written as plain labelled lines, each "
    "line starting with the exact label followed by a colon, in this order: "
    "Task ID, Task Title, Related User Story (a real story ID from section 1), "
    "Description, Acceptance Criteria, Estimated Effort, Dependencies.\n"
    "Never replace a label with a bold or numbered heading and never omit a "
    "label: the literal label text and its colon must always be present, for "
    "example 'Feature Name: Automated Response' and 'Task ID: DEV-001'.\n"
    "The plan must be internally consistent and complete. Before finishing, "
    "verify these grounding and coverage checks and fix any gap:\n"
    "- Every user story maps to a capability described in the product spec.\n"
    "- Every feature and every task references only story IDs that exist in "
    "section 1.\n"
    "- Every user story is grouped by at least one feature.\n"
    "- Every feature has at least one engineering task supporting it, and every "
    "user story is referenced by at least one task.\n"
    "- Every task supports one of the listed features and implements work "
    "described in the product spec.\n"
    "Do not rewrite or drop validated content; where a story or feature has no "
    "task yet, derive the missing tasks from the product spec below rather than "
    "leaving the coverage gap. "
    "\n\nProduct Spec:\n" + product_spec
)
synthesis_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_synthesis,
    knowledge=knowledge_synthesis,
)

# Project Plan Synthesis - Evaluation Agent
persona_synthesis_eval = (
    "You are an evaluation agent that checks whether a synthesized project plan "
    "is complete and internally consistent. You only judge the merged plan "
    "document as a whole."
)
evaluation_criteria_synthesis = (
    "The answer should be a single project plan document with three sections: "
    "(1) numbered user stories (US-1, US-2, ...) in the form 'As a [type of "
    "user], I want [an action or feature] so that [benefit/value].'; "
    "(2) product features, each written as labelled lines that literally start "
    "with 'Feature Name:', 'Description:', 'Key Functionality:', 'User "
    "Benefit:' and 'Related User Stories:' listing story IDs from section 1; "
    "(3) engineering tasks, each written as labelled lines that literally start "
    "with 'Task ID:', 'Task Title:', 'Related User Story:', 'Description:', "
    "'Acceptance Criteria:', 'Estimated Effort:' and 'Dependencies:', where "
    "every referenced user story ID exists in section 1. "
    "A feature or task whose fields are rendered as bold or numbered headings "
    "instead of the literal labels followed by a colon does not meet the "
    "criteria. "
    "The plan must also pass these grounding and coverage checks: each user "
    "story maps to a capability from the product spec; each user story is "
    "grouped by at least one feature; each feature is supported by at least one "
    "engineering task; each user story is referenced by at least one task; and "
    "each task supports one of the listed features. A plan whose tasks all "
    "reference the same single user story or cover only one feature does not "
    "meet the criteria."
)
synthesis_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_synthesis_eval,
    evaluation_criteria=evaluation_criteria_synthesis,
    worker_agent=synthesis_knowledge_agent,
    max_interactions=10,
)


# Error handling helpers
def call_with_retries(description, func, *args, max_attempts=3, delay_seconds=5):
    """Call func(*args), retrying on failure (e.g. API timeouts or transient errors)."""
    last_error: Exception = RuntimeError(f"{description} was never attempted")
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args)
        except Exception as error:
            last_error = error
            logger.warning(
                "%s failed on attempt %d/%d: %s",
                description, attempt, max_attempts, error,
            )
            if attempt < max_attempts:
                time.sleep(delay_seconds)
    logger.error("%s failed after %d attempts, giving up.", description, max_attempts)
    raise last_error


def run_worker_with_evaluation(role_name, knowledge_agent, evaluation_agent, query):
    """Run the worker and evaluator for a query and return the validated response.

    First the knowledge agent produces a worker response for the query. That
    response is then passed to the evaluation agent, which judges it and
    iterates with corrections until it is validated. Transient failures are
    retried; if the evaluation loop fails entirely, the workflow falls back to
    the unevaluated worker response instead of crashing.
    """
    worker_response = call_with_retries(
        f"{role_name} knowledge agent",
        knowledge_agent.respond,
        query,
    )  
    try:
        evaluation = call_with_retries(f"{role_name} evaluation loop", evaluation_agent.evaluate, worker_response)
        return evaluation["final_response"]
    except Exception as error:
        logger.error(
            "%s evaluation loop failed (%s); falling back to an unevaluated worker response.",
            role_name, error,
        )
        return worker_response


# Shared workflow state
# Every validated step result is recorded here so that later steps (and the
# final synthesis) build on the outputs of earlier steps instead of answering
# in isolation. This keeps all personas working on the same Email Router
# artifacts: the Program Manager groups the actual user stories the Product
# Manager wrote, and the Development Engineer references those same stories.
PRODUCT_NAME = "Email Router"
workflow_state = []  # list of {"role": ..., "step": ..., "result": ...}

# Upper bound for the shared context injected into each step, so the prompt
# (persona + knowledge incl. product spec + context + step) stays safely
# within the model's context window even if the plan has many steps.
MAX_SHARED_CONTEXT_CHARS = 20000


def format_shared_context():
    """Render the accumulated workflow state as context for the next step.

    If the accumulated results exceed MAX_SHARED_CONTEXT_CHARS, only the most
    recent entries that fit are included (oldest entries are dropped first).
    """
    if not workflow_state:
        return ""
    sections = [
        f"[{entry['role']}] Step: {entry['step']}\nValidated result:\n{entry['result']}"
        for entry in workflow_state
    ]
    kept = []
    total_chars = 0
    for section in reversed(sections):
        if kept and total_chars + len(section) > MAX_SHARED_CONTEXT_CHARS:
            logger.warning(
                "Shared context exceeds %d characters; dropping the %d oldest entries.",
                MAX_SHARED_CONTEXT_CHARS, len(sections) - len(kept),
            )
            break
        kept.insert(0, section)
        total_chars += len(section)
    return (
        f"Shared workflow context for the {PRODUCT_NAME} product. The following "
        "are the validated outputs of previously completed workflow steps. Stay "
        "consistent with them and reference them where applicable:\n\n"
        + "\n\n".join(kept)
    )


def build_step_query(step):
    """Anchor a routed step to the Email Router product and prior validated outputs."""
    query = f"Product: {PRODUCT_NAME}.\nCurrent step to complete: {step}"
    context = format_shared_context()
    if context:
        query = f"{context}\n\n{query}"
    return query


def record_step(role_name, step, result):
    """Store a validated step result in the shared workflow state."""
    workflow_state.append({"role": role_name, "step": step, "result": result})


# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function should:
#   1. Take the input query (e.g., a step from the action plan).
#   2. Get a response from the respective Knowledge Augmented Prompt Agent.
#   3. Have the response evaluated by the corresponding Evaluation Agent.
#   4. Return the final validated response.
def product_manager_support_function(query: str) -> str:
    """Support function for the Product Manager route."""
    step_query = build_step_query(query)
    worker_response = product_manager_knowledge_agent.respond(step_query)
    evaluation_result = product_manager_evaluation_agent.evaluate(worker_response)
    final_response = evaluation_result['final_response']
    record_step("Product Manager", query, final_response)
    return final_response


def program_manager_support_function(query: str) -> str:
    """Support function for the Program Manager route."""
    step_query = build_step_query(query)
    worker_response = program_manager_knowledge_agent.respond(step_query)
    evaluation_result = program_manager_evaluation_agent.evaluate(worker_response)
    final_response = evaluation_result['final_response']
    record_step("Program Manager", query, final_response)
    return final_response


def development_engineer_support_function(query: str) -> str:
    """Support function for the Development Engineer route."""
    step_query = build_step_query(query)
    worker_response = development_engineer_knowledge_agent.respond(step_query)
    evaluation_result = development_engineer_evaluation_agent.evaluate(worker_response)
    final_response = evaluation_result['final_response']
    record_step("Development Engineer", query, final_response)
    return final_response


# Routing Agent
# TODO: 10 - Instantiate a routing_agent. You will need to define a list of agent dictionaries (routes) for Product Manager, Program Manager, and Development Engineer. Each dictionary should contain 'name', 'description', and 'func' (linking to a support function). Assign this list to the routing_agent's 'agents' attribute.
routes = [
    {
        "name": "Product Manager",
        "description": (
            "Handles steps about defining user stories and user personas. "
            "Use this route to identify the different types of users and write "
            "user stories in the form 'As a [user], I want [action] so that "
            "[benefit]'. Keywords: user story, user stories, persona, user needs, "
            "who the users are, what users want. "
            "Does NOT group stories into features and does NOT define "
            "engineering or development tasks."
        ),
        "func": lambda x: product_manager_support_function(x),
    },
    {
        "name": "Program Manager",
        "description": (
            "Handles steps about defining product features by grouping related "
            "user stories into cohesive, named feature groups. "
            "Keywords: feature, features, group user stories, feature grouping, "
            "capabilities, product feature list. "
            "Does NOT write individual user stories and does NOT define "
            "engineering or development tasks."
        ),
        "func": lambda x: program_manager_support_function(x),
    },
    {
        "name": "Development Engineer",
        "description": (
            "Handles steps about defining the technical development or "
            "engineering tasks required to implement user stories. "
            "Keywords: development task, engineering task, implementation, build, "
            "code, technical work, what needs to be built. "
            "Does NOT write user stories and does NOT group stories into features."
        ),
        "func": lambda x: development_engineer_support_function(x),
    },
]
routing_agent = RoutingAgent(openai_api_key=openai_api_key, agents=routes)
routing_agent.agents = routes

# Run the workflow

print("\n*** Workflow execution started ***\n")
print(f"synthesis_step_needed = {synthesis_step_needed}")
# Workflow Prompt
# ****
workflow_prompt = (
    "Generate a full and comprehensive project plan for the Email Router product: "
    "1) detailed user stories in the form 'As a [type of user], I want [an action or feature] "
    "so that [benefit/value].' from a product management perspective; "
    "2) product features structured as 'Feature Name:', 'Description:', "
    "'Key Functionality:', 'User Benefit:' from a program management perspective; "
    "3) detailed engineering tasks structured as 'Task ID:', 'Task Title:', "
    "'Related User Story:', 'Description:', 'Acceptance Criteria:', "
    "'Estimated Effort:', 'Dependencies:' from a development perspective; "
)
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
# TODO: 12 - Implement the workflow.
#   1. Use the 'action_planning_agent' to extract steps from the 'workflow_prompt'.
#   2. Initialize an empty list to store 'completed_steps'.
#   3. Loop through the extracted workflow steps:
#      a. For each step, use the 'routing_agent' to route the step to the appropriate support function.
#      b. Append the result to 'completed_steps'.
#      c. Print information about the step being executed and its result.
#   4. After the loop, print the final output of the workflow (the last completed step).
try:
    workflow_steps = call_with_retries(
        "Action planning agent (step extraction)",
        action_planning_agent.extract_steps_from_prompt,
        workflow_prompt,
    )
except Exception as error:
    logger.critical("Could not extract workflow steps, aborting the workflow: %s", error)
    raise SystemExit(1) from error

if not workflow_steps:
    logger.critical("The action planning agent returned no steps, aborting the workflow.")
    raise SystemExit(1)

logger.info("Action planning agent produced %d workflow steps.", len(workflow_steps))

completed_steps = []
failed_steps = []
for index, step in enumerate(workflow_steps, start=1):
    print(f"\n--- Executing step {index}/{len(workflow_steps)} ---")
    print(f"Step: {step}")
    try:
        result = call_with_retries(f"Routing agent (step {index})", routing_agent.route, step)
    except Exception as error:
        logger.error("Step %d failed and will be skipped: %s", index, error)
        failed_steps.append((index, step))
        continue
    completed_steps.append(result)
    print(f"Result of step {index}:\n{result}")

# Final synthesis step: merge all validated outputs from the shared workflow
# state into one consistent project plan (user stories, features, tasks with
# resolved cross-references). Invoked directly rather than via embedding
# routing so the consolidation step can never be misrouted. Runs only when
# synthesis_step_needed is True; otherwise the last completed step is the
# final output, which allows comparing the workflow with and without synthesis.
final_project_plan = None
if not synthesis_step_needed:
    print("\nSynthesis step skipped (synthesis_step_needed=False); "
          "the final output is the last completed step.")
elif workflow_state:
    print(f"\n--- Executing final synthesis step ({len(workflow_state)} validated outputs) ---")
    synthesis_query = (
        f"Merge the validated outputs below into one complete, internally "
        f"consistent project plan document for the {PRODUCT_NAME} product with "
        "three sections: User Stories (numbered US-1, US-2, ...), Product "
        "Features (each listing the story IDs it groups as Related User "
        "Stories), and Engineering Tasks (each referencing a real story ID). "
        "Consolidate, deduplicate, and resolve all cross-references, and make "
        "sure every user story is grouped by at least one feature and every "
        "story and feature is covered by at least one engineering task; derive "
        "any missing task from the product spec instead of leaving a gap.\n\n"
        + format_shared_context()
    )
    try:
        final_project_plan = run_worker_with_evaluation(
            "Project Plan Synthesis",
            synthesis_knowledge_agent,
            synthesis_evaluation_agent,
            synthesis_query,
        )
        completed_steps.append(final_project_plan)
    except Exception as error:
        logger.error(
            "Final synthesis step failed (%s); falling back to the last completed step as output.",
            error,
        )

print("\n*** Workflow execution completed ***\n")
if failed_steps:
    logger.warning(
        "%d of %d steps failed: %s",
        len(failed_steps), len(workflow_steps),
        ", ".join(f"step {index} ('{step}')" for index, step in failed_steps),
    )

output_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agentic-workflow-output.txt"
)
if final_project_plan:
    final_output_label = "Final output of the workflow (synthesized project plan):"
    final_output = final_project_plan
elif completed_steps:
    if synthesis_step_needed:
        final_output_label = "Final output of the workflow (synthesis unavailable, last completed step):"
    else:
        final_output_label = "Final output of the workflow (synthesis disabled, last completed step):"
    final_output = completed_steps[-1]
else:
    final_output_label = None
    final_output = None

if final_output:
    print(final_output_label)
    print(final_output)
    try:
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(f"{final_output_label}\n\n{final_output}\n")
        print(f"\nFinal output written to {output_file_path}")
    except OSError as error:
        logger.error("Could not write the final output to %s: %s", output_file_path, error)
else:
    logger.error("All workflow steps failed; no final output is available.")