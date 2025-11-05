import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import FlightSearchAgent
import subprocess, json, sys, os

load_dotenv()

app = FastAPI(title="AutoFlights API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    origin: str
    destination: str
    month: str  

# Scrape endpoint
@app.post("/scrape")
async def scrape_flights_endpoint(req: ScrapeRequest):
    """
    Runs the Playwright scraper in a safe external subprocess with user inputs,
    then summarizes results using Groq + Autogen.
    Now streams live scraper + summarizer logs to the frontend in real time
    while still returning raw flights, table text, and summary as JSON.
    """

    try:
        print(f" Received scrape request: {req.origin} -> {req.destination} ({req.month})")
        print(" Launching scraper subprocess...")

        # Windows-specific loop policy
        if sys.platform == "win32":
            try:                
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                print("Event loop policy set to WindowsProactorEventLoopPolicy")
            except Exception as e:
                print("Could not set event loop policy:", e)
        # Run scraper as subprocess   
        venv_python = sys.executable
        result = subprocess.run([venv_python, "scrape_runner.py", 
        req.origin, req.destination, req.month], 
        capture_output=True, 
        text=True, 
        timeout=300 
        )

        if result.returncode != 0:
            print("Subprocess error:", result.stderr)
            return { "status": "error", "message": "Scraper failed to run properly. Check terminal for details." }
        # Parse output
        try:
            scraped = json.loads(result.stdout)
            flights = scraped.get("flights", [])
            table_text = scraped.get("table", "")
        except Exception as e:
            print("JSON parse error:", e) 
            print("Raw output:", result.stdout)
            
            return { "status": "error", 
            "message": "Invalid data received from scraper subprocess." }

        if not flights:
            print(" No flights found in subprocess output.")
            return {"status": "no_results", 
            "message": "No priced flights found. Try again with different cities or month.", 
            "flights": [], "table": "", 
            "summary": "" 
            }
        print(f"Subprocess returned {len(flights)} flights successfully.")

        # Summarize results with Groq + Autogen
        agent = FlightSearchAgent()            
        user_query = (
                "You are a precise and funny AI travel assistant. "
                "Analyze the following flight listings and output two sections.\n\n"
                "1️ TOP CHEAPEST FLIGHTS — show ONLY a neat table with exactly these columns:\n"
                "Airline | Price | Duration | Stops | Departure | Arrival\n"
                "Include only the 3 cheapest flights (even if prices repeat).\n\n"
                "2️ THOUGHTS SECTION — below the table, add a heading in bold 'Thoughts:'\n"
                "For each line under Thoughts, start it with a bullet point.\n"
                "Then give one short, witty line per flight — light humor, friendly tone, no negativity.\n"
                "Add a blank line before this section so it visually separates from the table.\n"
                "Keep it conversational like a fun travel buddy.\n\n"
                f"{table_text}"
            )

        print("Running Autogen + Groq summarizer...")
        summary = await agent.run_flight_search(user_query)
        table_flights = flights[:3]

        return { "status": "ok", 
        "message": f"Scraped {len(flights)} flights successfully.", 
        "flights": flights, 
        "table_flights": table_flights, 
        "summary": summary 
        }

    except subprocess.TimeoutExpired:
        print("Scraper took too long — timeout.")
        return {"status": "error", "message": "Scraper timeout — took longer than expected."}
    
    except Exception as e:
        print("Error while scraping:", e) 
        return {"status": "error", "error": str(e)}

# Summarize endpoint
@app.get("/summarize")
async def summarize_endpoint():
    """
    Old helper: reads the last scraped flight_results.txt and re-summarizes it.
    Use /scrape for live scraping instead.
    """
    try:
        with open("flight_results.txt", "r", encoding="utf-8") as f:
            flight_data = f.read().strip()
    except FileNotFoundError:
        return {"summary": "No flight_results.txt found. Run the scraper first."}

    if not flight_data:
        return {"summary": " flight_results.txt is empty. Run the scraper again."}

    agent = FlightSearchAgent()
    user_query = (
        "You are a precise and funny AI travel assistant. "
        "Analyze the following flight listings and output two sections.\n\n"
        "1️ TOP CHEAPEST FLIGHTS — show ONLY a neat table with exactly these columns:\n"
        "Airline | Price | Duration | Stops | Departure | Arrival\n"
        "Include only the 3 cheapest flights (even if prices repeat).\n\n"
        "2️ THOUGHTS SECTION — below the table, add a heading in bold 'Thoughts:'\n"
        "For each line under Thoughts, start it with a bullet point.\n"
        "Then give one short, witty line per flight — light humor, friendly tone, no negativity.\n"
        "Add a blank line before this section so it visually separates from the table.\n"
        "Keep it conversational like a fun travel buddy.\n\n"
        f"{flight_data}"
    )

    summary = await agent.run_flight_search(user_query)
    return {"summary": summary}

# CLI mode
async def main():
    print(" Welcome to AutoFlights Smart Summarizer!\n")
    print("Reading flight_results.txt (generated from Playwright scraper)...")

    try:
        with open("flight_results.txt", "r", encoding="utf-8") as f:
            flight_data = f.read().strip()
    except FileNotFoundError:
        print(" No flight_results.txt found. Run googleflights_auto.py first.")
        return

    if not flight_data:
        print("flight_results.txt is empty. Run the scraper again.")
        return

    agent = FlightSearchAgent()
    print("\n Analyzing flight data with Groq...\n")

    user_query = (
        "You are a precise and funny AI travel assistant. "
        "Analyze the following flight listings and output two sections.\n\n"
        "1️ TOP CHEAPEST FLIGHTS — show ONLY a neat table with exactly these columns:\n"
        "Airline | Price | Duration | Stops | Departure | Arrival\n"
        "Include only the 3 cheapest flights (even if prices repeat).\n\n"
        "2️ THOUGHTS SECTION — below the table, add a heading in bold 'Thoughts:'\n"
        "For each line under Thoughts, start it with a bullet point.\n"
        "Then give one short, witty line per flight — light humor, friendly tone, no negativity.\n"
        "Add a blank line before this section so it visually separates from the table.\n"
        "Keep it conversational like a fun travel buddy.\n\n"
        f"{flight_data}"
    )

    try:
        summary = await agent.run_flight_search(user_query)
        print(" Smart Summary with Humor:\n")
        print(summary)

        with open("cheapest_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n Saved summary with remarks to cheapest_summary.txt")

    except Exception as e:
        print(" Error while summarizing flights:", e)

if __name__ == "__main__":
    asyncio.run(main())
