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

# Define a style for each rectangle
rectangle_style = {
    'width': '100px',  # Width of each rectangle
    'height': '100px',  # Height of each rectangle
    'border': '1px solid black',  # Border style
    'display': 'inline-block',  # Display type to align horizontally
    'margin': '10px'  # Margin around each rectangle
}

# Define a style for the container of each row of rectangles
row_style = {
    'textAlign': 'center',  # Center align the rectangles
    'marginBottom': '20px'  # Margin at the bottom of each row
}

# Updated style for the first rectangle
rectangle_1_style = {
    'width': '100px',  # Width of the rectangle
    'height': '100px',  # Height of the rectangle
    'border': '1px solid black',  # Border style
    'display': 'flex',  # Use flexbox for centering
    'alignItems': 'center',  # Vertical centering
    'justifyContent': 'center',  # Horizontal centering
    'margin': '10px',  # Margin around the rectangle
    'backgroundColor': 'lightblue',  # Light blue background color
    'color': 'black',  # Black text color
    'cursor': 'pointer'  # Change cursor to indicate clickability
}

play_icon_style = {
    'width': '0',
    'height': '0',
    'borderTop': '15px solid transparent',  # Top border
    'borderBottom': '15px solid transparent',  # Bottom border
    'borderLeft': '30px solid black',  # Left border forms the triangle, pointing to the right
    'display': 'inline-block',
    'marginLeft': '10px',
    'verticalAlign': 'middle'  # Align vertically in the middle
}

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

skip_icon_style = {
    'position': 'relative',  # Relative positioning to contain the inner rectangle
    'display': 'inline-block',
    'marginLeft': '10px',
    'verticalAlign': 'middle'
}

triangle_style = {
    'width': '0',
    'height': '0',
    'borderTop': '15px solid transparent',
    'borderBottom': '15px solid transparent',
    'borderLeft': '30px solid black',
    'position': 'absolute',  # Positioned absolutely within the skip icon container
    'left': '0',
    'top': '0'
}

thin_rectangle_style = {
    'width': '8px',  # Width of the thin rectangle
    'height': '30px',  # Height should match the height of the triangle
    'backgroundColor': 'black',
    'position': 'absolute',  # Positioned absolutely to sit at the tip of the triangle
    'left': '30px',  # Positioned to the right of the triangle
    'top': '0'
}

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

square_icon_style = {
    'width': '30px',  # Width of the square
    'height': '30px',  # Height of the square
    'backgroundColor': 'red',  # Red color for the stop icon
    'display': 'inline-block',
    'verticalAlign': 'middle',
    'marginLeft': '10px'
}

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

# Assuming each rectangle is 100px wide with a 10px margin
combined_rectangle_width = 2 * 100 + 2 * 10  # Double width plus margins

combined_rectangle_style = {
    'width': f'{combined_rectangle_width}px',  # Set the combined width
    'height': '100px',  # Keep the height the same as the original rectangles
    'border': '1px solid black',  # Border style
    'display': 'inline-block',  # Display type to align horizontally
    'margin': '10px'  # Margin around the rectangle
}

combined_rectangle_content_style = {
    'textAlign': 'center',  # Center align text
    'paddingTop': '20px',  # Padding at the top for spacing
    'height': '100%'  # Ensure it fills the rectangle
}

dropdown_style = {
    'width': '80%',  # Width of the dropdown
    'margin': '0 auto'  # Center the dropdown horizontally
}

combined_rectangle_content = html.Div([
    html.Div("Sample Rate", style={'marginBottom': '10px'}),  # Sample Rate text
    dcc.Dropdown(
        id='sample-rate-dropdown',
        options=[
            {'label': '90 MSPS', 'value': '90MSPS'},
            {'label': '80 MSPS', 'value': '80MSPS'},
            {'label': '70 MSPS', 'value': '70MSPS'}
        ],
        value='80MSPS',  # Default value
        clearable=False,
        style=dropdown_style
    )
], style=combined_rectangle_content_style)

# Assuming each rectangle is 100px wide with a 10px margin on each side
long_rectangle_width = 3 * 100 + 4 * 10  # Three rectangles width plus margins

long_rectangle_style = {
    'width': f'{800}px',  # Set the combined width
    'height': '100px',  # Keep the height the same as the original rectangles
    'border': '1px solid black',  # Border style
    'display': 'inline-block',  # Display type to align horizontally
    'margin': '10px'  # Margin around the rectangle
}

# Long rectangle Scope setup stuff

long_rectangle_style_scope = {
    'width': f'{700}px',  # Set the combined width
    'height': '100px',  # Keep the height the same as the original rectangles
    'border': '1px solid black',  # Border style
    'display': 'inline-block',  # Display type to align horizontally
    'margin': '10px'  # Margin around the rectangle
}

inner_rectangle_style = {
    'border': '2px solid blue',
    'backgroundColor': 'transparent',
    'height': '80px',
    'width': '30%',  # Adjust as needed
    'display': 'inline-block',
    'textAlign': 'center',
    'lineHeight': '80px',  # Align text vertically
    'float': 'left'  # Align to the left
}

centered_section_style = {
    'display': 'inline-block',
    'margin': '0 10px',  # Spacing around the center section
    'textAlign': 'center',
    'verticalAlign': 'middle',
    'lineHeight': '100px'  # Adjust to align text vertically in the rectangle
}

dropdown_style = {
    'width': '100px',  # Width of the dropdown
    'display': 'inline-block',
    'verticalAlign': 'middle'
}

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
        )
    ], style={'display': 'inline-block', 'width': '60%', 'textAlign': 'center'})
], style={'height': '100%', 'width': '100%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-around'})

# Trigger setup

toggle_button_style = {
    'display': 'inline-block',
    'marginLeft': '10px',
    'padding': '5px 10px',
    'backgroundColor': '#ddd',
    'border': 'none',
    'cursor': 'pointer'
}

# Coupling need to specify more available options
rectangle_8_content = html.Div([
    html.Div("Trigger Setup", style=inner_rectangle_style),
    html.Div([
        html.Div("Level", style=centered_section_style),
        dcc.Dropdown(
            id='coupling-dropdown',
            options=[{'label': '1V', 'value': '1V'}, {'label': '5V', 'value': '5V'}],
            value='1V',  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div("Condition", style=centered_section_style),
        dcc.Dropdown(
            id='attenuation-dropdown',
            options=[{'label': '↑Rising', 'value': 'Rising'}, {'label': '↓Falling', 'value': 'Falling'}],
            value='Rising',  # Default value
            clearable=False,
            style=dropdown_style
        ),
        html.Div("Force Trigger", style=centered_section_style),
        html.Button("Off", id='force-trigger-button', style=toggle_button_style)
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
], style={'height': '100%', 'width': '100%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-around'})

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
    
# Row Style

row_style = {
    'textAlign': 'center',
    'marginBottom': '20px',
    'display': 'flex',  # Use flex display for better alignment control
    'alignItems': 'center',  # Align items vertically in the center
    'justifyContent': 'flex-start'  # Align items to the start of the row
}

# First row of rectangles with adjusted layout
first_row_rectangles = html.Div(style=row_style, children=[
    html.Div(id='rectangle-1', children="Connect to Simple Scope", style=rectangle_1_style),
    html.Div(id='boolean-value', children='True', style={'display': 'none'}),
    html.Div(style={'width': '10px', 'display': 'inline-block'}),  # Spacer Div
    html.Div(id='combined-rectangle-2-3', children=combined_rectangle_content, style=combined_rectangle_style),
    html.Div(id='rectangle-4', children=rectangle_4_content, style=long_rectangle_style_scope),  # Another longer rectangle
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
        html.Div(style={'width': '10px', 'display': 'inline-block'}),  # Spacer Div
        html.Div(id='rectangle-5', children=rectangle_5_content, style=rectangle_style),
        html.Div(id='rectangle-7', children=rectangle_7_content, style=rectangle_style),
        html.Div(id='rectangle-8', children=rectangle_8_content, style=long_rectangle_style),  # Another longer rectangle
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

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# New UI callbacks for Dash
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Connect to simple scope variable record
@app.callback(
    Output('boolean-value', 'children'),
    [Input('rectangle-1', 'n_clicks')],
    [State('boolean-value', 'children')]
)
def toggle_boolean_value(n_clicks, current_value):
    if n_clicks is None:
        raise PreventUpdate
    
    new_value = 'False' if current_value == 'True' else 'True'
    print(f"Boolean value changed to {new_value}")  # Log the change
    return new_value

# Confirmed tracking of the variable
@app.callback(
    Output('normal-button', 'children'),
    [Input('normal-button', 'n_clicks')],
    [State('normal-button', 'children')],
    prevent_initial_call=True
)
def toggle_normal_button(n_clicks, current_label):
    new_label = 'FFT' if current_label == 'Normal' else 'Normal'
    print(f"Normal button label changed to {new_label}")  # Log the change
    return new_label

if __name__ == '__main__':
    app.run_server(debug=True)
