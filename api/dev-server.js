/**
 * Servidor de desenvolvimento para testar a API Node.js OCR localmente.
 * Uso: node api/dev-server.js
 */

// IMPORTANTE: Carregar variáveis de ambiente ANTES de qualquer outro require
require('dotenv').config();

const http = require('http');
const ocrHandler = require('./ocr.js');

const PORT = process.env.API_PORT || 3001;

const server = http.createServer(async (req, res) => {
  // CORS básico
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Rota /api/ocr
  if (req.url === '/api/ocr' && req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        // Parsear body
        const parsedBody = JSON.parse(body);
        
        // Simular objeto req do Vercel
        const mockReq = {
          method: 'POST',
          body: parsedBody,
          headers: req.headers
        };
        
        // Simular objeto res do Vercel
        const mockRes = {
          statusCode: 200,
          responseData: null,
          status(code) {
            this.statusCode = code;
            return this;
          },
          json(data) {
            this.responseData = data;
            res.writeHead(this.statusCode, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
          }
        };
        
        await ocrHandler(mockReq, mockRes);
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    
    return;
  }
  
  // Health check
  if (req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
    return;
  }
  
  // 404 para outras rotas
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found', availableRoutes: ['/api/ocr', '/api/health'] }));
});

server.listen(PORT, () => {
  console.log(`🚀 API Server rodando em http://localhost:${PORT}`);
  console.log(`   - POST /api/ocr     - Processar OCR`);
  console.log(`   - GET  /api/health  - Health check`);
  console.log('');
  console.log('Variáveis de ambiente:');
  console.log(`   - GEMINI_API_KEY: ${process.env.GEMINI_API_KEY ? '✓ configurada' : '✗ NÃO configurada'}`);
  console.log(`   - INTERNAL_API_SECRET: ${process.env.INTERNAL_API_SECRET ? '✓ configurada' : '✗ NÃO configurada'}`);
});
