// server.js - Simple HTTP server to serve the Telegram Mini App for local testing

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;
const API_PORT = process.env.API_PORT || 5000;

// MIME types for static files
const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp4': 'video/mp4',
  '.woff': 'application/font-woff',
  '.ttf': 'application/font-ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'application/font-otf',
  '.wasm': 'application/wasm'
};

// Create HTTP server
const server = http.createServer((req, res) => {
  console.log(`Request received: ${req.method} ${req.url}`);
  
  // Handle API requests by proxying to Python backend
  if (req.url.startsWith('/api/')) {
    proxyRequestToPythonAPI(req, res);
    return;
  }
  
  // Handle the root path
  let filePath = req.url === '/' ? '/index.html' : req.url;
  filePath = path.join(__dirname, filePath);
  
  // Get file extension
  const extname = String(path.extname(filePath)).toLowerCase();
  const contentType = MIME_TYPES[extname] || 'application/octet-stream';
  
  // Read and serve the file
  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        // File not found
        console.log(`File not found: ${filePath}`);
        res.writeHead(404);
        res.end('404 Not Found');
      } else {
        // Server error
        console.log(`Server error: ${error.code}`);
        res.writeHead(500);
        res.end('500 Internal Server Error');
      }
    } else {
      // Success
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

// Proxy API requests to Python backend
function proxyRequestToPythonAPI(req, res) {
  // Create the proxy request using the built-in http module
  const options = {
    hostname: 'localhost',
    port: API_PORT,
    path: req.url, // Keep the full path including /api prefix
    method: req.method,
    headers: { ...req.headers }
  };
  
  // Remove the host header to avoid conflicts
  delete options.headers.host;
  
  // Create the proxy request
  const proxyReq = http.request(options, (proxyRes) => {
    // Forward the response headers
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    
    // Pipe the response data
    proxyRes.pipe(res);
  });
  
  // Handle proxy request errors
  proxyReq.on('error', (err) => {
    console.error('Proxy request error:', err);
    res.writeHead(502);
    res.end('Bad Gateway');
  });
  
  // Pipe the request data
  req.pipe(proxyReq);
}

// Handle port in use error
server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.log(`Port ${PORT} is already in use.`);
    process.exit(1);
  }
});

// Start the server
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log('Press Ctrl+C to stop the server');
});