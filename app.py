
import os
import uuid
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'csv'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_metadata(filepath):
    start_date_str, end_date_str = None, None
    default_meta = {'days': 365, 'year': 'N/A'}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i > 10: break
                if 'Start date:' in line: start_date_str = line.split(':')[-1].strip()
                if 'End date:' in line: end_date_str = line.split(':')[-1].strip()
    except Exception as e:
        print(f"Error reading metadata from {filepath}: {e}")
        return default_meta
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y%m%d')
            end_date = datetime.strptime(end_date_str, '%Y%m%d')
            return {'days': (end_date - start_date).days + 1, 'year': start_date.year}
        except ValueError: return default_meta
    return default_meta

def save_uploaded_files(request):
    if 'file1' not in request.files or 'file2' not in request.files: return None, None
    file1, file2 = request.files['file1'], request.files['file2']
    if file1.filename == '' or file2.filename == '': return None, None
    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.csv")
        file1.save(filepath1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.csv")
        file2.save(filepath2)
        return filepath1, filepath2
    return None, None

def cleanup_files(filepaths):
    for fp in filepaths:
        if fp and os.path.exists(fp):
            os.remove(fp)

# --- Analysis Functions ---
def analyze_channel_data(df1, df2, year1, year2):
    try:
        df1_agg = df1.groupby('Session primary channel group (Default Channel Group)')['Sessions'].sum().reset_index()
        df2_agg = df2.groupby('Session primary channel group (Default Channel Group)')['Sessions'].sum().reset_index()
        df_merged = pd.merge(df1_agg, df2_agg, on='Session primary channel group (Default Channel Group)', how='outer', suffixes=('_old', '_new')).fillna(0)
        df_merged['change'] = df_merged['Sessions_new'] - df_merged['Sessions_old']
        df_merged['percent_change'] = (df_merged['change'] / df_merged['Sessions_old'].replace(0, np.inf)) * 100
        top_channels = df_merged.nlargest(10, 'Sessions_old')
        fig, ax = plt.subplots(figsize=(12, 8)); x = np.arange(len(top_channels)); width = 0.35
        ax.bar(x - width/2, top_channels['Sessions_old'], width, label=f"{year1} (Pro-rated)", color='skyblue')
        ax.bar(x + width/2, top_channels['Sessions_new'], width, label=f"{year2}", color='lightcoral')
        ax.set_ylabel('Sessions'); ax.set_title('Channel-Level Analysis', fontsize=16)
        ax.set_xticks(x); ax.set_xticklabels(top_channels['Session primary channel group (Default Channel Group)'], rotation=45, ha="right")
        ax.legend(); fig.tight_layout()
        chart_filename = f"{uuid.uuid4()}.png"; plt.savefig(os.path.join(app.config['STATIC_FOLDER'], 'images', chart_filename)); plt.close(fig)
        total_change = (df_merged['Sessions_new'].sum() - df_merged['Sessions_old'].sum()) / df_merged['Sessions_old'].sum() * 100 if df_merged['Sessions_old'].sum() > 0 else 0
        return {'chart_filename': chart_filename, 'data': df_merged, 'total_change': total_change}
    except Exception as e: print(f"ERROR in analyze_channel_data: {e}"); return None

def analyze_page_data(df1, df2):
    try:
        df1_agg = df1.groupby('Page path and screen class')['Sessions'].sum().reset_index()
        df2_agg = df2.groupby('Page path and screen class')['Sessions'].sum().reset_index()
        df_merged = pd.merge(df1_agg, df2_agg, on='Page path and screen class', how='outer', suffixes=('_old', '_new')).fillna(0)
        df_merged['change'] = df_merged['Sessions_new'] - df_merged['Sessions_old']
        top_10_drops = df_merged.nsmallest(10, 'change')
        top_10_drops = top_10_drops[top_10_drops['change'] < 0]
        if top_10_drops.empty: return None
        fig, ax = plt.subplots(figsize=(12, 10)); y_pos = np.arange(len(top_10_drops))
        ax.barh(y_pos, top_10_drops['change'], align='center', color='lightcoral'); ax.set_yticks(y_pos); ax.set_yticklabels(top_10_drops['Page path and screen class'])
        ax.invert_yaxis(); ax.set_xlabel('Change in Sessions (YoY)'); ax.set_title('Top 10 Pages by Traffic Drop', fontsize=16); fig.tight_layout()
        chart_filename = f"{uuid.uuid4()}.png"; plt.savefig(os.path.join(app.config['STATIC_FOLDER'], 'images', chart_filename)); plt.close(fig)
        return {'chart_filename': chart_filename, 'data': top_10_drops}
    except Exception as e: print(f"ERROR in analyze_page_data: {e}"); return None

def analyze_time_data(df1, df2, year1, year2):
    try:
        df1['Date'] = pd.to_datetime(df1['Date']); df2['Date'] = pd.to_datetime(df2['Date'])
        df1_time = df1.set_index('Date').resample('W-Mon')['Sessions'].sum(); df2_time = df2.set_index('Date').resample('W-Mon')['Sessions'].sum()
        df1_time.index = df1_time.index.map(lambda dt: dt.replace(year=2024)); df2_time.index = df2_time.index.map(lambda dt: dt.replace(year=2024))
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(df1_time.index.strftime('%m-%d'), df1_time.values, label=f"{year1} (Pro-rated)", color='skyblue')
        ax.plot(df2_time.index.strftime('%m-%d'), df2_time.values, label=f"{year2}", color='lightcoral')
        ax.set_ylabel('Sessions per Week'); ax.set_title('When the Traffic Changed (Weekly)', fontsize=16); plt.xticks(rotation=45); ax.legend(); fig.tight_layout()
        chart_filename = f"{uuid.uuid4()}.png"; plt.savefig(os.path.join(app.config['STATIC_FOLDER'], 'images', chart_filename)); plt.close(fig)
        time_merged = pd.concat([df1_time.rename('old'), df2_time.rename('new')], axis=1).fillna(0); time_merged['change'] = time_merged['new'] - time_merged['old']
        return {'chart_filename': chart_filename, 'data': time_merged.nsmallest(1, 'change')}
    except Exception as e: print(f"ERROR in analyze_time_data: {e}"); return None

def analyze_device_data(df1, df2, year1, year2):
    try:
        df1_agg = df1.groupby('Device category')['Sessions'].sum().reset_index(); total1 = df1_agg['Sessions'].sum()
        df1_agg['share'] = (df1_agg['Sessions'] / total1) * 100 if total1 > 0 else 0
        df2_agg = df2.groupby('Device category')['Sessions'].sum().reset_index(); total2 = df2_agg['Sessions'].sum()
        df2_agg['share'] = (df2_agg['Sessions'] / total2) * 100 if total2 > 0 else 0
        df_merged = pd.merge(df1_agg.rename(columns={'share': 'share1'}), df2_agg.rename(columns={'share': 'share2'}), on='Device category', how='outer').fillna(0)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), sharey=True)
        bottom1 = 0
        for _, row in df_merged.iterrows(): ax1.barh(0, row['share1'], left=bottom1, label=row['Device category']); bottom1 += row['share1']
        ax1.set_title(f'{year1} Device Share'); ax1.set_xlabel('Percentage'); ax1.set_xlim(0, 100)
        bottom2 = 0
        for _, row in df_merged.iterrows(): ax2.barh(0, row['share2'], left=bottom2, label=row['Device category']); bottom2 += row['share2']
        ax2.set_title(f'{year2} Device Share'); ax2.set_xlabel('Percentage'); ax2.set_xlim(0, 100)
        handles, labels = ax1.get_legend_handles_labels(); fig.legend(handles, labels, loc='lower center', ncol=len(df_merged), bbox_to_anchor=(0.5, -0.05))
        fig.suptitle('Device Traffic Share Comparison', fontsize=16); fig.tight_layout(rect=[0, 0.05, 1, 1])
        chart_filename = f"{uuid.uuid4()}.png"; plt.savefig(os.path.join(app.config['STATIC_FOLDER'], 'images', chart_filename)); plt.close(fig)
        df_insight_data = pd.merge(df1.groupby('Device category')['Sessions'].sum(), df2.groupby('Device category')['Sessions'].sum(), on='Device category', how='outer', suffixes=('_old', '_new')).fillna(0)
        df_insight_data['change'] = df_insight_data['Sessions_new'] - df_insight_data['Sessions_old']
        return {'chart_filename': chart_filename, 'data': df_insight_data}
    except Exception as e: print(f"ERROR in analyze_device_data: {e}"); return None

def generate_insights(results):
    insights = []
    if 'channel' in results and results['channel']:
        df = results['channel']['data']; total_change = results['channel']['total_change']
        insight = f"Overall traffic changed by {total_change:.2f}%. "
        biggest_drop = df.nsmallest(1, 'change')
        if not biggest_drop.empty and biggest_drop['change'].iloc[0] < 0:
            insight += f"The largest driver is the '{biggest_drop['Session primary channel group (Default Channel Group)'].iloc[0]}' channel, which dropped by {abs(biggest_drop['percent_change'].iloc[0]):.2f}%."
        insights.append(insight)
    if 'page' in results and results['page']: insights.append(f"The traffic loss seems most concentrated on pages like '{results['page']['data']['Page path and screen class'].iloc[0]}'.")
    if 'time' in results and results['time']: insights.append(f"The most significant weekly drop occurred around {results['time']['data'].index[0].strftime('%B %Y')}.")
    if 'device' in results and results['device']:
        biggest_drop = results['device']['data'].nsmallest(1, 'change')
        if not biggest_drop.empty and biggest_drop['change'].iloc[0] < 0: insights.append(f"On a device level, '{biggest_drop['Device category'].iloc[0]}' traffic saw the most significant decrease.")
    if not insights: insights.append("No insights could be generated. Ensure your files contain columns like 'Session primary channel group', 'Page path and screen class', 'Date', or 'Device category'.")
    return insights

def run_analysis_suite(filepath1, filepath2):
    analysis_results, charts = {}, {}
    try:
        meta1, meta2 = get_file_metadata(filepath1), get_file_metadata(filepath2)
        pro_rata = meta2['days'] / meta1['days'] if meta1['days'] > 0 else 0
        
        # Load data robustly, handling potential parsing errors
        try:
            df1_raw = pd.read_csv(filepath1, comment='#')
            df2_raw = pd.read_csv(filepath2, comment='#')
        except Exception as e:
            return [f"Error reading CSV file: {e}"], {}

        # Pre-process DataFrames
        df1 = df1_raw[pd.to_numeric(df1_raw['Sessions'], errors='coerce').notna()].copy(); df1['Sessions'] = pd.to_numeric(df1['Sessions']) * pro_rata
        df2 = df2_raw[pd.to_numeric(df2_raw['Sessions'], errors='coerce').notna()].copy(); df2['Sessions'] = pd.to_numeric(df2['Sessions'])
        
        all_dims = set(df1.columns) & set(df2.columns)
        
        # --- Run Analyses ---
        charts['channel'] = analyze_channel_data(df1.copy(), df2.copy(), meta1['year'], meta2['year']) if 'Session primary channel group (Default Channel Group)' in all_dims else None
        charts['page'] = analyze_page_data(df1.copy(), df2.copy()) if 'Page path and screen class' in all_dims else None
        charts['time'] = analyze_time_data(df1.copy(), df2.copy(), meta1['year'], meta2['year']) if 'Date' in all_dims else None
        charts['device'] = analyze_device_data(df1.copy(), df2.copy(), meta1['year'], meta2['year']) if 'Device category' in all_dims else None
        
        for key, result in charts.items():
            if result: analysis_results[key] = result
        
        insights = generate_insights(analysis_results)
        return insights, charts
    except Exception as e:
        print(f"CRITICAL error in run_analysis_suite: {e}")
        return [f"A critical error occurred during analysis: {e}"], {}
    finally:
        cleanup_files([filepath1, filepath2])

# --- Routes ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def handle_analysis():
    filepath1, filepath2 = save_uploaded_files(request)
    if not filepath1 or not filepath2: return redirect(url_for('index'))
    insights, charts = run_analysis_suite(filepath1, filepath2)
    for key, chart_data in charts.items():
        if chart_data: chart_data['chart_url'] = url_for('static', filename=f"images/{chart_data['chart_filename']}")
    return render_template('results.html', insights=insights, charts=charts)

# --- Main Execution ---
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['STATIC_FOLDER'], 'images'), exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
