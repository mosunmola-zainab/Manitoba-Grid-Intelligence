# Manitoba Grid Intelligence

Real-time power grid analytics platform for Manitoba's electrical infrastructure.

## Vision

Manitoba Grid Intelligence is a data engineering platform designed to ingest, process, and analyze power grid data in real-time. The platform provides insights into:

- **Power Generation**: Monitor hydroelectric, wind, and solar generation across Manitoba Hydro facilities
- **Grid Demand**: Track electricity consumption patterns across regions
- **Predictive Analytics**: Forecast demand based on weather, time-of-day, and historical patterns
- **Anomaly Detection**: Identify unusual patterns that may indicate equipment issues or grid instability
- **Carbon Tracking**: Monitor emissions and support Manitoba's clean energy initiatives

## Architecture

```
[Data Sources] -> [Kafka] -> [Stream Processing] -> [TimescaleDB] -> [Analytics/BI]
                     |
              [Airflow DAGs]
                     |
              [Batch Processing]
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Message Broker | Apache Kafka | Real-time data streaming |
| Time-Series DB | TimescaleDB | Sensor data storage |
| Orchestration | Apache Airflow | Workflow management |
| Transformations | dbt | Data modeling |
| Infrastructure | Terraform | IaC for cloud deployment |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Make (optional)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd manitoba-grid-intelligence
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - Airflow UI: http://localhost:8081 (admin/admin)
   - Adminer: http://localhost:8080
   - Kafka: localhost:9094

## Project Structure

```
manitoba-grid-intelligence/
├── dags/                 # Airflow DAG definitions
├── docker/               # Dockerfiles and init scripts
├── src/
│   ├── ingestion/        # Data extraction scripts
│   ├── simulation/       # Sensor data simulator
│   ├── processing/       # Stream processing logic
│   └── models/           # dbt models
├── tests/                # Unit and integration tests
├── terraform/            # Infrastructure as Code
├── config/               # Configuration files
└── docs/                 # Documentation
```

## Data Sources

The platform is designed to integrate with:

- Manitoba Hydro open data APIs
- Environment Canada weather data
- Simulated sensor feeds for development
- SCADA system exports

## Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## License

MIT License
