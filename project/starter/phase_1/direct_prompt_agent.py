# Test script for DirectPromptAgent class

# 1 - Import the DirectPromptAgent class from workflow_agents.base_agents
from workflow_agents.base_agents import DirectPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 2 - Load the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

# 3 - Instantiate the DirectPromptAgent as direct_agent
direct_agent = DirectPromptAgent(openai_api_key)
# 4 - Use direct_agent to send the prompt defined above and store the response
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print(direct_agent_response)

# 5 - Print an explanatory message describing the knowledge source used by the agent to generate the response
print(
    "\nKnowledge source: The DirectPromptAgent sends the prompt straight to the "
    "gpt-3.5-turbo model with no system prompt, persona, or added knowledge. "
    "The answer therefore comes solely from the LLM's own pre-trained general knowledge."
)
