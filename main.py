from flask import Flask, jsonify, request
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


def plot_line(points, line_style='-', color='blue'):
    x, y = zip(*points)
    plt.plot(x, y, line_style, color=color)
    for txt in points:
        if (txt[0] != 0) or (txt[1] != 0):
            plt.text(txt[0], txt[1], f'({txt[0]}, {txt[1]})', ha='right', va="top")
    plt.scatter(x, y, color=color)


def main(save_path, first_line_points, second_line_points):
    plt.rc('lines', linewidth=2, color='red')
    plt.rc('grid', linestyle="-", color='black')

    fig, ax = plt.subplots()

    plot_line(first_line_points, '-', 'blue')
    plot_line(second_line_points, '-', 'red')

    # Set the X-Axis and Y-Axis Limit values
    last_point_x = int(first_line_points[-1][0])
    first_point_y = int(first_line_points[0][1])

    print(f"Chart X-Axis limit is {last_point_x}", file=sys.stderr)
    print(f"Chart Y-Axis limit is {first_point_y}", file=sys.stderr)

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
    return '''
    <html>
        <head>
        <title>Chart Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1, h2 {
                color: #333366;
            }
            p {
                font-size: 18px;
            }
            label {
                font-weight: bold;
            }
            input[type="text"] {
                width: 10%;
                padding: 8px;
                margin: 8px 0;
                box-sizing: border-box;
                font-weight: bold;
                font-size: 20px;
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 20px 40px;
                margin: 8px 0;
                font-size: 30px;   
                border: none;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
    <form id="plotForm">
        <h1>Water Supply Analysis</h1>

        <h2>First Line Points:</h2>
        <b>Point 1:</b> X: <input type="text" class="first-line x" value="0"> Y: <input type="text" class="first-line y" value="75"><br>
        <b>Point 2:</b> X: <input type="text" class="first-line x" value="699"> Y: <input type="text" class="first-line y" value="55"><br>
        <b>Point 3:</b> X: <input type="text" class="first-line x" value="1208"> Y: <input type="text" class="first-line y" value="20"><br>

        <br>

        <h2>Second Line Points:</h2>
        <b>Point 1:</b> X: <input type="text" class="second-line x" value="0"> Y: <input type="text" class="second-line y" value="0"><br>
        <b>Point 2:</b> X: <input type="text" class="second-line x" value="0"> Y: <input type="text" class="second-line y" value="0"><br>
        <b>Point 3:</b> X: <input type="text" class="second-line x" value="0"> Y: <input type="text" class="second-line y" value="0"><br>
        <br><br>
        <input type="submit" value="Show Chart">
    </form>

    <h2>Generated Chart:</h2>
    <p>Chart URL: <a id="serverURL" href=""></a></p>
    <img id="generatedPlot" src="" alt="Generated chart will appear here." style="display:none; width:800px; height:600px;">

    <script>
        function collectPoints(className) {
            const xs = Array.from(document.querySelectorAll(`.${className}.x`)).map(e => parseFloat(e.value));
            const ys = Array.from(document.querySelectorAll(`.${className}.y`)).map(e => parseFloat(e.value));

            return xs.map((x, i) => [x, ys[i]]);
        }

        document.getElementById('plotForm').addEventListener('submit', function(event) {
            event.preventDefault();

            const firstLinePoints = collectPoints('first-line');
            const secondLinePoints = collectPoints('second-line');
            const serverURL = window.location.origin;
            const serverURLLink = document.getElementById("serverURL");
            
            serverURLLink.textContent = serverURL;
            serverURLLink.href = serverURL;

            // Populate the server URL

            fetch('/generate_plot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    first_line_points: firstLinePoints,
                    second_line_points: secondLinePoints
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('generatedPlot').src = data.image_path;
                document.getElementById('generatedPlot').style.display = 'block';
                document.getElementById("serverURL").textContent = window.location.origin + "/" + data.image_path;
            });
        });

    </script>
    </body>
    </html>
    '''


@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    data = request.json
    first_line_points = data.get('first_line_points', [])
    second_line_points = data.get('second_line_points', [])

    unique_filename = str(uuid.uuid4()) + ".png"
    save_path = os.path.join("static", unique_filename)

    main(save_path, first_line_points, second_line_points)

    return jsonify({"image_path": save_path})


if __name__ == '__main__':
    scale.register_scale(HydraulicN185Scale)
    app.run(debug=True, host="0.0.0.0", port=3000)
