/**
 * Health Check API
 * Endpoint: GET /api/health
 * 
 * Retorna status de todas as APIs e serviços.
 */

module.exports = async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  const checks = {
    ocr_api: {
      status: 'ok',
      message: 'API Node.js OCR disponível'
    },
    gemini: {
      status: process.env.GEMINI_API_KEY ? 'ok' : 'error',
      message: process.env.GEMINI_API_KEY ? 'Chave configurada' : 'GEMINI_API_KEY não configurada'
    },
    internal_auth: {
      status: process.env.INTERNAL_API_SECRET ? 'ok' : 'error', 
      message: process.env.INTERNAL_API_SECRET ? 'Autenticação configurada' : 'INTERNAL_API_SECRET não configurada'
    }
  };

  const allOk = Object.values(checks).every(c => c.status === 'ok');

  return res.status(200).json({
    status: allOk ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    region: process.env.VERCEL_REGION || 'unknown',
    checks
  });
};
