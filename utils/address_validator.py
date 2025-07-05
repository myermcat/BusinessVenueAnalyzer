import requests
import json
import time
from typing import Optional, Dict, Tuple

class AddressValidator:
    """
    A class to validate addresses and retrieve their geographic coordinates.
    Uses OpenStreetMap Nominatim API for geocoding.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the address validator.
        
        Args:
            api_key (str, optional): API key for premium geocoding services
        """
        self.api_key = api_key
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'BusinessVenueAnalyzer/1.0 (https://github.com/your-repo)'
        }
    
    def validate_address(self, address: str) -> Dict:
        """
        Validate an address and return its coordinates.
        
        Args:
            address (str): The address to validate
            
        Returns:
            dict: Dictionary containing validation results and coordinates
        """
        try:
            # Prepare the request parameters
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            # Make the request to Nominatim
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    # Address found
                    result = data[0]
                    return {
                        'valid': True,
                        'address': address,
                        'latitude': float(result['lat']),
                        'longitude': float(result['lon']),
                        'display_name': result['display_name'],
                        'confidence': self._calculate_confidence(result),
                        'address_details': result.get('address', {})
                    }
                else:
                    # Address not found
                    return {
                        'valid': False,
                        'address': address,
                        'error': 'Address not found',
                        'latitude': None,
                        'longitude': None
                    }
            else:
                return {
                    'valid': False,
                    'address': address,
                    'error': f'API request failed with status code: {response.status_code}',
                    'latitude': None,
                    'longitude': None
                }
                
        except requests.exceptions.Timeout:
            return {
                'valid': False,
                'address': address,
                'error': 'Request timed out',
                'latitude': None,
                'longitude': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'valid': False,
                'address': address,
                'error': f'Request failed: {str(e)}',
                'latitude': None,
                'longitude': None
            }
        except Exception as e:
            return {
                'valid': False,
                'address': address,
                'error': f'Unexpected error: {str(e)}',
                'latitude': None,
                'longitude': None
            }
    
    def _calculate_confidence(self, result: Dict) -> str:
        """
        Calculate confidence level based on the geocoding result.
        
        Args:
            result (dict): The geocoding result from Nominatim
            
        Returns:
            str: Confidence level (high, medium, low)
        """
        # This is a simplified confidence calculation
        # In a real implementation, you might use more sophisticated logic
        display_name = result.get('display_name', '').lower()
        query = result.get('query', '').lower()
        
        # Check if key components match
        if 'ottawa' in display_name and 'ottawa' in query:
            return 'high'
        elif 'canada' in display_name or 'ontario' in display_name:
            return 'medium'
        else:
            return 'low'
    
    def batch_validate(self, addresses: list, delay: float = 1.0) -> list:
        """
        Validate multiple addresses with a delay between requests to respect rate limits.
        
        Args:
            addresses (list): List of addresses to validate
            delay (float): Delay between requests in seconds
            
        Returns:
            list: List of validation results
        """
        results = []
        
        for address in addresses:
            result = self.validate_address(address)
            results.append(result)
            
            # Add delay to respect rate limits
            if delay > 0:
                time.sleep(delay)
        
        return results
    
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for an address (simplified method).
        
        Args:
            address (str): The address to geocode
            
        Returns:
            tuple: (latitude, longitude) or None if not found
        """
        result = self.validate_address(address)
        
        if result['valid']:
            return (result['latitude'], result['longitude'])
        else:
            return None


# Example usage and testing
if __name__ == '__main__':
    # Initialize the validator
    validator = AddressValidator()
    
    # Test addresses
    test_addresses = [
        "centertown, Ottawa, canada"     # Fake address
    ]
    
    print("Address Validation Test")
    print("=" * 50)
    
    for address in test_addresses:
        print(f"\nValidating: {address}")
        print("-" * 30)
        
        result = validator.validate_address(address)
        
        if result['valid']:
            print(f"VALID")
            print(f"Latitude: {result['latitude']}")
            print(f"Longitude: {result['longitude']}")
            print(f"Display Name: {result['display_name']}")
            print(f"Confidence: {result['confidence']}")
            
            # Show address details
            if result['address_details']:
                print("Address Details:")
                for key, value in result['address_details'].items():
                    print(f"  {key}: {value}")
        else:
            print(f"INVALID")
            print(f"Error: {result['error']}")
        
        print()
    
    # Test batch validation
    print("Batch Validation Test")
    print("=" * 50)
    
    batch_results = validator.batch_validate(test_addresses, delay=1.0)
    
    for i, result in enumerate(batch_results):
        print(f"\nResult {i+1}: {result['address']}")
        if result['valid']:
            print(f"  Coordinates: ({result['latitude']}, {result['longitude']})")
        else:
            print(f"  Error: {result['error']}")
    
    # Test coordinate extraction
    print("\nCoordinate Extraction Test")
    print("=" * 50)
    
    for address in test_addresses:
        coords = validator.get_coordinates(address)
        if coords:
            print(f"{address}: {coords}")
        else:
            print(f"{address}: Not found") 