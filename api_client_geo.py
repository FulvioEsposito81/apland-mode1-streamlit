"""
API Client for Geotechnical Calculations
"""

import requests
from typing import Dict, Any, Optional
from config_app import API_BASE_URL, ENDPOINTS


class GeotechnicalAPIClient:
    """Client for communicating with the geotechnical calculation API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def calculate_sfd(
        self,
        c: float,
        gamma: float,
        h: float,
        alpha: float,
        phi: float
    ) -> Dict[str, Any]:
        """
        Calculate Safety Factor in absence of neutral pressures (SFd)
        
        Args:
            c: Effective cohesion (kPa)
            gamma: Unit weight of soil (kN/m³)
            h: Depth of sliding surface (m)
            alpha: Ground inclination angle (°)
            phi: Shear resistance angle (°)
            
        Returns:
            Dictionary with SFd value or error
            Example: {"sfd": 1.45, "success": True}
        """
        endpoint = f"{self.base_url}{ENDPOINTS['sfd']}"
        payload = {
            "c": c,
            "gamma": gamma,
            "H": h,
            "alpha": alpha,
            "phi": phi
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "sfd": response.json()['sfd']}
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to API server. Please check if the server is running."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "API request timed out."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def calculate_compute(
        self,
        c: float,
        gamma: float,
        h: float,
        alpha: float,
        phi: float,
        prisl: str,
        sfd: float,
        k: float,
        p: float,
        u_w0: float,
        event_id: str,
        duration: int,
        intensity: float,
        # Conditional parameters
        m_w: float = None,
        x0_1: float = None,
        sr: float = None,
        n: float = None
    ) -> Dict[str, Any]:
        """
        Perform complete geotechnical computation
        
        Args:
            c: Effective cohesion (kPa)
            gamma: Unit weight of soil (kN/m³)
            h: Depth of sliding surface (m)
            alpha: Ground inclination angle (°)
            phi: Shear resistance angle (°)
            prisl: Analysis type/approach
            sfd: Safety Factor value
            k: Hydraulic conductivity (m/s)
            p: Infiltration potential (mm/day)
            u_w0: Initial neutral pressure/suction (kPa)
            event_id: Rain event date or ID
            duration: Event duration (hours)
            intensity: Event intensity (mm/day)
            m_w: Hydraulic retention coefficient (kPa⁻¹) - for sfd <= 1
            x0_1: Parameter χ(S-1) (-) - for sfd <= 1
            sr: Degree of saturation (-) - for sfd > 1
            n: Porosity (-) - for sfd > 1
            
        Returns:
            Dictionary with computation results:
            - p: Result parameter p
            - I: Result parameter I
            - Uc: Result parameter Uc
            - H_Max: Maximum height
            - plot: Graph data
        """
        endpoint = f"{self.base_url}{ENDPOINTS['compute']}"
        
        # Build payload with always-required parameters
        payload = {
            "c": c,
            "gamma": gamma,
            "H": h,
            "alpha": alpha,
            "phi": phi,
            "prisl": prisl,
            "sfd": sfd,
            "k": k,
            "p": p,
            "u_w0": u_w0,
            "id": event_id,
            "duration": duration,
            "intensity": intensity
        }
        
        # Add conditional parameters based on SFd value
        if sfd <= 1:
            # For sfd <= 1, include unsaturated parameters
            if m_w is not None:
                payload["m_w"] = m_w
            if x0_1 is not None:
                payload["x0_1"] = x0_1
        else:
            # For sfd > 1, include saturated parameters
            if sr is not None:
                payload["sr"] = sr
            if n is not None:
                payload["n"] = n
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to API server. Please check if the server is running."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "API request timed out."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
