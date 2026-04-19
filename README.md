# 🌍 Autonomous Supply Chain & Logistics Triage (ASCLT)

[](https://www.google.com/search?q=%23)
[](https://www.google.com/search?q=%23)
[](https://www.google.com/search?q=%23)
[](https://www.google.com/search?q=%23)

> **Global logistics are chaotic. When a port strike happens or a Category 5 hurricane hits, companies lose millions while scrambling to locate and reroute shipments.**
>
> ASCLT is an enterprise-grade microservices architecture that solves this. It continuously ingests global event telemetry, cross-references it against active fleet coordinates, and uses Agentic AI to autonomously draft dynamic, cost-optimized contingency plans before a human even knows there's a problem.

-----

## ⚡ The "Wow" Factor: How It Works

1.  **The World Breaks:** A typhoon forms in the Pacific. The **Monitoring Agent** (Python/AI) detects this via global weather APIs and draws a "Geospatial Threat Matrix" around the affected coordinates.
2.  **The Fleet is Warned:** The **Node.js Engine** is constantly simulating fleet movement. It pings the Python service with current coordinates.
3.  **The Alarm Sounds:** The Python service detects a collision course. Node.js instantly fires a WebSocket event to the **React Frontend**, flashing the compromised cargo ship red on the live map.
4.  **Agentic Triage:** The **Routing Agent** evaluates the cargo's value, current fuel, and alternative ports. It generates three rerouting options with calculated time delays and cost impacts.
5.  **Human in the Loop:** The logistics manager clicks the flashing ship, reviews the AI's proposed routes in the side-panel, clicks "Execute," and the ship autonomously changes its trajectory on the map.

-----

## 🏗 System Architecture & Data Flow

This project strictly separates heavy AI inference from high-speed, real-time data streaming.

```mermaid
graph TD
    %% External Data
    NewsAPI[Global News/Weather APIs] -->|Polls Data| MonitoringAgent

    %% The Brain (FastAPI)
    subgraph The Brain (Python / FastAPI)
        MonitoringAgent[Monitoring Agent / LLM] -->|Defines| ThreatZones[(Threat Zones)]
        RoutingAgent[Routing Agent / LLM] -->|Calculates| TriagePlans[Triage Mitigations]
        ThreatZones --- RoutingAgent
    end

    %% The Face (Node.js)
    subgraph The Face (Node.js / Express)
        Cron[Live Movement Cron] -->|Updates Lat/Lng| DB[(PostgreSQL Fleet DB)]
        DB -->|Shipment Context| RiskEngine[Risk Assessment Engine]
    end

    %% The UI (React)
    subgraph The UI (React)
        Map[Interactive Mapbox/Google Map]
        SidePanel[AI Resolution Dashboard]
    end

    %% Cross-Service Connections
    RiskEngine -->|POST /analyze-risk| ThreatZones
    ThreatZones -->|Risk Detected = TRUE| RiskEngine
    RiskEngine -->|WebSocket Alert| Map
    
    Map -->|User Requests Fix| RiskEngine
    RiskEngine -->|POST /generate-triage| RoutingAgent
    RoutingAgent -->|Returns Costs & Routes| SidePanel
```

-----

## 🧠 Core Components Detailed

### 1\. "The Brain" (AI Microservice)

Built with **Python and FastAPI**, this service is the cognitive engine of the operation.

  * **Monitoring Agent:** Uses LLMs (via Groq/OpenAI) to read unstructured news reports ("Workers walking out at Port of LA") and convert them into structured JSON threat data (Severity, Radius, Lat/Lng).
  * **Routing Agent:** Evaluates disrupted shipments. It processes hard constraints (e.g., "$250k of electronics cannot be delayed by more than 4 days") and spits out alternative logistics routes, complete with a confidence score and estimated financial impact.

### 2\. "The Face" (Real-Time Operations)

Built with **Node.js, Express, and React**, this is the nervous system and the dashboard.

  * **Telemetry Simulator:** A Node.js background process that steadily updates the coordinates of seeded shipments in the PostgreSQL database, pushing updates to the UI via **Socket.io**.
  * **Geospatial Map UI:** A dark-mode, high-performance React map. It renders the active fleet, paints red radiuses over active threat zones, and houses the interactive AI Triage panel.

-----

## 🚀 Quick Start (Zero-Config Docker)

The entire enterprise stack is containerized. No need to mess with local Python environments or Node modules.

### Prerequisites

  * [Docker Desktop](https://www.google.com/search?q=https://www.docker.com/products/docker-desktop/) installed.
  * An API Key for your LLM provider (Groq/OpenAI) and a Weather API.

### 1\. Clone & Configure

```bash
git clone https://github.com/YourUsername/autonomous-supply-chain.git
cd autonomous-supply-chain
```

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgres://user:password@your-db-host:5432/dbname

# AI & External APIs
GROQ_API_KEY=your_llm_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Internal Docker Routing
FASTAPI_URL=http://brain-api:8000
```

### 2\. Launch the Fleet

Spin up the Database, the Python AI Agent, the Node Server, and the React UI with one command:

```bash
docker-compose up --build
```

### 3\. Command Center

  * **Live Fleet Map (React):** `http://localhost:80`
  * **Node API Health:** `http://localhost:3000/health`
  * **AI Agent Swagger Docs:** `http://localhost:8000/docs`

-----

## 🛣 Roadmap & Milestones

  - [x] **Phase 1:** Infrastructure foundation, Dockerization, and mock database seeding.
  - [x] **Phase 2:** Node.js WebSockets streaming live coordinates to the React Map.
  - [ ] **Phase 3:** Python Monitoring Agent successfully parsing live API data into threat zones.
  - [ ] **Phase 4:** End-to-end Agentic Triage (Node detects risk -\> Python creates routes -\> React displays them).
  - [ ] **Phase 5:** "Execute Route" functionality that updates the database and alters map trajectory.
  - [ ] **Phase 6 (Stretch):** Multi-agent negotiation (e.g., AI drafting an email to a trucking company to secure the new route).

-----

*Built by Mohamed Elguindy and Ali Mostafa to demonstrate real-world, enterprise applications of Agentic AI and microservices.*
