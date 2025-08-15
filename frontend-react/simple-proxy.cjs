const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = 8080;
const DJANGO_API = 'http://localhost:8000';

// MIME types for static files
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml',
};

function proxyRequest(req, res, targetUrl) {
  const options = {
    hostname: 'localhost',
    port: 8000,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: 'localhost:8000'
    }
  };

  console.log(`Proxying ${req.method} ${req.url} to Django`);

  const proxyReq = http.request(options, (proxyRes) => {
    console.log(`Django responded with: ${proxyRes.statusCode}`);
    
    // Set CORS headers before copying response headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    // Copy response headers from Django (except CORS ones to avoid conflicts)
    Object.keys(proxyRes.headers).forEach(key => {
      if (!key.toLowerCase().startsWith('access-control-')) {
        res.setHeader(key, proxyRes.headers[key]);
      }
    });

    res.writeHead(proxyRes.statusCode);
    
    // Collect response data
    let data = '';
    proxyRes.on('data', chunk => {
      data += chunk;
    });
    
    proxyRes.on('end', () => {
      console.log(`Response data: ${data.substring(0, 100)}...`);
      res.end(data);
    });
  });

  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Proxy error', details: err.message }));
  });

  // Handle request data
  let body = '';
  req.on('data', chunk => {
    body += chunk;
  });
  
  req.on('end', () => {
    console.log(`Request body: ${body}`);
    proxyReq.write(body);
    proxyReq.end();
  });
}

function serveStaticFile(req, res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('File not found');
      return;
    }

    const ext = path.extname(filePath);
    const mimeType = mimeTypes[ext] || 'application/octet-stream';
    
    res.setHeader('Content-Type', mimeType);
    res.writeHead(200);
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRFToken');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.writeHead(200);
    res.end();
    return;
  }

  // Add CORS headers to all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRFToken');

  // Proxy API requests to Django
  if (req.url.startsWith('/api/')) {
    proxyRequest(req, res);
    return;
  }

  // Serve static files
  let filePath = path.join(__dirname, 'dist', req.url === '/' ? 'index.html' : req.url);
  
  // If file doesn't exist, serve index.html (for React Router)
  if (!fs.existsSync(filePath)) {
    filePath = path.join(__dirname, 'dist', 'index.html');
  }

  serveStaticFile(req, res, filePath);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`
🚀 ESG Compass React App with API Proxy

📱 Frontend: http://localhost:${PORT}
🔗 API Proxy: http://localhost:${PORT}/api -> http://localhost:8000/api

✅ React app serving from: dist/
✅ API requests proxied to Django backend
✅ CORS enabled for all requests

Access your app at: http://localhost:${PORT}
  `);
});

process.on('SIGINT', () => {
  console.log('\n👋 Server shutting down...');
  process.exit(0);
});