# 1 - Import the AugmentedPromptAgent class
from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# 2 - Instantiate an object of AugmentedPromptAgent with the required parameters
augmented_agent = AugmentedPromptAgent(openai_api_key, persona)

# 3 - Send the 'prompt' to the agent and store the response in a variable named 'augmented_agent_response'
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

# 4 - Add a comment explaining:
# - What knowledge the agent likely used to answer the prompt.
# - How the system prompt specifying the persona affected the agent's response.
#
# Explanation:
# - Knowledge used: The agent relied on the LLM's own general pre-trained
#   knowledge (there is no supplied knowledge string), so it recalls that the
#   capital of France is Paris from its training data.
# - Persona effect: The system prompt sets a persona and instructs the model to
#   forget previous context. As a result the answer is framed in the professor
#   persona and begins with the required opening "Dear students,".
