from flask import Flask, request, send_from_directory, jsonify
import os
from flask_cors import CORS
import pandas as pd
from scipy.signal import lfilter
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import io

server = Flask(__name__)
CORS(server)

app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/', update_title=None)

initial_trace = go.Scatter(x=[], y=[], mode='lines')
layout = go.Layout(title="Input Signal", xaxis=dict(title='Time'), yaxis=dict(title='Amplitude (V)'))

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File'),
        multiple=False
    ),
    html.Button('Reset', id='reset-button'),
    dcc.Graph(id='my-graph', figure={'data': [initial_trace], 'layout': layout}),
    html.Button('Export Data', id='export-button')
])

@app.callback(
    Output('my-graph', 'figure'),
    [Input('upload-data', 'contents')]
)
def update_graph(contents):
    if contents is None:
        return {'data': [initial_trace], 'layout': layout}

    content_string = contents.split(',')[1]
    decoded = io.StringIO(pd.compat.str(content_string))
    df = pd.read_csv(decoded)

    trace = go.Scatter(x=df['t'], y=df['data'], mode='lines')
    return {'data': [trace], 'layout': layout}

@app.callback(
    Output('my-graph', 'figure'),
    [Input('reset-button', 'n_clicks')]
)
def reset_graph(n):
    return {'data': [initial_trace], 'layout': layout}

@server.route('/')
def root():
    return send_from_directory('.', 'simplescope_wave_viewer.html')

@server.route('/process', methods=['POST'])
def process_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return 'No file selected', 400

    df = pd.read_csv(uploaded_file)
    data = df['data'].values

    n = 5
    b = [1.0/n] * n
    a = [1]
    smoothed_data = lfilter(b, a, data)

    df['smoothed_data'] = smoothed_data
    response_csv = df.to_csv(index=False)
    
    return response_csv

@server.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        os.remove(filename)
        return jsonify(success=True, message=f"File {filename} deleted successfully.")
    except FileNotFoundError:
        return jsonify(success=False, message=f"File {filename} not found."), 404

if __name__ == '__main__':
    server.run(port=8000)
