# Water Supply Analysis Chart Generator

A Flask web application that generates professional hydraulic analysis charts for water supply systems. The application creates interactive charts with Hebrew text support and modern styling.

## Features

- **Hydraulic Analysis**: Generates charts using N=1.85 hydraulic scaling
- **Hebrew Text Support**: Full bidirectional text support for Hebrew labels
- **Modern Design**: Professional styling with clean typography and color scheme
- **Responsive Charts**: 640x400px resolution optimized for web display
- **Interactive Input**: Web form for entering measurement data and optional points
- **Real-time Generation**: Dynamic chart creation with unique file naming

## Requirements

- Python 3.7+
- Flask 2.3.3
- matplotlib 3.7.2
- numpy 1.24.3
- python-bidi 0.4.2

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd water-supply-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:3000`

## Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t water-supply-chart .

# Run the container
docker run -p 3000:3000 water-supply-chart
```

Or use Docker Compose:

```bash
docker-compose up
```

## Usage

1. **Enter Measurements**: Input flow and pressure values for two measurement points
2. **Add Optional Points**: Include additional data points with Hebrew labels if needed
3. **Generate Chart**: Click to create the hydraulic analysis chart
4. **Download**: Charts are saved as PNG files in the `static/charts` directory

### Input Parameters

- **Measurement 1 & 2**: Primary flow/pressure data points for the main analysis line
- **Optional Points**: Additional reference points with custom labels (supports Hebrew text)

### Chart Features

- Hydraulic scaling with N=1.85 transformation
- Automatic Q0 and Q20 calculations
- Professional color scheme and typography
- Grid lines and axis labels
- Point coordinates display
- Hebrew text rendering support

## File Structure

```
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yaml    # Docker Compose setup
├── build_run.bash         # Build script
├── debug_chart.py         # Chart debugging utility
├── static/
│   ├── css/
│   │   └── style.css      # Web interface styling
│   ├── js/
│   │   └── index.js       # Frontend JavaScript
│   └── charts/            # Generated chart images
└── templates/
    └── index.html         # Web interface template
```

## API Endpoints

### POST /generate_plot

Generates a hydraulic analysis chart from measurement data.

**Request Body:**
```json
{
  "measurement1": {"flow": 1000, "pressure": 80},
  "measurement2": {"flow": 1500, "pressure": 60},
  "optional_point1": {"flow": 800, "pressure": 85, "label": "נקודה 1"},
  "optional_point2": {"flow": 1200, "pressure": 70, "label": "נקודה 2"}
}
```

**Response:**
```json
{
  "image_path": "static/charts/uuid.png",
  "first_line_points": [[1000, 80], [1500, 60], [Q20, 20], [Q0, 0]],
  "second_line_points": [],
  "optional_points": [...]
}
```

## Technical Details

### Hydraulic Scaling

The application uses a custom matplotlib scale (`hydraulic-n-1.85`) that applies the hydraulic formula:
```
Q = k × (ΔH)^(1/1.85)
```

### Hebrew Text Support

- Automatic font detection for Hebrew-compatible fonts
- Bidirectional text processing using python-bidi
- Fallback text handling for systems without Hebrew fonts
- Support for mixed Hebrew/English text

### Chart Styling

- Modern color palette with professional appearance
- 640x400px resolution for web optimization
- Clean typography with bold labels
- Subtle grid lines and enhanced markers
- Responsive design elements

## Development

### Debug Mode

Run with debug logging:
```bash
python debug_chart.py
```

### Font Testing

The application automatically detects and configures Hebrew fonts. Check logs for font selection details.

### Custom Styling

Modify chart appearance by editing the styling parameters in the `main()` function.

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions, please create an issue in the repository or contact the development team.