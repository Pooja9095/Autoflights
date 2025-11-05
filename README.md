# AutoFlights- AI-Powered Flight Search and Summarizer

**Live Demo:** [AutoFlights on Hugging Face Spaces](https://huggingface.co/spaces/Pooja-Nigam/autoflights)

AutoFlights is a full-stack, end-to-end web application that scrapes live flight listings, analyzes them, and produces clear summaries with a touch of humor.
It combines an intelligent AI backend with a simple, modern React frontend, built for fast and automated travel insights.

AutoFlights automatically fetches flight details from Google Flights using Playwright and Serper API, processes the data, and summarizes the top results using a Groq LLM integrated with Autogen AI Agents.
The system is designed to demonstrate how real-world data extraction, automation, and AI summarization can work together in a single deployable project.

## Features
- **AI-Driven Summaries:** Uses Groq + Autogen to create concise, witty flight insights.
- **Backend Automation:** Playwright-based scraper runs asynchronously for live flight data.
- **Full-Stack Integration:** React frontend + FastAPI backend working seamlessly.
- **Dockerized Deployment:** Fully containerized for quick setup on any platform (including Hugging Face Spaces).
- **Flexible API Use:** Can integrate with any LLM API (Groq, OpenAI, Mistral, etc.).
- **Structured Results:** Displays both a full list of flights and a separate “Top Cheapest Flights” table.

## Tools & Libraries

### Backend (Python / FastAPI)
- **FastAPI** – API framework
- **Playwright** – browser automation for scraping
- **Autogen, Groq, LangChain** – AI summarization and reasoning
- **Pydantic, dotenv, asyncio, texttable** – data handling and formatting

### Frontend (React)
- **React + ReactMarkdown** – dynamic interface and summary rendering
- **HTML / CSS / JavaScript** – core UI
- Built with **create-react-app**

### Deployment
- **Docker** – containerization
- **Hugging Face Spaces** – live hosting and deployment
- Compatible with **Linux, macOS, and Windows** environments

## How to Use

### 1. Clone the Repository
``` bash
  git clone https://github.com/Pooja9095/Autoflights.git
  cd Autoflights
```

### 2. Set Up Backend Environment
Create and activate a virtual environment:
``` bash
  python -m venv myenv
  myenv\Scripts\activate   # on Windows
  # or
  source myenv/bin/activate  # on macOS/Linux
```
Install dependencies:
```bash
  pip install -r requirements.txt
```

### 3. Run the Backend
```bash
  uvicorn app:app --reload
```
This starts the FastAPI server locally at:
```bash
http://127.0.0.1:8000
```

### 4. Run the Frontend
Navigate to the frontend folder:
```bash
  cd frontend
  npm install
  npm start
```
Your React app will be available at:
```bash
  http://localhost:3000
```

### Notes
- The app uses Playwright Chromium in headless mode for compatibility on Hugging Face Spaces.
- You can replace the API keys for Groq or OpenAI in your .env file as needed.

### MIT License  

Copyright (c) 2025 Pooja Nigam  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.


