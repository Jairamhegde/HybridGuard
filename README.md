### HybridGuard System Architecture

```mermaid
graph TD
    %% 1. Data Generation
    subgraph "1. Telemetry Simulation"
        Faker[Faker Python Script] -->|Generates| HR[HR Records CSV]
        Faker -->|Generates| Plat[Platform Identity CSV]
        Faker -->|Generates| Roles[Role Mappings CSV]
    end

    %% 2. Ingestion & Storage
    subgraph "2. Core Engine & Storage"
        HR --> ETL[ETL Pipeline / normalizer.py]
        Plat --> ETL
        Roles --> ETL
        ETL -->|Ingests & Links| DB[(SQLite: hybridguard.db)]
    end

    %% 3. Analytics Engine
    subgraph "3. Threat Detection Analytics"
        DB -->|Cross-Platform SQL Joins| Engine[Detection Engine]
        Engine -->|Detects Ghost Accounts| Incidents[Security Incidents Table]
        Engine -->|Detects Privilege Creep| Incidents
        Engine -->|Detects Stale Tokens| Incidents
    end

    %% 4. User Interface & Remediation Loop
    subgraph "4. Interactive Dashboard"
        Incidents -->|Loads Data| UI[Streamlit UI]
        UI -->|Analyst Clicks 'Revoke'| Router[handle_remediation()]
        Router -.->|Executes targeted SQL DELETE/UPDATE| DB
    end

    %% Professional Styling
    classDef default fill:#ffffff,stroke:#333,stroke-width:1px,color:#000;
    classDef database fill:#e1ecf4,stroke:#3973ac,stroke-width:2px,color:#000;
    classDef frontend fill:#e8f4e8,stroke:#4d994d,stroke-width:2px,color:#000;
    
    class DB database;
    class UI frontend;


Live demo : https://hybridguard-console.streamlit.app/


