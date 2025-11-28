
import pandas as pd
import numpy as np

def analyze_traffic():
    # File paths
    file_2024 = 'Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)_2024_JantoNov.csv'
    file_2025 = 'Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)_2025_JantoNov.csv'

    print(f"Reading files:\n- {file_2024}\n- {file_2025}\n")

    # Load the datasets, skipping the header rows (first 9 rows are metadata)
    try:
        df_2024 = pd.read_csv(file_2024, skiprows=9)
        df_2025 = pd.read_csv(file_2025, skiprows=9)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Filter out summary rows (where 'Sessions' is not a number)
    df_2024 = df_2024[pd.to_numeric(df_2024['Sessions'], errors='coerce').notna()]
    df_2025 = df_2025[pd.to_numeric(df_2025['Sessions'], errors='coerce').notna()]

    # Convert sessions to numeric
    df_2024['Sessions'] = pd.to_numeric(df_2024['Sessions'])
    df_2025['Sessions'] = pd.to_numeric(df_2025['Sessions'])

    # Rename columns for merging
    df_2024.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'Sessions': 'sessions_2024'}, inplace=True)
    df_2025.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'Sessions': 'sessions_2025'}, inplace=True)

    # Merge the dataframes on the channel
    df_merged = pd.merge(df_2024[['channel', 'sessions_2024']], df_2025[['channel', 'sessions_2025']], on='channel', how='outer').fillna(0)

    # Calculate the change and percentage change
    df_merged['change'] = df_merged['sessions_2025'] - df_merged['sessions_2024']
    
    # Calculate percentage change, handling division by zero
    df_merged['percentage_change'] = np.where(
        df_merged['sessions_2024'] > 0, 
        (df_merged['change'] / df_merged['sessions_2024']) * 100, 
        0
    )

    # Sort by sessions_2024 descending to see biggest channels first
    df_merged = df_merged.sort_values(by='sessions_2024', ascending=False)

    print("Traffic Analysis Report (Jan-Nov 2024 vs Jan-Nov 2025):")
    print("-" * 80)
    print(f"{'Channel':<30} | {'2024 Sessions':<15} | {'2025 Sessions':<15} | {'Change %':<10}")
    print("-" * 80)

    for index, row in df_merged.iterrows():
        print(f"{row['channel']:<30} | {int(row['sessions_2024']):<15} | {int(row['sessions_2025']):<15} | {row['percentage_change']:>9.2f}%")
    
    print("-" * 80)

    # Overall Summary
    total_2024 = df_merged['sessions_2024'].sum()
    total_2025 = df_merged['sessions_2025'].sum()
    total_pct_change = ((total_2025 - total_2024) / total_2024 * 100) if total_2024 > 0 else 0

    print(f"{'TOTAL':<30} | {int(total_2024):<15} | {int(total_2025):<15} | {total_pct_change:>9.2f}%")
    print("-" * 80)

if __name__ == "__main__":
    analyze_traffic()
