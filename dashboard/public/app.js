/**
 * DESCRIPTION:
 * This is the frontend logic for the dashboard. It listens for the user to submit 
 * the data retrieval form, packages those inputs into a URL query, and makes an HTTP GET 
 * request to the Node.js Express backend (as shown in Figure 3's "Dual Query Access").
 * * INPUT:
 * Takes the 'room', 'date', and 'time' values from the HTML form when the "OK" button is clicked.
 * * OUTPUT:
 * Parses the JSON response from the backend server and dynamically generates an HTML table 
 * to display the timestamp, occupancy count, and sensor anomalies inside the results container.
 */

document.getElementById('dataForm').addEventListener('submit', async function(event) {
    // Prevent the page from refreshing on form submit
    event.preventDefault();

    // 1. Grab the values from the input fields
    const room = document.getElementById('room').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    // Grab the container where we will display the results
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = "<p style='color: yellow;'>Fetching data...</p>";

    try {
        // 2. Construct the API request URL
        // Assuming your Node.js server has a route set up at /api/sensor-data
        const queryParams = new URLSearchParams({ room: room, date: date, time: time });
        const apiUrl = `/api/sensor-data?${queryParams.toString()}`;

        // 3. Make the HTTP GET request to the backend
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // 4. Render the data into an HTML table
        if (data.length === 0) {
            resultsContainer.innerHTML = "<p style='color: red;'>No records found for this time.</p>";
            return;
        }

        // Build the table headers
        let tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Predicted Occupancy</th>
                        <th>Motion Detected (Exterior)</th>
                        <th>Anomalies (Fire/Intruder)</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Loop through the database rows and create table rows
        data.forEach(row => {
            tableHTML += `
                <tr>
                    <td>${new Date(row.timestamp).toLocaleString()}</td>
                    <td>${row.predicted_occupancy}</td>
                    <td>${row.motion_detected ? 'Yes' : 'No'}</td>
                    <td style="color: ${row.anomaly ? 'red' : 'white'};">
                        ${row.anomaly ? '⚠️ Detected' : 'Clear'}
                    </td>
                </tr>
            `;
        });

        tableHTML += `</tbody></table>`;

        // Inject the completed table into the DOM
        resultsContainer.innerHTML = tableHTML;

    } catch (error) {
        console.error("Failed to fetch data:", error);
        resultsContainer.innerHTML = `<p style='color: red;'>Error retrieving data: ${error.message}</p>`;
    }
});
