/**
 * API de OCR para Notas Fiscais
 * Endpoint: POST /api/ocr
 * 
 * Processa imagem de nota fiscal usando Gemini Vision
 * e retorna dados estruturados em JSON.
 */

const { validateRequest, validateImage } = require('./_lib/auth');
const { extractInvoiceData } = require('./_lib/gemini');

module.exports = async function handler(req, res) {
  // Apenas POST permitido
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  // Validar autenticação
  const authResult = validateRequest(req);
  if (!authResult.valid) {
    return res.status(401).json({ error: authResult.error });
  }

  try {
    // Verificar se há arquivo na requisição
    // Vercel pode receber como multipart ou base64 no body
    let base64Image, mimeType;

    if (req.body.image && req.body.mimeType) {
      // Formato: { image: base64, mimeType: 'image/jpeg' }
      base64Image = req.body.image;
      mimeType = req.body.mimeType;
    } else {
      return res.status(400).json({ error: 'Imagem não fornecida. Envie { image: base64, mimeType: string }' });
    }

    // Validar tamanho (base64 é ~33% maior que binário)
    const sizeInBytes = (base64Image.length * 3) / 4;
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (sizeInBytes > maxSize) {
      return res.status(400).json({ error: 'Imagem muito grande (máximo 10MB)' });
    }

    // Validar tipo MIME
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(mimeType)) {
      return res.status(400).json({ error: `Tipo de arquivo não permitido: ${mimeType}` });
    }

    // Processar OCR
    console.log('OCR: Iniciando processamento...');
    const startTime = Date.now();
    
    const result = await extractInvoiceData(base64Image, mimeType);
    
    const duration = Date.now() - startTime;
    console.log(`OCR: Processamento concluído em ${duration}ms`);

    if (!result.success) {
      return res.status(400).json({ error: result.error });
    }

    // Retornar dados extraídos
    return res.status(200).json({
      success: true,
      data: result.data,
      meta: {
        keyUsed: result.keyUsed,
        processingTimeMs: duration
      }
    });

  } catch (error) {
    console.error('OCR Error:', error);
    return res.status(500).json({ error: 'Erro interno ao processar imagem' });
  }
};
