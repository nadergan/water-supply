from flask import Flask, jsonify, request, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib import scale
from matplotlib import transforms as mtransforms
import os
import sys
import uuid
import logging
import re

# Configure matplotlib for Hebrew support
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# Try to find and set a Hebrew-compatible font
try:
    # Common Hebrew fonts that might be available
    hebrew_fonts = ['David', 'Arial Hebrew', 'Noto Sans Hebrew', 'DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    hebrew_font = None
    for font in hebrew_fonts:
        if font in available_fonts:
            hebrew_font = font
            break
    
    if hebrew_font:
        plt.rcParams['font.family'] = [hebrew_font]
        logging.info(f"Using Hebrew font: {hebrew_font}")
    else:
        # Fallback to DejaVu Sans which has some Hebrew support
        plt.rcParams['font.family'] = ['DejaVu Sans']
        logging.info("Using fallback font: DejaVu Sans")
        
except Exception as e:
    logging.warning(f"Font configuration error: {e}")
    plt.rcParams['font.family'] = ['DejaVu Sans']

def fix_hebrew_text(text):
    """
    Fix Hebrew text direction for matplotlib display.
    This function handles the bidirectional text issue.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Check if text contains Hebrew characters
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
    if not hebrew_pattern.search(text):
        return text  # No Hebrew, return as is
    
    try:
        # Try using python-bidi if available
        from bidi.algorithm import get_display
        return get_display(text)
    except ImportError:
        # Fallback method: simple character reversal for Hebrew parts
        logging.info("python-bidi not available, using fallback Hebrew text processing")
        
        # Split text into lines
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            if hebrew_pattern.search(line):
                # Simple approach: reverse the entire line if it contains Hebrew
                # This works for pure Hebrew text
                words = line.split()
                hebrew_words = []
                latin_words = []
                
                for word in words:
                    if hebrew_pattern.search(word):
                        # Reverse Hebrew words
                        hebrew_words.append(word[::-1])
                    else:
                        latin_words.append(word)
                
                # Combine: Hebrew words first (reversed), then Latin words
                if hebrew_words and latin_words:
                    fixed_line = ' '.join(hebrew_words) + ' ' + ' '.join(latin_words)
                elif hebrew_words:
                    fixed_line = ' '.join(reversed(hebrew_words))
                else:
                    fixed_line = ' '.join(latin_words)
            else:
                fixed_line = line
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class HydraulicN185Scale(scale.ScaleBase):
    name = 'hydraulic-n-1.85'

    def __init__(self, axis, **kwargs):
        scale.ScaleBase.__init__(self, axis)

    def get_transform(self):
        return HydraulicN185Transform()

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(MultipleLocator(100))
        axis.set_minor_locator(MultipleLocator(10))

class HydraulicN185Transform(mtransforms.Transform):
    input_dims = 1
    output_dims = 1
    is_separable = True

    def transform_non_affine(self, a):
        array = np.array(list(map(lambda x: max((x / 100) * 1.85, 1) * x, a)))
        return array

    def inverted(self):
        return HydraulicN185Transform()

scale.register_scale(HydraulicN185Scale)

def plot_line(points, line_style='-', color='blue'):
    """
    Plot a line connecting the provided points and label the first three points.

    :param points: List of (x, y) points
    :param line_style: Line style for the plot
    :param color: Color of the line and points
    """
    x, y = zip(*points)
    plt.plot(x[:2], y[:2], line_style, color=color)  # Plot the line between the first two points
    if len(points) >= 3:
        plt.plot(x[1:3], y[1:3], '--', color=color)  # Plot the line between the second and third points
    for txt in points[:3]:  # Label the first three points
        if (txt[0] != 0) or (txt[1] != 0):
            plt.text(txt[0], txt[1], f'({int(txt[0])}, {int(txt[1])})', ha='left', va="center")
    plt.scatter(x[:3], y[:3], color=color)  # Scatter the first three points

def plot_optional_point(point, label, color='green'):
    """
    Plot an optional data point with a line from origin and label.

    :param point: (x, y) coordinates of the point
    :param label: Label for the point (supports Hebrew)
    :param color: Color of the point and line
    """
    x, y = point
    # Draw line from origin (0,0) to the point
    plt.plot([0, x], [0, y], '--', color=color, alpha=0.7)
    # Plot the point
    plt.scatter([x], [y], color=color, s=100, marker='o')
    
    # Format coordinates
    coord_text = f'({int(x)}, {int(y)})'
    
    # Combine label with coordinates and fix Hebrew text
    if label and label.strip():
        # Fix Hebrew text direction
        fixed_label = fix_hebrew_text(label.strip())
        display_text = f'{fixed_label}\n{coord_text}'
    else:
        display_text = coord_text
    
    # Add label with Hebrew support
    plt.text(x, y, display_text, ha='center', va='bottom', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3),
             fontsize=10, wrap=True)

def calculated_samples(points):
    """
    Calculate Q0 and Q20 based on the provided points.

    :param points: List of (x, y) points
    :return: List of two points: [Q20, 20] and [Q0, 0]
    """
    y1 = points[0][1]
    x2 = points[1][0]
    y2 = points[1][1]

    k = (x2) / ((y1 - y2) ** (1.0 / 1.85))
    Q0 = int(k * (y1 ** (1.0 / 1.85)))
    Q20 = int(k * ((y1 - 20) ** (1.0 / 1.85)))
    return [[Q20, 20], [Q0, 0]]

def main(save_path, first_line_points, second_line_points, optional_points=None):
    """
    Generate the chart using Matplotlib and save it to the specified path.

    :param save_path: Path to save the generated chart image
    :param first_line_points: List of points for the first line
    :param second_line_points: List of points for the second line
    :param optional_points: List of optional points with labels
    """
    # Close any existing figures
    plt.close('all')
    
    plt.rc('lines', linewidth=2, color='red')
    plt.rc('grid', linestyle="-", color='black')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    plot_line(first_line_points, '-', 'blue')
    
    if second_line_points:
        plot_line(second_line_points, '-', 'red')

    # Plot optional points if provided
    if optional_points:
        colors = ['green', 'purple']  # Different colors for the two optional points
        for i, point_data in enumerate(optional_points):
            if point_data and 'flow' in point_data and 'pressure' in point_data:
                flow = float(point_data['flow'])
                pressure = float(point_data['pressure'])
                label = point_data.get('label', f'Point {i+1}')
                color = colors[i % len(colors)]
                plot_optional_point((flow, pressure), label, color)

    # Set the X-Axis and Y-Axis Limit values
    last_point_x = int(first_line_points[-2][0])
    first_point_y = int(first_line_points[0][1])
    
    # Consider optional points for axis limits
    all_x_values = [point[0] for point in first_line_points]
    all_y_values = [point[1] for point in first_line_points]
    
    if optional_points:
        for point_data in optional_points:
            if point_data and 'flow' in point_data and 'pressure' in point_data:
                all_x_values.append(float(point_data['flow']))
                all_y_values.append(float(point_data['pressure']))
    
    max_x = max(all_x_values) if all_x_values else last_point_x
    max_y = max(all_y_values) if all_y_values else first_point_y
    
    plt.xlim(0, max_x * 1.1)  
    plt.ylim(0, max_y * 1.2)  

    plt.gca().set_xscale('hydraulic-n-1.85')
    plt.gca().xaxis.set_major_locator(MultipleLocator(230))
    plt.gca().yaxis.set_major_locator(MultipleLocator(10))
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))
    plt.gca().tick_params(axis='both', which='both', length=0)

    plt.tick_params(axis='both', which='both', left=True, bottom=True, right=False, top=False, color='black')
    plt.tick_params(axis='both', which='minor', width=1, length=0)

    # Set labels with Hebrew support
    plt.ylabel('Pressure (psi)', fontsize=12)
    plt.xlabel('Flow (gpm)', fontsize=12)
    plt.title('WATER SUPPLY ANALYSIS', fontsize=14)
    plt.grid(True)

    plt.tight_layout()
    
    # Save with higher DPI for better text rendering
    plt.savefig(save_path, dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    try:
        data = request.json
        
        # Extract measurement1 and measurement2 values from the JSON data
        measurement1 = data.get('measurement1', {})
        measurement2 = data.get('measurement2', {})

        # Extract optional points
        optional_point1 = data.get('optional_point1', {})
        optional_point2 = data.get('optional_point2', {})
        optional_points = []
        
        if optional_point1.get('flow') and optional_point1.get('pressure'):
            optional_points.append(optional_point1)
        if optional_point2.get('flow') and optional_point2.get('pressure'):
            optional_points.append(optional_point2)

        # Extract flow and pressure values for each measurement
        flow1 = float(measurement1.get('flow', 0))
        pressure1 = float(measurement1.get('pressure', 0))
        flow2 = float(measurement2.get('flow', 0))
        pressure2 = float(measurement2.get('pressure', 0))

        # Create first_line_points and second_line_points
        first_line_points = [(flow1, pressure1), (flow2, pressure2)]
        second_line_points = []  # Add points for the second line if needed

        # Input validation
        if not first_line_points:
            return jsonify({"error": "Missing or invalid data points"}), 400

        logging.info(f"First line points: {first_line_points}")
        logging.info(f"Optional points: {optional_points}")

        q0_q20 = calculated_samples(first_line_points)
        first_line_points.extend(q0_q20)

        logging.info(f"Updated first line points: {first_line_points}")

        # Create directories if they don't exist
        charts_dir = "static/charts"
        os.makedirs(charts_dir, exist_ok=True)
        
        unique_filename = str(uuid.uuid4()) + ".png"
        save_path = os.path.join(charts_dir, unique_filename)

        main(save_path, first_line_points, second_line_points, optional_points)

        return jsonify({
            "image_path": save_path,
            "first_line_points": first_line_points,
            "second_line_points": second_line_points,
            "optional_points": optional_points
        })
    except Exception as e:
        logging.error(f"Error generating plot: {str(e)}")
        import traceback
        logging.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"error": "An error occurred while generating the plot"}), 500

if __name__ == '__main__':
    scale.register_scale(HydraulicN185Scale)
    app.run(debug=True, host="0.0.0.0", port=3000)
    