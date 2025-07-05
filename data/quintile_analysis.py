import pandas as pd
import numpy as np

# Load the data
print("Loading census data...")
df = pd.read_csv('data/census_data.csv')

# Clean column names
df.columns = df.columns.str.strip()

print(f"Loaded {len(df)} census areas")
print(f"Total population: {df['Population'].sum():,}")

# Calculate population density
df['Population Density'] = df['Population'] / df['Area (sq km)']

# Define the metrics to analyze
metrics = {
    'Average Age': 'v_CA21_386: Average age',
    'Average Household Size': 'v_CA21_452: Average household size', 
    'Median Income': 'v_CA21_560: Median total income in 2020 among recipients ($)',
    'Median Dwelling Value': 'v_CA21_4311: Median value of dwellings ($) (60)',
    'Population Density': 'Population Density',
    'Area (sq km)': 'Area (sq km)',
    'Population': 'Population',
    'Dwellings': 'Dwellings',
    'Households': 'Households'
}

# Create quintiles based on population
print("\nCreating quintiles based on population...")
df['Population Quintile'] = pd.qcut(df['Population'], q=5, labels=['Q1 (Lowest 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest 20%)'])

print("\n" + "="*80)
print("QUINTILE ANALYSIS - MEDIAN VALUES BY POPULATION SEGMENT")
print("="*80)

# Analyze each metric
for metric_name, column in metrics.items():
    print(f"\n{metric_name}:")
    print("-" * 50)
    
    # Remove missing values
    valid_data = df[df[column].notna()].copy()
    
    if len(valid_data) > 0:
        # Calculate median for each quintile
        quintile_medians = valid_data.groupby('Population Quintile', observed=True)[column].median()
        
        # Calculate overall median for comparison
        overall_median = valid_data[column].median()
        
        # Calculate population-weighted median
        weighted_median = valid_data.groupby('Population Quintile', observed=True).apply(
            lambda x: np.median(np.repeat(x[column], x['Population']))
        )
        
        # Display results
        print(f"{'Quintile':<20} {'Median':<15} {'Weighted Median':<20} {'Count':<10}")
        print("-" * 65)
        
        for quintile in ['Q1 (Lowest 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest 20%)']:
            if quintile in quintile_medians.index:
                median_val = quintile_medians[quintile]
                weighted_med = weighted_median[quintile]
                count = len(valid_data[valid_data['Population Quintile'] == quintile])
                
                # Format based on metric type
                if 'Income' in metric_name or 'Value' in metric_name:
                    median_str = f"${median_val:,.0f}"
                    weighted_str = f"${weighted_med:,.0f}"
                elif 'Density' in metric_name:
                    median_str = f"{median_val:.1f} people/km²"
                    weighted_str = f"{weighted_med:.1f} people/km²"
                elif 'Area' in metric_name:
                    median_str = f"{median_val:.2f} km²"
                    weighted_str = f"{weighted_med:.2f} km²"
                else:
                    median_str = f"{median_val:.1f}"
                    weighted_str = f"{weighted_med:.1f}"
                
                print(f"{quintile:<20} {median_str:<15} {weighted_str:<20} {count:<10}")
        
        # Show overall median
        if 'Income' in metric_name or 'Value' in metric_name:
            overall_str = f"${overall_median:,.0f}"
        elif 'Density' in metric_name:
            overall_str = f"{overall_median:.1f} people/km²"
        elif 'Area' in metric_name:
            overall_str = f"{overall_median:.2f} km²"
        else:
            overall_str = f"{overall_median:.1f}"
        
        print("-" * 65)
        print(f"{'Overall Median':<20} {overall_str:<15} {'N/A':<20} {len(valid_data):<10}")
        print(f"Valid Records: {len(valid_data)}/{len(df)} ({len(valid_data)/len(df)*100:.1f}%)")
    else:
        print("No valid data found")

print("\n" + "="*80)
print("QUINTILE POPULATION STATISTICS")
print("="*80)

# Show population distribution across quintiles
quintile_stats = df.groupby('Population Quintile', observed=True).agg({
    'Population': ['count', 'sum', 'mean', 'median'],
    'Area (sq km)': ['sum', 'mean'],
    'Dwellings': 'sum',
    'Households': 'sum'
}).round(2)

print("\nPopulation Distribution:")
print("-" * 60)
for quintile in ['Q1 (Lowest 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest 20%)']:
    if quintile in quintile_stats.index:
        count = quintile_stats.loc[quintile, ('Population', 'count')]
        total_pop = quintile_stats.loc[quintile, ('Population', 'sum')]
        avg_pop = quintile_stats.loc[quintile, ('Population', 'mean')]
        median_pop = quintile_stats.loc[quintile, ('Population', 'median')]
        total_area = quintile_stats.loc[quintile, ('Area (sq km)', 'sum')]
        avg_area = quintile_stats.loc[quintile, ('Area (sq km)', 'mean')]
        
        print(f"{quintile}:")
        print(f"  Areas: {count:.0f}")
        print(f"  Total Population: {total_pop:,.0f}")
        print(f"  Average Population: {avg_pop:,.0f}")
        print(f"  Median Population: {median_pop:,.0f}")
        print(f"  Total Area: {total_area:,.1f} km²")
        print(f"  Average Area: {avg_area:.2f} km²")
        print()

print("\n" + "="*80)
print("SUMMARY TABLE - MEDIAN VALUES BY QUINTILE")
print("="*80)

# Create a summary table with proper formatting
summary_data = []
for metric_name, column in metrics.items():
    valid_data = df[df[column].notna()].copy()
    
    if len(valid_data) > 0:
        quintile_medians = valid_data.groupby('Population Quintile', observed=True)[column].median()
        
        # Create formatted row
        row = {'Metric': metric_name}
        for quintile in ['Q1 (Lowest 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest 20%)']:
            if quintile in quintile_medians.index:
                val = quintile_medians[quintile]
                
                # Format based on metric type
                if 'Income' in metric_name or 'Value' in metric_name:
                    row[quintile] = f"${val:,.0f}"
                elif 'Density' in metric_name:
                    row[quintile] = f"{val:.1f} people/km²"
                elif 'Area' in metric_name:
                    row[quintile] = f"{val:.2f} km²"
                else:
                    row[quintile] = f"{val:.1f}"
            else:
                row[quintile] = "N/A"
        
        summary_data.append(row)

# Create DataFrame with formatted strings
summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n" + "="*80)
print("QUINTILE RANGES")
print("="*80)

# Show the population ranges for each quintile
print("\nPopulation Ranges by Quintile:")
print("-" * 40)
quintile_ranges = df.groupby('Population Quintile', observed=True)['Population'].agg(['min', 'max']).round(0)
for quintile in ['Q1 (Lowest 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest 20%)']:
    if quintile in quintile_ranges.index:
        min_pop = quintile_ranges.loc[quintile, 'min']
        max_pop = quintile_ranges.loc[quintile, 'max']
        print(f"{quintile}: {min_pop:,.0f} - {max_pop:,.0f} people") 