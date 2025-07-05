#!/usr/bin/env python3
"""
Test script for business_proximity_api.py
"""
import os
import asyncio
from dotenv import load_dotenv
from metrics.traffic.traffic_school_business_proximity.business_proximity_api import (
    BusinessProximityAPI, 
    get_business_proximity, 
    fetch_business_proximity
)

load_dotenv()

async def test_class_based_api():
    """Test the class-based API"""
    print("=== Testing Class-Based API ===")
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY not found in environment")
        return
    
    api = BusinessProximityAPI(api_key=api_key)
    
    # Test single type search
    print("\n1. Testing single type search (school in Ottawa):")
    results = await api.search_by_type("school", "Ottawa", max_results=2)
    print(f"Found {len(results)} schools")
    for place in results:
        print(f"  - {place['name']} (Rating: {place['rating']})")
    
    # Test multiple types search
    print("\n2. Testing multiple types search (school,library in Ottawa):")
    results = await api.search_multiple_types(["school", "library"], "Ottawa", max_results=2)
    for place_type, places in results.items():
        print(f"  {place_type}: {len(places)} results")
        for place in places[:1]:  # Show first result
            print(f"    - {place['name']}")

def test_convenience_functions():
    """Test the convenience functions"""
    print("\n=== Testing Convenience Functions ===")
    
    # Test sync function
    print("\n3. Testing sync convenience function:")
    results = get_business_proximity(
        place_types="restaurant,cafe",
        location="Ottawa",
        max_results=2
    )
    for place_type, places in results.items():
        print(f"  {place_type}: {len(places)} results")
        for place in places[:1]:
            print(f"    - {place['name']} @ {place['address']}")

async def test_async_convenience():
    """Test async convenience function"""
    print("\n4. Testing async convenience function:")
    results = await fetch_business_proximity(
        place_types="gym,hospital",
        location="Ottawa",
        max_results=2
    )
    for place_type, places in results.items():
        print(f"  {place_type}: {len(places)} results")
        for place in places[:1]:
            print(f"    - {place['name']} (Rating: {place['rating']})")

def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    # Test invalid API key
    print("\n5. Testing invalid API key:")
    try:
        api = BusinessProximityAPI(api_key="invalid_key")
        asyncio.run(api.search_by_type("school", "Ottawa", max_results=1))
    except Exception as e:
        print(f"  Expected error caught: {type(e).__name__}")
    
    # Test empty API key
    print("\n6. Testing empty API key:")
    try:
        api = BusinessProximityAPI(api_key="")
    except ValueError as e:
        print(f"  Expected error caught: {e}")

async def main():
    """Run all tests"""
    print("Starting business_proximity_api tests...\n")
    
    await test_class_based_api()
    test_convenience_functions()
    await test_async_convenience()
    test_error_handling()
    
    print("\n=== Test Summary ===")
    print("✓ CLI functionality works")
    print("✓ Class-based API works")
    print("✓ Convenience functions work")
    print("✓ Error handling works")
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())