
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import os
import sys

def load_and_clean_data(filepath, year):
    """Loads a single CSV file, cleans it, and calculates pro-rata sessions."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        sys.exit(1)
        
    df = pd.read_csv(filepath, skiprows=9)
    df = df[pd.to_numeric(df['Sessions'], errors='coerce').notna()]
    df['Sessions'] = pd.to_numeric(df['Sessions'])
    
    # Pro-rata adjustment. Assumes the first file is a full year.
    # A more robust solution could parse dates from the file header.
    if year == 'old':
        days_in_period = 330 # Assuming Jan 1 - Nov 26 for the 'new' file
        days_in_year = 366 # Assuming a leap year for the 'old' file
        pro_rata_factor = days_in_period / days_in_year
        df['adjusted_sessions'] = df['Sessions'] * pro_rata_factor
    else:
        df['adjusted_sessions'] = df['Sessions']

    df.rename(columns={'Session primary channel group (Default Channel Group)': 'channel'}, inplace=True)
    return df[['channel', 'adjusted_sessions']]

def analyze_and_visualize(filepath_old, filepath_new, output_filename):
    """Main function to perform analysis and generate PDF report."""
    
    # Load data
    df_old = load_and_clean_data(filepath_old, 'old')
    df_new = load_and_clean_data(filepath_new, 'new')

    # Rename for merging
    df_old.rename(columns={'adjusted_sessions': 'sessions_old'}, inplace=True)
    df_new.rename(columns={'adjusted_sessions': 'sessions_new'}, inplace=True)

    # Merge dataframes
    df_merged = pd.merge(df_old, df_new, on='channel', how='outer').fillna(0)
    
    # Get top 5 channels from the old data
    top_5_channels = df_merged.nlargest(5, 'sessions_old')
    
    # --- PDF Creation ---
    with PdfPages(output_filename) as pdf:
        # --- Chart Page ---
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(top_5_channels['channel']))
        width = 0.35
        
        rects1 = ax.bar(x - width/2, top_5_channels['sessions_old'], width, label='Year 1 (Pro-rated)', color='skyblue')
        rects2 = ax.bar(x + width/2, top_5_channels['sessions_new'], width, label='Year 2', color='lightcoral')
        
        ax.set_ylabel('Sessions')
        ax.set_title('Top 5 Channel Traffic Comparison', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(top_5_channels['channel'], rotation=45, ha="right")
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
        
        top_5_channels['change'] = top_5_channels['sessions_new'] - top_5_channels['sessions_old']
        top_5_channels['percentage_change'] = (top_5_channels['change'] / top_5_channels['sessions_old'] * 100).fillna(0).round(2)
        
        table_data = top_5_channels[['channel', 'sessions_old', 'sessions_new', 'percentage_change']]
        table_data.columns = ['Channel', 'Year 1 Sessions', 'Year 2 Sessions', '% Change']
        
        table_data['Year 1 Sessions'] = table_data['Year 1 Sessions'].map('{:,.0f}'.format)
        table_data['Year 2 Sessions'] = table_data['Year 2 Sessions'].map('{:,.0f}'.format)
        table_data['% Change'] = table_data['% Change'].map('{:.2f}%'.format)
        
        table = ax.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.2)

        ax.set_title('Top 5 Channels (Year 1) - Data Summary', fontsize=16, fontweight='bold', pad=20)
        pdf.savefig(fig)
        plt.close(fig)

    print(f"Success: PDF report '{output_filename}' has been created.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze and visualize traffic data from two CSV files.')
    parser.add_argument('file1', help='The file path for the first (older) CSV file.')
    parser.add_argument('file2', help='The file path for the second (newer) CSV file.')
    parser.add_argument('-o', '--output', default='Traffic_Comparison_Report.pdf', help='The name of the output PDF file.')
    
    args = parser.parse_args()
    
    analyze_and_visualize(args.file1, args.file2, args.output)
