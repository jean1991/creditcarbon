"""
Satellite API integration for DRC climate action reporting platform.
Integrates with Global Forest Watch and other satellite data providers.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DRC Province to Admin Code mapping for Global Forest Watch
# Based on official DRC administrative divisions
DRC_PROVINCE_ADMIN_MAPPING = {
    # Province Name: (admin_code, gfw_admin_id)
    "Kinshasa": ("CD-KN", "CD.1"),
    "Bas-Congo": ("CD-BC", "CD.2"), 
    "Bandundu": ("CD-BN", "CD.3"),
    "Équateur": ("CD-EQ", "CD.4"),
    "Province Orientale": ("CD-OR", "CD.5"),
    "Nord-Kivu": ("CD-NK", "CD.6"),
    "Sud-Kivu": ("CD-SK", "CD.7"),
    "Maniema": ("CD-MA", "CD.8"),
    "Katanga": ("CD-KA", "CD.9"),
    "Kasaï-Oriental": ("CD-KE", "CD.10"),
    "Kasaï-Occidental": ("CD-KW", "CD.11"),
    # New provinces (post-2015 administrative reform)
    "Kongo Central": ("CD-KC", "CD.12"),
    "Kwango": ("CD-KG", "CD.13"),
    "Kwilu": ("CD-KL", "CD.14"),
    "Mai-Ndombe": ("CD-MN", "CD.15"),
    "Sankuru": ("CD-SA", "CD.16"),
    "Lomami": ("CD-LO", "CD.17"),
    "Lualaba": ("CD-LU", "CD.18"),
    "Haut-Lomami": ("CD-HL", "CD.19"),
    "Haut-Katanga": ("CD-HK", "CD.20"),
    "Tanganyika": ("CD-TA", "CD.21"),
    "Haut-Uele": ("CD-HU", "CD.22"),
    "Bas-Uele": ("CD-BU", "CD.23"),
    "Ituri": ("CD-IT", "CD.24"),
    "Tshopo": ("CD-TO", "CD.25"),
    "Mongala": ("CD-MO", "CD.26"),
    "Nord-Ubangi": ("CD-NU", "CD.27"),
    "Sud-Ubangi": ("CD-SU", "CD.28"),
    "Tshuapa": ("CD-TU", "CD.29")
}

class SatelliteAPIClient:
    """Client for satellite data APIs including Global Forest Watch."""
    
    def __init__(self, gfw_api_key: Optional[str] = None):
        """
        Initialize satellite API client.
        
        Args:
            gfw_api_key: Optional API key for Global Forest Watch
        """
        self.gfw_api_key = gfw_api_key
        self.base_urls = {
            'gfw': 'https://production-api.globalforestwatch.org',
            'gfw_data': 'https://data-api.globalforestwatch.org'
        }
        
    def get_province_admin_code(self, province_name: str) -> Optional[Tuple[str, str]]:
        """
        Get admin code and GFW admin ID for a DRC province.
        
        Args:
            province_name: Name of the DRC province
            
        Returns:
            Tuple of (admin_code, gfw_admin_id) or None if not found
        """
        return DRC_PROVINCE_ADMIN_MAPPING.get(province_name)
    
    def list_available_provinces(self) -> List[str]:
        """Get list of all available DRC provinces."""
        return list(DRC_PROVINCE_ADMIN_MAPPING.keys())
    
    def get_forest_loss_data(self, province_name: str, year_range: Tuple[int, int] = (2020, 2023)) -> Dict:
        """
        Get forest loss data for a specific DRC province from Global Forest Watch.
        
        Args:
            province_name: Name of the DRC province
            year_range: Tuple of (start_year, end_year)
            
        Returns:
            Dictionary containing forest loss data
        """
        admin_info = self.get_province_admin_code(province_name)
        if not admin_info:
            raise ValueError(f"Province '{province_name}' not found in mapping")
        
        admin_code, gfw_admin_id = admin_info
        
        # Example GFW API endpoint for forest loss
        # Note: This is a simplified example - actual GFW API may require different parameters
        url = f"{self.base_urls['gfw_data']}/dataset/umd_tree_cover_loss/latest/query"
        
        params = {
            'sql': f'''
                SELECT year, SUM(area__ha) as loss_area_ha
                FROM data 
                WHERE iso = 'COD' 
                AND adm1 = '{gfw_admin_id}'
                AND year >= {year_range[0]} 
                AND year <= {year_range[1]}
                GROUP BY year
                ORDER BY year
            '''
        }
        
        headers = {}
        if self.gfw_api_key:
            headers['Authorization'] = f'Bearer {self.gfw_api_key}'
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'province': province_name,
                'admin_code': admin_code,
                'gfw_admin_id': gfw_admin_id,
                'year_range': year_range,
                'forest_loss_data': data.get('data', []),
                'metadata': {
                    'source': 'Global Forest Watch',
                    'dataset': 'University of Maryland Tree Cover Loss',
                    'units': 'hectares'
                }
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching forest loss data: {e}")
            # Return mock data for development/testing
            return self._get_mock_forest_loss_data(province_name, admin_code, year_range)
    
    def get_fire_data(self, province_name: str, date_range: Tuple[str, str]) -> Dict:
        """
        Get fire/hotspot data for a specific DRC province.
        
        Args:
            province_name: Name of the DRC province
            date_range: Tuple of (start_date, end_date) in 'YYYY-MM-DD' format
            
        Returns:
            Dictionary containing fire data
        """
        admin_info = self.get_province_admin_code(province_name)
        if not admin_info:
            raise ValueError(f"Province '{province_name}' not found in mapping")
        
        admin_code, gfw_admin_id = admin_info
        
        # Mock implementation - replace with actual API calls
        return {
            'province': province_name,
            'admin_code': admin_code,
            'date_range': date_range,
            'fire_alerts': [],
            'metadata': {
                'source': 'FIRMS/MODIS',
                'last_updated': date_range[1]
            }
        }
    
    def _get_mock_forest_loss_data(self, province_name: str, admin_code: str, year_range: Tuple[int, int]) -> Dict:
        """
        Generate mock forest loss data for development/testing.
        """
        mock_data = []
        for year in range(year_range[0], year_range[1] + 1):
            # Generate realistic mock data
            base_loss = 1000 + (year - year_range[0]) * 50  # Increasing trend
            mock_data.append({
                'year': year,
                'loss_area_ha': base_loss
            })
        
        return {
            'province': province_name,
            'admin_code': admin_code,
            'gfw_admin_id': DRC_PROVINCE_ADMIN_MAPPING[province_name][1],
            'year_range': year_range,
            'forest_loss_data': mock_data,
            'metadata': {
                'source': 'Mock Data (Development)',
                'dataset': 'Simulated Tree Cover Loss',
                'units': 'hectares',
                'note': 'This is mock data for development purposes'
            }
        }

# Example usage and testing
def example_usage():
    """Example of how to use the satellite API client."""
    client = SatelliteAPIClient()
    
    # List available provinces
    print("Available DRC Provinces:")
    for province in client.list_available_provinces():
        print(f"  - {province}")
    
    # Get admin code for a province
    admin_info = client.get_province_admin_code("Kinshasa")
    print(f"\nKinshasa admin info: {admin_info}")
    
    # Get forest loss data
    try:
        forest_data = client.get_forest_loss_data("Kinshasa", (2020, 2023))
        print(f"\nForest loss data for Kinshasa:")
        print(json.dumps(forest_data, indent=2))
    except Exception as e:
        print(f"Error getting forest data: {e}")

if __name__ == "__main__":
    example_usage()