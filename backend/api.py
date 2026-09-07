from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

from backend.security_insidents import (
    generate_security_incidents,
    damage_score,
    dormancy_threat,
    calculate_risk_score,
    disable_hr_status,
    revoke_account_access,
    rotate_account_token,
    revoke_account_tier,
    generate_executive_report
)

app = FastAPI(title="HybridGuard API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_dict(data: dict) -> dict:
    cleaned = {}
    for k, v in data.items():
        if pd.isna(v) or v is None:
            cleaned[k] = None
        elif isinstance(v, (np.int64, np.int32)):
            cleaned[k] = int(v)
        elif isinstance(v, (np.float64, np.float32)):
            cleaned[k] = float(v)
        else:
            cleaned[k] = v
    return cleaned

def df_to_clean_dicts(df: pd.DataFrame) -> List[dict]:
    if df is None or df.empty:
        return []
    records = df.to_dict(orient="records")
    return [clean_dict(r) for r in records]

# Request Schemas for Remediation
class DisableStatusRequest(BaseModel):
    identity_id: int

class RevokeAccessRequest(BaseModel):
    identity_id: int
    platform: str
    incident_type: Optional[str] = None

class RotateTokenRequest(BaseModel):
    identity_id: int
    platform: str

class RevokeTierRequest(BaseModel):
    identity_id: int
    platform: str
    elevated_tier: str

@app.get("/api/overview")
def get_overview_data():
    incidents_raw, prevelage_df, ghost_acc, stale_token = generate_security_incidents()
    damage_df = damage_score()
    dormancy_df = dormancy_threat()
    risk_df = calculate_risk_score(damage_df, dormancy_df)
    
    total_identities = len(risk_df)
    high_damage_acc = len(damage_df[damage_df['damage_score'] >= 60])
    dormant_acc = len(dormancy_df[dormancy_df['days_dormant'] >= 60])
    total_incidents = len(incidents_raw)
    
    top_risk = risk_df.head(10)
    
    return {
        "metrics": {
            "total_incidents": total_incidents,
            "high_risk_accounts": high_damage_acc,
            "dormant_identities": dormant_acc,
            "total_identities": total_identities,
        },
        "top_risk_identities": df_to_clean_dicts(top_risk)
    }

@app.get("/api/dormancy")
def get_dormancy_data():
    dormancy_df = dormancy_threat()
    if dormancy_df.empty:
        return {"metrics": {}, "distribution": [], "heatmap": [], "ledger": []}
    
    total_monitored = dormancy_df["identity_name"].nunique()
    max_days_dormant = float(dormancy_df["days_dormant"].max()) if not dormancy_df["days_dormant"].isnull().all() else 0.0
    dormant_60_plus = len(dormancy_df[dormancy_df["days_dormant"] >= 60])
    avg_dormancy_score = float(dormancy_df["dormancy_score"].mean()) if not dormancy_df["dormancy_score"].isnull().all() else 0.0
    
    # Inactivity distribution histogram buckets
    counts, bin_edges = np.histogram(dormancy_df["days_dormant"].dropna(), bins=10)
    distribution = []
    for i in range(len(counts)):
        distribution.append({
            "range": f"{int(bin_edges[i])}-{int(bin_edges[i+1])}d",
            "count": int(counts[i])
        })
        
    # Heatmap data (privilege tier vs HR status)
    heatmap_records = []
    if "highiest_privilage" in dormancy_df.columns and "hr_status" in dormancy_df.columns:
        pivot = dormancy_df.pivot_table(
            index="highiest_privilage",
            columns="hr_status",
            values="days_dormant",
            aggfunc="mean"
        ).fillna(0)
        for tier in pivot.index:
            for status in pivot.columns:
                heatmap_records.append({
                    "tier": str(tier),
                    "status": str(status),
                    "avg_days": round(float(pivot.loc[tier, status]), 1)
                })

    ledger = dormancy_df.sort_values("days_dormant", ascending=False)
    
    return {
        "metrics": {
            "total_monitored": total_monitored,
            "max_days_dormant": max_days_dormant,
            "dormant_60_plus": dormant_60_plus,
            "avg_dormancy_score": round(avg_dormancy_score, 1)
        },
        "distribution": distribution,
        "heatmap": heatmap_records,
        "ledger": df_to_clean_dicts(ledger)
    }

@app.get("/api/damage")
def get_damage_data():
    damage_df = damage_score()
    if damage_df.empty:
        return {"metrics": {}, "tier_counts": [], "registry": []}
        
    avg_damage = float(damage_df["damage_score"].mean())
    tier_0_count = len(damage_df[damage_df["highest_tier_held"] == "Tier 0"])
    tier_1_count = len(damage_df[damage_df["highest_tier_held"] == "Tier 1"])
    tier_2_count = len(damage_df[damage_df["highest_tier_held"] == "Tier 2"])
    high_risk_count = len(damage_df[damage_df["damage_score"] >= 60])
    
    tier_counts = [
        {"tier": "Tier 0", "count": tier_0_count},
        {"tier": "Tier 1", "count": tier_1_count},
        {"tier": "Tier 2", "count": tier_2_count},
    ]
    
    registry = damage_df.sort_values("damage_score", ascending=False)
    
    return {
        "metrics": {
            "avg_damage_score": round(avg_damage, 1),
            "tier_0_count": tier_0_count,
            "tier_1_count": tier_1_count,
            "high_risk_accounts": high_risk_count
        },
        "tier_counts": tier_counts,
        "registry": df_to_clean_dicts(registry)
    }

@app.get("/api/remediation")
def get_remediation_data(
    severity: Optional[str] = Query("All"),
    search: Optional[str] = Query("")
):
    incidents_raw, prevelage_df, ghost_acc, stale_token = generate_security_incidents()
    incidents = incidents_raw.rename(columns={"incident_type": "rule_type"}).copy()
    
    for col in incidents.columns:
        if col.lower() in ["platform", "on platform"]:
            incidents.rename(columns={col: "platform"}, inplace=True)
            
    if "platform" not in incidents.columns:
        incidents["platform"] = ""
        
    incidents["severity"] = incidents["severity"].str.title()
    
    critical_n = len(incidents[incidents["severity"] == "Critical"])
    high_n = len(incidents[incidents["severity"] == "High"])
    medium_n = len(incidents[incidents["severity"] == "Medium"])
    
    filtered = incidents.copy()
    if severity and severity != "All":
        filtered = filtered[filtered["severity"].str.lower() == severity.lower()]
        
    if search:
        q = search.lower()
        filtered = filtered[
            filtered["rule_type"].astype(str).str.lower().str.contains(q) |
            filtered["description"].astype(str).str.lower().str.contains(q)
        ]
        
    return {
        "metrics": {
            "total_incidents": len(incidents),
            "critical": critical_n,
            "high": high_n,
            "medium": medium_n
        },
        "incidents": df_to_clean_dicts(filtered)
    }

@app.get("/api/identities")
def get_identities_data(search: Optional[str] = Query("")):
    damage_df = damage_score()
    dormancy_df = dormancy_threat()
    risk_df = calculate_risk_score(damage_df, dormancy_df)
    
    if search:
        q = search.lower()
        risk_df = risk_df[risk_df["identity_name"].astype(str).str.lower().str.contains(q)]
        
    return {
        "total": len(risk_df),
        "identities": df_to_clean_dicts(risk_df)
    }

@app.get("/api/report")
def get_report():
    report_text = generate_executive_report()
    return {"report": report_text}

# Remediation Actions Endpoints
@app.post("/api/remediation/disable-status")
def action_disable_status(req: DisableStatusRequest):
    try:
        disable_hr_status(req.identity_id)
        return {"status": "success", "message": f"Status disabled for identity ID: {req.identity_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remediation/revoke-access")
def action_revoke_access(req: RevokeAccessRequest):
    try:
        revoke_account_access(req.identity_id, req.platform, req.incident_type)
        return {"status": "success", "message": f"Revoked access for identity ID: {req.identity_id} on {req.platform}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remediation/rotate-token")
def action_rotate_token(req: RotateTokenRequest):
    try:
        rotate_account_token(req.identity_id, req.platform)
        return {"status": "success", "message": f"Rotated token for identity ID: {req.identity_id} on {req.platform}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remediation/revoke-tier")
def action_revoke_tier(req: RevokeTierRequest):
    try:
        revoke_account_tier(req.identity_id, req.platform, req.elevated_tier)
        return {"status": "success", "message": f"Revoked tier {req.elevated_tier} for identity ID: {req.identity_id} on {req.platform}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refresh-cache")
def action_refresh_cache():
    try:
        generate_security_incidents()
        return {"status": "success", "message": "Pipeline refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
