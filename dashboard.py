import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pandas as pd

# Database setup
engine = create_engine('sqlite:///metrics.db')
Session = sessionmaker(bind=engine)
session = Session()

# Function to fetch recent metrics from the database
def fetch_metrics():
    print("Fetching metrics from the database...")
    # Filter data from the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)  # Ensure using UTC time
    query = session.execute(text("SELECT * FROM vm_metrics WHERE timestamp >= :yesterday").params(yesterday=yesterday))
    df = pd.DataFrame(query.fetchall(), columns=query.keys())
    print("Data fetched: ", df.head())
    return df

# Create Dash application
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div(children=[
    html.H1(children='VM Metrics Dashboard'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Refresh every 60 seconds
        n_intervals=0
    ),
    dcc.Graph(id='cpu-graph'),
    dcc.Graph(id='memory-graph')
])

# Callback to update graphs
@app.callback(
    [Output('cpu-graph', 'figure'), Output('memory-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    print(f"Interval triggered: {n}")
    df = fetch_metrics()
    cpu_fig = {
        'data': [
            go.Scatter(
                x=df['timestamp'],
                y=df['cpu_percent'],
                mode='lines+markers',
                name='CPU Usage'
            )
        ],
        'layout': {
            'title': 'CPU Usage Over Time'
        }
    }
    memory_fig = {
        'data': [
            go.Scatter(
                x=df['timestamp'],
                y=df['memory_percent'],
                mode='lines+markers',
                name='Memory Usage'
            )
        ],
        'layout': {
            'title': 'Memory Usage Over Time'
        }
    }
    return cpu_fig, memory_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

