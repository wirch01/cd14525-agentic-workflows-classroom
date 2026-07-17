# agentic_workflow.py

# TODO: 1 - Import the following agents: ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent from the workflow_agents.base_agents module
from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import logging
import os
import time

from dotenv import load_dotenv

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
    "A development Plan for a product contains all these components"
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
persona_product_manager_eval = (
    "You are an evaluation agent that checks whether the Product Manager's "
    "answers are valid user stories. You only judge user-story quality and "
    "structure; you do not evaluate features or development tasks."
)
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
    "engineering implementation tasks."
)
# Instantiate a program_manager_knowledge_agent using 'persona_program_manager' and 'knowledge_program_manager'
# (This is a necessary step before TODO 8. Students should add the instantiation code here.)
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager,
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = (
    "You are an evaluation agent that checks whether the Program Manager's "
    "answers are valid product features. You only judge feature quality and "
    "structure; you do not evaluate user stories or development tasks."
)

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
    "User Benefit: How this feature creates value for the user"
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
    "user stories and not feature groupings."
)
# Instantiate a development_engineer_knowledge_agent using 'persona_dev_engineer' and 'knowledge_dev_engineer'
# (This is a necessary step before TODO 9. Students should add the instantiation code here.)
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer,
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = (
    "You are an evaluation agent that checks whether the Development Engineer's "
    "answers are valid development tasks. You only judge development-task quality "
    "and structure; you do not evaluate user stories or features."
)
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
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev_engineer,
    worker_agent=development_engineer_knowledge_agent,
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
    """Get a response from a knowledge agent and validate it with its evaluation agent.

    Retries transient failures; if evaluation fails but the worker responded,
    falls back to the unevaluated response instead of crashing the workflow.
    """
    response = call_with_retries(f"{role_name} knowledge agent", knowledge_agent.respond, query)
    try:
        evaluation = call_with_retries(f"{role_name} evaluation agent", evaluation_agent.evaluate, response)
        return evaluation["final_response"]
    except Exception as error:
        logger.error(
            "%s evaluation failed (%s); returning the unevaluated response as a fallback.",
            role_name, error,
        )
        return response


# Job function persona support functions
# TODO: 11 - Define the support functions for the routes of the routing agent (e.g., product_manager_support_function, program_manager_support_function, development_engineer_support_function).
# Each support function should:
#   1. Take the input query (e.g., a step from the action plan).
#   2. Get a response from the respective Knowledge Augmented Prompt Agent.
#   3. Have the response evaluated by the corresponding Evaluation Agent.
#   4. Return the final validated response.
def product_manager_support_function(query: str) -> str:
    """Route product-persona/user-story steps through the Product Manager agents."""
    return run_worker_with_evaluation(
        "Product Manager",
        product_manager_knowledge_agent,
        product_manager_evaluation_agent,
        query,
    )


def program_manager_support_function(query: str) -> str:
    """Route product-feature steps through the Program Manager agents."""
    return run_worker_with_evaluation(
        "Program Manager",
        program_manager_knowledge_agent,
        program_manager_evaluation_agent,
        query,
    )


def development_engineer_support_function(query: str) -> str:
    """Route engineering-task steps through the Development Engineer agents."""
    return run_worker_with_evaluation(
        "Development Engineer",
        development_engineer_knowledge_agent,
        development_engineer_evaluation_agent,
        query,
    )


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

print("\n*** Workflow execution completed ***\n")
if failed_steps:
    logger.warning(
        "%d of %d steps failed: %s",
        len(failed_steps), len(workflow_steps),
        ", ".join(f"step {index} ('{step}')" for index, step in failed_steps),
    )
if completed_steps:
    print("Final output of the workflow:")
    print(completed_steps[-1])
else:
    logger.error("All workflow steps failed; no final output is available.")