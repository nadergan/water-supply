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

app = Flask(__name__)


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

# Draw the Chart lines
def plot_line(points, line_style='-', color='black'):
    x, y = zip(*points)
    plt.plot(x[:2], y[:2], line_style, color=color)  # Plot the line between the first two points
    if len(points) >= 3:
        plt.plot(x[1:3], y[1:3], '--', color=color)  # Plot the line between the second and third points
    for txt in points[:3]:  # Label the first three points
        if (txt[0] != 0) or (txt[1] != 0):
            plt.text(txt[0], txt[1], f'({txt[0]}, {txt[1]})', ha='left', va="center")
    plt.scatter(x[:3], y[:3], color=color)  # Scatter the first three points


## Calculate the Q0 and Q20
def calculated_samples(points):
    y1 = points[0][1]
    x2 = points[1][0]
    y2 = points[1][1]
    
    k   = (x2) / ( (y1-y2) ** ( 1.0 / 1.85 ) )
    Q0  = int( k * (  y1  ** (1.0 / 1.85) ) )
    Q20 = int( k * ( ( y1 - 20 ) ** (1.0 / 1.85) ) )
    return [ [Q20, 20], [Q0, 0] ]


## 
def main(save_path, first_line_points, second_line_points):
    plt.rc('lines', linewidth=2, color='red')
    plt.rc('grid', linestyle="-", color='black')

    fig, ax = plt.subplots()

    plot_line(first_line_points, '-', 'blue')
    plot_line(second_line_points, '-', 'red')

    # Set the X-Axis and Y-Axis Limit values
    last_point_x = int(first_line_points[-1][0])
    first_point_y = int(first_line_points[0][1])

    ax.set_xlim([0, int(last_point_x * 1.05 )])
    ax.set_ylim([0, int(first_point_y * 1.3 )])

    ## 
    gca = plt.gca()
    gca.set_xscale('hydraulic-n-1.85')
    gca.xaxis.set_major_locator(MultipleLocator(200))
    gca.yaxis.set_major_locator(MultipleLocator(10))
    gca.yaxis.set_minor_locator(MultipleLocator(1))
    gca.tick_params(axis='both', which='both', length=0)
    plt.tick_params('both', which='both', left='on', bottom='on', right='off', top='off', color='black')
    plt.tick_params('both', which='minor', width=1, length=0)

    plt.ylabel('Pressure (psi)')
    plt.xlabel('Flow (gpm)')
    plt.title('WATER SUPPLY ANALYSIS')
    plt.grid(True)

    plt.savefig(save_path)


@app.route('/')
def index():
 return render_template('index.html')

@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    data = request.json
    first_line_points = data.get('first_line_points', [])
    second_line_points = data.get('second_line_points', [])
    print(first_line_points,file=sys.stderr)
    
    q0_q20 = calculated_samples(first_line_points)
    
    first_line_points.extend(q0_q20)  # Append the return value to first_line_points
    print(first_line_points,file=sys.stderr)

    unique_filename = str(uuid.uuid4()) + ".png"
    save_path = os.path.join("static/charts/", unique_filename)

    main(save_path, first_line_points, second_line_points)

    return jsonify({"image_path": save_path, 
                     "first_line_points": first_line_points,
                     "second_line_points": second_line_points 
                 })


if __name__ == '__main__':
    scale.register_scale(HydraulicN185Scale)
    app.run(debug=True, host="0.0.0.0", port=3000)
