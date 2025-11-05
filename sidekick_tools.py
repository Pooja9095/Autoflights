from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from autogen_ext.tools.langchain import LangChainToolAdapter
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Search Tool (Serper)
serper = GoogleSerperAPIWrapper(serper_api_key=os.getenv("SERPER_API_KEY"))
search_tool = Tool(
    name="internet_search",
    func=serper.run,
    description="Useful for searching flight or travel information online."
)
autogen_search_tool = LangChainToolAdapter(search_tool)

# Groq Analyzer Tool 
def analyze_flights_with_groq(dummy: str=None):
    """
    Reads 'flight_results.txt' and uses Groq's Llama 3.1 model to summarize
    the top cheapest flights.
    """
    try:
        with open("flight_results.txt", "r", encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        return "No flight_results.txt found. Please run googleflights_auto.py first."

    if not data.strip():
        return "The flight_results.txt file is empty."

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )

    prompt = (
        "You are a smart travel assistant.\n"
        "Read the following flight data and summarize the 3 cheapest flights "
        "with airline, price, duration, and stops.\n"
        "Respond cleanly in a small table.\n\n"
        f"{data}"
    )

    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

# Wrap Groq analysis for Autogen
groq_analysis_tool = Tool(
    name="analyze_flights_with_groq",
    func=analyze_flights_with_groq,
    description="Analyzes flight_results.txt using Groq to find and summarize the cheapest flights."
)
autogen_groq_tool = LangChainToolAdapter(groq_analysis_tool)

# File Management Tools
file_tools = FileManagementToolkit(root_dir=".").get_tools()

#Combine tools for Autogen
autogen_tools = [autogen_groq_tool, autogen_search_tool] + [LangChainToolAdapter(t) for t in file_tools]
