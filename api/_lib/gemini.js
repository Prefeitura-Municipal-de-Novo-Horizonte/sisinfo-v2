/**
 * Cliente Gemini com rotação de chaves e tracking de quota.
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');

// Parse das chaves API
function getApiKeys() {
  const keysStr = process.env.GEMINI_API_KEY;
  if (!keysStr) {
    throw new Error('GEMINI_API_KEY não configurada');
  }

  try {
    // Tentar parsear como JSON array
    const parsed = JSON.parse(keysStr);
    if (Array.isArray(parsed)) {
      return parsed.filter(k => k && k.trim());
    }
    return [String(parsed).trim()];
  } catch {
    // Fallback: separar por vírgula
    return keysStr.split(',').map(k => k.trim()).filter(Boolean);
  }
}

// Map para rastrear chaves esgotadas hoje
const exhaustedToday = new Map();

/**
 * Retorna a primeira chave disponível (não esgotada hoje).
 * @returns {{ key: string, index: number } | null}
 */
function getAvailableKey() {
  const keys = getApiKeys();
  const today = new Date().toDateString();

  for (let i = 0; i < keys.length; i++) {
    const exhaustedDate = exhaustedToday.get(i);
    
    // Se não está esgotada ou foi em outro dia, está disponível
    if (!exhaustedDate || exhaustedDate !== today) {
      console.log(`Gemini: Usando chave ${i + 1}/${keys.length}`);
      return { key: keys[i], index: i };
    }
  }

  console.log(`Gemini: Todas as ${keys.length} chaves esgotadas hoje`);
  return null;
}

/**
 * Marca uma chave como esgotada no dia atual.
 * @param {number} keyIndex 
 */
function markKeyExhausted(keyIndex) {
  const today = new Date().toDateString();
  exhaustedToday.set(keyIndex, today);
  console.log(`Gemini: Chave ${keyIndex + 1} marcada como esgotada`);
}

/**
 * Verifica se erro é de quota esgotada.
 * @param {Error} error 
 */
function isQuotaError(error) {
  const msg = error.message || '';
  return msg.includes('429') || 
         msg.includes('RESOURCE_EXHAUSTED') || 
         msg.includes('quota') ||
         msg.includes('rate limit');
}

/**
 * Extrai dados da nota fiscal usando Gemini Vision.
 * @param {string} base64Image - Imagem em base64
 * @param {string} mimeType - Tipo MIME (image/jpeg, image/png, etc)
 * @returns {Promise<object>}
 */
async function extractInvoiceData(base64Image, mimeType) {
  const availableKey = getAvailableKey();
  
  if (!availableKey) {
    return {
      success: false,
      error: 'Todas as chaves API estão esgotadas hoje. Tente novamente amanhã ou cadastre manualmente.'
    };
  }

  const genAI = new GoogleGenerativeAI(availableKey.key);
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

  const prompt = `
EXTRAIA OS DADOS DA NOTA FISCAL.
Retorne APENAS um JSON válido. Não use Markdown (\`\`\`json).

Siga ESTRITAMENTE esta estrutura:
{
  "nota_fiscal": {
    "numero": "string",
    "serie": "string",
    "data_emissao": "dd/mm/aaaa",
    "chave_acesso": "string (44 digitos)",
    "natureza_operacao": "string"
  },
  "emitente": {
    "razao_social": "string",
    "cnpj": "string",
    "endereco": "string",
    "municipio": "string",
    "uf": "string"
  },
  "destinatario": {
    "razao_social": "string",
    "cnpj_cpf": "string"
  },
  "itens": [
    {
      "codigo": "string",
      "descricao": "string",
      "unidade": "string",
      "quantidade": "float",
      "valor_unitario": "float",
      "valor_total": "float",
      "cfop": "string"
    }
  ],
  "valores_totais": {
    "valor_total_nota": "float",
    "valor_total_produtos": "float"
  },
  "dados_adicionais": {
    "informacoes_complementares": "string"
  }
}

IMPORTANTE: 
- Se campo não existir, use string vazia "" ou 0 para números.
- Formate datas sempre como DD/MM/AAAA.
`;

  try {
    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          data: base64Image,
          mimeType: mimeType
        }
      }
    ]);

    const response = await result.response;
    let text = response.text();

    // Limpar markdown se presente
    if (text.includes('```json')) {
      text = text.split('```json')[1].split('```')[0];
    } else if (text.includes('```')) {
      text = text.split('```')[1].split('```')[0];
    }

    const data = JSON.parse(text.trim());

    return {
      success: true,
      data: data,
      keyUsed: availableKey.index + 1
    };

  } catch (error) {
    console.error('Gemini Error:', error.message);

    // Se for erro de quota, marcar chave e tentar próxima
    if (isQuotaError(error)) {
      markKeyExhausted(availableKey.index);
      
      // Tentar recursivamente com próxima chave
      return extractInvoiceData(base64Image, mimeType);
    }

    return {
      success: false,
      error: error.message || 'Erro ao processar imagem'
    };
  }
}

module.exports = {
  extractInvoiceData,
  getAvailableKey,
  markKeyExhausted
};
