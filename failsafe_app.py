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
from scipy.signal import lfilter
from datetime import datetime
from style import styles, play_icon_style, rectangle_1_style, rectangle_style, triangle_style, thin_rectangle_style, square_icon_style, dropdown_style, combined_rectangle_content_style, combined_rectangle_style, inner_rectangle_style, centered_section_style, long_rectangle_style_scope, long_rectangle_style, row_style, toggle_button_style

import scope_interface as si
import numpy as np 
import time 

server = Flask(__name__)
CORS(server)
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')

def run():
    global df
    force = other_state_array[0]
    trig = other_state_array[2]
    trig_bin = "{0:012b}".format(int(trig*1000))
    trig_low = int(trig_bin[4:12], 2)
    trig_hi = int(trig_bin[0:4], 2)

    rise = other_state_array[1]

    print('Use Trigger: ' + str(force))

    atten = other_state_array[3]
    coupl = other_state_array[4]

    trig_condition = "".join([str(rise), str(force)])

    configs = [1, int(trig_condition, 2), trig_low, trig_hi, atten, coupl]
    #configs = [1, 2, 3, 4, 5, 6]
    print('Configs are: ' + str(configs))

    try:
        si.configure_scope(configs)
        print('Device Configured!')
    except usb.core.USBError:
        print('Device Not Ready')
        pass

    v_data = []
    t_data = []

    data_ready = None
    try:
        data_ready = si.check_for_data()
    except usb.core.USBError:
        print('Data Not Ready')

    print('Interrupt Received From Device - Requesting Data...')

    v_data = si.get_samples()
    t_data = np.arange(0, len(v_data), 1)

    d = {'t': t_data, 'data': v_data}
    df = pd.DataFrame(d)

    print(len(v_data))
    #print(df)

# Plotly init
initial_trace = go.Scatter(x=[], y=[], mode='lines')
layout = go.Layout(
    title="Input Signal",
    xaxis=dict(title='Time'),
    yaxis=dict(title='Amplitude (V)'),
    autosize=True
)

global_state = {
    'connect_to_scope': 0,
    'sample_rate': 80,
    'coupling': 0,
    'attenuation': 0,
    'single_button': 0,
    'run_button': 0,
    'stop_button': 0,
    'level': 1,
    'condition': 0,
    'force_trigger': 0,
    'normal_button': 0
}

# Arrays to store the values
# index: variable
# 0: connect_to_scope
# 1: single_button
# 2: run_button
# 3: stop_button
# 4: normal_button
control_buttons_array = [None] * 5  # For the specified control buttons
# index: variable
# 0: force_trigger
# 1: condition (rise/fall)
# 2: level (trigger value)
# 3: attenuation
# 5: coupling
# 6: sample_rate
other_state_array = [None] * 6  # For the remaining states


# !!!!!!!!!!!!!!!
# Rectangles
# !!!!!!!!!!!!!!!

# Rectangle 1 is defined in styles

# Sample Rate Rectangle
combined_rectangle_content = html.Div([
    html.Div("Sample Rate", style={'marginBottom': '10px'}),  # Sample Rate text
    dcc.Dropdown(
        id='sample-rate-dropdown',
        options=[
            {'label': '80 MSPS', 'value': 80},
            {'label': '70 MSPS', 'value': 70},
            {'label': '60 MSPS', 'value': 60},
            {'label': '50 MSPS', 'value': 50},
            {'label': '40 MSPS', 'value': 40},
        ],
        value=80,  # Default value
        clearable=False,
        style=dropdown_style
    )
], style=combined_rectangle_content_style)

# Coupling/Attenuation rectangle
# Needs more options for selection
rectangle_4_content = html.Div([
    html.Div("Scope Setup", style=inner_rectangle_style),
    html.Div([
        html.Div("Coupling", style=centered_section_style),
        dcc.Dropdown(
            id='coupling-dropdown',
            options=[
                {'label': 'AC', 'value': 'AC'},
                {'label': 'DC', 'value': 'DC'}
            ],
            value='AC',  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div(id='dummy-output-coupling', style={'display': 'none'}),
        html.Div("Attenuation", style=centered_section_style),
        dcc.Dropdown(
            id='attenuation-dropdown',
            options=[
                {'label': '1x', 'value': '1x'},
                {'label': '10x', 'value': '10x'}
            ],
            value='1x',  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div(id='dummy-output-attenuation', style={'display': 'none'}),
    ], style={'display': 'inline-block', 'width': '60%', 'textAlign': 'center'})
], style={'height': '100%', 'width': '100%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-around'})

#  Single button 
rectangle_6_content = html.Div([
    html.Div("Single", style={
        'display': 'inline-block', 
        'verticalAlign': 'middle',
        'marginRight': '10px'  # Add some space between the text and the icon
    }),
    html.Div(style={
        'display': 'inline-block', 
        'position': 'relative',
        'verticalAlign': 'middle',
        'height': '30px',  # Match the height of the triangle and rectangle
        'width': '40px'  # Adjust the width to contain the triangle and the thin rectangle
    }, children=[
        html.Div(style=triangle_style),
        html.Div(style=thin_rectangle_style)
    ])
], style={
    'textAlign': 'center',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'height': '100%',
    'width': '100%'  # Ensure the container takes the full width of the parent
})

# Run button triangle
rectangle_5_content = html.Div([
    html.Div("Run", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
    html.Div(style=play_icon_style)  # This div represents the play icon
], style={
    'textAlign': 'center',
    'display': 'flex',
    'alignItems': 'center',  # Center align items vertically
    'justifyContent': 'center',  # Center align items horizontally
    'height': '100%',  # Ensure the container takes the full height of the parent
})

# Stop Button
rectangle_7_content = html.Div([
    html.Div("Stop", style={
        'display': 'inline-block', 
        'verticalAlign': 'middle',
        'marginRight': '10px'  # Space between the text and the icon
    }),
    html.Div(style=square_icon_style)  # This div represents the stop icon
], style={
    'textAlign': 'center',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'height': '100%',
    'width': '100%'
})

# Trigger/Conditions, needs some clarification, also force trigger btn
rectangle_8_content = html.Div([
    html.Div("Trigger Setup", style=inner_rectangle_style),
    html.Div([
        html.Div("Level", style=centered_section_style),
        dcc.Dropdown(
            id='level-dropdown',
            options=[{'label': '1V', 'value': 1}, 
                     {'label': '5V', 'value': 5}],
            value=1,  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div(id='dummy-output-level', style={'display': 'none'}),
        html.Div("Condition", style=centered_section_style),
        dcc.Dropdown(
            id='condition-dropdown',
            options=[{'label': '↑Rising', 'value': 'Rising'}, 
                     {'label': '↓Falling', 'value': 'Falling'}],
            value='Rising',  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div(id='dummy-output-condition', style={'display': 'none'}),
        html.Div("Force Trigger", style=centered_section_style),
        html.Button("On", id='force-trigger-button', style=toggle_button_style),
        html.Div(id='dummy-output-force-trigger', style={'display': 'none'}),
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
], style={'height': '100%', 'width': '100%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-around'})

# First row of rectangles with adjusted layout
first_row_rectangles = html.Div(style=row_style, children=[
    html.Div(id='rectangle-1', children="Connect to Simple Scope", style=rectangle_1_style),
    html.Div(id='boolean-value', children='False', style={'display': 'none'}),
    html.Div(style={'width': '10px', 'display': 'inline-block'}),  # Spacer Div
    html.Div(id='combined-rectangle-2-3', children=combined_rectangle_content, style=combined_rectangle_style),
    html.Div(id='dummy-output-sample-rate', style={'display': 'none'}),
    html.Div(id='rectangle-4', children=rectangle_4_content, style=long_rectangle_style_scope),
])

# App layout definition including Upload component and Graph component
# Define the layout of your app
app.layout = html.Div([

    # Place new elements here
    # First row of rectangles
    first_row_rectangles,

    # Second row of rectangles
    html.Div(style=row_style, children=[
        html.Div(id='rectangle-6', children=rectangle_6_content, style=rectangle_style),
        html.Div(id='single-boolean-value', children='False', style={'display': 'none'}),
        html.Div(style={'width': '10px', 'display': 'inline-block'}),  # Spacer Div
        html.Div(id='rectangle-5', children=rectangle_5_content, style=rectangle_style),
        html.Div(id='run-boolean-value', children='False', style={'display': 'none'}),
        html.Div(id='rectangle-7', children=rectangle_7_content, style=rectangle_style),
        html.Div(id='stop-boolean-value', children='False', style={'display': 'none'}),
        html.Div(id='rectangle-8', children=rectangle_8_content, style=long_rectangle_style),  # Another longer rectangle
    ]),
    
    # Placeholder for the graph with division lines (styled as per your CSS)
    html.Div(id='chartDiv', style=styles['chartDiv'], children=[
        dcc.Graph(id='my-graph', figure={'data': [initial_trace], 'layout': layout}),
    ]),

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
    dcc.Download(id='download-dataframe-csv'),
    dcc.Interval(id='interval-component',
    interval=1*1000,  # in milliseconds
    n_intervals=0
)

])

# Initialize 'df' as a global variable outside of your callbacks
global df
d = {'t': [], 'data': []}
df = pd.DataFrame(d)

# I think this is the force trigger button
@app.callback(
    Output('force-trigger-button', 'children'),
    [Input('force-trigger-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_force_trigger(n_clicks):
    if n_clicks % 2 == 0:
        return "Off"
    else:
        return "On"

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
    [Input('interval-component', 'n_intervals')],
  # Add the switch's value as State
    prevent_initial_call=True
)
def update_graph(refresh):
    global df 
    ctx = dash.callback_context

    # Determine which input was triggered
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    """
    # If the reset button is clicked, clear the graph
    if triggered_id == 'reset-button':
        df = pd.DataFrame()  # Reset the 'df' variable
        return {'data': [initial_trace], 'layout': layout}
    """

    # If new file data is uploaded, update the graph
    if triggered_id == 'interval-component':
        # Generate a timestamp to force the update
        timestamp = datetime.now()
        if control_buttons_array[2] == 1:
            run()
        
        """
        # Check if the filter switch is enabled and apply the filter
        if 'On' in filter_toggle_label:
            # Define filter coefficients here for smoothing
            b = [1, -0.95]  # Numerator coefficients
            a = [1]         # Denominator coefficients
            filtered_data = lfilter(b, a, df['data'])
            trace = go.Scatter(x=df['t'], y=filtered_data, mode='lines', name='Filtered Data')
        else:
        """   
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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# New UI callbacks for Dash
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# "Connect to simple scope" button
@app.callback(
    Output('boolean-value', 'children'),
    [Input('rectangle-1', 'n_clicks')],
    [State('boolean-value', 'children')]
)
def toggle_boolean_value(n_clicks, current_value):
    if n_clicks is None:
        raise PreventUpdate
    new_value = current_value

    si.program_scope()
    time.sleep(1)
    try:
        si.connect_to_scope()
    except ValueError:
        print('error encountered')
        new_value = 'False'
        print(f"Boolean value changed to {new_value}")  # Log the change
        bit_value = 0
        global_state['connect_to_scope'] = bit_value
        return new_value
    
    new_value = 'True'
    if new_value == 'False':
        bit_value = 0
    if new_value == 'True':
        bit_value = 1
    global_state['connect_to_scope'] = bit_value
    print(f"Boolean value changed to {new_value}")  # Log the change
    return new_value

# Sample Rate
@app.callback(
    Output('dummy-output-sample-rate', 'children'),
    [Input('sample-rate-dropdown', 'value')],
    prevent_initial_call=True
)
def log_sample_rate_change(new_value):
    global_state['sample_rate'] = new_value
    print(f"Sample rate changed to {new_value}")
    return ""  # Dummy output, not used

# Coupling
@app.callback(
    Output('dummy-output-coupling', 'children'),
    [Input('coupling-dropdown', 'value')],
    prevent_initial_call=True
)
def log_coupling_change(new_value):
    if new_value == 'AC':
        bit_value = 0
    if new_value == 'DC':
        bit_value = 1
    global_state['coupling'] = bit_value
    print(f"Coupling changed to {new_value}")
    return ""  # Dummy output, not used

# Attentuation
@app.callback(
    Output('dummy-output-attenuation', 'children'),
    [Input('attenuation-dropdown', 'value')],
    prevent_initial_call=True
)
def log_attenuation_change(new_value):
    if new_value == '1x':
        bit_value = 0
    if new_value == '10x':
        bit_value = 1
    global_state['attenuation'] = bit_value
    print(f"Attenuation changed to {new_value}")
    return ""  # Dummy output, not used

# Single Button
@app.callback(
    Output('single-boolean-value', 'children'),
    [Input('rectangle-6', 'n_clicks')],
    [State('single-boolean-value', 'children')]
)
def toggle_single_boolean_value(n_clicks, current_value):
    if n_clicks is None:
        raise PreventUpdate
    
    run_stat = control_buttons_array[2]
    if run_stat == 0:
        run()
    new_value = 'False'
    if new_value == 'False':
        bit_value = 0
    if new_value == 'True':
        bit_value = 1
    global_state['single_button'] = bit_value
    print(f"Single button boolean value changed to {new_value}")  # Log the change
    return new_value

# Run Button
@app.callback(
    Output('run-boolean-value', 'children'),
    [Input('rectangle-5', 'n_clicks'),
    Input('rectangle-7', 'n_clicks')],
    [State('run-boolean-value', 'children')]
)
def toggle_run_boolean_value(n_clicks, stop, current_value):
    if n_clicks is None:
        new_value = 'False'
        return new_value
        raise PreventUpdate
    
    ctx = dash.callback_context
    # Determine which input was triggered
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    new_value = 'False'

    if triggered_id == 'rectangle-7':
        new_value = 'False'
    else:
        new_value = 'True'

    if new_value == 'False':
        bit_value = 0
    if new_value == 'True':
        bit_value = 1
    global_state['run_button'] = bit_value
    print(f"Run button boolean value changed to {new_value}")  # Log the change
    return new_value

# Stop Button
@app.callback(
    Output('stop-boolean-value', 'children'),
    [Input('rectangle-7', 'n_clicks')],
    [State('stop-boolean-value', 'children')]
)
def toggle_stop_boolean_value(n_clicks, current_value):
    if n_clicks is None:
        raise PreventUpdate
    
    new_value = 'False' if current_value == 'True' else 'True'
    if new_value == 'False':
        bit_value = 0
    if new_value == 'True':
        bit_value = 1
    global_state['stop_button'] = bit_value
    print(f"Stop button boolean value changed to {new_value}")  # Log the change
    return new_value

# Level Selection:
@app.callback(
    Output('dummy-output-level', 'children'),
    [Input('level-dropdown', 'value')],
    prevent_initial_call=True
)
def log_level_change(new_value):
    global_state['level'] = new_value
    print(f"Level changed to {new_value}")
    return ""  # Dummy output, not used

# Condition DropDown
@app.callback(
    Output('dummy-output-condition', 'children'),
    [Input('condition-dropdown', 'value')],
    prevent_initial_call=True
)
def log_condition_change(new_value):
    if new_value == 'Rising':
        bit_value = 0
    if new_value == 'Falling':
        bit_value = 1
    global_state['condition'] = bit_value
    print(f"Condition changed to {new_value}")
    return ""  # Dummy output, not used

# Force trigger
@app.callback(
    Output('dummy-output-force-trigger', 'children'),
    [Input('force-trigger-button', 'n_clicks')],
    [State('dummy-output-force-trigger', 'children')],
    prevent_initial_call=True
)
def toggle_force_trigger_button(n_clicks, current_state):
    new_state = 'On' if current_state == 'Off' else 'Off'
    if new_state == 'Off':
        bit_value = 0
    if new_state == 'On':
        bit_value = 1
    global_state['force_trigger'] = bit_value
    print(f"Force Trigger state changed to {new_state}")  # Log the change
    return new_state

# FTT to Normal Switch
# Confirmed tracking of the variable
@app.callback(
    Output('normal-button', 'children'),
    [Input('normal-button', 'n_clicks')],
    [State('normal-button', 'children')],
    prevent_initial_call=True
)
def toggle_normal_button(n_clicks, current_label):
    new_label = 'Filter' if current_label == 'Normal' else 'Normal'
    if new_label == 'Normal':
        bit_value = 0
    if new_label == 'Filter':
        bit_value = 1
    global_state['normal_button'] = bit_value
    print(f"Normal button label changed to {new_label}")  # Log the change
    return new_label

# button state tracking
@app.callback(
    Output('interval-component', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_every_second(n):
    # Update control_buttons_array based on global_state
    control_buttons_array[0] = global_state['connect_to_scope']
    control_buttons_array[1] = global_state['single_button']
    control_buttons_array[2] = global_state['run_button']
    control_buttons_array[3] = global_state['stop_button']
    control_buttons_array[4] = global_state['normal_button']

    # Synchronize other_state_array with global_state
    other_state_array[0] = global_state['force_trigger']
    other_state_array[1] = global_state['condition']
    other_state_array[2] = global_state['level']
    other_state_array[3] = global_state['attenuation']
    other_state_array[4] = global_state['coupling']
    other_state_array[5] = global_state['sample_rate']

    #print(f"Control Buttons Array: {control_buttons_array}")
    #print(f"Other States Array: {other_state_array}")
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
