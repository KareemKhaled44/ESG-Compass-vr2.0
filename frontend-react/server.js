import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = 8000;

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, 'dist')));

// Handle React Router routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`
🚀 ESG Compass React App is running!

📱 Access the app in your browser:
   http://localhost:${PORT}
   http://127.0.0.1:${PORT}

🌐 Network access:
   Check your network IP and use: http://[your-ip]:${PORT}

Press Ctrl+C to stop the server
  `);
});