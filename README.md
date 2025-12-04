# NeuroGraph AI Assistant - Complete Setup & Usage Guide

## Project Overview

The NeuroGraph AI Assistant is a **two-step pipeline** for discovering patterns and motifs in graph data:

1. **Step 1: Generate Graph** - Upload CSV files and generate a NetworkX graph (returns `job_id`)
2. **Step 2: Mine Patterns** - Use the `job_id` to discover patterns with custom configuration

### System Components

- **Custom AtomSpace Builder**: Converts CSV data into NetworkX graphs (directed or undirected)
- **Neural Subgraph Miner**: Discovers motifs and patterns using configurable mining algorithms
- **Integration Service**: Orchestrates the workflow and provides REST APIs (Port 9000)

### How It Works

```
User → Upload CSV → Generate Graph → Get job_id → Mine Patterns → Get Results
         (Step 1)                        ↓           (Step 2)
                                    Save job_id!
```

---

##  Project Structure

```
NeuroGraph-AI-Assistant/
├── .gitmodules                          # Git submodule configuration
├── docker-compose.yml                   # Integration service orchestration
├── .env                                 # Environment variables
├── integration_service/                 # Main orchestration service
│   ├── main.py                          # FastAPI application entry
│   ├── config/settings.py               # Configuration management
│   ├── api/pipeline.py                  # API endpoints
│   ├── services/                        # Business logic
│   │   ├── orchestration_service.py     # Pipeline coordinator
│   │   └── miner_service.py             # Neural miner client
│   └── output/                          # Local output directory
│       └── {job_id}/
│           ├── results/
│           │   ├── patterns.json        # Discovered patterns
│           │   └── patterns.pkl
│           └── plots/
│               └── cluster/             # Pattern visualizations
└── submodules/
    ├── custom-atomspace-builder/        # Graph generation service
    │   └── output/                      # Shared volume
    │       └── {job_id}/
    │           ├── networkx_graph.pkl
    │           └── networkx_metadata.json  # Contains graph_type
    └── neural-subgraph-matcher-miner/   # Motif discovery service
```

---

##  Complete Setup Instructions

### Step 1: Clone Repository with Submodules

```bash
# Clone the main repository
git clone https://github.com/NeuroGraph-AI-Assistant.git
cd NeuroGraph-AI-Assistant

# Initialize and update submodules
git submodule update --init --recursive
```

### Step 2: Set up Custom AtomSpace Builder

```bash
# Navigate to the Custom AtomSpace Builder
cd submodules/custom-atomspace-builder

# Copy environment configuration
cp example.env .env

# Build and start all services (development mode)
make build-dev
make up-dev

# Verify services are running
make logs-dev
```

**Expected Output:** You should see three services starting:
- `atomspace-api-dev` on port 8000
- `neo4j` on ports 7474/7687
- `hugegraph` on ports 8080/8182

### Step 3: Set up Neural Subgraph Miner

```bash
# Navigate to Neural Miner
cd ../neural-subgraph-matcher-miner

# Build the Docker image
docker build -t neural-miner:latest .

# Verify the image was built
docker images | grep neural-miner
```

### Step 4: Configure Integration Service

```bash
# Navigate back to project root
cd ../..

# Verify docker-compose.yml has correct environment variables
cat docker-compose.yml
```

**Important Environment Settings** (in docker-compose.yml):

```yaml
environment:
  - API_PORT=9000
  - ATOMSPACE_API_URL=http://atomspace-api-dev:8000
  - NEURAL_MINER_URL=http://neural-miner:5000
  - ATOMSPACE_TIMEOUT=600
  - MINER_TIMEOUT=1800
```

### Step 5: Start Integration Service

```bash
# Build and start the integration service
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f integration-service
```

**Expected Output:**
```
NAME                                          STATUS
neurograph-ai-assistant-integration-service   Up
neurograph-ai-assistant-neural-miner          Up
custom-atomspace-builder-atomspace-api-dev-1  Up
custom-atomspace-builder-neo4j-1              Up
custom-atomspace-builder-hugegraph-1          Up
```

---

##  Verification & Testing

### Health Checks

```bash
# Check Integration Service (Port 9000)
curl http://localhost:9000/health

# Check Custom AtomSpace Builder (Port 8000)
curl http://localhost:8000/api/health
# Expected outputs:
# {"status": "healthy", "service": "integration-service"}
# {"status": "healthy"}
```

---

##  API Endpoints

**Base URL:** `http://localhost:9000`

### 1️ Generate NetworkX Graph

**Endpoint:** `POST /api/generate-graph`

**Purpose:** Upload CSV files and generate a NetworkX graph. Returns a `job_id` for use in Step 2.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `files` | File[] |  Yes | - | CSV files (nodes and edges) |
| `config` | JSON String |  Yes | - | Graph configuration |
| `schema_json` | JSON String |  Yes | - | Schema definition |
| `writer_type` | String |  No | `networkx` | Writer type (networkx, metta, neo4j) |
| `graph_type` | String |  No | `directed` | **Graph type: `directed` or `undirected`** |

**Example:**

```bash
curl -X POST "http://localhost:9000/api/generate-graph" -F "files=@data.csv" -F "files=@edges.csv" -F "config=$(cat config.json)" -F "schema_json=$(cat schema.json)" -F "writer_type=networkx" -F "graph_type=undirected"
```

**Response:**

```json
{
  "job_id": "abc-123-def-456",
  "status": "success",
  "networkx_file": "/shared/output/abc-123-def-456/networkx_graph.pkl"
}
```

** Save the `job_id` - you'll need it for Step 2!**

---

### 2️ Mine Patterns

**Endpoint:** `POST /api/mine-patterns`

**Purpose:** Discover patterns in a previously generated graph using the `job_id` from Step 1. The `graph_type` is automatically detected from metadata!

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `job_id` | String |  Yes | - | **Job ID from Step 1** |
| `min_pattern_size` | Integer |  No | `5` | Minimum pattern size (nodes) |
| `max_pattern_size` | Integer |  No | `10` | Maximum pattern size (nodes) |
| `min_neighborhood_size` | Integer |  No | `5` | Minimum neighborhood size |
| `max_neighborhood_size` | Integer |  No | `10` | Maximum neighborhood size |
| `n_neighborhoods` | Integer | No | `2000` | Number of neighborhoods to sample |
| `n_trials` | Integer |  No | `100` | Number of search trials |
| `graph_type` | String |  No | `auto` | **Auto-detected from metadata** (can override) |
| `search_strategy` | String |  No | `greedy` | Search strategy (greedy, mcts) |
| `sample_method` | String | No | `tree` | Sampling method (tree, radial) |

**Example (Minimal - uses defaults):**

```bash
curl -X POST "http://localhost:9000/api/mine-patterns" -F "job_id=abc-123-def-456"
```

**Example (Custom Configuration):**

```bash
curl -X POST "http://localhost:9000/api/mine-patterns" -F "job_id=abc-123-def-456" -F "min_pattern_size=3" -F "max_pattern_size=8" -F "n_neighborhoods=1000" -F "n_trials=50" -F "search_strategy=greedy"
```

**Response:**

```json
{
  "job_id": "abc-123-def-456",
  "status": "success",
  "output_paths": {
    "results": "./integration_service/output/abc-123-def-456/results",
    "plots": "./integration_service/output/abc-123-def-456/plots"
  }
}
```

---

##  Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f integration-service
docker-compose logs -f neural-miner

# AtomSpace Builder
cd submodules/custom-atomspace-builder
make logs-dev
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart integration-service

# Restart AtomSpace Builder
cd submodules/custom-atomspace-builder
make down-dev
make up-dev
```

### Stop Services

```bash
# Stop Integration Service and Neural Miner
docker-compose down

# Stop AtomSpace Builder
cd submodules/custom-atomspace-builder
make down-dev
```

### Rebuild After Code Changes

```bash
# Rebuild Integration Service
docker-compose build integration-service
docker-compose up -d integration-service

# Rebuild Neural Miner
docker-compose build neural-miner
docker-compose up -d neural-miner

# Rebuild all
docker-compose build
docker-compose up -d
```

---

##  Output Structure

After successful pipeline execution, results are organized as:

```
./integration_service/output/{job_id}/
├── results/
│   ├── patterns.json          # Discovered patterns (JSON format)
│   └── patterns.pkl            # Discovered patterns (Pickle format)
└── plots/
    └── cluster/
        ├── pattern_1.png       # Pattern visualization (PNG)
        ├── pattern_1.pdf       # Pattern visualization (PDF)
        └── pattern_1.html      # Interactive visualization (HTML)
```

**Shared Volume (contains metadata):**

```
/shared/output/{job_id}/
├── networkx_graph.pkl          # Generated NetworkX graph
├── networkx_metadata.json      # Graph metadata (includes graph_type)
├── results/
└── plots/
```

---

##  Complete Workflow

1. **User uploads CSV files** (nodes and edges) → **Step 1**
2. **Integration Service** forwards to **AtomSpace Builder**
3. **AtomSpace Builder** generates NetworkX graph with specified `graph_type`
4. **System returns `job_id`** → User saves it
5. **User submits `job_id` + mining config** → **Step 2**
6. **Integration Service** reads `graph_type` from metadata (auto-detection)
7. **Neural Miner** discovers patterns using the correct graph type
8. **Integration Service** copies results to local directory
9. **User accesses results** at `./integration_service/output/{job_id}/`

---

##  Key Points

- **Port 9000**: Integration Service (your main API)
- **Port 8000**: AtomSpace Builder (internal)
- **Port 5000**: Neural Miner (internal)

- **Step 1**: Upload CSV → Get `job_id`
- **Step 2**: Use `job_id` + mining config → Get results

- **Graph Type**: Specified in Step 1, auto-detected in Step 2!

---
