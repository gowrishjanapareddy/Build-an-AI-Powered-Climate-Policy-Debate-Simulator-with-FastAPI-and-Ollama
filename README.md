# Climate Policy Debate Simulator

An advanced AI-powered multi-agent simulation that facilitates structured debates on global climate policy between representatives from the **USA**, **EU**, and **China**. 

This project leverages **Retrieval-Augmented Generation (RAG)** to ensure that every argument made by the AI agents is grounded in official policy documentation, providing a realistic and informative simulation of international climate negotiations.

---

## Features

-   **Multi-Agent Orchestration**: A turn-based debate system featuring three distinct AI personas, each with unique geopolitical perspectives and constraints.
-   **RAG-Powered Arguments**: Agents dynamically retrieve relevant information from official climate policy documents stored in a **ChromaDB** vector database.
-   **Local LLM Integration**: Powered by **Ollama**, allowing for high-performance, private, and cost-effective simulation without external API dependencies.
-   **Interactive Dashboard**: A modern, responsive web interface built with FastAPI and Vanilla CSS to monitor the debate transcript in real-time.
-   **Containerized Architecture**: Fully Dockerized for seamless "one-command" setup and deployment.

---

## Technology Stack

-   **Backend**: Python, FastAPI
-   **AI Engine**: Ollama (llama3:8b)
-   **Vector Database**: ChromaDB
-   **Frontend**: HTML5, Vanilla CSS, JavaScript
-   **Infrastructure**: Docker, Docker Compose

---

## Setup & Usage

### Prerequisites

-   [Docker](https://www.docker.com/) and Docker Compose installed.
-   [Ollama](https://ollama.com/) (if running locally without Docker, though Docker is recommended).

### One-Command Startup

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```

2.  **Initialize Environment**:
    ```bash
    cp .env.example .env
    ```

3.  **Start the Application**:
    ```bash
    docker-compose up --build
    ```

### Accessing the Simulator

-   **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
-   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

> [!IMPORTANT]
> On the first run, the system will initialize the vector database by ingesting documents from `data/policies/`. This process happens automatically in the background.

---

## Project Structure

```text
├── agents/             # AI agent logic and persona definitions
├── core/               # Core services (RAG, ChromaDB integration)
├── data/policies/      # Official policy JSON documents
├── static/             # Frontend assets (HTML, CSS, JS)
├── tests/              # Automated test suite
├── Dockerfile          # API service container definition
├── docker-compose.yml  # Multi-container orchestration
└── main.py             # FastAPI entry point
```

---

## Testing

The project includes a suite of automated tests to verify API functionality and agent behavior.

```bash
# Run tests inside the container
docker-compose exec api pytest tests/
```
