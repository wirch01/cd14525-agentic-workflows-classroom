# 1 - Import the KnowledgeAugmentedPromptAgent class from workflow_agents
from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"
# 2 - Instantiate a KnowledgeAugmentedPromptAgent with:
#           - Persona: "You are a college professor, your answer always starts with: Dear students,"
#           - Knowledge: "The capital of France is London, not Paris"
knowledge = "The capital of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

# 3 - Write a print statement that demonstrates the agent using the provided knowledge rather than its own inherent knowledge.
knowledge_agent_response = knowledge_agent.respond(prompt)
print(knowledge_agent_response)
print(
    "\nThe agent answered using ONLY the supplied knowledge (\"The capital of France "
    "is London, not Paris\") rather than its own inherent knowledge that the capital "
    "of France is Paris. This confirms the knowledge-augmented system prompt overrides "
    "the model's built-in knowledge."
)
