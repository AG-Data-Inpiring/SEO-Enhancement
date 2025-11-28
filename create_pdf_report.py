
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load the datasets, skipping the header rows
df_2024 = pd.read_csv('Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2024.csv', skiprows=9)
df_2025 = pd.read_csv('Traffic_acquisition_Session_primary_channel_group_(Default_Channel_Group)-2025.csv', skiprows=9)

# The GA4 export might have a summary row at the end, let's remove it if it exists.
df_2024 = df_2024[pd.to_numeric(df_2024['Sessions'], errors='coerce').notna()]
df_2025 = df_2025[pd.to_numeric(df_2025['Sessions'], errors='coerce').notna()]

# Convert sessions to numeric
df_2024['Sessions'] = pd.to_numeric(df_2024['Sessions'])
df_2025['Sessions'] = pd.to_numeric(df_2025['Sessions'])

# Pro-rata adjustment for 2024 data
days_in_2025_period = 330
days_in_2024 = 366
pro_rata_factor = days_in_2025_period / days_in_2024
df_2024['adjusted_sessions_2024'] = df_2024['Sessions'] * pro_rata_factor

# Rename columns
df_2024.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'adjusted_sessions_2024': 'sessions_2024'}, inplace=True)
df_2025.rename(columns={'Session primary channel group (Default Channel Group)': 'channel', 'Sessions': 'sessions_2025'}, inplace=True)

# Merge dataframes
df_merged = pd.merge(df_2024[['channel', 'sessions_2024']], df_2025[['channel', 'sessions_2025']], on='channel', how='outer').fillna(0)

# Get top 5 channels from 2024
top_5_2024_channels = df_merged.nlargest(5, 'sessions_2024')

# Create PDF
with PdfPages('Traffic_Analysis_Report.pdf') as pdf:
    # --- Chart Page ---
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(top_5_2024_channels['channel']))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, top_5_2024_channels['sessions_2024'], width, label='2024 (Pro-rated)', color='skyblue')
    rects2 = ax.bar(x + width/2, top_5_2024_channels['sessions_2025'], width, label='2025', color='lightcoral')
    
    ax.set_ylabel('Sessions')
    ax.set_title('Top 5 Channel Traffic: 2024 vs 2025 Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_5_2024_channels['channel'], rotation=45, ha="right")
    ax.legend()
    
    ax.bar_label(rects1, padding=3, fmt='%d')
    ax.bar_label(rects2, padding=3, fmt='%d')
    
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)

    # --- Table Page ---
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Calculate percentage change
    top_5_2024_channels['change'] = top_5_2024_channels['sessions_2025'] - top_5_2024_channels['sessions_2024']
    top_5_2024_channels['percentage_change'] = (top_5_2024_channels['change'] / top_5_2024_channels['sessions_2024'] * 100).fillna(0).round(2)

    
    table_data = top_5_2024_channels[['channel', 'sessions_2024', 'sessions_2025', 'percentage_change']]
    table_data.columns = ['Channel', '2024 Sessions', '2025 Sessions', '% Change']
    
    # Format numbers for display
    table_data['2024 Sessions'] = table_data['2024 Sessions'].map('{:,.0f}'.format)
    table_data['2025 Sessions'] = table_data['2025 Sessions'].map('{:,.0f}'.format)
    table_data['% Change'] = table_data['% Change'].map('{:.2f}%'.format)


    table = ax.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc = 'center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)

    ax.set_title('Top 5 Channels (2024) - Data Summary', fontsize=16, fontweight='bold', pad=20)
    pdf.savefig(fig)
    plt.close(fig)

print("PDF report 'Traffic_Analysis_Report.pdf' has been created.")

