import pandas as pd
import numpy as np

# Load the data
print("Loading census data...")
df = pd.read_csv('data/census_data.csv')

# Clean column names
df.columns = df.columns.str.strip()

print(f"Loaded {len(df)} census areas")
print(f"Total population: {df['Population '].sum():,}")

# Calculate population density
df['Population Density'] = df['Population '] / df['Area (sq km)']

print("\n" + "="*60)
print("WEIGHTED AVERAGES (Population-weighted)")
print("="*60)

# Calculate weighted averages for each metric
metrics = {
    'Average Age': 'v_CA21_386: Average age',
    'Average Household Size': 'v_CA21_452: Average household size', 
    'Median Income': 'v_CA21_560: Median total income in 2020 among recipients ($)',
    'Median Dwelling Value': 'v_CA21_4311: Median value of dwellings ($) (60)',
    'Population Density': 'Population Density'
}

for metric_name, column in metrics.items():
    # Remove missing values
    valid_data = df[df[column].notna()]
    
    if len(valid_data) > 0:
        # Calculate weighted average
        weighted_sum = (valid_data[column] * valid_data['Population ']).sum()
        total_weight = valid_data['Population '].sum()
        weighted_avg = weighted_sum / total_weight
        
        # Calculate simple average for comparison
        simple_avg = valid_data[column].mean()
        
        print(f"\n{metric_name}:")
        if 'Income' in metric_name or 'Value' in metric_name:
            print(f"  Weighted Average: ${weighted_avg:,.0f}")
            print(f"  Simple Average:   ${simple_avg:,.0f}")
        elif 'Density' in metric_name:
            print(f"  Weighted Average: {weighted_avg:.1f} people/km²")
            print(f"  Simple Average:   {simple_avg:.1f} people/km²")
        else:
            print(f"  Weighted Average: {weighted_avg:.1f}")
            print(f"  Simple Average:   {simple_avg:.1f}")
        
        print(f"  Valid Records:    {len(valid_data)}/{len(df)} ({len(valid_data)/len(df)*100:.1f}%)")

print("\n" + "="*60)
print("ADDITIONAL STATISTICS")
print("="*60)

# Overall statistics
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

print("\n" + "="*60)
print("SUMMARY TABLE")
print("="*60)

# Create summary table
summary_data = []
for metric_name, column in metrics.items():
    valid_data = df[df[column].notna()]
    if len(valid_data) > 0:
        weighted_sum = (valid_data[column] * valid_data['Population ']).sum()
        total_weight = valid_data['Population '].sum()
        weighted_avg = weighted_sum / total_weight
        simple_avg = valid_data[column].mean()
        
        summary_data.append({
            'Metric': metric_name,
            'Weighted Avg': weighted_avg,
            'Simple Avg': simple_avg,
            'Records': f"{len(valid_data)}/{len(df)}"
        })

summary_df = pd.DataFrame(summary_data)

# Format the output
for i, row in summary_df.iterrows():
    metric = row['Metric']
    if 'Income' in metric or 'Value' in metric:
        summary_df.loc[i, 'Weighted Avg'] = f"${row['Weighted Avg']:,.0f}"
        summary_df.loc[i, 'Simple Avg'] = f"${row['Simple Avg']:,.0f}"
    elif 'Density' in metric:
        summary_df.loc[i, 'Weighted Avg'] = f"{row['Weighted Avg']:.1f} people/km²"
        summary_df.loc[i, 'Simple Avg'] = f"{row['Simple Avg']:.1f} people/km²"
    else:
        summary_df.loc[i, 'Weighted Avg'] = f"{row['Weighted Avg']:.1f}"
        summary_df.loc[i, 'Simple Avg'] = f"{row['Simple Avg']:.1f}"

print(summary_df.to_string(index=False)) 