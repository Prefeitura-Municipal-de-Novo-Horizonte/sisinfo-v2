"""
Serviço de OCR para Notas Fiscais usando Google Gemini API.

Este módulo contém o serviço principal de extração de dados
de imagens de notas fiscais.

Módulos relacionados:
- ocr_types.py: Dataclasses (InvoiceProduct, ExtractedInvoiceData)
- ocr_parser.py: Parsing de resposta JSON
- supplier_finder.py: Busca de fornecedores
"""
from decouple import config

from google import genai
from google.genai import types

from .ocr_types import ExtractedInvoiceData
from .ocr_parser import parse_ocr_response

# Re-exportar para manter compatibilidade
from .ocr_types import InvoiceProduct, ExtractedInvoiceData
from .supplier_finder import find_supplier_by_cnpj, find_similar_materials


# Prompt para extração de dados da nota fiscal
OCR_PROMPT = """
EXTRAIA OS DADOS DA NOTA FISCAL.
Retorne APENAS um JSON válido. Não use Markdown (```json).

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
      "quantidade": "float (ex: 10.5)",
      "valor_unitario": "float (ex: 100.00)",
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
- Use ponto (.) como separador decimal para números.
"""


class InvoiceOCRService:
    """
    Serviço de extração de dados de notas fiscais via Gemini Vision.
    
    Suporta múltiplas chaves API com rotação automática quando
    uma chave atinge o limite de quota.
    
    Uso:
        service = InvoiceOCRService()
        result = service.extract_from_url("https://...")
        
        if result.has_error:
            print(f"Erro: {result.error}")
        else:
            print(f"Nota: {result.number}")
            for product in result.products:
                print(f"  - {product.description}")
    """
    
    def __init__(self):
        """
        Inicializa o serviço de OCR com suporte a múltiplas chaves API.
        
        Formatos suportados no .env:
        1. Lista JSON: GEMINI_API_KEY=["chave1", "chave2", "chave3"]
        2. Separado por vírgula: GEMINI_API_KEY=chave1,chave2,chave3
        """
        import json
        
        api_keys_str = config('GEMINI_API_KEY', default=None)
        
        if not api_keys_str:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        
        # Limpar aspas externas se houver
        if api_keys_str.startswith('"') and api_keys_str.endswith('"'):
            api_keys_str = api_keys_str[1:-1]
        
        # Tentar parsear como JSON primeiro
        try:
            parsed = json.loads(api_keys_str)
            if isinstance(parsed, list):
                self.api_keys = [key.strip() for key in parsed if key and key.strip()]
            else:
                self.api_keys = [str(parsed).strip()]
        except (json.JSONDecodeError, ValueError):
            # Fallback: separar por vírgula
            self.api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]
        
        if not self.api_keys:
            raise ValueError("Nenhuma chave API válida encontrada em GEMINI_API_KEY")
        
        # Buscar primeira chave disponível
        self.current_key_index = self._get_available_key_index()
        self.client = None
        
        if self.current_key_index is not None:
            self._initialize_client()
        else:
            print(f"OCR: Todas as {len(self.api_keys)} chaves estão esgotadas hoje")
    
    def _get_available_key_index(self) -> int | None:
        """Retorna o índice da primeira chave não esgotada hoje."""
        try:
            from fiscal.models import APIKeyStatus
            return APIKeyStatus.get_available_key_index(len(self.api_keys))
        except Exception as e:
            print(f"OCR: Erro ao verificar status das chaves: {e}")
            return 0
    
    def _mark_current_key_exhausted(self):
        """Marca a chave atual como esgotada no banco."""
        try:
            from fiscal.models import APIKeyStatus
            APIKeyStatus.mark_key_exhausted(self.current_key_index)
            print(f"OCR: Chave {self.current_key_index + 1} marcada como esgotada")
        except Exception as e:
            print(f"OCR: Erro ao marcar chave como esgotada: {e}")
    
    def _initialize_client(self):
        """Inicializa o cliente com a chave atual."""
        try:
            current_key = self.api_keys[self.current_key_index]
            print(f"OCR: Usando chave {self.current_key_index + 1}/{len(self.api_keys)}")
            self.client = genai.Client(api_key=current_key)
        except Exception as e:
            raise ValueError(f"Erro ao inicializar cliente Gemini: {str(e)}")
    
    def extract_from_image(self, image_path: str) -> ExtractedInvoiceData:
        """
        Extrai dados de uma nota fiscal a partir do caminho da imagem.
        
        Args:
            image_path: Caminho local para o arquivo de imagem
            
        Returns:
            ExtractedInvoiceData: Dados extraídos
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return self._process_image(image_data, "image/png")
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def extract_from_bytes(self, image_bytes: bytes, mime_type: str = "image/png") -> ExtractedInvoiceData:
        """
        Extrai dados de uma nota fiscal a partir de bytes da imagem.
        
        Args:
            image_bytes: Bytes da imagem
            mime_type: Tipo MIME da imagem
            
        Returns:
            ExtractedInvoiceData: Dados extraídos
        """
        try:
            return self._process_image(image_bytes, mime_type)
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def extract_from_url(self, image_url: str) -> ExtractedInvoiceData:
        """
        Extrai dados de uma nota fiscal a partir de URL da imagem.
        
        Args:
            image_url: URL pública da imagem
            
        Returns:
            ExtractedInvoiceData: Dados extraídos
        """
        try:
            import urllib.request
            with urllib.request.urlopen(image_url, timeout=30) as response:
                image_bytes = response.read()
                content_type = response.headers.get('Content-Type', 'image/png')
            return self._process_image(image_bytes, content_type)
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def _process_image(self, image_bytes: bytes, mime_type: str) -> ExtractedInvoiceData:
        """
        Processa a imagem com Gemini Vision.
        
        Args:
            image_bytes: Bytes da imagem
            mime_type: Tipo MIME
            
        Returns:
            ExtractedInvoiceData: Dados extraídos
        """
        # Verificar se cliente está inicializado
        if self.client is None:
            return ExtractedInvoiceData(
                error="Todas as chaves API estão esgotadas hoje. Tente novamente amanhã."
            )
        
        try:
            # Criar conteúdo com imagem
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
            
            # Configuração para forçar resposta JSON
            generate_config = types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.0  # Zero para máxima precisão
            )

            # Chamar API Gemini
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=[OCR_PROMPT, image_part],
                config=generate_config
            )
            
            # Parsear resposta usando módulo separado
            return parse_ocr_response(response.text)
            
        except Exception as e:
            return self._handle_api_error(e, image_bytes, mime_type)
    
    def _handle_api_error(
        self, 
        error: Exception, 
        image_bytes: bytes, 
        mime_type: str
    ) -> ExtractedInvoiceData:
        """
        Trata erros da API, fazendo rotação de chaves se necessário.
        
        Args:
            error: Exceção ocorrida
            image_bytes: Bytes da imagem (para retry)
            mime_type: Tipo MIME (para retry)
            
        Returns:
            ExtractedInvoiceData: Resultado ou erro
        """
        error_str = str(error)
        
        # Verificar se é erro de quota ou chave inválida
        is_quota_error = '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower()
        is_invalid_key = '400' in error_str or 'INVALID_ARGUMENT' in error_str or 'API_KEY_INVALID' in error_str
        
        if is_quota_error or is_invalid_key:
            error_type = "quota esgotada" if is_quota_error else "chave inválida"
            print(f"OCR: Chave {self.current_key_index + 1} falhou ({error_type})")
            
            # Marcar chave atual como esgotada
            self._mark_current_key_exhausted()
            
            # Buscar próxima chave disponível
            next_available = self._get_available_key_index()
            
            if next_available is not None and next_available != self.current_key_index:
                self.current_key_index = next_available
                print(f"OCR: Tentando chave {self.current_key_index + 1}/{len(self.api_keys)}...")
                self._initialize_client()
                # Retry com a nova chave
                return self._process_image(image_bytes, mime_type)
            else:
                # Todas as chaves esgotadas
                print(f"OCR: Todas as {len(self.api_keys)} chaves estão esgotadas hoje")
                return ExtractedInvoiceData(
                    error=f"Todas as {len(self.api_keys)} chaves API estão esgotadas hoje. "
                          f"Tente novamente amanhã ou cadastre manualmente."
                )
        
        # Outros erros
        print(f"OCR ERROR: {error}")
        return ExtractedInvoiceData(error=error_str)
