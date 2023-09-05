function collectPoints(className) {
    const xs = Array.from(document.querySelectorAll(`.${className}.x`)).map(e => parseFloat(e.value));
    const ys = Array.from(document.querySelectorAll(`.${className}.y`)).map(e => parseFloat(e.value));

    return xs.map((x, i) => [x, ys[i]]);
}

function checkInputs() {
    const yInputs = Array.from(document.querySelectorAll('.first-line.y'));
    const submitButton = document.getElementById('submitButton');

    if (yInputs.some(input => parseFloat(input.value) == 0)) {
        submitButton.disabled = true;
    } else {
        submitButton.disabled = false;
    }
}

const toggleInputs = document.getElementById('toggleInputs');
const inputGroup = document.getElementById('secondLinePoints');

toggleInputs.addEventListener('change', function() {
    inputGroup.style.display = this.checked ? 'block' : 'none';
});

document.getElementById('plotForm').addEventListener('submit', function(event) {
    event.preventDefault();
    console.log("submit");

    const firstLinePoints = collectPoints('first-line');
    const secondLinePoints = collectPoints('second-line');
    const serverURL = window.location.origin;
    const serverURLLink = document.getElementById("serverURL");

    const tableArea = document.getElementById('tableArea');
    tableArea.style.display = 'block';

    const chartArea = document.getElementById('chartArea');
    chartArea.style.display = 'block'; 

    
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

        // Populate the server URL

          const tableBody = document.querySelector('#pointsTable tbody');

        // Clear the table body
        tableBody.innerHTML = '';

        // Add the points to the table
        data.first_line_points.forEach(point => {
            const row = document.createElement('tr');
            const xCell = document.createElement('td');
            const yCell = document.createElement('td');

            xCell.textContent = point[0];
            yCell.textContent = point[1];

            row.appendChild(xCell);
            row.appendChild(yCell);

            tableBody.appendChild(row);
        });
    });
});

document.querySelectorAll('.first-line.y').forEach(input => {
     input.addEventListener('input', checkInputs);
});

checkInputs();
