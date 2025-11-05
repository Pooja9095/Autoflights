from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from sidekick_tools import autogen_tools
from dotenv import load_dotenv
import os


class FlightSearchAgent(AssistantAgent):
    # Autogen agent for summarizing flight data
    def __init__(self, name="flight_agent"):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        # Model setup
        model_info = {
            "family": "llama3.1",              
            "function_calling": True,
            "vision": False,
            "supports_response_format": True,
            "json_output": True,
            "structured_output": True,               
        }

        # Groq LLaMa 3.1 model
        model_client = OpenAIChatCompletionClient(
            model="llama-3.1-8b-instant",
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model_info=model_info,
        )

        # Initialize agent
        super().__init__(
            name=name,
            model_client=model_client,
            system_message=(
                "You are AutoFlights AI — a travel assistant that analyzes real flight data "
                "from Google Flights (saved in flight_results.txt) and summarizes the best deals. "
                "Use available tools to read, search, and reason about flight information."
            ),
            tools=autogen_tools,
            reflect_on_tool_use=True,
        )

    async def run_flight_search(self, user_query: str):
        # Run summarization for flight data
        message = TextMessage(role="user", content=user_query, source="user")
        response = await self.on_messages([message], cancellation_token=CancellationToken())
        return response.chat_message.content
