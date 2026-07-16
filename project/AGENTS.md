# AGENT.md

## Purpose

This repository implements the **Email Router project-planning workflow** required by the Udacity Agentic AI project rubric. Coding agents working in this repository must implement, test, and preserve a modular Python agent toolkit plus an orchestrated workflow that converts a high-level Email Router product request into:

1. valid user stories,
2. structured product features, and
3. detailed engineering tasks.

Treat every requirement in this file as mandatory unless it is explicitly marked **optional / stretch**.

---

## 1. Scope and required files

The implementation must include at least:

```text
project/
├── project_overview.md
├── requirements.txt
└── starter/
    ├── phase_1/
    │   ├── README.md
    │   ├── workflow_agents/
    │   │   ├── __init__.py        # keep empty
    │   │   └── base_agents.py     # all seven agent classes
    │   ├── direct_prompt_agent.py
    │   ├── augmented_prompt_agent.py
    │   ├── knowledge_augmented_prompt_agent.py
    │   ├── rag_knowledge_prompt_agent.py
    │   ├── evaluation_agent.py
    │   ├── routing_agent.py
    │   └── action_planning_agent.py
    └── phase_2/
        ├── README.md
        ├── Product-Spec-Email-Router.txt
        ├── agentic_workflow.py
        └── workflow_agents/
            ├── __init__.py
            └── base_agents.py
```

Work **in the corresponding starter phase**, not in an invented root-level layout. The Phase 1 scripts are standalone execution/test scripts beside `workflow_agents/`; do not move or rename them merely to impose a `tests/` convention. For Phase 2, ensure the completed Phase 1 `base_agents.py` is available in `phase_2/workflow_agents/` as expected by `agentic_workflow.py`. Store screenshots or terminal-output evidence in the submission location accepted by Udacity; an extra `evidence/` directory is optional, not part of the starter structure.

Do not rename starter files, public classes, or required public methods without also updating every import and test. Preserve the provided `RAGKnowledgePromptAgent`; do not regress it while implementing the six student-owned agents.

## 1.1 Source-of-truth and change discipline

- This file is aligned to repository commit `9ed2037decad05e86d81c36ef417abe57965c583` and the Udacity rubric.
- The checked-out starter files, their `TODO` comments, and the phase-specific README files are the source of truth for exact constructor signatures, predefined personas, knowledge strings, golden prompts, and filenames.
- Fill the existing TODOs in place. Do not replace the starter architecture with a different framework, CLI, test layout, or configuration system.
- Requirements added here for robustness or maintainability must not conflict with rubric-visible behavior. If a recommendation conflicts with the starter code or rubric, preserve the starter/rubric contract.

---

## 2. Runtime and dependency rules

- Use the Python environment and dependency versions defined by the supplied `project/requirements.txt`; do not impose a new Python-version requirement unless the repository requires it.
- Load the OpenAI API key with `python-dotenv` from a local `.env` file and/or the process environment, using the variable `OPENAI_API_KEY`. Store the loaded value in `openai_api_key` in `agentic_workflow.py`.
- Never hardcode, print, commit, or log API keys or other secrets.
- Pass the API key into each agent constructor that requires it.
- Agents that perform chat completion must use `gpt-3.5-turbo`, unless the starter project explicitly specifies a different model for that class.
- `RoutingAgent` embeddings must use `text-embedding-3-large`.
- `EvaluationAgent` evaluation and correction calls must use `temperature=0`.
- Keep external dependencies minimal and consistent with the starter repository.
- If the installed OpenAI SDK differs from the starter code, adapt calls consistently without changing the required public interfaces or behavior.

---

## 3. Required agent implementations

Implement all six classes in `workflow_agents/base_agents.py`:

- `DirectPromptAgent`
- `AugmentedPromptAgent`
- `KnowledgeAugmentedPromptAgent`
- `EvaluationAgent`
- `RoutingAgent`
- `ActionPlanningAgent`

Each class must:

1. define an explicit `__init__` method;
2. initialize all state needed by its behavior;
3. expose the required primary public method;
4. return exactly the required type and shape;
5. include a concise docstring describing its contract; and
6. avoid unrelated responsibilities and hidden global state.

### 3.1 `DirectPromptAgent`

**Constructor state**

- API key and/or initialized OpenAI client, following the starter-code convention.
- Chat model set to `gpt-3.5-turbo`.

**Public method**

```python
respond(prompt: str) -> str
```

**Behavior**

- Validate or clearly reject an empty prompt.
- Send the supplied prompt directly as a single `user` message.
- Do not add a system message, persona, knowledge, or prior context.
- Return only the assistant's textual content, not the full API response object.

### 3.2 `AugmentedPromptAgent`

**Constructor state**

- API key/client.
- `persona: str`.
- Chat model set to `gpt-3.5-turbo`.

**Public method**

```python
respond(prompt: str) -> str
```

**Behavior**

- Build a system message that establishes the configured persona.
- Explicitly instruct the model to ignore/forget previous conversational context.
- Send the supplied prompt as the user message.
- Return only textual content.

### 3.3 `KnowledgeAugmentedPromptAgent`

**Constructor state**

- API key/client.
- `persona: str`.
- `knowledge: str`.
- Chat model set to `gpt-3.5-turbo`.

**Public method**

```python
respond(prompt: str) -> str
```

**Behavior**

- Build a system message containing the persona and the complete supplied knowledge.
- Explicitly instruct the model to use **only** the supplied knowledge.
- Explicitly instruct it to ignore/forget other or previous context.
- Do not silently supplement the answer with external knowledge.
- Return only textual content.

### 3.4 `EvaluationAgent`

**Constructor state**

- API key/client.
- `persona: str`.
- `evaluation_criteria: str`.
- `agent_to_evaluate`: worker object exposing `respond(prompt: str) -> str`.
- `max_interactions: int`, which must be positive.
- Chat model set to `gpt-3.5-turbo`.

**Public method**

```python
evaluate(prompt: str) -> dict
```

**Required return object**

```python
{
    "final_response": str,
    "evaluation": str,
    "iterations": int,
}
```

Use these exact keys unless the provided starter instructions already define an equivalent exact schema.

**Behavior**

1. Ask the worker agent for an initial response to the original prompt.
2. Evaluate the response against the configured criteria using `temperature=0`.
3. If the response satisfies all criteria, return it immediately.
4. Otherwise, generate deterministic, specific correction instructions.
5. Ask the worker to revise the answer using the original request plus the correction instructions.
6. Repeat until the response passes or `max_interactions` is reached.
7. Return the best/latest response, latest evaluation, and actual number of worker attempts.
8. Never exceed `max_interactions`; avoid an off-by-one error.

The evaluation prompt must make the pass/fail signal unambiguous and machine-detectable. Do not use brittle substring matching where a structured or exact verdict can be used. Correction instructions must identify concrete deficiencies rather than merely saying “improve the answer.”

### 3.5 `RoutingAgent`

**Constructor state**

- API key/client.
- `agents`, a list of route dictionaries. Each route must contain:

```python
{
    "name": str,
    "description": str,
    "func": callable,
}
```

**Public methods**

```python
get_embedding(text: str) -> list[float]
route(prompt: str) -> str
```

Equivalent private naming for the embedding helper is acceptable only if starter tests do not require a public method.

**Behavior**

1. Create embeddings with `text-embedding-3-large`.
2. Embed the incoming prompt and every route description.
3. Compute cosine similarity between the prompt vector and each description vector.
4. Select the route with the highest score.
5. Call the selected route's `func(prompt)`.
6. Return that function's response.

Required safeguards:

- Reject an empty `agents` list with a clear error.
- Validate that each route contains `name`, `description`, and callable `func`.
- Handle zero-length vectors safely in cosine similarity.
- Make tie behavior deterministic, preferably choosing the first highest-scoring route.
- Do not route by hardcoded keywords.

### 3.6 `ActionPlanningAgent`

**Constructor state**

- API key/client.
- Provided action-planning knowledge, if the starter signature requires it.
- Chat model set to `gpt-3.5-turbo`.

**Public method**

```python
extract_steps_from_prompt(prompt: str) -> list[str]
```

**Behavior**

- Use a system prompt that defines the agent as an action-plan extractor.
- Ask for discrete, ordered, actionable steps suitable for downstream routing.
- Parse the model response into a clean Python list.
- Remove numbering, bullets, blank lines, and surrounding whitespace.
- Do not return headings, commentary, or an empty pseudo-step.
- Preserve meaningful step text and ordering.

---

## 4. `agentic_workflow.py` setup

### 4.1 Imports and inputs

Import these classes from `workflow_agents.base_agents`:

```python
ActionPlanningAgent
KnowledgeAugmentedPromptAgent
EvaluationAgent
RoutingAgent
```

The workflow must:

- read `OPENAI_API_KEY` from the environment;
- fail early with a clear message if it is absent;
- read `Product-Spec-Email-Router.txt` using an explicit text encoding such as UTF-8;
- store the file's contents in `product_spec`;
- report a clear error if the product-spec file cannot be read.

Do not duplicate the product specification manually in source code.

### 4.2 Core and specialist agents

Instantiate:

1. `action_planning_agent` with the supplied `knowledge_action_planning`;
2. a Product Manager `KnowledgeAugmentedPromptAgent` using `persona_product_manager` and `knowledge_product_manager + product_spec`;
3. a Program Manager `KnowledgeAugmentedPromptAgent` using `persona_program_manager` and `knowledge_program_manager`;
4. a Development Engineer `KnowledgeAugmentedPromptAgent` using `persona_dev_engineer` and `knowledge_dev_engineer`.

Ensure separators/newlines are inserted when appending `product_spec`; do not accidentally join words at the boundary.

### 4.3 Evaluation agents

Instantiate one `EvaluationAgent` per specialist.

#### Product Manager evaluator

- Persona: `You are an evaluation agent that checks the answers of other worker agents`.
- Worker: Product Manager knowledge agent.
- Criterion: every user story must use exactly this semantic structure:

```text
As a [type of user], I want [an action or feature] so that [benefit/value].
```

#### Program Manager evaluator

Use `persona_program_manager_eval`, the Program Manager knowledge agent, and criteria that require every feature to contain all of:

```text
Feature Name: ...
Description: ...
Key Functionality: ...
User Benefit: ...
```

#### Development Engineer evaluator

Use `persona_dev_engineer_eval`, the Development Engineer knowledge agent, and criteria that require every task to contain all of:

```text
Task ID: ...
Task Title: ...
Related User Story: ...
Description: ...
Acceptance Criteria: ...
Estimated Effort: ...
Dependencies: ...
```

Criteria must reject missing labels, empty values, vague acceptance criteria, and tasks that cannot be traced to a user story.

### 4.4 Routing agent configuration

Set `routing_agent.agents` to exactly three functional routes:

- **Product Manager** — responsible for product personas and user stories only.
- **Program Manager** — responsible for product features and feature-level planning.
- **Development Engineer** — responsible for technical implementation tasks.

Every route dictionary must contain `name`, a role-specific `description`, and `func`. Descriptions must be mutually distinguishable so embedding-based routing has a meaningful basis.

---

## 5. Support functions

Define one support function for each specialist, for example:

```python
product_manager_support_function(query: str) -> str
program_manager_support_function(query: str) -> str
development_engineer_support_function(query: str) -> str
```

Each function must:

1. accept one workflow step as `query`;
2. call the corresponding knowledge agent's `respond(query)`;
3. pass the result through the corresponding evaluator;
4. return the evaluator's `final_response` string.

Because `EvaluationAgent.evaluate()` normally invokes its configured worker itself, avoid unintentionally generating two unrelated initial answers. If the starter architecture explicitly requires the support function to call `respond()` first, construct the evaluation input so the evaluator refines that response deterministically; otherwise let `evaluate(query)` own the worker loop. Whichever pattern is used must satisfy the rubric, avoid duplicate API work, and be consistent in all three support functions.

---

## 6. Main orchestration

Place executable orchestration behind:

```python
if __name__ == "__main__":
```

The workflow must:

1. define a high-level `workflow_prompt` requesting a complete Email Router project plan;
2. call `action_planning_agent.extract_steps_from_prompt(workflow_prompt)`;
3. store the result in `workflow_steps`;
4. create an empty `completed_steps` list;
5. iterate through all steps in order;
6. print the current step;
7. call `routing_agent.route(current_step)`;
8. append the returned result to `completed_steps`;
9. print the current result; and
10. after the loop, print a final consolidated output or the final completed result.

A valid complete run must contain user stories, product features, and engineering tasks. Do not assume that the last routed result alone always represents the complete plan; prefer a clearly labeled consolidation of all completed steps.

---

## 7. Output contracts

### 7.1 User stories

Every story must be independently understandable and follow:

```text
As a [type of user], I want [an action or feature] so that [benefit/value].
```

Do not accept stories missing the user, action, or benefit.

### 7.2 Product features

Every feature must include, in order:

```text
Feature Name: <concise unique name>
Description: <purpose and scope>
Key Functionality: <specific capabilities>
User Benefit: <observable value>
```

### 7.3 Engineering tasks

Every task must include:

```text
Task ID: <stable unique identifier>
Task Title: <imperative, concise title>
Related User Story: <story identifier or exact traceable reference>
Description: <implementation scope>
Acceptance Criteria: <objective, testable completion conditions>
Estimated Effort: <consistent unit, such as story points or ideal days>
Dependencies: <task IDs, external dependency, or None>
```

Acceptance criteria must be verifiable. Dependencies must not reference nonexistent task IDs. Task IDs must be unique.

---

## 8. Testing requirements

Provide a separate executable test script for each of the six implemented agents and one for the provided `RAGKnowledgePromptAgent`.

Every test script must:

- import its class from `workflow_agents.base_agents`;
- obtain the API key securely;
- instantiate the class with all required parameters;
- call the primary public method with the sample prompt required by the project instructions;
- print the prompt where useful and print the relevant result;
- fail visibly on exceptions or invalid return types.

Required script-specific evidence:

- `DirectPromptAgent`: include the required statement explaining the response's knowledge source.
- `AugmentedPromptAgent`: include comments discussing the knowledge source and effect of the persona.
- `KnowledgeAugmentedPromptAgent`: print confirmation that supplied knowledge was used.
- `EvaluationAgent`: show final response, evaluation, and iteration count.
- `RoutingAgent`: demonstrate that an appropriate route function was selected and called.
- `ActionPlanningAgent`: print the cleaned list of steps.
- `RAGKnowledgePromptAgent`: run and capture the provided agent's output without breaking its existing behavior.

Store successful terminal output or screenshots for **all seven** scripts in `evidence/` or the submission location mandated by the course.

Where practical, also add deterministic unit tests with mocked OpenAI responses covering:

- required message roles and prompt content;
- exact return types and dictionary keys;
- evaluator pass on first attempt;
- evaluator correction and retry;
- evaluator termination at `max_interactions`;
- routing similarity selection and deterministic ties;
- action-step cleanup;
- missing API key, missing product spec, malformed route, and empty model content.

Do not make live API calls in the default automated unit-test suite. Keep live integration scripts separate or explicitly marked.

---

## 9. Code quality and robustness

- Follow PEP 8 naming: `PascalCase` classes and `snake_case` functions/variables.
- Use descriptive names and type hints on public methods.
- Add docstrings to classes and nontrivial functions.
- Comment design intent or complex logic, not obvious syntax.
- Keep agent classes distinct and modular.
- Organize `agentic_workflow.py` into setup, instantiation, support functions, and orchestration.
- Avoid broad `except Exception` blocks unless re-raising with useful context.
- Handle empty/malformed LLM responses explicitly.
- Add bounded retry/error handling for transient API failures if compatible with the starter SDK.
- Prefer standard logging for diagnostics; never log secrets or full sensitive prompts.
- Keep model names, temperatures, and maximum interactions easy to identify and test.
- Do not introduce unrelated refactors while completing rubric requirements.

---

## 10. Definition of done

A change is complete only when all of the following are true:

- [ ] All six required agent classes exist in `workflow_agents/base_agents.py`.
- [ ] Every class has the required constructor and primary public method.
- [ ] Chat agents use `gpt-3.5-turbo`.
- [ ] Routing embeddings use `text-embedding-3-large` and cosine similarity.
- [ ] API keys are injected/read from the environment and never hardcoded.
- [ ] Evaluations and correction instructions use `temperature=0`.
- [ ] `EvaluationAgent` respects `max_interactions` and returns the required dictionary.
- [ ] Action planning returns a clean `list[str]`.
- [ ] `agentic_workflow.py` loads `Product-Spec-Email-Router.txt`.
- [ ] Product, Program, and Engineering knowledge agents and evaluators are correctly instantiated.
- [ ] Routing contains three valid role routes.
- [ ] All planned steps are routed, captured, and printed.
- [ ] Final output contains structurally valid user stories, features, and engineering tasks.
- [ ] Seven separate functional test scripts exist and run successfully.
- [ ] Screenshot or text-output evidence for all seven runs is included in the Udacity submission.
- [ ] Code is readable, modular, documented, and free of committed secrets.

---

## 11. Optional enhancements only after mandatory completion

After all mandatory checks pass, agents may:

- vary `workflow_prompt` to generate only features or a product risk assessment and document the changed behavior;
- add a scoring mechanism to one evaluator while retaining the required pass/fail contract;
- add structured logging and resilient API error handling;
- add `reflection.md` describing strengths, limitations, and one specific architectural improvement.

Optional enhancements must not alter required class names, method names, output schemas, models, or baseline workflow behavior.

---

## 12. Instructions for coding agents

Before editing:

1. inspect the repository tree and starter code;
2. read `Product-Spec-Email-Router.txt` and any project instruction document;
3. identify existing public interfaces and tests;
4. make the smallest coherent change that closes a rubric gap.

After editing:

1. run formatting/lint checks already configured in the repository;
2. run deterministic tests;
3. run live test scripts only when `OPENAI_API_KEY` is available;
4. inspect the final output against every structure in Section 7;
5. report changed files, tests run, and any remaining rubric gaps.

Never claim a test passed unless it was actually executed successfully. Never fabricate API output or submission evidence.
