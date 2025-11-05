import sys, io
import json, asyncio
from googleflights_auto import scrape_flights

# Ensure UTF-8 output for subprocess logs
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set Windows event loop policy
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception as e:
        print("Warning: Could not set Windows event loop policy:", e, file=sys.stderr)

async def run():
    # Read CLI args: origin, destination, month
    try:
        origin, destination, month = sys.argv[1:4]
    except ValueError:
        print("Error: Please provide origin, destination, and month.", file=sys.stderr)
        sys.exit(1)
        
    # Run scraper and return JSON
    try:
        data, table = await scrape_flights(origin, destination, month)
        print(json.dumps({"flights": data, "table": table}, ensure_ascii=False), file=sys.stdout)
    except Exception as e:
        print(f"Scraping failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run())
