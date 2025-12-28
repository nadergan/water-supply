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
plt.rcParams['axes.unicode_minus'] = False

# Try to find and set a Hebrew-compatible font
def setup_hebrew_fonts():
    try:
        # Get all available fonts
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        logging.info(f"Total available fonts: {len(available_fonts)}")
        
        # Common Hebrew fonts that might be available (in order of preference)
        hebrew_fonts = [
            'Arial Unicode MS',  # Best Hebrew support
            'Noto Sans Hebrew', 
            'Arial Hebrew',
            'David',
            'Times New Roman',   # Often has Hebrew support
            'Arial',            # Basic Hebrew support
            'DejaVu Sans'       # Fallback
        ]
        
        hebrew_font = None
        for font in hebrew_fonts:
            if font in available_fonts:
                hebrew_font = font
                logging.info(f"Found Hebrew-compatible font: {hebrew_font}")
                break
        
        if hebrew_font:
            plt.rcParams['font.family'] = [hebrew_font, 'sans-serif']
            logging.info(f"Using Hebrew font: {hebrew_font}")
        else:
            # Last resort - try system default with Hebrew fallback
            plt.rcParams['font.family'] = ['sans-serif']
            logging.warning("No specific Hebrew font found, using system default")
        
        # Additional font settings for better Hebrew rendering
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.weight'] = 'normal'
        
        return hebrew_font
        
    except Exception as e:
        logging.error(f"Font configuration error: {e}")
        plt.rcParams['font.family'] = ['sans-serif']
        return None

# Setup fonts
current_font = setup_hebrew_fonts()

def test_font_support():
    """Test if the current font supports Hebrew characters"""
    try:
        import matplotlib.font_manager as fm
        # Get current font
        current_font_prop = fm.FontProperties(family=plt.rcParams['font.family'])
        font_path = fm.findfont(current_font_prop)
        logging.info(f"Current font path: {font_path}")
        
        # Test Hebrew character rendering
        test_hebrew = "בדיקה"  # Hebrew word meaning "test"
        logging.info(f"Testing Hebrew text: {test_hebrew}")
        
    except Exception as e:
        logging.error(f"Font support test failed: {e}")

# Test font support on startup
test_font_support()

def fix_hebrew_text(text):
    """
    Fix Hebrew text direction for matplotlib display.
    Enhanced version with better error handling.
    """
    if not text or not isinstance(text, str):
        return text
    
    # Check if text contains Hebrew characters
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
    if not hebrew_pattern.search(text):
        return text  # No Hebrew, return as is
    
    try:
        # Try using python-bidi (best solution for mixed Hebrew/English text)
        from bidi.algorithm import get_display
        result = get_display(text)
        logging.debug(f"Hebrew text processed with bidi: '{text}' -> '{result}'")
        return result
    except ImportError:
        logging.warning("python-bidi not available, using fallback Hebrew processing")
        # Fallback: simple character reversal for pure Hebrew text
        return text[::-1] if hebrew_pattern.search(text) else text
    except Exception as e:
        logging.error(f"Error processing Hebrew text '{text}': {e}")
        return text  # Return original text if processing fails

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

def plot_line(points, line_style='-', color='blue', label=None):
    """
    Plot a line connecting the provided points and label the first three points.

    :param points: List of (x, y) points
    :param line_style: Line style for the plot
    :param color: Color of the line and points
    :param label: Legend label for the line
    """
    x, y = zip(*points)
    
    # Plot main line with improved styling
    plt.plot(x[:2], y[:2], line_style, color=color, linewidth=3, 
             label=label, marker='o', markersize=8, markerfacecolor='white', 
             markeredgecolor=color, markeredgewidth=2)
    
    # Plot dashed extension line
    if len(points) >= 3:
        plt.plot(x[1:3], y[1:3], '--', color=color, linewidth=2, alpha=0.8)
    
    # Add point labels with better styling
    for i, txt in enumerate(points[:3]):
        if (txt[0] != 0) or (txt[1] != 0):
            plt.text(txt[0], txt[1], f'({int(txt[0])}, {int(txt[1])})', 
                    ha='left', va='bottom', fontsize=9, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                             edgecolor=color, alpha=0.8))
    
    # Plot points with enhanced styling
    plt.scatter(x[:3], y[:3], color=color, s=80, zorder=5, 
               edgecolors='white', linewidth=2)

def plot_optional_point(point, label, color='green'):
    """
    Plot an optional data point with a line from origin and label.

    :param point: (x, y) coordinates of the point
    :param label: Label for the point (supports Hebrew)
    :param color: Color of the point and line
    """
    x, y = point
    
    # Draw line from origin with improved styling
    plt.plot([0, x], [0, y], '--', color=color, alpha=0.6, linewidth=2)
    
    # Plot the point with enhanced styling
    plt.scatter([x], [y], color=color, s=120, marker='D', zorder=6,
               edgecolors='white', linewidth=2)
    
    # Format coordinates
    coord_text = f'({int(x)}, {int(y)})'
    
    # Combine label with coordinates and fix Hebrew text
    if label and label.strip():
        # Fix Hebrew text direction
        fixed_label = fix_hebrew_text(label.strip())
        display_text = f'{fixed_label}\n{coord_text}'
        logging.info(f"Plotting label: original='{label}', fixed='{fixed_label}'")
    else:
        display_text = coord_text
    
    # Add label with enhanced styling
    plt.text(x, y, display_text, ha='center', va='bottom', 
             bbox=dict(boxstyle="round,pad=0.4", facecolor=color, alpha=0.2,
                      edgecolor=color, linewidth=1),
             fontsize=10, fontfamily='sans-serif', fontweight='bold')

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
    
    # Modern styling
    plt.style.use('default')  # Clean base style
    
    # Set figure size for 640px width while maintaining aspect ratio (640x400px at 100 DPI)
    fig, ax = plt.subplots(figsize=(6.4, 4), facecolor='white')
    
    # Set background color
    ax.set_facecolor('#f8f9fa')  # Light gray background
    
    # Configure grid for better visibility
    ax.grid(True, linestyle='-', alpha=0.5, color='#999999', linewidth=1)
    ax.set_axisbelow(True)  # Put grid behind data
    
    plot_line(first_line_points, '-', '#2E86AB')  # Modern blue
    
    if second_line_points:
        plot_line(second_line_points, '-', '#A23B72')  # Modern purple-red

    # Plot optional points if provided
    if optional_points:
        colors = ['#F18F01', '#C73E1D']  # Modern orange and red
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
    
    # Set X-axis to end at exactly 10% beyond the last value
    plt.xlim(0, max_x * 0.90)   # 10% margin (current setting)
    plt.ylim(0, max_y * 1.15)   # 20% margin for Y-axis  

    plt.gca().set_xscale('hydraulic-n-1.85')
    
    # Force x-axis to show labels
    ax.xaxis.set_visible(True)
    ax.yaxis.set_visible(True)
    
    # Enhanced axis styling
    ax = plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(100))  # More frequent x-axis ticks
    ax.xaxis.set_minor_locator(MultipleLocator(50))   # Add minor ticks for x-axis
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    
    # Configure tick marks and labels
    ax.tick_params(axis='both', which='both', length=0, width=0)  # Remove tick marks
    ax.tick_params(axis='both', which='major', labelsize=11, colors='#000000')
    ax.tick_params(axis='x', which='major', labelsize=12, colors='#000000', labelbottom=True)  # Ensure x-axis labels are visible
    ax.tick_params(axis='y', which='major', labelleft=True)  # Ensure y-axis labels are visible
    
    # Style the spines (borders)
    for spine in ax.spines.values():
        spine.set_color('#cccccc')
        spine.set_linewidth(1)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Enhanced labels and title
    plt.ylabel('Pressure (psi)', fontsize=12, fontweight='bold', color='#333333')
    plt.xlabel('Flow (gpm)', fontsize=12, fontweight='bold', color='#333333')
    plt.title('WATER SUPPLY ANALYSIS', fontsize=16, fontweight='bold', 
              color='#2c3e50', pad=20)
    
    # Add legend if there are multiple lines
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True,
                  framealpha=0.9, edgecolor='#cccccc')

    plt.tight_layout()
    
    # Save with 100 DPI for 640x400px output (remove bbox_inches to maintain exact size)
    plt.savefig(save_path, dpi=100, 
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
