
import pandas as pd
import numpy as np

# Load the datasets, skipping the header rows
df_2024 = pd.read_csv('Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2024.csv', skiprows=9)
df_2025 = pd.read_csv('Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2025.csv', skiprows=9)

# The GA4 export might have a summary row at the end, let's remove it if it exists.
# It usually contains non-data strings like "Grand Total"
df_2024 = df_2024[pd.to_numeric(df_2024['Sessions'], errors='coerce').notna()]
df_2025 = df_2025[pd.to_numeric(df_2025['Sessions'], errors='coerce').notna()]


# Convert sessions to numeric
df_2024['Sessions'] = pd.to_numeric(df_2024['Sessions'])
df_2025['Sessions'] = pd.to_numeric(df_2025['Sessions'])


# The 2024 data is for the full year, and 2025 is until Nov 26.
# To make a fair comparison, we should adjust the 2024 data to the same period.
# The 2025 data is for 330 days (Jan 1 to Nov 26).
# The 2024 data is for 366 days (leap year).
days_in_2025_period = 330
days_in_2024 = 366
pro_rata_factor = days_in_2025_period / days_in_2024

df_2024['adjusted_sessions_2024'] = df_2024['Sessions'] * pro_rata_factor

# Rename columns for merging
df_2024.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'adjusted_sessions_2024': 'sessions_2024'}, inplace=True)
df_2025.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'Sessions': 'sessions_2025'}, inplace=True)

# Merge the dataframes on the channel
df_merged = pd.merge(df_2024[['channel', 'sessions_2024']], df_2025[['channel', 'sessions_2025']], on='channel', how='outer').fillna(0)

# Calculate the change and percentage change
df_merged['change'] = df_merged['sessions_2025'] - df_merged['sessions_2024']
# handle division by zero
df_merged['percentage_change'] = np.where(df_merged['sessions_2024'] > 0, (df_merged['change'] / df_merged['sessions_2024']) * 100, 0)


print("Traffic Analysis Report:")
print("="*30)
print(df_merged[['channel', 'sessions_2024', 'sessions_2025', 'percentage_change']])
print("="*30)


# Summarize the findings
total_sessions_2024 = df_merged['sessions_2024'].sum()
total_sessions_2025 = df_merged['sessions_2025'].sum()
total_change = total_sessions_2025 - total_sessions_2024
total_percentage_change = (total_change / total_sessions_2024) * 100 if total_sessions_2024 > 0 else 0

print(f"\nOverall Traffic Change: {total_percentage_change:.2f}%")

# Specific channel analysis
organic_search = df_merged[df_merged['channel'] == 'Organic Search']
direct = df_merged[df_merged['channel'] == 'Direct']
paid_referral_channels = ['Paid Search', 'Referral', 'Paid Social', 'Organic Social', 'Email', 'Display']
paid_referral = df_merged[df_merged['channel'].isin(paid_referral_channels)]

def get_channel_change(df, channel_name):
    if not df.empty:
        return df['percentage_change'].values[0]
    return 0.0

organic_search_change = get_channel_change(organic_search, 'Organic Search')
direct_change = get_channel_change(direct, 'Direct')

paid_referral_2024 = paid_referral['sessions_2024'].sum()
paid_referral_2025 = paid_referral['sessions_2025'].sum()
paid_referral_change = ((paid_referral_2025 - paid_referral_2024) / paid_referral_2024) * 100 if paid_referral_2024 > 0 else 0

print(f"\nChannel-Specific Changes:")
print(f"- Organic Search Traffic Change: {organic_search_change:.2f}%")
print(f"- Direct Traffic Change: {direct_change:.2f}%")
print(f"- Paid/Referral Traffic Change: {paid_referral_change:.2f}%")

if total_percentage_change < -30:
    print("\nConclusion: The total traffic drop from last year is confirmed to be over 30%.")
else:
    print("\nConclusion: The total traffic drop is not over 30%.")

all_channels_dropped = all(df_merged['percentage_change'] < 0)
if all_channels_dropped:
    print("All channels experienced a traffic drop.")
else:
    print("Not all channels experienced a traffic drop.")

if organic_search_change < 0 and direct_change < 0 and paid_referral_change < 0:
    print("The drop is across Organic Search, Direct, and Paid/Referral channels.")
else:
    if organic_search_change < 0:
        print("There is a drop in Organic Search traffic.")
    if direct_change < 0:
        print("There is a drop in Direct traffic.")
    if paid_referral_change < 0:
        print("There is a drop in Paid/Referral traffic.")
