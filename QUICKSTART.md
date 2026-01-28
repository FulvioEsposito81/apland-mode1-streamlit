# Quick Start Guide

## Installation

### 1. Install Python
Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Basic Usage (Without API)
```bash
streamlit run geotechnical_app.py
```

The application will open at `http://localhost:8501`

### With API Integration

1. **Edit the API endpoint** in `api_integration_example.py`:
   ```python
   api = GeotechnicalAPI(base_url="http://your-api-endpoint.com/api")
   ```

2. **Integrate with main app** by adding these imports to `geotechnical_app.py`:
   ```python
   from api_integration_example import GeotechnicalAPI
   
   # Initialize API client
   api = GeotechnicalAPI(base_url="http://your-api-endpoint.com/api")
   ```

3. **Replace the TODO section** in the Calculate button handler:
   ```python
   if st.button("Calcola"):
       with st.spinner("Elaborazione in corso..."):
           result = api.calculate_slope_stability(parameters)
           
           if "error" in result:
               st.error(f"Errore: {result['error']}")
           else:
               st.session_state['results'] = result
               st.success("Calcolo completato!")
   ```

## Application Structure

```
.
├── geotechnical_app.py          # Main Streamlit application
├── api_integration_example.py   # API client template
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
└── QUICKSTART.md               # This file
```

## Input Parameters Overview

### Geometric Data
- **H** (m): Depth of sliding surface
- **α** (°): Ground inclination angle

### Mechanical Properties
- **γ** (kN/m³): Unit weight of soil
- **φ** (°): Shear resistance angle
- **c'** (kPa): Effective cohesion

### Hydraulic Properties (Saturated)
- **k** (m/s): Hydraulic conductivity
- **p** (mm/day): Infiltration potential
- **u_w0** (kPa): Initial neutral pressure
- **Sr** (-): Degree of saturation
- **n** (-): Porosity

### Hydraulic Properties (Unsaturated)
- Same parameters as saturated + additional:
- **m_w** (kPa⁻¹): Hydraulic retention coefficient
- **χ** (-): χ parameter

### Rain Event
- **Date**: Event date or ID
- **Duration** (hours): Event duration
- **Intensity** (mm/day): Rainfall intensity

## Expected API Response Format

Your API should return JSON in this structure:

```json
{
  "safety_factors": {
    "sfd_no_pressure": 1.45,
    "sf_with_pressure": 1.23,
    "sf_minimum": 1.15,
    "critical_time_hours": 24.5
  },
  "pressures": {
    "initial_suction_kpa": -15.2,
    "final_pressure_kpa": 8.7
  },
  "time_series": {
    "time_hours": [0, 6, 12, 18, 24],
    "safety_factor": [1.45, 1.38, 1.28, 1.20, 1.15],
    "pore_pressure_kpa": [-15.2, -10.5, -5.3, 2.1, 8.7]
  }
}
```

## Troubleshooting

### Port Already in Use
```bash
streamlit run geotechnical_app.py --server.port 8502
```

### API Connection Issues
- Check that your API server is running
- Verify the API endpoint URL
- Check firewall settings
- Review API logs for errors

### Dependencies Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. Test the UI by running the application
2. Prepare your API endpoint following the expected format
3. Update the API integration code with your endpoint
4. Test with real calculations
5. Customize styling and add additional features as needed

## Support

For issues or questions:
1. Check the full README.md for detailed documentation
2. Review the API integration example
3. Check Streamlit documentation: https://docs.streamlit.io
