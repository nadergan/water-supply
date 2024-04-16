from flask import Flask, jsonify, request, render_template
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib import scale
from matplotlib import transforms as mtransforms
import os
import sys
import uuid
import logging

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

def main(save_path, first_line_points, second_line_points):
    """
    Generate the chart using Matplotlib and save it to the specified path.

    :param save_path: Path to save the generated chart image
    :param first_line_points: List of points for the first line
    :param second_line_points: List of points for the second line
    """
    plt.figure(figsize=(10, 6))
    plt.rc('lines', linewidth=2, color='red')
    plt.rc('grid', linestyle="-", color='black')
    fig, ax = plt.subplots()
    plot_line(first_line_points, '-', 'blue')
    
    if second_line_points:
        plot_line(second_line_points, '-', 'red')

   # Set the X-Axis and Y-Axis Limit values
    last_point_x = int(first_line_points[-2][0])
    first_point_y = int(first_line_points[0][1])
    plt.xlim(0, last_point_x * 1.1)  
    plt.ylim(0, first_point_y * 1.2)  

    plt.gca().set_xscale('hydraulic-n-1.85')
    plt.gca().xaxis.set_major_locator(MultipleLocator(230))
    plt.gca().yaxis.set_major_locator(MultipleLocator(10))
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))
    plt.gca().tick_params(axis='both', which='both', length=0)

    plt.tick_params(axis='both', which='both', left=True, bottom=True, right=False, top=False, color='black')
    plt.tick_params(axis='both', which='minor', width=1, length=0)

    plt.ylabel('Pressure (psi)')
    plt.xlabel('Flow (gpm)')
    plt.title('WATER SUPPLY ANALYSIS')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()



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

        q0_q20 = calculated_samples(first_line_points)
        first_line_points.extend(q0_q20)

        logging.info(f"Updated first line points: {first_line_points}")

        unique_filename = str(uuid.uuid4()) + ".png"
        save_path = os.path.join("static/charts/", unique_filename)

        main(save_path, first_line_points, second_line_points)

        return jsonify({
            "image_path": save_path,
            "first_line_points": first_line_points,
            "second_line_points": second_line_points
        })
    except Exception as e:
        logging.error(f"Error generating plot: {str(e)}")
        return jsonify({"error": "An error occurred while generating the plot"}), 500
    


if __name__ == '__main__':
    scale.register_scale(HydraulicN185Scale)
    app.run(debug=True, host="0.0.0.0", port=3000)
