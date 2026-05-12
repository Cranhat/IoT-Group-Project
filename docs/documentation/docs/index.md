# IoT Group Project

Group project with main goal of creating IoT network in order to exchange information between devices safely.


## Project roles
    * Cyprian Burdzy (Cranhat) - Technical Leader
    * Nicole Jarczewska (Naitomi) - Developer
    * Natalia Kułak (Natomkul) - Developer
    * Oleh Marushchak () - Developer
    * Tomek Piaseczny () - Developer

## Technology Used
- **Communication Protocol**: HTTP (with custom security features)
- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL
- **Frontend**: Vue.js 3 (Vite)
- **Network Analysis**: Packet Sniffer (Scapy)
- **Documentation**: MkDocs with PlantUML

## Project Layout
```text
IoT-Group-Project/
├── backend/            # Python FastAPI backend & database logic
│   ├── api/            # API endpoints
│   └── database/       # Database models and CRUD logic
├── frontend/           # Vue.js frontend application
├── packet_sniffer/     # Scapy-based network monitoring tool
├── docs/               # Project documentation
│   └── documentation/  # MkDocs source and config
├── docker-compose.yml  # Container orchestration
└── README.md
```

## Documentation
- **Hosted**: GitHub Pages
- **Generator**: MkDocs
- **Plugins**: PlantUML, Search
