import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import timedelta

# --- 1. OOP: Class for the Mood Entry (Data Structure) ---
class MoodEntry:
    """
    Represents a single mood log entry with proper data types.
    """
    def __init__(self, mood_score, stress_level, activity, notes):
        self.mood_score = int(mood_score)
        self.stress_level = int(stress_level)
        self.activity = str(activity).strip()
        self.notes = str(notes).strip()
        self.timestamp = pd.Timestamp.now()
    
    def to_dict(self):
        """Converts the object to a dictionary for DataFrame storage."""
        return {
            'timestamp': self.timestamp,
            'mood_score': self.mood_score,
            'stress_level': self.stress_level,
            'activity': self.activity,
            'notes': self.notes
        }

# --- 2. Data Initialization and Flask Setup ---
app = Flask(__name__)

def load_data():
    global data
    try:
        data = pd.read_csv('mood_data.csv')
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        print("Loaded existing data from mood_data.csv.")
    except FileNotFoundError:
        data = pd.DataFrame(columns=['timestamp', 'mood_score', 'stress_level', 'activity', 'notes'])
        print("Created new empty data file.")

load_data()

# --- 3. Visualization and Analysis Logic ---

def generate_trend_chart(df):
    """Generates a visual trend chart for the last 14 days."""
    if df.empty:
        return None

    fourteen_days_ago = pd.Timestamp.now() - timedelta(days=14)
    df_recent = df[df['timestamp'] >= fourteen_days_ago].sort_values('timestamp')

    if len(df_recent) < 2:
        return None

    plt.figure(figsize=(10, 5), dpi=100)
    
    # Plot Mood Score
    plt.plot(df_recent['timestamp'], df_recent['mood_score'], marker='o', label='Mood Score (1-5)', color='#4CAF50', linewidth=2)
    
    # Plot Stress Level (Scaled 1-5)
    plt.plot(df_recent['timestamp'], df_recent['stress_level'].apply(lambda x: x / 2), 
             marker='x', label='Stress (Scaled 1-5)', color='#F44336', linestyle='--', linewidth=1.5)
    
    plt.title('14-Day Mood & Stress Trend', fontsize=16, color='#2c3e50')
    plt.xlabel('Date/Time', fontsize=12)
    plt.ylabel('Score (1-5)', fontsize=12)
    plt.yticks(np.arange(1, 6, 1))
    plt.grid(axis='both', alpha=0.5, linestyle=':')
    plt.legend(loc='upper right', fontsize=10)
    
    plt.gcf().autofmt_xdate(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True) 
    plt.close()
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{image_base64}"

def get_analysis_data(df):
    """Generates summary statistics and activity frequency analysis safely."""
    # --- FIX: Safe return block if DataFrame is empty ---
    if df.empty:
        return {
            'summary': {
                'total_logs': 0,
                'avg_mood': 'N/A',
                'avg_stress': 'N/A'
            },
            'history': [],
            'activity_analysis': [],
            'df_sorted': df
        }

    # Calculate overall summary statistics
    summary = {
        'total_logs': len(df),
        'avg_mood': f"{df['mood_score'].mean():.1f}",
        'avg_stress': f"{df['stress_level'].mean():.1f}",
    }

    # Prepare recent history data (last 8 entries, descending order)
    data_sorted = df.sort_values('timestamp', ascending=False)
    recent_data = data_sorted.head(8).to_dict('records')
    
    # Activity Analysis
    activity_analysis = []
    if 'activity' in df.columns:
        # Filter out rows where activity is empty or just whitespace
        df_activities = df[df['activity'].astype(str).str.strip() != '']
        if not df_activities.empty:
            activity_summary = df_activities.groupby('activity').agg(
                count=('activity', 'size'),
                avg_mood=('mood_score', 'mean'),
                avg_stress=('stress_level', 'mean')
            ).reset_index().sort_values('count', ascending=False).head(5)

            activity_analysis = activity_summary.to_dict('records')

    return {
        'summary': summary, 
        'history': recent_data, 
        'activity_analysis': activity_analysis, 
        'df_sorted': data_sorted
    }

# --- 4. Flask Routes ---

@app.route('/')
def index():
    """Renders the main dashboard page (index)."""
    analysis = get_analysis_data(data)
    return render_template('index.html', 
                           view='dashboard',
                           summary=analysis['summary'], 
                           data=analysis['history'])

@app.route('/log_page')
def log_page():
    """Renders the dedicated logging page."""
    return render_template('index.html', view='log_form')

@app.route('/analysis_page')
def analysis_page():
    """Renders the detailed analysis page with charts and tables."""
    analysis = get_analysis_data(data)
    chart_img = generate_trend_chart(analysis['df_sorted'])

    chart_error = None
    if chart_img is None:
        chart_error = "Not enough data (need at least 2 entries in the last 14 days) to generate a trend chart."

    return render_template('index.html', 
                           view='analysis',
                           chart_img=chart_img, 
                           chart_error=chart_error,
                           activity_analysis=analysis['activity_analysis'])

@app.route('/log', methods=['POST'])
def log_mood():
    """Handles the form submission, processes data, and redirects to thank you."""
    global data
    try:
        new_entry = MoodEntry(
            request.form.get('mood_score'), 
            request.form.get('stress_level'), 
            request.form.get('activity'), 
            request.form.get('notes')
        )
    except (ValueError, TypeError) as e:
        return f"Invalid input data: {e}. Mood and Stress scores must be valid numbers.", 400
    
    new_row = pd.DataFrame([new_entry.to_dict()])
    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv('mood_data.csv', index=False)
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    """Renders the thank you/confirmation page."""
    return render_template('index.html', view='thank_you')

# --- 5. Application Run ---
if __name__ == '__main__':
    app.run(debug=True)