const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 8080;

// Enable CORS for all routes
app.use(cors({
  origin: true,
  credentials: true
}));

// Proxy API requests to Django backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  logLevel: 'debug',
  onError: (err, req, res) => {
    console.error('Proxy error:', err.message);
    res.status(500).json({ error: 'Proxy error', details: err.message });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying ${req.method} ${req.url} to Django backend`);
  }
}));

// Serve static React build files
app.use(express.static(path.join(__dirname, 'dist')));

// Handle React Router - serve index.html for all non-API routes
app.get('*', (req, res) => {
  if (!req.url.startsWith('/api')) {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`
🚀 ESG Compass React App with API Proxy

📱 Frontend: http://localhost:${PORT}
🔗 API Proxy: http://localhost:${PORT}/api -> http://localhost:8000/api

✅ React app serving from: dist/
✅ API requests proxied to Django backend
✅ CORS enabled for cross-origin requests

Access your app at: http://localhost:${PORT}
  `);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Server shutting down...');
  process.exit(0);
});