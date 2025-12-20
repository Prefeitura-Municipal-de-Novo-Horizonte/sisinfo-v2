// Edge Function para processar OCR de Notas Fiscais via Gemini
// Esta função roda no Supabase com timeout de 150s (vs 10s da Vercel)
// Inclui rotação de chaves com reset diário
// Version: 1.1.0 - Usa callback HTTP para atualizar Django

import "jsr:@supabase/functions-js/edge-runtime.d.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import { GoogleGenerativeAI } from "https://esm.sh/@google/generative-ai@0.21.0"

// Tipos
interface OCRRequest {
  job_id: string
  image_path: string
  gemini_keys: string  // Múltiplas chaves separadas por vírgula
  gemini_model: string  // Modelo a usar (ex: gemini-flash-latest)
  callback_url: string  // URL para callback ao Django
  callback_secret: string  // Secret para autenticação
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
  dados_adicionais: {
    informacoes_complementares: string
  }
}

interface ProcessResult {
  success: boolean
  data?: InvoiceData
  error?: string
  keyUsed?: number
}

// Cache simples para chaves esgotadas (em memória, reseta ao reiniciar a function)
const exhaustedKeys = new Map<number, string>()

/**
 * Parse das chaves Gemini (suporta JSON array ou string separada por vírgula)
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
  return (
    msg.includes('429') ||
    msg.includes('RESOURCE_EXHAUSTED') ||
    msg.includes('quota') ||
    msg.includes('rate limit')
  )
}

/**
 * Processa imagem com uma chave específica
 */
async function processWithKey(
  keys: string[],
  keyIndex: number,
  base64Image: string,
  modelName: string = "gemini-flash-latest"
): Promise<ProcessResult> {
  if (keyIndex < 0 || keyIndex >= keys.length) {
    return { success: false, error: "Todas as chaves API esgotadas hoje" }
  }

  const key = keys[keyIndex]
  
  try {
    const genAI = new GoogleGenerativeAI(key)
    const model = genAI.getGenerativeModel({ model: modelName })

    const prompt = `Analise esta imagem de uma Nota Fiscal brasileira e extraia as seguintes informações em formato JSON:

{
  "nota_fiscal": {
    "numero": "número da nota",
    "serie": "série da nota",
    "data_emissao": "data no formato YYYY-MM-DD",
    "chave_acesso": "44 dígitos da chave de acesso (só números)"
  },
  "emitente": {
    "razao_social": "nome do fornecedor/emitente",
    "cnpj": "CNPJ do emitente (só números)"
  },
  "itens": [
    {
      "codigo": "código do produto",
      "descricao": "descrição do produto",
      "quantidade": 0.0,
      "unidade": "UN, KG, etc",
      "valor_unitario": 0.00,
      "valor_total": 0.00
    }
  ],
  "valores_totais": {
    "valor_total_nota": 0.00
  },
  "dados_adicionais": {
    "informacoes_complementares": "texto adicional se houver"
  }
}

IMPORTANTE:
- Retorne APENAS o JSON, sem markdown ou texto adicional
- Use números decimais (não strings) para valores
- Datas no formato YYYY-MM-DD
- CNPJ e chave de acesso apenas números (sem pontuação)
- Se não encontrar algum campo, use string vazia ou 0`

    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          mimeType: "image/jpeg",
          data: base64Image,
        },
      },
    ])

    const responseText = result.response.text()
    
    // Limpar markdown se houver
    let jsonText = responseText
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim()

    const data = JSON.parse(jsonText) as InvoiceData

    return {
      success: true,
      data,
      keyUsed: keyIndex + 1,
    }
  } catch (error) {
    console.error(`OCR Error (chave ${keyIndex + 1}):`, error)

    // Se for erro de quota, tentar próxima chave
    if (isQuotaError(error as Error)) {
      markKeyExhausted(keyIndex)
      console.log(`OCR: Tentando próxima chave...`)
      return processWithKey(keys, keyIndex + 1, base64Image)
    }

    return {
      success: false,
      error: (error as Error).message || 'Erro ao processar imagem'
    }
  }
}

/**
 * Envia resultado para o Django via callback HTTP
 */
async function sendCallback(
  callbackUrl: string,
  callbackSecret: string,
  status: "completed" | "failed",
  result: object | null,
  errorMessage: string | null
): Promise<boolean> {
  try {
    console.log(`OCR Function: Enviando callback para ${callbackUrl}`)
    
    const response = await fetch(callbackUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
        result,
        error_message: errorMessage,
        secret: callbackSecret,
      }),
    })

    if (!response.ok) {
      console.error(`Callback failed: ${response.status} ${response.statusText}`)
      return false
    }

    console.log("OCR Function: Callback enviado com sucesso")
    return true
  } catch (error) {
    console.error("Callback error:", error)
    return false
  }
}

Deno.serve(async (req) => {
  console.log("OCR Function: Iniciando processamento")

  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  }

  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders })
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Método não permitido" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    })
  }

  try {
    const body: OCRRequest = await req.json()
    const { job_id, image_path, gemini_keys, gemini_model, callback_url, callback_secret } = body
    
    // Modelo padrão se não fornecido
    const modelToUse = gemini_model || "gemini-flash-latest"

    if (!job_id || !image_path || !gemini_keys) {
      return new Response(
        JSON.stringify({ error: "job_id, image_path e gemini_keys são obrigatórios" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      )
    }

    if (!callback_url || !callback_secret) {
      return new Response(
        JSON.stringify({ error: "callback_url e callback_secret são obrigatórios" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      )
    }

    // Parse das chaves
    const keys = parseGeminiKeys(gemini_keys)
    if (keys.length === 0) {
      return new Response(
        JSON.stringify({ error: "Nenhuma chave Gemini válida fornecida" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      )
    }

    console.log(`OCR Function: Processando job ${job_id} com ${keys.length} chaves disponíveis`)

    // Inicializar cliente Supabase para Storage
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Baixar imagem do Storage
    console.log(`OCR Function: Baixando imagem de ${image_path}`)
    const { data: imageData, error: downloadError } = await supabase.storage
      .from("ocr-images")
      .download(image_path)

    if (downloadError || !imageData) {
      const errorMsg = `Erro ao baixar imagem: ${downloadError?.message}`
      await sendCallback(callback_url, callback_secret, "failed", null, errorMsg)
      throw new Error(errorMsg)
    }

    // Converter para base64
    const arrayBuffer = await imageData.arrayBuffer()
    const base64Image = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))

    // Obter primeira chave disponível
    const keyIndex = getAvailableKeyIndex(keys)
    
    // Processar OCR com rotação de chaves
    console.log("OCR Function: Chamando Gemini Vision API")
    const ocrResult = await processWithKey(keys, keyIndex, base64Image, modelToUse)
    
    if (!ocrResult.success) {
      await sendCallback(callback_url, callback_secret, "failed", null, ocrResult.error || "Erro no OCR")
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

    // Enviar resultado via callback
    await sendCallback(callback_url, callback_secret, "completed", formattedResult, null)

    console.log(`OCR Function: Job ${job_id} completado com sucesso (chave ${ocrResult.keyUsed})`)

    return new Response(
      JSON.stringify({ success: true, job_id, keyUsed: ocrResult.keyUsed }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    )

  } catch (error) {
    console.error("OCR Function Error:", error)

    return new Response(
      JSON.stringify({ success: false, error: (error as Error).message || "Erro interno" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }
})
