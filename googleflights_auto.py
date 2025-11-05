import asyncio
import sys

# Set event loop for Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import re
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from playwright.async_api import async_playwright
from texttable import Texttable

# Helpers
def first_line(s: str) -> str:
    """Return only the first non-empty line of text."""
    return (s or "").strip().splitlines()[0].strip() if s else ""


def extract_price(s: str) -> Tuple[str, Optional[int]]:
    """Find first currency amount like $341 and return both display + numeric."""
    m = re.search(r'([$€£]\s?\d[\d,]*)', s or "")
    if not m:
        return "", None
    disp = m.group(1).replace(" ", "")
    val = int(re.sub(r"[^\d]", "", disp))
    return disp, val


def extract_airline(s: str) -> str:
    """Extract clean airline name (last meaningful line)."""
    lines = [ln.strip() for ln in (s or "").splitlines() if ln.strip()]
    if not lines:
        return "N/A"
    cand = lines[-1]
    cand = cand.replace("round trip", "").strip()
    return cand or "N/A"

# Main scraper
async def scrape_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    month_input: Optional[str] = None
) -> Tuple[List[Dict], str]:
    """Scrape Google Flights using Playwright and return flight data + ASCII table."""

    print("Launching AutoFlights Google Reader...", file=sys.stderr)

    # Get user input if missing
    if not origin:
        origin = input("Enter departure city or airport (e.g., Dallas): ").strip()
    if not destination:
        destination = input("Enter destination city or airport (e.g., Paris): ").strip()
    if not month_input:
        month_input = input("Enter travel month and year (e.g., Jan 2026): ").strip()

    # Parse month safely
    try:
        parsed = datetime.strptime(month_input, "%b %Y")
    except:
        try:
            parsed = datetime.strptime(month_input, "%B %Y")
        except:
            print("Invalid format. Using current month.", file=sys.stderr)
            parsed = datetime.now()
    date_str = parsed.strftime("%Y-%m")

    # Launch Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=150)
        page = await browser.new_page()

        print(f"Opening Google Flights for {origin} -> {destination} ({date_str})...", file=sys.stderr)
        url = f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination}+in+{date_str}"
        await page.goto(url, timeout=120000)
        print("Click 'Search' if needed — the script will auto-detect flight results.", file=sys.stderr)

        # Wait for results 
        try:
            await page.wait_for_selector('text=$', timeout=180000)
            print("Flight results detected! Collecting data...", file=sys.stderr)
        except:
            print("No flight results detected within time limit.", file=sys.stderr)
            await browser.close()
            return [], ""

        # Scroll to load more
        print("Scrolling to load more flights...", file=sys.stderr)
        for _ in range(5):
            await page.mouse.wheel(0, 3000)
            await asyncio.sleep(2)

        # Get flight blocks
        flights = await page.query_selector_all('div[role="listitem"], .pIav2d, .Rk10dc, .zBTtmb')
        print(f"Found {len(flights)} possible flight entries.", file=sys.stderr)

        flight_data = []

        async def get_text(el):
            if el:
                try:
                    return (await el.inner_text()).strip()
                except:
                    return "N/A"
            return "N/A"

        # Extract data
        for f in flights[:20]:
            departure_time = await f.query_selector('span[aria-label*="Departure time"]')
            arrival_time = await f.query_selector('span[aria-label*="Arrival time"]')
            airline = await f.query_selector(".sSHqwe, .Ir0Voe")
            duration = await f.query_selector("div.gvkrdb, .Ak5kof")
            stops = await f.query_selector("div.hF6lYb span.rGRiKd, .Gwsj3b")
            price = await f.query_selector("div.FpEdX span, .U3gSDe")

            departure = await get_text(departure_time)
            arrival = await get_text(arrival_time)
            airline_raw = await get_text(airline)
            price_raw = await get_text(price)
            duration_raw = await get_text(duration)
            stops_raw = await get_text(stops)

            airline_text = extract_airline(airline_raw)
            price_disp, price_val = extract_price(price_raw)
            duration_text = re.sub(r"[A-Z]{3}–[A-Z]{3}", "", first_line(duration_raw)).strip()
            stops_text = first_line(stops_raw)

            if price_val is None or airline_text in ["", "N/A"] or airline_text.isdigit():
                continue

            flight_data.append({
                "airline": airline_text,
                "price": price_disp,
                "price_number": price_val,
                "duration": duration_text,
                "stops": stops_text,
                "departure": departure,
                "arrival": arrival
            })

        # Duplicate + sort
        seen = set()
        deduped = []
        for f in flight_data:
            key = (f["airline"], f["departure"], f["arrival"], f["price"])
            if key not in seen:
                seen.add(key)
                deduped.append(f)

        flight_data = sorted(deduped, key=lambda x: x["price_number"])
        table_text = ""

        # Output table
        if not flight_data:
            print("No priced flights found. Try scrolling or changing filters.", file=sys.stderr)
        else:
            print(f"Found {len(flight_data)} priced flights.", file=sys.stderr)
            table = Texttable(max_width=0)
            table.header(["Airline", "Price", "Duration", "Stops", "Departure", "Arrival"])
            for f in flight_data[:10]:
                table.add_row([
                    f["airline"], f["price"], f["duration"],
                    f["stops"], f["departure"], f["arrival"]
                ])
            table_text = table.draw()
            print(table_text, file=sys.stderr)

            # Save files
            with open("flight_data.json", "w", encoding="utf-8") as fjson:
                json.dump(flight_data, fjson, ensure_ascii=False, indent=4)
            with open("flight_results.txt", "w", encoding="utf-8") as ftxt:
                ftxt.write(table_text)

            print("Saved clean results to flight_results.txt and flight_data.json", file=sys.stderr)

        await browser.close()

    # Normalize text
    def normalize_spacing(text: str) -> str:
        """Add missing spaces or commas between AM/PM airport names, times, and cities for readability."""
        if not text:
            return ""
        text = re.sub(r'(?<=\d)(AM|PM)(?=\S)', r' \1 ', text)
        text = re.sub(r'(?<=\d)\s*(AM|PM)', r' \1', text)
        text = re.sub(r'(AM|PM)(?=[A-Za-z])', r'\1 ', text)

        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"(\d)([A-Z])", r"\1 \2", text)
        text = re.sub(r"([A-Z]{3})([A-Z])", r"\1 \2", text)
        text = re.sub(r"([a-z])([A-Z]{3})", r"\1 \2", text)

        text = text.replace("Airport ", "Airport, ")
        text = text.replace("min", " min")

        text = text.replace("  ", " ")
        return text.strip()

    # Clean text fields
    for f in flight_data:
        for k in ["departure", "arrival", "airline", "duration", "stops"]:
            if f.get(k):
                f[k] = (
                    f[k]
                    .encode("latin1", "ignore")
                    .decode("utf-8", "ignore")
                    .replace("â€¯", " ")
                    .replace("â€“", "-")
                    .replace("â€”", "-")
                    .replace("Â", "")
                    .replace("Ã", "")
                    .replace("\u202f", " ")
                    .replace("\xa0", " ")
                    .replace("†", "")
                    .replace("¤", "")
                    .replace("‰", "")
                    .replace("œ", "oe")
                    .replace("”", "")
                    .replace("“", "")
                    .replace("‘", "")
                    .replace("’", "")
                    .replace("�", "")
                    .strip()
                )
                f[k] = normalize_spacing(f[k])

    return flight_data, table_text


# CLI mode 
async def main():
    data, table = await scrape_flights(None, None, None)
    if not table:
        print("No results.", file=sys.stderr)
    else:
        print("Done.", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
