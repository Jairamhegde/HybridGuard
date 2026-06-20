from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.db_connection import connect_db

myapp = FastAPI()

# Enable CORS for standard local development ports
myapp.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncidentOutput(BaseModel):
    id: int
    user_id: str
    full_name: str
    incident_type: str
    severity: str
    platform: str
    description: str
    detected_at: str

@myapp.get("/", response_model=list[IncidentOutput])
def root_data():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Try querying the incidents table. If it doesn't exist yet, return an empty list.
    try:
        cursor.execute("""
            SELECT id, user_id, full_name, incident_type, severity, platform, description, detected_at 
            FROM security_incidents 
            ORDER BY id ASC;
        """)
        rows = cursor.fetchall()
    except Exception:
        rows = []
        
    conn.close()

    incidents = []
    for r in rows:
        incidents.append(IncidentOutput(
            id=r[0],
            user_id=r[1],
            full_name=r[2],
            incident_type=r[3],
            severity=r[4],
            platform=r[5],
            description=r[6],
            detected_at=str(r[7])
        ))
    return incidents
