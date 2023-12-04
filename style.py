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

square_icon_style = {
    'width': '30px',  # Width of the square
    'height': '30px',  # Height of the square
    'backgroundColor': 'red',  # Red color for the stop icon
    'display': 'inline-block',
    'verticalAlign': 'middle',
    'marginLeft': '10px'
}

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

# Assuming each rectangle is 100px wide with a 10px margin on each side
long_rectangle_width = 3 * 100 + 4 * 10  # Three rectangles width plus margins

long_rectangle_style = {
    'width': f'{800}px',  # Set the combined width
    'height': '100px',  # Keep the height the same as the original rectangles
    'border': '1px solid black',  # Border style
    'display': 'inline-block',  # Display type to align horizontally
    'margin': '10px'  # Margin around the rectangle
}

# Row Style
row_style = {
    'textAlign': 'center',
    'marginBottom': '20px',
    'display': 'flex',  # Use flex display for better alignment control
    'alignItems': 'center',  # Align items vertically in the center
    'justifyContent': 'flex-start'  # Align items to the start of the row
}

# Trigger setup
toggle_button_style = {
    'display': 'inline-block',
    'marginLeft': '10px',
    'padding': '5px 10px',
    'backgroundColor': '#ddd',
    'border': 'none',
    'cursor': 'pointer'
}
