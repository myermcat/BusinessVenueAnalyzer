from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os
import sys

# Add the parent directory to Python path to import census_metric and address validator
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from metrics.census.census_metric import CensusDataProcessor
from utils.address_validator import AddressValidator

app = FastAPI(title="Census Demographics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the census processor and address validator
try:
    census_processor = CensusDataProcessor(
        geojson_path="../data/census.geojson",
        csv_path="../data/census_data.csv"
    )
except Exception as e:
    print(f"Warning: Could not initialize census processor: {e}")
    census_processor = None

try:
    address_validator = AddressValidator()
except Exception as e:
    print(f"Warning: Could not initialize address validator: {e}")
    address_validator = None


class CensusAnalysisRequest(BaseModel):
    # Support both address and coordinates
    address: Optional[str] = Field(None, description="Address to analyze (e.g., 'centretown ottawa canada')")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of the location")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of the location")
    walking_radius_km: float = Field(default=1.0, gt=0, le=10, description="Walking radius in kilometers")
    driving_radius_km: float = Field(default=5.0, gt=0, le=50, description="Driving radius in kilometers")
    include_detailed_areas: bool = Field(default=False, description="Include detailed area breakdown")
    
    def model_validate(cls, values):
        # Ensure either address or both lat/lng are provided
        address = values.get('address')
        latitude = values.get('latitude')
        longitude = values.get('longitude')
        
        if not address and not (latitude is not None and longitude is not None):
            raise ValueError('Either address or both latitude and longitude must be provided')
        
        return values


class AreaInfo(BaseModel):
    geo_uid: str
    distance_km: float
    population: int
    population_density: float
    median_income: float
    median_dwelling_value: float
    average_age: float
    average_household_size: float
    households: int
    dwellings: int
    area_sq_km: float


class RadiusStats(BaseModel):
    total_population: int
    num_areas: int
    avg_population_density: float
    avg_median_income: float
    avg_median_dwelling_value: float
    avg_age: float
    avg_household_size: float
    total_households: int
    total_dwellings: int
    total_area_km2: float
    areas: Optional[List[AreaInfo]] = None


class LocationInfo(BaseModel):
    latitude: float
    longitude: float


class RadiiInfo(BaseModel):
    walking_km: float
    driving_km: float


class CensusAnalysisResponse(BaseModel):
    location: LocationInfo
    radii: RadiiInfo
    walking_radius: RadiusStats
    driving_radius: RadiusStats
    address_validation: Optional[Dict] = None  # Include address validation info if address was provided


@app.post("/api/v1/census/analyze", response_model=CensusAnalysisResponse)
async def analyze_demographics(request: CensusAnalysisRequest):
    """
    Analyze demographic data for a given location within walking and driving radii.
    
    Accepts either:
    - Text address (e.g., "centretown ottawa canada") - will be geocoded automatically
    - Latitude and longitude coordinates
    
    Returns comprehensive demographic statistics including population density,
    median income, dwelling values, and age demographics.
    """
    if not census_processor:
        raise HTTPException(
            status_code=500, 
            detail="Census data processor not available. Check data files."
        )
    
    try:
        # Validate walking radius is not larger than driving radius
        if request.walking_radius_km > request.driving_radius_km:
            raise HTTPException(
                status_code=400,
                detail="Walking radius cannot be larger than driving radius"
            )
        
        # Determine coordinates
        latitude = request.latitude
        longitude = request.longitude
        address_validation_info = None
        
        # If address is provided, validate and get coordinates
        if request.address:
            if not address_validator:
                raise HTTPException(
                    status_code=500,
                    detail="Address validator not available"
                )
            
            validation_result = address_validator.validate_address(request.address)
            
            if not validation_result['valid']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Address validation failed: {validation_result.get('error', 'Unknown error')}"
                )
            
            latitude = validation_result['latitude']
            longitude = validation_result['longitude']
            address_validation_info = {
                'original_address': request.address,
                'validated_address': validation_result['display_name'],
                'confidence': validation_result['confidence'],
                'coordinates_source': 'geocoded'
            }
        else:
            address_validation_info = {
                'coordinates_source': 'provided_directly'
            }
        
        # Ensure we have valid coordinates
        if latitude is None or longitude is None:
            raise HTTPException(
                status_code=400,
                detail="Could not determine valid coordinates from the provided input"
            )
        
        # Get demographic analysis
        if request.include_detailed_areas:
            result = census_processor.get_detailed_analysis(
                latitude,
                longitude,
                request.walking_radius_km,
                request.driving_radius_km
            )
        else:
            result = census_processor.calculate_demographic_stats(
                latitude,
                longitude,
                request.walking_radius_km,
                request.driving_radius_km
            )
        
        # Convert areas to AreaInfo objects if they exist
        if 'areas' in result.get('walking_radius', {}):
            walking_areas = [AreaInfo(**area) for area in result['walking_radius']['areas']]
            result['walking_radius']['areas'] = walking_areas
        
        if 'areas' in result.get('driving_radius', {}):
            driving_areas = [AreaInfo(**area) for area in result['driving_radius']['areas']]
            result['driving_radius']['areas'] = driving_areas
        
        # Add address validation info to response
        result['address_validation'] = address_validation_info
        
        return CensusAnalysisResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/v1/census/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "census_processor_available": census_processor is not None,
        "address_validator_available": address_validator is not None,
        "message": "Census Demographics API is running"
    }


@app.get("/api/v1/census/stats")
async def get_data_stats():
    """Get statistics about the loaded census data"""
    if not census_processor:
        raise HTTPException(
            status_code=500,
            detail="Census data processor not available"
        )
    
    try:
        total_areas = len(census_processor.combined_data)
        total_population = sum(
            area.get('population', 0) 
            for area in census_processor.combined_data.values()
        )
        
        return {
            "total_census_areas": total_areas,
            "total_population_covered": total_population,
            "data_sources": ["census.geojson", "census_data.csv"],
            "available_metrics": [
                "population",
                "population_density", 
                "median_income",
                "median_dwelling_value",
                "average_age",
                "average_household_size",
                "households",
                "dwellings"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)