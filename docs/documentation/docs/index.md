# IoT Group Project
Group project with main goal of creating IoT network in order to exchange information between devices safely.


## Project roles
    * Cyprian Burdzy (Cranhat) - Technical Leader
    * Nicole Jarczewska (Naitomi) - Developer
    * Natalia Kułak (Natomkul) - Developer
    * Oleh Marushchak (Ol3hhh) - Developer
    * Tomek Piaseczny (tpiasek) - Developer

## Technology Used
- **Backend**: Python (FastAPI)
- **Communication**: TCP with TLS (Transport Layer Security)
- **Database**: PostgreSQL
- **Frontend**: Vue.js 3 (Vite)
- **Network Analysis**: Packet Sniffer (Scapy)
- **Documentation**: MkDocs with PlantUML
- **Containerization**: Docker


## Documentation
- **Hosted**: GitHub Pages
- **Generator**: MkDocs
- **Plugins**: PlantUML, Search

## Project Layout
```text
IoT-Group-Project/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── backend/                    # Python FastAPI backend and database logic
│   ├── api/                    # API application code
│   ├── database/               # Database source code and tests
│   ├── Dockerfile              # Backend container image definition
│   ├── main.py                 # Backend entry point
│   └── requirements.txt        # Backend Python dependencies
├── client/                     # Client-side communication component
├── communication/
│   └── keys/                   # TLS keys and certificates used for communication
├── docs/
│   └── documentation/
│       ├── docs/               # MkDocs documentation pages
│       ├── hooks/              # Documentation build hooks
│       └── mkdocs.yml          # MkDocs configuration
├── frontend/                   # Vue.js 3 frontend application
│   ├── public/                 # Static frontend assets
│   ├── src/                    # Frontend source code
│   ├── Dockerfile              # Frontend container image definition
│   ├── package.json            # Frontend dependencies and scripts
│   └── vite.config.js          # Vite configuration
├── packet_sniffer/             # Scapy-based network monitoring tool
│   ├── tests/                  # Packet sniffer tests
│   ├── Dockerfile              # Packet sniffer container image definition
│   ├── main.py                 # Packet sniffer entry point
│   └── requirements.txt        # Packet sniffer Python dependencies
├── .env.example                # Example environment configuration
├── docker-compose.yaml         # Container orchestration
└── README.md                   # Project overview
```
