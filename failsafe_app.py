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
from datetime import datetime


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

# Define a vertical layout style
vertical_layout_style = {
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'left',
    'justifyContent': 'center',
    'gap': '10px',  # Adjust the gap to your liking
}

# Define a style for the buttons and upload to make them less wide
button_style = {
    'width': 'auto',  # Set the width to 'auto' or specific value to make buttons less wide
    'maxWidth': '300px',  # Adjust the max width as needed
    'margin': '0 auto 10px auto'  # Add margins to center the buttons in the parent container
}

# App layout definition including Upload component and Graph component
# Define the layout of your app
app.layout = html.Div([
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Button('Upload File', style={'width': '10%'}),
            multiple=False,
            style={'width': '100%'}
        ),
        html.Button('Enable Filter: Off', id='filter-toggle', n_clicks=0, style={'width': '10%'}),
        html.Button('Reset', id='reset-button', style={'width': '10%'}),
        html.Button('Export Data', id='export-button', style={'width': '10%'}),
    ], style=vertical_layout_style),
    
    # Graph control buttons (styled as per your CSS)
    # Graph control buttons (styled as per your CSS)
    html.Div(id='graphControl', style=styles['graphControl'], children=[
        html.Div(id='buttonGroup1', style=styles['buttonGroup'], children=[
            html.Button('↑', id='zoom-in1'),
            html.Button('Sub 3', id='sub-31'),
            html.Button('↓', id='zoom-out1'),
        ]),
        html.Div(id='buttonGroup2', style=styles['buttonGroup'], children=[
            html.Button('↑', id='zoom-in2'),
            html.Button('↓', id='zoom-out2'),
            html.Button('Sub 3', id='sub-32')
        ]),
        html.Button('Button 3', id='btn-3'),
        html.Button('Button 4', id='btn-4'),
    ]),

    
    # Placeholder for the graph with division lines (styled as per your CSS)
    html.Div(id='chartDiv', style=styles['chartDiv'], children=[
        dcc.Graph(id='my-graph', figure={'data': [initial_trace], 'layout': layout}),
    ]),
    
    # Small buttons in the lower left corner (styled as per your CSS)
    # html.Div(id='cornerButtons', style=styles['cornerButtons'], children=[
    #    html.Button('Vert', id='vert-button'),
    #    html.Button('Horz', id='horz-button'),
    # ]),

    # Add a large transparent rectangle with a smaller rectangle and a button inside
    html.Div(id='large-rectangle', style={
        'position': 'absolute',
        'left': '10px',
        'bottom': '10px',
        'width': '250px',  # Increased width of the parent rectangle
        'height': '60px',  # Height of the parent rectangle
        'border': '1px solid black',  # Black border for the parent rectangle
        'borderRadius': '5px',  # Optional rounded corners for the parent
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'space-between',  # Adjusted for spacing between elements
        'backgroundColor': 'transparent',  # Transparent background
        'padding': '5px',  # Padding inside the parent rectangle
    }, children=[
        html.Div('View Mode', style={
            'border': '2px solid darkblue',  # Dark blue border for the child rectangle
            'padding': '10px 20px',  # Padding inside the child rectangle
            'borderRadius': '5px',  # Optional rounded corners for the child
            'backgroundColor': 'transparent',  # Transparent background for the child
            'color': 'darkblue',  # Text color
            'fontWeight': 'bold',  # Bold text
        }),
        html.Button('Normal', id='normal-button', style={
            'display': 'inline-block',  # Adjusted display property
            'margin': '0 auto',  # Centering the button
            'textAlign': 'center',  # Center text inside the button
        })
    ]),


    html.Div(id='upload-timestamp', style={'display': 'none'}),
    
    # Component for triggering downloads
    dcc.Download(id='download-dataframe-csv')
])

# Initialize 'df' as a global variable outside of your callbacks
global df
df = pd.DataFrame()

# Callback to handle filter toggle button
@app.callback(
    Output('filter-toggle', 'children'),
    [Input('filter-toggle', 'n_clicks')]
)
def toggle_filter(n_clicks):
    if n_clicks % 2 == 0:  # If even number of clicks, filter is off
        return 'Enable Filter: Off'
    else:  # If odd number of clicks, filter is on
        return 'Enable Filter: On'


# Combined callback for updating graph with uploaded CSV data, resetting the graph, and applying a filter
@app.callback(
    Output('my-graph', 'figure'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename'),  # Change the input to filename
     Input('reset-button', 'n_clicks')],
    [State('filter-toggle', 'children')],  # Add the switch's value as State
    prevent_initial_call=True
)
def update_graph(contents, filename, reset_clicks, filter_toggle_label):
    global df 
    ctx = dash.callback_context

    # Determine which input was triggered
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # If the reset button is clicked, clear the graph
    if triggered_id == 'reset-button':
        df = pd.DataFrame()  # Reset the 'df' variable
        return {'data': [initial_trace], 'layout': layout}

    # If new file data is uploaded, update the graph
    if triggered_id == 'upload-data' and contents:
        # Generate a timestamp to force the update
        timestamp = datetime.now()
        
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Check if the filter switch is enabled and apply the filter
        if 'On' in filter_toggle_label:
            # Define filter coefficients here for smoothing
            b = [1, -0.95]  # Numerator coefficients
            a = [1]         # Denominator coefficients
            filtered_data = lfilter(b, a, df['data'])
            trace = go.Scatter(x=df['t'], y=filtered_data, mode='lines', name='Filtered Data')
        else:
            trace = go.Scatter(x=df['t'], y=df['data'], mode='lines', name='Original Data')

        return {'data': [trace], 'layout': layout}

    # Prevents update if not triggered by the inputs we're interested in
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

# Callback to trigger a download when the 'Export Data' button is clicked
@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('export-button', 'n_clicks')],
    prevent_initial_call=True
)
def export_data(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    # Trigger download
    return dcc.send_data_frame(df.to_csv, "data.csv", index=False)

# Callback to toggle the "Normal" button label
@app.callback(
    Output('normal-button', 'children'),
    [Input('normal-button', 'n_clicks')],
    [State('normal-button', 'children')],
    prevent_initial_call=True
)
def toggle_normal_button(n_clicks, current_label):
    if current_label == 'Normal':
        return 'FFT'
    else:
        return 'Normal'

if __name__ == '__main__':
    app.run_server(debug=True)
