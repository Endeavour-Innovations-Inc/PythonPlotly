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

# App layout definition including Upload component and Graph component
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload File'),
        multiple=False
    ),
    html.Button('Reset', id='reset-button'),
    dcc.Graph(id='my-graph', figure={'data': [initial_trace], 'layout': layout}),
    html.Button('Export Data', id='export-button'),
    html.Div(id='dummy-div')  # Dummy div for triggering the download
])

# Combined callback for updating graph with uploaded CSV data and resetting the graph
@app.callback(
    Output('my-graph', 'figure'),
    [Input('upload-data', 'contents'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_graph(contents, reset_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        # If no inputs have been triggered, there's nothing to update
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'upload-data' and contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        trace = go.Scatter(x=df['t'], y=df['data'], mode='lines')
        return {'data': [trace], 'layout': layout}

    elif triggered_id == 'reset-button':
        return {'data': [initial_trace], 'layout': layout}

    raise PreventUpdate

# Callback for exporting the current graph's data to Excel
@app.callback(
    Output('dummy-div', 'children'),
    [Input('export-button', 'n_clicks')],
    [State('my-graph', 'figure')],
    prevent_initial_call=True
)

def export_to_csv(n_clicks, figure_data):
    if n_clicks is None:
        raise PreventUpdate

    global df  # Declare 'df' as global so it can be accessed in the download_csv route
    df = pd.DataFrame({
        't': figure_data['data'][0]['x'],
        'data': figure_data['data'][0]['y']
    })

    # Instead of returning send_file, we return a dcc.Location component to redirect.
    return dcc.Location(href='/download-csv', id='download-csv-trigger')


@server.route('/download-csv')
def download_csv():
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
