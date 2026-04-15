# IoT-Group-Project

### Requirements
- Python 3.10+
- Node.js 18+ (with npm)
- PostgreSQL database

### Create a virtual environment && install needed tools (bash):
cd backend/database
python -m venv venv

    Windows:    venv\Scripts\activate
    Linux:      source venv/bin/activate

pip install fastapi uvicorn psycopg2-binary

### Create a database connection:
python backend/main.py

### Run Vue server:
cd frontend
npm install
npm run dev