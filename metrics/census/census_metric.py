import json
import csv
import math
from typing import Dict, List, Optional, Tuple
import pandas as pd

class CensusDataProcessor:
    """
    A class to process and combine census data from both census.geojson and census_data.csv files.
    Matches GeoUID from CSV with ID from GeoJSON to provide comprehensive demographic analysis.

    gives the following metrics:
    - population density
    - median income
    - median dwelling value
    - average age
    - average household size
    - total households

    use this class by calling the calculate_demographic_stats method with the following arguments:
    - latitude: float
    - longitude: float
    - walking_radius_km: float
    - driving_radius_km: float

    this will return a dictionary with the following keys: 
    - location: dictionary with latitude and longitude
    - radii: dictionary with walking and driving radii
    - walking_radius: dictionary with the following keys:
        - total_population: int
        - num_areas: int
        - avg_population_density: float
        - avg_median_income: float
    """
    
    def __init__(self, geojson_path: str = "data/census.geojson", csv_path: str = "data/census_data.csv"):
        """
        Initialize the processor with both census data files.
        
        Args:
            geojson_path (str): Path to the census.geojson file
            csv_path (str): Path to the census_data.csv file
        """
        self.geojson_path = geojson_path
        self.csv_path = csv_path
        self.geojson_data = self._load_geojson_data()
        self.csv_data = self._load_csv_data()
        self.combined_data = self._combine_data()
    
    def _load_geojson_data(self) -> Dict:
        """Load and parse the census.geojson file"""
        try:
            with open(self.geojson_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"GeoJSON data file not found: {self.geojson_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in GeoJSON data file: {self.geojson_path}")
    
    def _load_csv_data(self) -> pd.DataFrame:
        """Load and parse the census_data.csv file"""
        try:
            df = pd.read_csv(self.csv_path)
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV data file not found: {self.csv_path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    
    def _combine_data(self) -> Dict[str, Dict]:
        """
        Combine GeoJSON and CSV data by matching GeoUID from CSV with ID from GeoJSON.
        
        Returns:
            Dict: Combined data with GeoUID as key
        """
        combined = {}
        
        # Create a mapping from GeoJSON ID to feature
        geojson_mapping = {}
        for feature in self.geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geo_id = properties.get('id')
            if geo_id:
                geojson_mapping[geo_id] = feature
        
        # Combine with CSV data
        for _, row in self.csv_data.iterrows():
            geo_uid = str(row['GeoUID'])
            
            if geo_uid in geojson_mapping:
                geojson_feature = geojson_mapping[geo_uid]
                
                # Combine properties
                combined_properties = {
                    # GeoJSON properties
                    'geometry': geojson_feature.get('geometry'),
                    'area_sq_km': float(geojson_feature.get('properties', {}).get('a', 0)),
                    'type': geojson_feature.get('properties', {}).get('t', ''),
                    
                    # CSV properties
                    'population': int(row['Population ']) if pd.notna(row['Population ']) else 0,
                    'dwellings': int(row['Dwellings ']) if pd.notna(row['Dwellings ']) else 0,
                    'households': int(row['Households ']) if pd.notna(row['Households ']) else 0,
                    'average_age': float(row['v_CA21_386: Average age']) if pd.notna(row['v_CA21_386: Average age']) else 0,
                    'average_household_size': float(row['v_CA21_452: Average household size']) if pd.notna(row['v_CA21_452: Average household size']) else 0,
                    'median_income': float(row['v_CA21_560: Median total income in 2020 among recipients ($)']) if pd.notna(row['v_CA21_560: Median total income in 2020 among recipients ($)']) else 0,
                    'median_dwelling_value': float(row['v_CA21_4311: Median value of dwellings ($) (60)']) if pd.notna(row['v_CA21_4311: Median value of dwellings ($) (60)']) else 0,
                    
                    # Calculated properties
                    'population_density': self._calculate_population_density(
                        int(row['Population ']) if pd.notna(row['Population ']) else 0,
                        float(geojson_feature.get('properties', {}).get('a', 0))
                    )
                }
                
                combined[geo_uid] = combined_properties
        
        return combined
    
    def _calculate_population_density(self, population: int, area_sq_km: float) -> float:
        """Calculate population density per square kilometer"""
        if area_sq_km > 0:
            return population / area_sq_km
        return 0.0
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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
    
    def _calculate_centroid(self, coordinates: List[List[List[float]]]) -> Tuple[float, float]:
        """Calculate centroid of a MultiPolygon geometry"""
        all_lats = []
        all_lons = []
        
        for polygon in coordinates:
            for ring in polygon:
                for coord in ring:
                    all_lons.append(coord[0])
                    all_lats.append(coord[1])
        
        if all_lats and all_lons:
            return sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)
        return 0.0, 0.0
    
    def find_areas_within_radius(self, center_lat: float, center_lon: float, radius_km: float) -> List[Dict]:
        """
        Find all census areas within the specified radius.
        
        Args:
            center_lat (float): Latitude of center point
            center_lon (float): Longitude of center point
            radius_km (float): Radius in kilometers
            
        Returns:
            list: List of dictionaries containing area information
        """
        areas_within_radius = []
        
        for geo_uid, area_data in self.combined_data.items():
            geometry = area_data.get('geometry')
            
            if geometry and geometry.get('type') == 'MultiPolygon':
                centroid_lat, centroid_lon = self._calculate_centroid(geometry['coordinates'])
                
                if centroid_lat != 0.0 and centroid_lon != 0.0:
                    distance = self.calculate_distance(center_lat, center_lon, centroid_lat, centroid_lon)
                    
                    if distance <= radius_km:
                        area_info = {
                            'geo_uid': geo_uid,
                            'distance_km': distance,
                            'population': area_data.get('population', 0),
                            'population_density': area_data.get('population_density', 0),
                            'median_income': area_data.get('median_income', 0),
                            'median_dwelling_value': area_data.get('median_dwelling_value', 0),
                            'average_age': area_data.get('average_age', 0),
                            'average_household_size': area_data.get('average_household_size', 0),
                            'households': area_data.get('households', 0),
                            'dwellings': area_data.get('dwellings', 0),
                            'area_sq_km': area_data.get('area_sq_km', 0)
                        }
                        areas_within_radius.append(area_info)
        
        return areas_within_radius
    
    def calculate_demographic_stats(self, latitude: float, longitude: float, 
                                  walking_radius_km: float, driving_radius_km: float) -> Dict:
        """
        Calculate comprehensive demographic statistics for both walking and driving radii.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            walking_radius_km (float): Walking distance radius in kilometers
            driving_radius_km (float): Driving distance radius in kilometers
            
        Returns:
            dict: Dictionary containing demographic statistics for both radii
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
        
        # Find areas for both radii
        walking_areas = self.find_areas_within_radius(latitude, longitude, walking_radius_km)
        driving_areas = self.find_areas_within_radius(latitude, longitude, driving_radius_km)
        
        # Calculate statistics for walking radius
        walking_stats = self._calculate_area_stats(walking_areas)
        
        # Calculate statistics for driving radius
        driving_stats = self._calculate_area_stats(driving_areas)
        
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
    
    def _calculate_area_stats(self, areas: List[Dict]) -> Dict:
        """Calculate statistics for a list of areas"""
        if not areas:
            return {
                'total_population': 0,
                'num_areas': 0,
                'avg_population_density': 0,
                'avg_median_income': 0,
                'avg_median_dwelling_value': 0,
                'avg_age': 0,
                'avg_household_size': 0,
                'total_households': 0,
                'total_dwellings': 0,
                'total_area_km2': 0
            }
        
        total_population = sum(area['population'] for area in areas)
        total_households = sum(area['households'] for area in areas)
        total_dwellings = sum(area['dwellings'] for area in areas)
        total_area = sum(area['area_sq_km'] for area in areas)
        
        # Calculate weighted averages
        weighted_income = sum(area['population'] * area['median_income'] for area in areas if area['median_income'] > 0)
        weighted_dwelling_value = sum(area['population'] * area['median_dwelling_value'] for area in areas if area['median_dwelling_value'] > 0)
        weighted_age = sum(area['population'] * area['average_age'] for area in areas if area['average_age'] > 0)
        weighted_household_size = sum(area['population'] * area['average_household_size'] for area in areas if area['average_household_size'] > 0)
        
        return {
            'total_population': total_population,
            'num_areas': len(areas),
            'avg_population_density': round(total_population / total_area, 2) if total_area > 0 else 0,
            'avg_median_income': round(weighted_income / total_population, 2) if total_population > 0 else 0,
            'avg_median_dwelling_value': round(weighted_dwelling_value / total_population, 2) if total_population > 0 else 0,
            'avg_age': round(weighted_age / total_population, 1) if total_population > 0 else 0,
            'avg_household_size': round(weighted_household_size / total_population, 2) if total_population > 0 else 0,
            'total_households': total_households,
            'total_dwellings': total_dwellings,
            'total_area_km2': round(total_area, 2)
        }
    
    def get_detailed_analysis(self, latitude: float, longitude: float, 
                            walking_radius_km: float, driving_radius_km: float) -> Dict:
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
        basic_stats = self.calculate_demographic_stats(latitude, longitude, walking_radius_km, driving_radius_km)
        
        # Get detailed area information
        walking_areas = self.find_areas_within_radius(latitude, longitude, walking_radius_km)
        driving_areas = self.find_areas_within_radius(latitude, longitude, driving_radius_km)
        
        # Add detailed area breakdowns
        basic_stats['walking_radius']['areas'] = walking_areas
        basic_stats['driving_radius']['areas'] = driving_areas
        
        return basic_stats


# Example usage and testing
if __name__ == '__main__':
    try:
        # Initialize the processor
        processor = CensusDataProcessor()
        
        # Example coordinates (Ottawa, Canada)
        latitude = 45.4215
        longitude = -75.6972
        walking_radius = 1.0  # 1 km walking radius
        driving_radius = 5.0  # 5 km driving radius
        
        # Calculate demographic statistics
        result = processor.calculate_demographic_stats(latitude, longitude, walking_radius, driving_radius)
        
        print("Census Data Analysis")
        print("=" * 50)
        print(f"Location: {latitude}, {longitude}")
        print(f"Walking radius: {walking_radius} km")
        print(f"Driving radius: {driving_radius} km")
        print()
        
        print("Walking Radius Statistics:")
        print(f"  Total population: {result['walking_radius']['total_population']:,} people")
        print(f"  Number of areas: {result['walking_radius']['num_areas']}")
        print(f"  Average population density: {result['walking_radius']['avg_population_density']} people/km²")
        print(f"  Average median income: ${result['walking_radius']['avg_median_income']:,}")
        print(f"  Average median dwelling value: ${result['walking_radius']['avg_median_dwelling_value']:,}")
        print(f"  Average age: {result['walking_radius']['avg_age']} years")
        print(f"  Average household size: {result['walking_radius']['avg_household_size']}")
        print()
        
        print("Driving Radius Statistics:")
        print(f"  Total population: {result['driving_radius']['total_population']:,} people")
        print(f"  Number of areas: {result['driving_radius']['num_areas']}")
        print(f"  Average population density: {result['driving_radius']['avg_population_density']} people/km²")
        print(f"  Average median income: ${result['driving_radius']['avg_median_income']:,}")
        print(f"  Average median dwelling value: ${result['driving_radius']['avg_median_dwelling_value']:,}")
        print(f"  Average age: {result['driving_radius']['avg_age']} years")
        print(f"  Average household size: {result['driving_radius']['avg_household_size']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure both census.geojson and census_data.csv files exist in the data directory.") 