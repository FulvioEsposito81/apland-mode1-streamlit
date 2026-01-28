# API Specification - MODEI Geotechnical Application

## Overview

The MODEI API consists of 2 endpoints for geotechnical slope stability analysis.

## Base URL

Configure in `config_app.py`:
```python
API_BASE_URL = "http://localhost:5000"  # Change to your API server
```

---

## Endpoint 1: Calculate Safety Factor (SFd)

**POST** `/functions/sfd`

Calculate the Safety Factor in absence of neutral pressures.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "c": 10.0,
  "gamma": 18.0,
  "H": 5.0,
  "alpha": 15.0,
  "phi": 30.0
}
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| c | float | kPa | Effective cohesion |
| gamma | float | kN/m³ | Unit weight of soil |
| H | float | m | Depth of sliding surface from ground level |
| alpha | float | ° | Ground inclination angle |
| phi | float | ° | Shear resistance angle |

### Response

**Success (200):**
```json
{
  "success": true,
  "sfd": 1.45
}
```

**Error (400/500):**
```json
{
  "success": false,
  "error": "Error description"
}
```

### Formula

Using infinite slope stability formula:

```
         c' + γ·H·cos²(α)·tan(φ)
SFd = ──────────────────────────────
         γ·H·sin(α)·cos(α)
```

---

## Endpoint 2: Complete Geotechnical Computation

**POST** `/functions/compute`

Perform complete slope stability computation with rainfall infiltration analysis.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body Structure:**

The body contains **always-required parameters** plus **conditional parameters** based on SFd value.

#### Always Required Parameters

```json
{
  "c": 10.0,
  "gamma": 18.0,
  "H": 5.0,
  "alpha": 15.0,
  "phi": 30.0,
  "prisl": "unsaturated",
  "sfd": 0.85,
  "k": 1.5e-6,
  "p": 5.0,
  "u_w0": -15.0,
  "id": "2026-01-28",
  "duration": 24,
  "intensity": 50.0
}
```

| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| c | float | kPa | Effective cohesion |
| gamma | float | kN/m³ | Unit weight of soil |
| H | float | m | Depth of sliding surface |
| alpha | float | ° | Ground inclination angle |
| phi | float | ° | Shear resistance angle |
| prisl | string | - | Analysis approach ("saturated" or "unsaturated") |
| sfd | float | - | Safety Factor value (from /functions/sfd) |
| k | float | m/s | Hydraulic conductivity |
| p | float | mm/day | Infiltration potential |
| u_w0 | float | kPa | Initial neutral pressure/suction |
| id | string | - | Rain event date or ID |
| duration | int | hours | Event duration |
| intensity | float | mm/day | Rainfall intensity |

#### Conditional Parameters

**If SFd ≤ 1** (Unsaturated analysis):
```json
{
  ...all required parameters...,
  "m_w": 0.005,
  "x0_1": 0.85
}
```

| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| m_w | float | kPa⁻¹ | Hydraulic retention coefficient |
| x0_1 | float | - | Parameter χ(S-1) for effective stress |

**If SFd > 1** (Saturated analysis):
```json
{
  ...all required parameters...,
  "sr": 0.95,
  "n": 0.35
}
```

| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| sr | float | - | Degree of saturation (0-1) |
| n | float | - | Porosity (0-1) |

### Complete Request Examples

#### Example 1: SFd ≤ 1 (Unsaturated)

```json
{
  "c": 5.0,
  "gamma": 20.0,
  "H": 10.0,
  "alpha": 30.0,
  "phi": 25.0,
  "prisl": "unsaturated",
  "sfd": 0.85,
  "k": 1.5e-6,
  "p": 5.0,
  "u_w0": -15.0,
  "id": "2026-01-28",
  "duration": 24,
  "intensity": 50.0,
  "m_w": 0.005,
  "x0_1": 0.85
}
```

#### Example 2: SFd > 1 (Saturated)

```json
{
  "c": 15.0,
  "gamma": 18.0,
  "H": 3.0,
  "alpha": 10.0,
  "phi": 35.0,
  "prisl": "saturated",
  "sfd": 1.5,
  "k": 2.0e-5,
  "p": 8.0,
  "u_w0": 5.0,
  "id": "2026-01-28",
  "duration": 48,
  "intensity": 35.0,
  "sr": 0.95,
  "n": 0.35
}
```

### Response

**Success (200):**
```json
{
  "success": true,
  "p": 0.000003,
  "I": 50.5,
  "Uc": 153.0,
  "H_Max": 12.5,
  "plot": {
    "time_hours": [0, 6, 12, 18, 24],
    "safety_factor": [1.45, 1.38, 1.28, 1.20, 1.15],
    "pore_pressure": [-15.0, -10.5, -5.3, 2.1, 8.7],
    "infiltration": [0, 12.6, 25.2, 37.9, 50.5],
    "title": "Analysis Results - Event 2026-01-28",
    "xlabel": "Time (hours)",
    "ylabel_sf": "Safety Factor",
    "ylabel_pressure": "Pore Pressure (kPa)",
    "ylabel_infiltration": "Infiltration (mm)"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Indicates if computation was successful |
| p | float | Computed parameter p |
| I | float | Computed parameter I (total infiltration) |
| Uc | float | Computed parameter Uc (critical stress) |
| H_Max | float | Maximum height parameter |
| plot | object | Graph data for visualization |

**Plot Object Structure:**

| Field | Type | Description |
|-------|------|-------------|
| time_hours | array | Time points (hours) |
| safety_factor | array | Safety factor values over time |
| pore_pressure | array | Pore pressure values (kPa) over time |
| infiltration | array | Cumulative infiltration (mm) over time |
| title | string | Plot title |
| xlabel | string | X-axis label |
| ylabel_sf | string | Y-axis label for safety factor |
| ylabel_pressure | string | Y-axis label for pore pressure |
| ylabel_infiltration | string | Y-axis label for infiltration |

**Error Response:**
```json
{
  "success": false,
  "error": "Error description"
}
```

---

## Application Flow

```
1. User enters geometric and mechanical parameters
   ↓
2. App calls POST /functions/sfd
   ↓
3. API returns SFd value
   ↓
4. If SFd ≤ 1:
   - Enable unsaturated soil section
   - User fills: k, p, u_w0, m_w, x0_1
   
   If SFd > 1:
   - Enable saturated soil section
   - User fills: k, p, u_w0, sr, n
   ↓
5. User enters rain event data (id, duration, intensity)
   ↓
6. User clicks "Calcola"
   ↓
7. App calls POST /functions/compute with appropriate parameters
   ↓
8. API returns p, I, Uc, H_Max, plot
   ↓
9. App displays results and graphs
```

---

## Error Handling

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Invalid endpoint |
| 500 | Internal Server Error - Computation error |
| 503 | Service Unavailable - Server not responding |

### Client-Side Error Handling

The API client (`api_client_geo.py`) handles:
- Connection errors
- Timeout errors
- HTTP errors
- JSON parsing errors

All errors are returned in a consistent format:
```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

---

## Testing with Mock API

The included `mock_api.py` implements both endpoints with mock calculations:

### Start Mock Server
```bash
python mock_api.py
```

Server runs on: `http://localhost:5000`

### Test Endpoints

**Test SFd calculation:**
```bash
curl -X POST http://localhost:5000/functions/sfd \
  -H "Content-Type: application/json" \
  -d '{"c":10,"gamma":18,"H":5,"alpha":15,"phi":30}'
```

**Test compute (SFd ≤ 1):**
```bash
curl -X POST http://localhost:5000/functions/compute \
  -H "Content-Type: application/json" \
  -d '{
    "c":5,"gamma":20,"H":10,"alpha":30,"phi":25,
    "prisl":"unsaturated","sfd":0.85,
    "k":1.5e-6,"p":5,"u_w0":-15,
    "id":"2026-01-28","duration":24,"intensity":50,
    "m_w":0.005,"x0_1":0.85
  }'
```

**Test compute (SFd > 1):**
```bash
curl -X POST http://localhost:5000/functions/compute \
  -H "Content-Type: application/json" \
  -d '{
    "c":15,"gamma":18,"H":3,"alpha":10,"phi":35,
    "prisl":"saturated","sfd":1.5,
    "k":2.0e-5,"p":8,"u_w0":5,
    "id":"2026-01-28","duration":48,"intensity":35,
    "sr":0.95,"n":0.35
  }'
```

---

## Integration Checklist

### Implementing Your API

- [ ] Implement POST `/functions/sfd` endpoint
- [ ] Implement POST `/functions/compute` endpoint
- [ ] Handle SFd ≤ 1 case (unsaturated parameters)
- [ ] Handle SFd > 1 case (saturated parameters)
- [ ] Return all required fields: p, I, Uc, H_Max, plot
- [ ] Include error handling with success: false
- [ ] Test with both saturated and unsaturated scenarios

### Connecting to Your API

1. Update `config_app.py`:
```python
API_BASE_URL = "http://your-api-server.com"
```

2. Test connection in app sidebar

3. Verify SFd calculation works

4. Test full computation with both SFd cases

---

## Support

For issues:
1. Check API server is running
2. Verify endpoint URLs in config
3. Test with curl commands
4. Check server logs for errors
5. Review browser console (F12) for client errors
