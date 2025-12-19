/**
 * Validação de autenticação para APIs internas.
 */

const API_SECRET = process.env.INTERNAL_API_SECRET;

/**
 * Valida o token de API.
 * @param {Request} req 
 * @returns {{ valid: boolean, error?: string }}
 */
function validateRequest(req) {
  // Debug logging para produção
  console.log('AUTH DEBUG:', {
    hasSecret: !!API_SECRET,
    secretLength: API_SECRET ? API_SECRET.length : 0,
    secretPreview: API_SECRET ? `${API_SECRET.substring(0, 4)}...` : 'null',
    hasToken: !!req.headers['x-api-key'],
    tokenLength: req.headers['x-api-key'] ? req.headers['x-api-key'].length : 0,
    tokenPreview: req.headers['x-api-key'] ? `${req.headers['x-api-key'].substring(0, 4)}...` : 'null',
    match: req.headers['x-api-key'] === API_SECRET
  });

  // Verificar se secret está configurado
  if (!API_SECRET) {
    console.error('INTERNAL_API_SECRET não configurada');
    return { valid: false, error: 'Configuração de servidor inválida' };
  }

  // Verificar header de autenticação
  const token = req.headers['x-api-key'];
  
  if (!token) {
    return { valid: false, error: 'Token de autenticação não fornecido' };
  }

  if (token !== API_SECRET) {
    return { valid: false, error: 'Token de autenticação inválido' };
  }

  return { valid: true };
}

/**
 * Valida o arquivo de imagem.
 * @param {File} file 
 * @returns {{ valid: boolean, error?: string }}
 */
function validateImage(file) {
  if (!file) {
    return { valid: false, error: 'Nenhuma imagem enviada' };
  }

  // Tipos MIME permitidos
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: `Tipo de arquivo não permitido: ${file.type}` };
  }

  // Tamanho máximo: 10MB
  const maxSize = 10 * 1024 * 1024;
  
  if (file.size > maxSize) {
    return { valid: false, error: 'Arquivo muito grande (máximo 10MB)' };
  }

  return { valid: true };
}

module.exports = {
  validateRequest,
  validateImage
};
