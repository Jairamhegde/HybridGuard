from fastapi import FastAPI
from pydantic import BaseModel
from backend.security_insidents import generate_security_incidents
from fastapi.middleware.cors import CORSMiddleware

myapp = FastAPI()

myapp.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncidentOutput(BaseModel):
    incident_type : str
    severity : str
    description : str
    
@myapp.get("/",response_model=list[IncidentOutput])
def root_data():
    df = generate_security_incidents()
    if df is not None and not df.empty:
        incidents = []
        for _,row in df.iterrows():
            incidents.append(IncidentOutput(
                incident_type= row['incident_type'],
                severity= row['severity'],
                description= row['description']
                )
                )
        return incidents
    return []

@myapp.get('/damage_score')
def damage_score():
    df = damage_score()
    return df

@myapp.get('/dormancy_threat')
def dorman_threat_score():
    df = dorman_threat_score()
    return df




