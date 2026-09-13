"""Authority Situation Summary & Decision Support Briefing Generator for AAGAAH.

Produces structured, exportable (Markdown / JSON / printable) decision-support summaries
specifically formatted for District Emergency Operations Centres (DEOC) and Incident Commanders.
"""
from datetime import datetime, timezone

def generate_situation_briefing(location: dict, pilot: dict, as_of: str | None = None) -> str:
    loc_id = location.get('id', 'unknown')
    loc_name = location.get('name', 'Unknown Reach').replace(' (001)', '')
    alert = location.get('alert_level', 'Unknown')
    risk = location.get('routed_risk')
    risk_str = f"{round(risk * 100, 1)}%" if risk is not None else "UNAVAILABLE"
    conf = location.get('confidence', 0.0)
    conf_str = f"{round(conf * 100, 1)}%"
    priority = location.get('priority', 0.0)
    rank = location.get('rank', 1)
    anomaly = "UNUSUAL ENVIRONMENTAL SIGNAL DETECTED" if location.get('anomaly') else "TYPICAL BACKGROUND ENVELOPE"

    feat = location.get('features', {})
    rain_1 = feat.get('rain_1h')
    rain_24 = feat.get('rain_24h')
    soil = feat.get('soil_moisture')
    slope = location.get('terrain', {}).get('slope_deg', 'N/A')
    elev = location.get('terrain', {}).get('elevation_m', 'N/A')
    upstream_area = location.get('terrain', {}).get('upstream_area_km2', 'N/A')

    explanation = location.get('explanation', [])
    top_drivers = "\n".join([
        f"  - **{e['feature']}** ({e.get('value', 'N/A')}): {e['contribution_log_odds']:+.3f} log-odds impact"
        for e in explanation[:4]
    ]) if explanation else "  - Local feature attribution pending data synchronization."

    exposure = location.get('exposure', {})
    counts = exposure.get('counts', {})
    assets_str = (
        f"Settlements: {counts.get('settlement', 0)} | "
        f"Road Segments: {counts.get('road', 0)} | "
        f"Bridges: {counts.get('bridge', 0)} | "
        f"Hospitals/Clinics: {counts.get('hospital', 0)}"
    )

    downstream = location.get('downstream', [])
    downstream_str = ", ".join(downstream) if downstream else "Basin outlet reach (Rudraprayag confluence)."
    dominant = location.get('dominant_origin', loc_id)
    origin_note = (
        f"Local in-situ hazard dominates." if dominant == loc_id
        else f"Upstream propagation from **{dominant}** dominates downstream risk."
    )

    quality = location.get('quality', {})
    reasons = location.get('confidence_reasons', [])
    reasons_str = "\n".join([f"  - {r}" for r in reasons]) if reasons else "  - Telemetry meets standard data adequacy benchmarks."

    rec = location.get('recommendation', 'Maintain standard routine monitoring.')

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    as_of_str = as_of or now_utc

    briefing = f"""# FLASH-FLOOD SITUATIONAL INTELLIGENCE BRIEFING
**STATE DISASTER MANAGEMENT AUTHORITY / DISTRICT EMERGENCY OPERATIONS CENTRE**
**SYSTEM: AAGAAH (Problem Statement 26192 | Pilot: Mandakini Basin)**

---

### LOCATION: {loc_name.upper()} ({loc_id})
- **Evaluation Timestamp**: {as_of_str}
- **Document Generated**: {now_utc}
- **Operational Advisory Status**: **[{alert.upper()}]**
- **Decision-Support Priority Rank**: **#{rank}** (Score: {priority:.3f})

---

### 1. OPERATIONAL SITUATION MATRIX (FOUR INDEPENDENT PILLARS)

| Pillar | Metric / Assessment | Operational Meaning |
| :--- | :---: | :--- |
| **Physical Hazard Probability** | **{risk_str}** | Model-estimated likelihood of rapid runoff exceedance |
| **Data Adequacy Confidence** | **{conf_str}** | Freshness, coverage, and sensor availability score |
| **Impact Vulnerability Weight** | **{assets_str}** | Mapped infrastructure within 150m river corridor |
| **Operational Priority Rank** | **Rank #{rank}** | Advisory queue ranking for authority attention |

- **Anomaly Sentinel Status**: {anomaly}

---

### 2. HYDROMETEOROLOGICAL & TERRAIN CONTEXT
- **Current 1-Hour Rainfall**: {rain_1 if rain_1 is not None else 'N/A'} mm
- **24-Hour Accumulated Rainfall**: {rain_24 if rain_24 is not None else 'N/A'} mm
- **Topsoil Moisture**: {f"{round(soil*100, 1)}%" if soil is not None else 'N/A'} (ECMWF land reanalysis/forecast)
- **Catchment Slope**: {slope}° | **Elevation**: {elev} m ASL | **Upstream Contributing Area**: {upstream_area} km²

---

### 3. EXPLAINABILITY & PRIMARY DRIVERS (TreeSHAP Log-Odds)
{top_drivers}

---

### 4. HYDROLOGICAL CONNECTIVITY & REACH PROPAGATION
- **Hydrological Influence**: {origin_note}
- **Downstream Reaches at Risk**: {downstream_str}
- **Attenuation Model**: Exponential metric reach decay (decay scale: 120 km) along D8 river channel.

---

### 5. DATA ADEQUACY & LIMITATIONS AUDIT
- **Observation Age**: {quality.get('age_hours', 'N/A')} hours
- **24h Telemetry Coverage**: {round(quality.get('coverage', {}).get('24', 1.0) * 100, 1)}%
{reasons_str}
*Notice: Upper Mandakini river stage gauges lack open public REST feeds. Model natively accounts for missing telemetry without linear hallucination.*

---

### 6. MANDATED AUTHORITY VERIFICATION ACTIONS
**Duty Officer Protocol**:
1. **Field Ground-Truth Check**: Contact local police outpost or temple board staff to verify physical rain intensity and river turbidity.
2. **Upstream Alert Coordination**: Alert upstream outposts at Gaurikund and Kedarnath regarding downstream gorge transit risk.
3. **Bridge & Road Infrastructure Check**: Dispatch highway patrol to inspect bridge approach embankments on NH-107.
4. **Communication Redundancy**: Verify VHF radio and satellite phone connectivity with DEOC Rudraprayag.
5. **Advisory Formulation**: {rec}

---

*DISCLAIMER: This document is an advisory decision-support briefing for authorized disaster authorities. It does not replace executive command discretion and does not issue autonomous evacuation orders.*
"""
    return briefing
