/**
 * DESCRIPTION:
 * Node.js/Express backend server. It serves the frontend UI and provides the 
 * API routes (like /api/sensor-data) to query the PostgreSQL/TimescaleDB database.
 * * INPUT:
 * HTTP GET requests from app.js containing query parameters (room, date, time).
 * * OUTPUT:
 * JSON arrays containing the queried database rows, sent back to the frontend.
 */

const express = require('express');
const path = require('path');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from the 'public' directory (index.html, app.js)
app.use(express.static(path.join(__dirname, 'public')));

// ==========================================
// DATABASE CONFIGURATION
// ==========================================
// Update these values to match your local PostgreSQL setup
const pool = new Pool({
    user: 'postgres',          // Default postgres user
    host: 'localhost',
    database: 'smarthome_db',  // The database where your Python script saves data
    password: 'yourpassword',  // Enter your DB password
    port: 5432,
});

// Test Database Connection
pool.connect((err, client, release) => {
    if (err) {
        console.error('Error acquiring client', err.stack);
    } else {
        console.log('Successfully connected to PostgreSQL database');
    }
});

// ==========================================
// API ROUTES (From Architecture Fig 3)
// ==========================================

// Route: /api/sensor-data
// Fetches data based on room, date, and start time
app.get('/api/sensor-data', async (req, res) => {
    const { room, date, time } = req.query;

    if (!room || !date || !time) {
        return res.status(400).json({ error: 'Missing required parameters: room, date, or time.' });
    }

    try {
        // Construct a timestamp string for the SQL query (e.g., '2023-10-27 14:30:00')
        const startTimestamp = `${date} ${time}:00`;

        // SQL Query to fetch data from TimescaleDB/PostgreSQL
        // Adjust the table name ('sensor_logs') to match exactly what your Python script created
        const queryText = `
            SELECT 
                timestamp, 
                predicted_occupancy, 
                motion_detected, 
                anomaly 
            FROM sensor_logs 
            WHERE room_id = $1 
              AND timestamp >= $2 
            ORDER BY timestamp ASC 
            LIMIT 100;
        `;
        
        const values = [room, startTimestamp];

        const result = await pool.query(queryText, values);
        
        // Send the rows back to the frontend (app.js)
        res.json(result.rows);

    } catch (err) {
        console.error('Database query error:', err);
        res.status(500).json({ error: 'Internal server error while querying database.' });
    }
});

// Placeholder for other routes mentioned in your diagram
app.get('/api/camera-data', (req, res) => {
    res.json({ message: "Camera data route ready for implementation." });
});

app.get('/api/triggered-events', (req, res) => {
    res.json({ message: "Triggered events route ready for implementation." });
});

// ==========================================
// START SERVER
// ==========================================
app.listen(PORT, () => {
    console.log(`🚀 Smart Home Dashboard running on http://localhost:${PORT}`);
});
