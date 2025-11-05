import React, { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";

function App() {
  // State variables
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [flights, setFlights] = useState([]);
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [month, setMonth] = useState("");
  const [tableFlights, setTableFlights] = useState([]);
  const [logs, setLogs] = useState("");

  // Clean markdown formatting for summary
  const tidySummary = (s) =>
    (s || "")
      .replace(/\*\*Thoughts:\*\*\s*\n+/g, '**Thoughts:**\n')
      .replace(/\n{3,}/g, '\n\n');

  // Function to trigger scraper + summarizer
  const handleSearchFlights = async () => {
    if (!origin || !destination || !month) {
      alert("Please fill in all fields before searching!");
      return;
    }

    setLoading(true);
    setSummary("");
    setFlights([]);
    setLogs("Starting search...\n");

    const timers = [];

    const schedule = (msg, delay) => {
      const id = setTimeout(() => setLogs(msg), delay);
      timers.push(id);
    };
    // Simulated progress messages
    setTimeout(() => setLogs("Launching scraper subprocess..."), 2000);
    setTimeout(() => setLogs("Opening Google Flights..."), 5000);
    setTimeout(() => setLogs("Collecting flight data..."), 9000);
    setTimeout(() => setLogs("Running Autogen + LLM summarizer..."), 13000);
    setTimeout(() => setLogs("Running Autogen + LLM summarizer..."), 13000);


    try{
      // Send scrape request to FastAPI backend
      const res = await fetch("http://127.0.0.1:8000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ origin, destination, month }),
      });

      const data = await res.json();

      // Handle API response
      if (data.status === "ok") { 
        setFlights(data.flights); 
        setTableFlights(data.table_flights || []); 
        setSummary(data.summary);
        setLogs("Flights scraped and summarized successfully!"); 
      } else { 
        setSummary(data.message || "No flights found.");
        setLogs(" No results found or an issue occurred."); 
      } 
    } catch (err) {
      timers.forEach(clearTimeout); 
      console.error(err); 
      setSummary("Error scraping flights.");
      setLogs("Error scraping flights."); 
    } finally { 
      setLoading(false); 
    } 
  };                
  
  // UI
  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>AutoFlights Smart Summarizer</h1>
      <p>Enter trip details to search for new flights.</p>

      {/* Input Form */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        <input
          type="text"
          placeholder="From (e.g., Dallas)"
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          style={{
            padding: "8px",
            borderRadius: "5px",
            border: "1px solid #ccc",
            width: "200px",
          }}
        />
        <input
          type="text"
          placeholder="To (e.g., Paris)"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          style={{
            padding: "8px",
            borderRadius: "5px",
            border: "1px solid #ccc",
            width: "200px",
          }}
        />
        <input
          type="text"
          placeholder="Month (e.g., Jan 2026)"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{
            padding: "8px",
            borderRadius: "5px",
            border: "1px solid #ccc",
            width: "200px",
          }}
        />
        <button
          onClick={handleSearchFlights}
          disabled={loading}
          style={{
            backgroundColor: "#28a745",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          {loading ? "Searching..." : "Search Flights"}
        </button>
      </div>

      {/* 🛰 Live Progress Logs */}
      {logs && (
        <div
          style={{
            marginTop: "15px",
            padding: "10px",
            backgroundColor: "#f5f5f5",
            borderRadius: "8px",
            border: "1px solid #ddd",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            color: "#333",
            textAlign: "center",
            fontWeight: "500",
          }}
        >
          {logs}
        </div>
      )}


      {/* Results Box */}
      <div
        style={{
          marginTop: "30px",
          padding: "20px",
          border: "1px solid #ccc",
          borderRadius: "10px",
          backgroundColor: "#f9f9f9",
        }}
      >
        {flights.length > 0 && (
          <>
            <h3 style={{ marginBottom: "10px" }}>Available Flights</h3>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "10px",
              }}
            >
              <thead>
                <tr style={{ background: "#eee" }}>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Airline</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Price</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Duration</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Stops</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Departure</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Arrival</th>
                </tr>
              </thead>
              <tbody>
                {flights.map((f, i) => (
                  <tr key={i}>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.airline}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.price}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.duration}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.stops}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.departure}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.arrival}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {tableFlights.length > 0 && (
          <>
            <h3 style={{ marginTop: "30px" }}> Top Cheapest Flights</h3>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "10px",
              }}
            >
              <thead>
                <tr style={{ background: "#eee" }}>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Airline</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Price</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Duration</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Stops</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Departure</th>
                  <th style={{ border: "1px solid #ccc", padding: "6px" }}>Arrival</th>
                </tr>
              </thead>
              <tbody>
                {tableFlights.map((f, i) => (
                  <tr key={i}>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.airline}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.price}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.duration}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.stops}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.departure}</td>
                    <td style={{ border: "1px solid #ddd", padding: "6px" }}>{f.arrival}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {summary && (
          <div
            style={{
              whiteSpace: "pre-wrap",
              wordWrap: "break-word",
              marginTop: "20px",
              lineHeight: "1.6",
            }}
          >
            <ReactMarkdown
              components={{
                p: ({ node, ...props }) => (
                  <p style={{ marginTop: 0, marginBottom: 0, lineHeight: "1.5" }} {...props} />
                ),
                strong: ({ node, ...props }) => (
                  <strong style={{ display: "inline", margin: 0 }} {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul style={{ marginTop: 2, marginBottom: 4, paddingLeft: 18 }} {...props} />
                ),
                li: ({ node, ...props }) => (
                  <li style={{ marginBottom: 2, lineHeight: "1.5" }} {...props} />
                ),
              }}
            >
  {tidySummary(summary)}
</ReactMarkdown>

          </div>
        )}

      </div>
    </div>
  );
}

export default App;

