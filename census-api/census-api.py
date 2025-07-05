import json
import math
import numpy as np

class CensusData:
    """
    A class to calculate population statistics within specified walking and driving distance radii.
    Uses census data from either affordability.geojson or density.geojson to provide population analysis.
    """
    
    def __init__(self, file_path):
        """
        Initialize the calculator with census data.
        
        Args:
            file_path (str): Path to the census data file (affordability.geojson or density.geojson)
        """
        self.file_path = file_path
        self.census_data = self._load_census_data()
    
    def _load_census_data(self):
        """Load and parse the census data file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data['features']
        except FileNotFoundError:
            raise FileNotFoundError(f"Census data file not found: {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in census data file: {self.file_path}")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: Coordinates of first point
            lat2, lon2: Coordinates of second point
            
        Returns:
            float: Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def find_areas_within_radius(self, center_lat, center_lon, radius_km):
        """
        Find all areas within the specified radius.
        
        Args:
            center_lat (float): Latitude of center point
            center_lon (float): Longitude of center point
            radius_km (float): Radius in kilometers
            
        Returns:
            list: List of dictionaries containing area information
        """
        areas_within_radius = []
        
        for feature in self.census_data:
            geometry = feature['geometry']
            properties = feature['properties']
            
            # Extract population data (works for both density and affordability files)
            population = int(properties.get('pop', 0))
            
            if population <= 0:
                continue
            
            # Check if the area intersects with our radius
            # For simplicity, we'll check if the centroid is within radius
            # In a more sophisticated implementation, you'd check polygon intersection
            
            if geometry['type'] == 'MultiPolygon':
                # Calculate centroid of the multipolygon
                coords = geometry['coordinates'][0][0]  # First polygon's outer ring
                if coords:
                    # Calculate centroid (simplified)
                    lats = [coord[1] for coord in coords]
                    lons = [coord[0] for coord in coords]
                    centroid_lat = sum(lats) / len(lats)
                    centroid_lon = sum(lons) / len(lons)
                    
                    distance = self.calculate_distance(center_lat, center_lon, centroid_lat, centroid_lon)
                    
                    if distance <= radius_km:
                        areas_within_radius.append({
                            'population': population,
                            'distance_km': distance
                        })
            
            elif geometry['type'] == 'Polygon':
                coords = geometry['coordinates'][0]  # Outer ring
                if coords:
                    lats = [coord[1] for coord in coords]
                    lons = [coord[0] for coord in coords]
                    centroid_lat = sum(lats) / len(lats)
                    centroid_lon = sum(lons) / len(lons)
                    
                    distance = self.calculate_distance(center_lat, center_lon, centroid_lat, centroid_lon)
                    
                    if distance <= radius_km:
                        areas_within_radius.append({
                            'population': population,
                            'distance_km': distance
                        })
        
        return areas_within_radius
    
    def calculate_population_stats(self, latitude, longitude, walking_radius_km, driving_radius_km):
        """
        Calculate population statistics for both walking and driving radii.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            walking_radius_km (float): Walking distance radius in kilometers
            driving_radius_km (float): Driving distance radius in kilometers
            
        Returns:
            dict: Dictionary containing population statistics for both radii
            
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate input
        if not (-90 <= latitude <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        if not (-180 <= longitude <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        if walking_radius_km <= 0 or driving_radius_km <= 0:
            raise ValueError('Radii must be positive')
        if walking_radius_km > driving_radius_km:
            raise ValueError('Walking radius cannot be larger than driving radius')
        
        # Calculate populations for both radii
        walking_areas = self.find_areas_within_radius(latitude, longitude, walking_radius_km)
        driving_areas = self.find_areas_within_radius(latitude, longitude, driving_radius_km)
        
        # Calculate total populations
        walking_population = sum(area['population'] for area in walking_areas)
        driving_population = sum(area['population'] for area in driving_areas)
        
        # Calculate additional statistics
        walking_stats = {
            'total_population': walking_population,
            'num_areas': len(walking_areas)
        }
        
        driving_stats = {
            'total_population': driving_population,
            'num_areas': len(driving_areas)
        }
        
        return {
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'radii': {
                'walking_km': walking_radius_km,
                'driving_km': driving_radius_km
            },
            'walking_radius': walking_stats,
            'driving_radius': driving_stats
        }
    
    def get_detailed_analysis(self, latitude, longitude, walking_radius_km, driving_radius_km):
        """
        Get detailed analysis including individual area breakdowns.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            walking_radius_km (float): Walking distance radius in kilometers
            driving_radius_km (float): Driving distance radius in kilometers
            
        Returns:
            dict: Detailed analysis with individual area information
        """
        # Get basic stats
        basic_stats = self.calculate_population_stats(latitude, longitude, walking_radius_km, driving_radius_km)
        
        # Get detailed area information
        walking_areas = self.find_areas_within_radius(latitude, longitude, walking_radius_km)
        driving_areas = self.find_areas_within_radius(latitude, longitude, driving_radius_km)
        
        # Add detailed area breakdowns
        basic_stats['walking_radius']['areas'] = walking_areas
        basic_stats['driving_radius']['areas'] = driving_areas
        
        return basic_stats


# Example usage and testing
if __name__ == '__main__':
    # Example usage
    try:
        # Initialize with density data
        density_calculator = CensusData('data\density.geojson')
        
        # Example coordinates (Ottawa, Canada)
        latitude = 45.4215
        longitude = -75.6972
        walking_radius = 1.0  # 1 km walking radius
        driving_radius = 5.0  # 5 km driving radius
        
        # Calculate population statistics
        result = density_calculator.calculate_population_stats(latitude, longitude, walking_radius, driving_radius)
        
        print("Population Analysis")
        print("=" * 40)
        print(f"Location: {latitude}, {longitude}")
        print(f"Walking radius: {walking_radius} km")
        print(f"Driving radius: {driving_radius} km")
        print()
        
        print("Walking Radius Statistics:")
        print(f"  Total population: {result['walking_radius']['total_population']:,} people")
        print(f"  Number of areas: {result['walking_radius']['num_areas']}")
        print()
        
        print("Driving Radius Statistics:")
        print(f"  Total population: {result['driving_radius']['total_population']:,} people")
        print(f"  Number of areas: {result['driving_radius']['num_areas']}")
        
        # Example with affordability data (if available)
        try:
            affordability_calculator = CensusData('../data/affordability.geojson')
            affordability_result = affordability_calculator.calculate_population_stats(latitude, longitude, walking_radius, driving_radius)
            
            print("\n" + "=" * 40)
            print("Affordability Data Analysis:")
            print(f"Walking radius population: {affordability_result['walking_radius']['total_population']:,} people")
            print(f"Driving radius population: {affordability_result['driving_radius']['total_population']:,} people")
            
        except FileNotFoundError:
            print("\nAffordability data file not found, skipping affordability analysis.")
        
    except Exception as e:
        print(f"Error: {e}")
