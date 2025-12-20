// Edge Function para processar OCR de Notas Fiscais via Gemini
// Esta função roda no Supabase com timeout de 150s (vs 10s da Vercel)
// Inclui rotação de chaves com reset diário
// Version: 1.0.0 - Deploy via GitHub Actions

import "jsr:@supabase/functions-js/edge-runtime.d.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import { GoogleGenerativeAI } from "https://esm.sh/@google/generative-ai@0.21.0"

// Tipos
interface OCRRequest {
  job_id: string
  image_path: string
  gemini_keys: string  // Múltiplas chaves separadas por vírgula
}

interface InvoiceData {
  nota_fiscal: {
    numero: string
    serie: string
    data_emissao: string
    chave_acesso: string
  }
  emitente: {
    razao_social: string
    cnpj: string
  }
  itens: Array<{
    codigo: string
    descricao: string
    quantidade: number
    unidade: string
    valor_unitario: number
    valor_total: number
  }>
  valores_totais: {
    valor_total_nota: number
  }
  dados_adicionais?: {
    informacoes_complementares?: string
  }
}

// Storage KV para rastrear chaves esgotadas (em memória - reseta quando function reinicia)
// Em produção, poderia usar Supabase Table ou KV Store
const exhaustedKeys = new Map<number, string>()

/**
 * Parse das chaves API do Gemini
 */
function parseGeminiKeys(keysStr: string): string[] {
  if (!keysStr) return []
  
  try {
    // Tentar parsear como JSON array
    const parsed = JSON.parse(keysStr)
    if (Array.isArray(parsed)) {
      return parsed.filter((k: string) => k && k.trim())
    }
    return [String(parsed).trim()]
  } catch {
    // Fallback: separar por vírgula
    return keysStr.split(',').map(k => k.trim()).filter(Boolean)
  }
}

/**
 * Retorna a primeira chave disponível (não esgotada hoje)
 */
function getAvailableKeyIndex(keys: string[]): number {
  const today = new Date().toDateString()
  
  for (let i = 0; i < keys.length; i++) {
    const exhaustedDate = exhaustedKeys.get(i)
    
    // Se não está esgotada ou foi em outro dia, está disponível
    if (!exhaustedDate || exhaustedDate !== today) {
      console.log(`OCR: Usando chave ${i + 1}/${keys.length}`)
      return i
    }
  }
  
  console.log(`OCR: Todas as ${keys.length} chaves esgotadas hoje`)
  return -1
}

/**
 * Marca uma chave como esgotada no dia atual
 */
function markKeyExhausted(keyIndex: number) {
  const today = new Date().toDateString()
  exhaustedKeys.set(keyIndex, today)
  console.log(`OCR: Chave ${keyIndex + 1} marcada como esgotada`)
}

/**
 * Verifica se erro é de quota esgotada
 */
function isQuotaError(error: Error): boolean {
  const msg = error.message || ''
  return msg.includes('429') || 
         msg.includes('RESOURCE_EXHAUSTED') || 
         msg.includes('quota') ||
         msg.includes('rate limit')
}

// Prompt para o Gemini (igual ao do Node.js)
const OCR_PROMPT = `
EXTRAIA OS DADOS DA NOTA FISCAL.
Retorne APENAS um JSON válido. Não use Markdown (\`\`\`json).

Siga ESTRITAMENTE esta estrutura:
{
  "nota_fiscal": {
    "numero": "string",
    "serie": "string",
    "data_emissao": "dd/mm/aaaa",
    "chave_acesso": "string (44 digitos)"
  },
  "emitente": {
    "razao_social": "string",
    "cnpj": "string"
  },
  "itens": [
    {
      "codigo": "string",
      "descricao": "string",
      "unidade": "string",
      "quantidade": "float",
      "valor_unitario": "float",
      "valor_total": "float"
    }
  ],
  "valores_totais": {
    "valor_total_nota": "float"
  },
  "dados_adicionais": {
    "informacoes_complementares": "string"
  }
}

IMPORTANTE: 
- Se campo não existir, use string vazia "" ou 0 para números.
- Formate datas sempre como DD/MM/AAAA.
`

/**
 * Processa OCR com uma chave específica
 */
async function processWithKey(
  keys: string[], 
  keyIndex: number, 
  base64Image: string
): Promise<{ success: boolean; data?: InvoiceData; error?: string; keyUsed?: number }> {
  
  if (keyIndex < 0 || keyIndex >= keys.length) {
    return { 
      success: false, 
      error: 'Todas as chaves API estão esgotadas hoje. Tente novamente amanhã ou cadastre manualmente.' 
    }
  }
  
  const genAI = new GoogleGenerativeAI(keys[keyIndex])
  // Usar gemini-flash-latest - mesmo modelo do Node.js que funciona
  const model = genAI.getGenerativeModel({ model: "gemini-flash-latest" })
  
  try {
    const result = await model.generateContent([
      OCR_PROMPT,
      {
        inlineData: {
          mimeType: "image/jpeg",
          data: base64Image,
        },
      },
    ])

    const responseText = result.response.text()
    
    // Limpar markdown se presente
    let cleanText = responseText.trim()
    if (cleanText.startsWith("```json")) {
      cleanText = cleanText.slice(7)
    }
    if (cleanText.startsWith("```")) {
      cleanText = cleanText.slice(3)
    }
    if (cleanText.endsWith("```")) {
      cleanText = cleanText.slice(0, -3)
    }
    
    const invoiceData: InvoiceData = JSON.parse(cleanText.trim())
    
    return {
      success: true,
      data: invoiceData,
      keyUsed: keyIndex + 1
    }
    
  } catch (error) {
    console.error(`OCR Error (chave ${keyIndex + 1}):`, (error as Error).message)
    
    // Se for erro de quota, marcar chave e tentar próxima
    if (isQuotaError(error as Error)) {
      markKeyExhausted(keyIndex)
      
      // Tentar com próxima chave disponível
      const nextKeyIndex = getAvailableKeyIndex(keys)
      if (nextKeyIndex >= 0 && nextKeyIndex !== keyIndex) {
        console.log(`OCR: Tentando com chave ${nextKeyIndex + 1}...`)
        return processWithKey(keys, nextKeyIndex, base64Image)
      }
      
      return {
        success: false,
        error: 'Todas as chaves API estão esgotadas hoje. Cadastre manualmente.'
      }
    }
    
    return {
      success: false,
      error: (error as Error).message || 'Erro ao processar imagem'
    }
  }
}

Deno.serve(async (req) => {
  console.log("OCR Function: Iniciando processamento")

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Método não permitido" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    })
  }

  try {
    const body: OCRRequest = await req.json()
    const { job_id, image_path, gemini_keys } = body

    if (!job_id || !image_path || !gemini_keys) {
      return new Response(
        JSON.stringify({ error: "job_id, image_path e gemini_keys são obrigatórios" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      )
    }

    // Parse das chaves
    const keys = parseGeminiKeys(gemini_keys)
    if (keys.length === 0) {
      return new Response(
        JSON.stringify({ error: "Nenhuma chave Gemini válida fornecida" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      )
    }

    console.log(`OCR Function: Processando job ${job_id} com ${keys.length} chaves disponíveis`)

    // Inicializar cliente Supabase
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Atualizar status para "processing"
    await supabase
      .from("fiscal_ocrjob")
      .update({ 
        status: "processing", 
        started_at: new Date().toISOString() 
      })
      .eq("id", job_id)

    // Baixar imagem do Storage
    console.log(`OCR Function: Baixando imagem de ${image_path}`)
    const { data: imageData, error: downloadError } = await supabase.storage
      .from("ocr-images")
      .download(image_path)

    if (downloadError || !imageData) {
      throw new Error(`Erro ao baixar imagem: ${downloadError?.message}`)
    }

    // Converter para base64
    const arrayBuffer = await imageData.arrayBuffer()
    const base64Image = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))

    // Obter primeira chave disponível
    const keyIndex = getAvailableKeyIndex(keys)
    
    // Processar OCR com rotação de chaves
    console.log("OCR Function: Chamando Gemini Vision API")
    const ocrResult = await processWithKey(keys, keyIndex, base64Image)
    
    if (!ocrResult.success) {
      throw new Error(ocrResult.error || "Erro no OCR")
    }

    // Formatar resultado para o Django
    const invoiceData = ocrResult.data!
    const formattedResult = {
      number: invoiceData.nota_fiscal?.numero || "",
      series: invoiceData.nota_fiscal?.serie || "",
      access_key: (invoiceData.nota_fiscal?.chave_acesso || "").replace(/\D/g, ""),
      issue_date: invoiceData.nota_fiscal?.data_emissao || "",
      supplier_name: invoiceData.emitente?.razao_social || "",
      supplier_cnpj: (invoiceData.emitente?.cnpj || "").replace(/\D/g, ""),
      total_value: invoiceData.valores_totais?.valor_total_nota || 0,
      observations: invoiceData.dados_adicionais?.informacoes_complementares || "",
      products: (invoiceData.itens || []).map((item) => ({
        code: item.codigo || "",
        description: item.descricao || "",
        quantity: item.quantidade || 0,
        unit: item.unidade || "UN",
        unit_price: item.valor_unitario || 0,
        total_price: item.valor_total || 0,
      })),
    }

    // Atualizar job como completado
    await supabase
      .from("fiscal_ocrjob")
      .update({
        status: "completed",
        result: formattedResult,
        completed_at: new Date().toISOString(),
      })
      .eq("id", job_id)

    console.log(`OCR Function: Job ${job_id} completado com sucesso (chave ${ocrResult.keyUsed})`)

    return new Response(
      JSON.stringify({ success: true, job_id, result: formattedResult, keyUsed: ocrResult.keyUsed }),
      { headers: { "Content-Type": "application/json" } }
    )

  } catch (error) {
    console.error("OCR Function Error:", error)

    // Tentar atualizar job como falho
    try {
      const body = await req.clone().json()
      if (body.job_id) {
        const supabaseUrl = Deno.env.get("SUPABASE_URL")!
        const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
        const supabase = createClient(supabaseUrl, supabaseKey)

        await supabase
          .from("fiscal_ocrjob")
          .update({
            status: "failed",
            error_message: (error as Error).message || "Erro desconhecido",
            completed_at: new Date().toISOString(),
          })
          .eq("id", body.job_id)
      }
    } catch {
      // Ignora erro ao atualizar
    }

    return new Response(
      JSON.stringify({ success: false, error: (error as Error).message || "Erro interno" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }
})
