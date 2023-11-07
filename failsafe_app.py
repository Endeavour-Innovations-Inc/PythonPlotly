import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask import Flask, send_from_directory, request, send_file
import plotly.graph_objs as go
import pandas as pd
import base64
import io
from flask_cors import CORS
from dash.exceptions import PreventUpdate
from flask import send_file
import xlsxwriter
import csv
from scipy.signal import lfilter


server = Flask(__name__)
CORS(server)
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')

# Define initial empty trace and layout for the graph
initial_trace = go.Scatter(x=[], y=[], mode='lines')
layout = go.Layout(
    title="Input Signal",
    xaxis=dict(title='Time'),
    yaxis=dict(title='Amplitude (V)'),
    autosize=True
)

# Define your CSS styles inside a style tag
styles = {
    'graphControl': {
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'margin': '40px 0',
        'gap': '15px'
    },
    'buttonGroup': {
        'display': 'flex',
        'gap': '1px'
    },
    'chartDiv': {
        'borderTop': '1px solid rgba(0, 0, 0, 0.3)',
        'borderBottom': '1px solid rgba(0, 0, 0, 0.3)',
        'margin': '20px 0'
    },
    'cornerButtons': {
        'position': 'absolute',
        'left': '10px',
        'bottom': '10px',
        'display': 'flex',
        'gap': '10px'
    },
    'switch': {
        'display': 'flex',
        'alignItems': 'center'
    },
    'switchInput': {
        'display': 'none'
    },
    'switchLabel': {
        'position': 'relative',
        'display': 'inline-block',
        'width': '60px',
        'height': '34px'
    },
    'switchLabelBefore': {
        'content': '""',  # This might not work as expected, pseudo-elements may need to be handled differently
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'backgroundColor': '#ccc',
        'borderRadius': '34px',
        'transition': '.4s'
    },
    'switchLabelAfter': {
        'content': '""',  # Same issue with content property here
        'position': 'absolute',
        'top': '4px',
        'left': '4px',
        'width': '26px',
        'height': '26px',
        'backgroundColor': 'white',
        'borderRadius': '50%',
        'transition': '.4s'
    },
    'switchInputChecked': {
        'backgroundColor': '#2196F3'
    },
    'switchLabelAfterChecked': {
        'transform': 'translateX(26px)'
    }
}

# App layout definition including Upload component and Graph component
# Define the layout of your app
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File'),
        multiple=False
    ),
    html.Label([
        "Enable Filter:",
        dcc.Checklist(
            id='filter-switch',
            options=[{'label': '', 'value': 'on'}],  # Empty label for custom styling
            value=[],
            className="switch"  # This is the custom class name for styling
        )
    ], className="switch-container"),  # Add a class for the label if needed for additional styling
    html.Button('Reset', id='reset-button'),
    html.Button('Export Data', id='export-button'),
    
    # Graph control buttons (styled as per your CSS)
    html.Div(id='graphControl', style=styles['graphControl'], children=[
        html.Div(id='buttonGroup', style=styles['buttonGroup'], children=[
            html.Button('↑', id='zoom-in'),
            html.Button('↓', id='zoom-out'),
            html.Button('Sub 3', id='sub-3')
        ]),
        html.Button('Button 2', id='btn-2'),
        html.Button('Button 3', id='btn-3'),
        html.Button('Button 4', id='btn-4'),
    ]),
    
    # Placeholder for the graph with division lines (styled as per your CSS)
    html.Div(id='chartDiv', style=styles['chartDiv'], children=[
        dcc.Graph(id='my-graph', figure={'data': [initial_trace], 'layout': layout}),
    ]),
    
    # Small buttons in the lower left corner (styled as per your CSS)
    html.Div(id='cornerButtons', style=styles['cornerButtons'], children=[
        html.Button('Vert', id='vert-button'),
        html.Button('Horz', id='horz-button'),
    ]),
    
    # Dummy div for triggering downloads
    html.Div(id='dummy-div')
])

# Initialize 'df' as a global variable outside of your callbacks
global df
df = pd.DataFrame()

# Combined callback for updating graph with uploaded CSV data, resetting the graph, and applying a filter
@app.callback(
    Output('my-graph', 'figure'),
    [Input('upload-data', 'contents'),
     Input('reset-button', 'n_clicks')],
    [State('filter-switch', 'value')],  # Add the switch's value as State
    prevent_initial_call=True
)
def update_graph(contents, reset_clicks, filter_enabled):
    global df 
    # You would still define your filter coefficients here if they are not already defined
    b = [1, -0.95]  # Numerator coefficients
    a = [1]         # Denominator coefficients

    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'reset-button':
        # This clears the graph to its initial state
        df = pd.DataFrame()  # Reset the 'df' variable
        return {'data': [initial_trace], 'layout': layout}

    if triggered_id == 'upload-data' and contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Check if the filter switch is enabled and apply the filter
        if 'on' in filter_enabled:  # Ensure 'on' is in the list to check for the filter
            filtered_data = lfilter(b, a, df['data'])
            trace = go.Scatter(x=df['t'], y=filtered_data, mode='lines', name='Filtered Data')
        else:
            trace = go.Scatter(x=df['t'], y=df['data'], mode='lines', name='Original Data')

        return {'data': [trace], 'layout': layout}

    elif triggered_id == 'reset-button':
        # This clears the graph to its initial state
        return {'data': [initial_trace], 'layout': layout}

    raise PreventUpdate

@server.route('/download-csv')
def download_csv():
    global df  
    # This function uses the 'df' global DataFrame to create a CSV in memory
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='data.csv'
    )

if __name__ == '__main__':
    app.run_server(debug=True)
