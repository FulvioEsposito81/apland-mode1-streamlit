# Geotechnical Analysis Application

A Streamlit-based web application for geotechnical slope stability analysis, replicating a professional engineering interface.

## Features

- **Geometric Data Input**: Configure slope geometry parameters
- **Mechanical Characterization**: Define soil mechanical properties
- **Safety Factor Calculations**: Display safety factors for different conditions
- **Hydraulic Characterization**: Configure saturated and partially saturated soil parameters
- **Rain Event Analysis**: Input rainfall event data for analysis
- **Results Visualization**: Display calculation results and graphs

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Application Structure

### Input Sections (Left Panel)

1. **Dati geometrici** (Geometric Data)
   - Depth of sliding surface
   - Slope angle

2. **Caratterizzazione meccanica del terreno** (Mechanical Characterization)
   - Unit weight of soil
   - Friction angle
   - Effective cohesion

3. **Fattore di Sicurezza** (Safety Factor)
   - Safety factors for different failure conditions

4. **Caratterizzazione idraulica** (Hydraulic Characterization)
   - Saturated soil parameters
   - Partially saturated soil parameters

5. **Evento pioggia** (Rain Event)
   - Event date/ID
   - Duration
   - Intensity

### Output Section (Right Panel)

- Results display area
- Tabs for different visualizations:
  - Numerical results
  - Graphs and diagrams
  - Additional details

## API Integration

The application is designed to integrate with an external API for calculations. To integrate your API:

1. Create an `api_client.py` file with your API connection logic
2. Import and use it in `app.py` when the "Calcola" (Calculate) button is clicked
3. Update the results display section with the API response

Example API client structure:

```python
# api_client.py
import requests

class GeotechnicalAPI:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def calculate(self, parameters):
        response = requests.post(
            f"{self.base_url}/calculate",
            json=parameters
        )
        return response.json()
```

## Customization

### Styling

The application uses custom CSS defined in the `st.markdown()` section. You can modify:
- Colors
- Font sizes
- Spacing
- Component styles

### Adding New Fields

To add new input fields:
1. Add the field in the appropriate section
2. Use the same column layout pattern for consistency
3. Update the API payload structure accordingly

### Language

The current interface is in Italian. To change to another language:
1. Update all text labels in the `st.number_input()`, `st.markdown()`, and other text elements
2. Update section headers and descriptions

## Version

Current version: 1.0.0.9

## Notes

- All numeric inputs accept decimal values
- Date inputs default to the current date
- The "NaN" badges indicate values that need to be calculated
- The info icons (ℹ️) provide additional context for specific parameters
