# NeuroGraph AI Assistant

The **NeuroGraph AI Assistant** is a comprehensive platform designed for advanced graph processing, neural pattern mining, and interactive knowledge graph exploration. It integrates multiple specialized services to transform raw data into actionable insights through a unified pipeline.

## System Architecture

The system is composed of:

*   **Integration Service**: The central orchestrator that manages workflows, streams data between services, and provides a unified REST API for the frontend.
*   **Custom AtomSpace Builder**: A powerful graph processing engine that ingests CSV/JSON data and transforms it into NetworkX graphs, MeTTa formats, or Neo4j databases.
*   **Neural Subgraph Miner**: A specialized mining engine that uses neural search strategies (Greedy, MCTS) to discover frequent patterns and motifs within the generated graphs.
*   **Annotation Tool (Frontend)**: A modern, interactive React/Remix web interface for uploading data, visualizing Knowledge Graphs (KG), running mining jobs, and exploring results.
*   **Annotation Query Backend**: A supporting backend service that handles graph queries and history management for the visualization tool.

## Features

### Core Capabilities
*   **End-to-End Pipeline**: A seamless workflow from raw CSV upload to visualized graph patterns.
*   **Neural Mining**: Advanced subgraph mining using neural networks to guide the search for significant motifs.
*   **Interactive Visualization**: Explore your Knowledge Graph (KG) with an interactive, node-link diagram interface.
*   **Multi-Format Support**: Generate outputs in NetworkX, MeTTa, and Neo4j formats.
*   **Job Management**: Track and manage your data ingestion and mining jobs with persistent history.

### Frontend Experience
*   **Data Import**: Easy-to-use drag-and-drop interface for uploading CSV nodes and edges.
*   **Graph Exploration**: Visualizers for graph schema, top entities, and connectivity stats.
*   **Mining Configuration**: Fine-grained control over mining parameters (Pattern Size, Search Strategy, Sampling Method).
*   **Results Dashboard**: Downloadable reports and visualized mining outcomes.

## Installation & Setup

### 1. Clone the Repository

Clone the repository and ensure all submodules are initialized.

```bash
git clone https://github.com/Samrawitgebremaryam/NeuroGraph-AI-Assistant.git
cd NeuroGraph-AI-Assistant

# Initialize and update submodules
git submodule update --init --recursive
```

### 2. Configuration (`.env`)

The project uses a root-level `.env` file to configure the services.

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Edit `.env` and configure the necessary variables:
    ```bash

    # Service Ports (defaults)
    INTEGRATION_PORT=9000
    ANNOTATION_GUI_PORT=3000
    ANNOTATION_API_PORT=8001
    ATOMSPACE_PORT=8000
    
    # Neo4j Settings
    NEO4J_PASSWORD=change_to_your_own_password
    ```

### 3. Frontend Configuration

The Annotation Tool (frontend) requires its own environment configuration to talk to the backend services.

1.  Navigate to the annotation tool directory:
    ```bash
    cd submodules/annotation-tool
    ```

2.  Create the `.env` file:
    ```bash
    cp .env.example .env
    ```

3.  Ensure the URLs match your Docker service ports (usually default is fine):
    ```env
    API_URL=http://localhost:8000
    INTEGRATION_URL=http://localhost:9000
    ANNOTATION_URL=http://localhost:8001
    ```

### 4. Build and Run

Return to the root directory and start the entire system using Docker Compose.

```bash
cd ../..  # Go back to root
docker-compose up --build -d
```
frontend
```bash
cd submodules/annotation-tool
npm install
npm run dev
```

*Note: The first build may take some time as it compiles the frontend and builds the backend images.*

## Usage

### Accessing the Application

Once all services are up (check with `docker-compose ps`), access the web interface:

*   **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
    *   Navigate here to start importing data and running mining jobs.

### Typical Workflow

1.  **Import Data**:
    *   Go to the **Import** page.
    *   Upload your Nodes CSV and Edges CSV.
    *   Submit to generate the graph.
2.  **View Statistics**:
    *   Once generated, you'll see a dashboard with Graph Statistics (Node counts, Edge counts, Schema).
    *   **Copy the Job ID** from the success card.
3.  **Mine Patterns**:
    *   Go to the **Mine** page.
    *   Paste the Job ID.
    *   Configure mining parameters (e.g., Min Pattern Size=3, Strategy=Greedy).
    *   Click "Start Mining".
4.  **Analyze Results**:
    *   Download the results ZIP file containing the mined patterns and instances.

## Service Endpoints

*   **Integration API**: [http://localhost:9000/docs](http://localhost:9000/docs) (Swagger UI)
*   **AtomSpace Builder API**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Annotation Backend**: [http://localhost:8001](http://localhost:8001)
*   **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (User: `neo4j`, Pass: `atomspace123`)

## Troubleshooting

### Common Issues

*   **"Frontend cannot connect to backend"**: Ensure you created the `.env` file in `submodules/annotation-tool` and that the URLs point to the correct ports exposed by Docker.
*   **"Container exited with code 1"**: Check logs using `dockerlogs <container_name>`.
*   **"Submodule not found"**: Run `git submodule update --init --recursive` again.

### Useful Commands

```bash
# View logs for all services
docker-compose logs -f

# Restart a specific service
docker-compose restart integration-service

# Rebuild a specific service
docker-compose up -d --build --no-deps annotation-frontend
```

## detailed System Flow

![System Flow Diagram](./docs/system_flow.png)

*(Note: Ensure you have the `docs/system_flow.png` file or update this path to your actual diagram)*

## License

[MIT License](LICENSE)
