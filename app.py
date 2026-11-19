from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import re
from datetime import datetime
import pytz
import os

app = Flask(__name__)
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Play Store Data_3.csv')
def parse_size_mb(size_str):
    if pd.isna(size_str) or str(size_str).strip() == 'Varies with device':
        return np.nan
    s = str(size_str).strip()
    if s.endswith('M') or s.endswith('m'):
        try: return float(s[:-1])
        except: return np.nan
    elif s.endswith('k') or s.endswith('K'):
        try: return float(s[:-1]) / 1024.0
        except: return np.nan
    try: return float(s)
    except: return np.nan
def parse_installs(inst_str):
    if pd.isna(inst_str): return np.nan
    s = str(inst_str).replace('+', '').replace(',', '').strip()
    try: return float(s)
    except: return np.nan
def parse_price(price_str):
    if pd.isna(price_str): return 0.0
    s = str(price_str).replace('$', '').strip()
    try: return float(s)
    except: return 0.0

def parse_android_ver(ver_str):
    if pd.isna(ver_str) or str(ver_str).strip() == 'Varies with device':
        return np.nan
    match = re.search(r'(\d+\.\d+|\d+)', str(ver_str))
    if match:
        try: return float(match.group(1))
        except: return np.nan
    return np.nan

def load_dual_axis_data():
    if not os.path.exists(DATA_PATH):
        return None
        
    df = pd.read_csv(DATA_PATH)
    
    # Cleaning columns
    df['Size_MB'] = df['Size'].apply(parse_size_mb)
    df['Installs_clean'] = df['Installs'].apply(parse_installs)
    df['Price_clean'] = df['Price'].apply(parse_price)
    df['Android_Ver_num'] = df['Android Ver'].apply(parse_android_ver)
    df['App_len'] = df['App'].astype(str).str.len()
    df['Revenue'] = df['Installs_clean'] * df['Price_clean']
    
    # Applying strict filter rules:
    # 1. Installs >= 10,000
    # 2. Android Version > 4.0
    # 3. Size > 15 MB
    # 4. Content Rating == 'Everyone'
    # 5. App Name length <= 30 chars
    # 6. Revenue >= $10,000 for Paid apps (Free apps naturally have $0)
    cond = (
        (df['Installs_clean'] >= 10000) &
        (df['Android_Ver_num'] > 4.0) &
        (df['Size_MB'] > 15.0) &
        (df['Content Rating'] == 'Everyone') &
        (df['App_len'] <= 30) &
        ((df['Type'] == 'Free') | ((df['Type'] == 'Paid') & (df['Revenue'] >= 10000)))
    )
    df_filtered = df[cond].copy()
    
    # Identify top 3 categories by total installs
    top3_categories = df_filtered.groupby('Category')['Installs_clean'].sum().sort_values(ascending=False).head(3).index.tolist()
    
    df_top3 = df_filtered[df_filtered['Category'].isin(top3_categories)]
    
    # Aggregating Average Installs and Average Revenue per (Category, Type)
    agg = df_top3.groupby(['Category', 'Type']).agg(
        avg_installs=('Installs_clean', 'mean'),
        avg_revenue=('Revenue', 'mean')
    ).reset_index()
    
    categories = top3_categories
    chart_data = {
        'categories': categories,
        'free_installs': [],
        'paid_installs': [],
        'free_revenue': [],
        'paid_revenue': []
    }
    
    for cat in categories:
        free_row = agg[(agg['Category'] == cat) & (agg['Type'] == 'Free')]
        paid_row = agg[(agg['Category'] == cat) & (agg['Type'] == 'Paid')]
        
        chart_data['free_installs'].append(round(free_row['avg_installs'].values[0], 2) if not free_row.empty else 0)
        chart_data['paid_installs'].append(round(paid_row['avg_installs'].values[0], 2) if not paid_row.empty else 0)
        chart_data['free_revenue'].append(round(free_row['avg_revenue'].values[0], 2) if not free_row.empty else 0)
        chart_data['paid_revenue'].append(round(paid_row['avg_revenue'].values[0], 2) if not paid_row.empty else 0)
        
    return chart_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dual-axis-data')
def dual_axis_data():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    # Active Window: 1 PM IST to 2 PM IST (13:00 to 14:00 IST)
    is_active = (13 <= now.hour < 14)
    
    data = load_dual_axis_data()
    return jsonify({
        'is_active': is_active,
        'data': data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
