# Manitoba Grid Intelligence

Real-time power grid analytics platform for Manitoba's electrical infrastructure.

---

## Vision

Manitoba Grid Intelligence is a data engineering platform designed to ingest, process, and analyze power grid data in real-time. The platform provides insights into:

- **Power Generation**: Monitor hydroelectric, wind, and solar generation across Manitoba Hydro facilities
- **Grid Demand**: Track electricity consumption patterns across regions
- **Predictive Analytics**: Forecast demand based on weather, time-of-day, and historical patterns
- **Anomaly Detection**: Identify unusual patterns that may indicate equipment issues or grid instability
- **Carbon Tracking**: Monitor emissions and support Manitoba's clean energy initiatives

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA SOURCES                                         │
├───────────────────────────────┬─────────────────────────┬───────────────────────────────┤
│          REAL-TIME            │        HISTORICAL       │            MARKET             │
│  ┌─────────────────────────┐  │  ┌───────────────────┐  │  ┌─────────────────────────┐  │
│  │  SCADA Sensors          │  │  │  Weather Archives │  │  │  MISO LMP Prices        │  │
│  │  Grid Frequency (60Hz)  │  │  │  Outage Records   │  │  │  Demand Forecasts       │  │
│  │  Transformer Readings   │  │  │  Maintenance Logs │  │  │  Generation Mix         │  │
│  │  Line Temperatures      │  │  │  Asset Registry   │  │  │  Interchange Schedules  │  │
│  │  Breaker States         │  │  │  GIS Data         │  │  │  Ancillary Services     │  │
│  └───────────┬─────────────┘  │  └─────────┬─────────┘  │  └───────────┬─────────────┘  │
│              │                │            │            │              │                │
└──────────────┼────────────────┴────────────┼────────────┴──────────────┼────────────────┘
               │                             │                           │
               ▼                             ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   STREAMING LAYER                                        │
│                                   Apache Kafka                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ sensor.readings  │  │  grid.frequency  │  │  market.prices   │  │  grid.alerts     │ │
│  │   6 partitions   │  │   3 partitions   │  │   3 partitions   │  │   1 partition    │ │
│  │   7-day retain   │  │   7-day retain   │  │   30-day retain  │  │   90-day retain  │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
│           │                     │                     │                     │           │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┼───────────┘
            │                     │                     │                     │
            └─────────────────────┴──────────┬──────────┴─────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PROCESSING & STORAGE                                        │
├─────────────────────────┬─────────────────────────┬─────────────────────────────────────┤
│     STREAM PROCESSING   │    BATCH PROCESSING     │              STORAGE                │
│  ┌───────────────────┐  │  ┌───────────────────┐  │  ┌───────────────────────────────┐  │
│  │  Faust / Kafka    │  │  │  Airflow DAGs     │  │  │        TimescaleDB            │  │
│  │  Streams          │  │  │                   │  │  │  ┌─────────────────────────┐  │  │
│  │                   │  │  │  ┌─────────────┐  │  │  │  │  BRONZE (raw)           │  │  │
│  │  • Windowed Aggs  │  │  │  │ Ingestion   │  │  │  │  │  sensor_readings        │  │  │
│  │  • Anomaly Detect │  │  │  │ Quality     │  │  │  │  │  market_prices          │  │  │
│  │  • Event Triggers │  │  │  │ Transform   │  │  │  │  └─────────────────────────┘  │  │
│  │                   │  │  │  └─────────────┘  │  │  │  ┌─────────────────────────┐  │  │
│  └─────────┬─────────┘  │  │                   │  │  │  │  SILVER (cleaned)       │  │  │
│            │            │  │  ┌─────────────┐  │  │  │  │  validated_readings     │  │  │
│            │            │  │  │ dbt Models  │  │  │  │  │  interpolated_gaps      │  │  │
│            │            │  │  │             │──┼──┼──│  └─────────────────────────┘  │  │
│            │            │  │  │ staging     │  │  │  │  ┌─────────────────────────┐  │  │
│            │            │  │  │ marts       │  │  │  │  │  GOLD (aggregated)      │  │  │
│            │            │  │  │ metrics     │  │  │  │  │  hourly_station_stats   │  │  │
│            │            │  │  └─────────────┘  │  │  │  │  equipment_health       │  │  │
│            │            │  │                   │  │  │  │  demand_forecasts       │  │  │
│            │            │  └───────────────────┘  │  │  └─────────────────────────┘  │  │
│            │            │                         │  │                               │  │
└────────────┼────────────┴─────────────────────────┴──┴───────────────────────────────┴──┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 INTELLIGENCE LAYER                                       │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────┐ │
│  │ Demand Forecasting│  │ Equipment Health  │  │ Anomaly Detection │  │    Price      │ │
│  │                   │  │    Scoring        │  │                   │  │  Optimizer    │ │
│  │  • XGBoost        │  │                   │  │  • Isolation      │  │               │ │
│  │  • Prophet        │  │  • Transformer    │  │    Forest         │  │  • MISO LMP   │ │
│  │  • LSTM           │  │    Health Index   │  │  • Statistical    │  │    Forecast   │ │
│  │                   │  │  • Remaining      │  │    Process Ctrl   │  │  • Marginal   │ │
│  │  Horizons:        │  │    Useful Life    │  │  • Pattern        │  │    Cost Calc  │ │
│  │  15min, 1h, 24h,  │  │  • Failure Prob   │  │    Recognition    │  │  • Buy/Sell   │ │
│  │  7-day            │  │                   │  │                   │  │    Signals    │ │
│  └─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘  └───────┬───────┘ │
│            │                      │                      │                    │         │
└────────────┼──────────────────────┼──────────────────────┼────────────────────┼─────────┘
             │                      │                      │                    │
             └──────────────────────┴───────────┬──────────┴────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SERVING LAYER                                          │
│  ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │              DASHBOARD                   │  │             REST API                │   │
│  │                                          │  │                                     │   │
│  │  • Real-time grid status                 │  │  GET  /api/v1/demand/forecast       │   │
│  │  • Equipment health heatmaps             │  │  GET  /api/v1/equipment/{id}/health │   │
│  │  • Demand vs. generation curves          │  │  GET  /api/v1/prices/current        │   │
│  │  • Anomaly alerts                        │  │  GET  /api/v1/carbon/intensity      │   │
│  │  • Price optimization recommendations    │  │  POST /api/v1/alerts/subscribe      │   │
│  │                                          │  │  WS   /ws/v1/stream                 │   │
│  └─────────────────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INFRASTRUCTURE                                         │
│                                                                                           │
│   Docker Compose    │    Terraform (AWS)    │    GitHub Actions    │    Observability    │
│   ──────────────    │    ───────────────    │    ──────────────    │    ────────────     │
│   Local Dev         │    EKS / RDS          │    CI/CD Pipeline    │    Prometheus       │
│   Integration       │    MSK / S3           │    Testing           │    Grafana          │
│   Testing           │    CloudWatch         │    Deployment        │    Alertmanager     │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Message Broker | Apache Kafka | Real-time data streaming |
| Time-Series DB | TimescaleDB | Sensor data storage with hypertables |
| Orchestration | Apache Airflow | Workflow management and scheduling |
| Transformations | dbt | Data modeling and documentation |
| Stream Processing | Faust | Python-native stream processing |
| Infrastructure | Terraform | IaC for cloud deployment |
| Monitoring | Prometheus + Grafana | Metrics and alerting |

---

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

5. Run the sensor simulator:
   ```bash
   python -m src.simulation.sensor_simulator
   ```

---

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

---

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

---

## License

MIT License
