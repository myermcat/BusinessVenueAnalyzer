#!/usr/bin/env python3
"""
Calculate weighted averages for census data metrics.
Uses population as the weight for all calculations.
"""

import pandas as pd
import numpy as np

def calculate_weighted_averages(csv_file_path):
    """
    Calculate weighted averages for all metrics in the census data.
    
    Args:
        csv_file_path (str): Path to the census_data.csv file
        
    Returns:
        dict: Dictionary containing weighted averages for each metric
    """
    
    # Read the CSV file
    print("Loading census data...")
    df = pd.read_csv(csv_file_path)
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    print(f"Loaded {len(df)} census areas")
    print(f"Total population: {df['Population '].sum():,}")
    
    # Define the metrics to calculate weighted averages for
    metrics = {
        'Average Age': 'v_CA21_386: Average age',
        'Average Household Size': 'v_CA21_452: Average household size',
        'Median Income': 'v_CA21_560: Median total income in 2020 among recipients ($)',
        'Median Dwelling Value': 'v_CA21_4311: Median value of dwellings ($) (60)'
    }
    
    # Calculate population density for each area
    df['Population Density'] = df['Population '] / df['Area (sq km)']
    
    # Add population density to metrics
    metrics['Population Density'] = 'Population Density'
    
    results = {}
    
    print("\nCalculating weighted averages...")
    print("=" * 60)
    
    for metric_name, column_name in metrics.items():
        if column_name in df.columns:
            # Remove rows with missing values
            valid_data = df[df[column_name].notna()]
            
            if len(valid_data) > 0:
                # Calculate weighted average using population as weight
                weighted_sum = (valid_data[column_name] * valid_data['Population ']).sum()
                total_weight = valid_data['Population '].sum()
                
                if total_weight > 0:
                    weighted_average = weighted_sum / total_weight
                    
                    # Calculate additional statistics
                    simple_average = valid_data[column_name].mean()
                    median_value = valid_data[column_name].median()
                    min_value = valid_data[column_name].min()
                    max_value = valid_data[column_name].max()
                    std_dev = valid_data[column_name].std()
                    
                    results[metric_name] = {
                        'weighted_average': weighted_average,
                        'simple_average': simple_average,
                        'median': median_value,
                        'min': min_value,
                        'max': max_value,
                        'std_dev': std_dev,
                        'valid_records': len(valid_data),
                        'total_records': len(df)
                    }
                    
                    # Format output based on metric type
                    if 'Income' in metric_name or 'Value' in metric_name:
                        print(f"{metric_name}:")
                        print(f"  Weighted Average: ${weighted_average:,.0f}")
                        print(f"  Simple Average:   ${simple_average:,.0f}")
                        print(f"  Median:           ${median_value:,.0f}")
                        print(f"  Range:            ${min_value:,.0f} - ${max_value:,.0f}")
                    elif 'Density' in metric_name:
                        print(f"{metric_name}:")
                        print(f"  Weighted Average: {weighted_average:.1f} people/km²")
                        print(f"  Simple Average:   {simple_average:.1f} people/km²")
                        print(f"  Median:           {median_value:.1f} people/km²")
                        print(f"  Range:            {min_value:.1f} - {max_value:.1f} people/km²")
                    else:
                        print(f"{metric_name}:")
                        print(f"  Weighted Average: {weighted_average:.1f}")
                        print(f"  Simple Average:   {simple_average:.1f}")
                        print(f"  Median:           {median_value:.1f}")
                        print(f"  Range:            {min_value:.1f} - {max_value:.1f}")
                    
                    print(f"  Valid Records:    {len(valid_data)}/{len(df)} ({len(valid_data)/len(df)*100:.1f}%)")
                    print()
                else:
                    print(f"{metric_name}: No valid population data")
                    print()
            else:
                print(f"{metric_name}: No valid data found")
                print()
        else:
            print(f"{metric_name}: Column '{column_name}' not found")
            print()
    
    # Calculate additional aggregate statistics
    print("Additional Statistics:")
    print("=" * 60)
    
    # Total area and population
    total_area = df['Area (sq km)'].sum()
    total_population = df['Population '].sum()
    overall_density = total_population / total_area
    
    print(f"Total Area:        {total_area:,.1f} km²")
    print(f"Total Population:  {total_population:,}")
    print(f"Overall Density:   {overall_density:.1f} people/km²")
    
    # Housing statistics
    total_dwellings = df['Dwellings '].sum()
    total_households = df['Households '].sum()
    
    print(f"Total Dwellings:   {total_dwellings:,}")
    print(f"Total Households:  {total_households:,}")
    print(f"Dwelling/Household Ratio: {total_dwellings/total_households:.2f}")
    
    return results

def print_summary_table(results):
    """Print a summary table of the weighted averages"""
    
    print("\n" + "=" * 80)
    print("SUMMARY TABLE - WEIGHTED AVERAGES")
    print("=" * 80)
    
    # Create a summary table with proper data types
    summary_data = []
    for metric_name, stats in results.items():
        summary_data.append({
            'Metric': metric_name,
            'Weighted Average': stats['weighted_average'],
            'Simple Average': stats['simple_average'],
            'Median': stats['median'],
            'Valid Records': f"{stats['valid_records']}/{stats['total_records']}"
        })
    
    # Create DataFrame with explicit dtypes
    summary_df = pd.DataFrame(summary_data)
    
    # Format the numeric columns based on metric type
    formatted_data = []
    for _, row in summary_df.iterrows():
        metric = row['Metric']
        weighted_avg = row['Weighted Average']
        simple_avg = row['Simple Average']
        median_val = row['Median']
        
        # Format based on metric type
        if 'Income' in metric or 'Value' in metric:
            formatted_weighted = f"${weighted_avg:,.0f}"
            formatted_simple = f"${simple_avg:,.0f}"
            formatted_median = f"${median_val:,.0f}"
        elif 'Density' in metric:
            formatted_weighted = f"{weighted_avg:.1f} people/km²"
            formatted_simple = f"{simple_avg:.1f} people/km²"
            formatted_median = f"{median_val:.1f} people/km²"
        else:
            formatted_weighted = f"{weighted_avg:.1f}"
            formatted_simple = f"{simple_avg:.1f}"
            formatted_median = f"{median_val:.1f}"
        
        formatted_data.append({
            'Metric': metric,
            'Weighted Average': formatted_weighted,
            'Simple Average': formatted_simple,
            'Median': formatted_median,
            'Valid Records': row['Valid Records']
        })
    
    # Create final DataFrame with formatted strings
    final_df = pd.DataFrame(formatted_data)
    print(final_df.to_string(index=False))
    print("\nNote: Weighted averages use population as the weight for each census area.")

if __name__ == "__main__":
    try:
        # Calculate weighted averages
        results = calculate_weighted_averages('data/census_data.csv')
        
        # Print summary table
        print_summary_table(results)
        
    except FileNotFoundError:
        print("Error: census_data.csv file not found in the data directory.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc() 