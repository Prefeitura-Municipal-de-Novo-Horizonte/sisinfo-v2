"""
Serviço de OCR para Notas Fiscais usando Google Gemini API.
Extrai dados estruturados de imagens de notas fiscais.
"""
import re
import json
import base64
from dataclasses import dataclass, field
from decouple import config

from google import genai
from google.genai import types


@dataclass
class InvoiceProduct:
    """Produto extraído da nota fiscal."""
    code: str = ""
    description: str = ""
    quantity: float = 0.0
    unit: str = "UN"
    unit_price: float = 0.0
    total_price: float = 0.0


@dataclass
class ExtractedInvoiceData:
    """Dados extraídos da nota fiscal."""
    number: str = ""
    series: str = ""
    access_key: str = ""
    issue_date: str = ""  # formato dd/mm/yyyy
    supplier_name: str = ""
    supplier_cnpj: str = ""
    total_value: float = 0.0
    products: list = field(default_factory=list)
    observations: str = ""  # Novo campo
    raw_text: str = ""
    confidence: float = 0.0
    error: str = ""




class InvoiceOCRService:
    """Serviço de extração de dados de notas fiscais via Gemini Vision."""
    
    def __init__(self):
        """
        Inicializa o serviço de OCR com suporte a múltiplas chaves API.
        
        Formatos suportados no .env:
        1. Lista JSON: GEMINI_API_KEY=["chave1", "chave2", "chave3"]
        2. Separado por vírgula: GEMINI_API_KEY=chave1,chave2,chave3
        
        O sistema tentará cada chave em sequência até encontrar uma que funcione.
        """
        import json
        
        api_keys_str = config('GEMINI_API_KEY', default=None)
        
        if not api_keys_str:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        
        # Limpar aspas externas se houver
        if api_keys_str.startswith('"') and api_keys_str.endswith('"'):
            api_keys_str = api_keys_str[1:-1]
        
        # Tentar parsear como JSON primeiro (formato de lista)
        try:
            parsed = json.loads(api_keys_str)
            if isinstance(parsed, list):
                self.api_keys = [key.strip() for key in parsed if key and key.strip()]
            else:
                # Se for string única no JSON, usar como única chave
                self.api_keys = [str(parsed).strip()]
        except (json.JSONDecodeError, ValueError):
            # Fallback: separar por vírgula (formato antigo)
            self.api_keys = [key.strip() for key in api_keys_str.split(',') if key.strip()]
        
        if not self.api_keys:
            raise ValueError("Nenhuma chave API válida encontrada em GEMINI_API_KEY")
        
        # Inicializar com a primeira chave
        self.current_key_index = 0
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente com a chave atual."""
        try:
            current_key = self.api_keys[self.current_key_index]
            print(f"OCR: Usando chave {self.current_key_index + 1}/{len(self.api_keys)}")
            self.client = genai.Client(api_key=current_key)
        except Exception as e:
            raise ValueError(f"Erro ao inicializar cliente Gemini: {str(e)}")
    
    def extract_from_image(self, image_path: str) -> ExtractedInvoiceData:
        """Extrai dados de uma nota fiscal a partir do caminho da imagem."""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return self._process_image(image_data, "image/png")
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def extract_from_bytes(self, image_bytes: bytes, mime_type: str = "image/png") -> ExtractedInvoiceData:
        """Extrai dados de uma nota fiscal a partir de bytes da imagem."""
        try:
            return self._process_image(image_bytes, mime_type)
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def extract_from_url(self, image_url: str) -> ExtractedInvoiceData:
        """Extrai dados de uma nota fiscal a partir de URL da imagem."""
        try:
            import urllib.request
            with urllib.request.urlopen(image_url, timeout=30) as response:
                image_bytes = response.read()
                content_type = response.headers.get('Content-Type', 'image/png')
            return self._process_image(image_bytes, content_type)
        except Exception as e:
            return ExtractedInvoiceData(error=str(e))
    
    def _process_image(self, image_bytes: bytes, mime_type: str) -> ExtractedInvoiceData:
        """Processa a imagem com Gemini Vision."""
        
        prompt = """
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
        - Use ponto (.) como separador decimal para números, ou mantenha original com vírgula se preferir (será tratado).
        """
        
        try:
            # Criar conteúdo com imagem
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
            
            # Configuração para forçar resposta JSON limpa
            generate_config = types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.0  # Zero para máxima precisão e consistência
            )

            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=[prompt, image_part],
                config=generate_config
            )
            
            # Parsear resposta
            return self._parse_response(response.text)
            
        except Exception as e:
            error_str = str(e)
            
            # Verificar se é erro de quota (429) ou chave inválida (400)
            is_quota_error = '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower()
            is_invalid_key = '400' in error_str or 'INVALID_ARGUMENT' in error_str or 'API_KEY_INVALID' in error_str
            
            if is_quota_error or is_invalid_key:
                error_type = "quota esgotada" if is_quota_error else "chave inválida"
                print(f"OCR: Chave {self.current_key_index + 1} falhou ({error_type})")
                
                # Tentar próxima chave se houver
                if self.current_key_index < len(self.api_keys) - 1:
                    self.current_key_index += 1
                    print(f"OCR: Tentando próxima chave ({self.current_key_index + 1}/{len(self.api_keys)})...")
                    self._initialize_client()
                    # Retry com a nova chave
                    return self._process_image(image_bytes, mime_type)
                else:
                    # Todas as chaves esgotadas ou inválidas
                    print(f"OCR: Todas as {len(self.api_keys)} chaves falharam")
                    return ExtractedInvoiceData(
                        error=f"Todas as {len(self.api_keys)} chaves API falharam. "
                              f"Verifique se as chaves estão corretas ou aguarde o reset diário."
                    )
            
            # Outros erros
            print(f"OCR ERROR: {e}")
            return ExtractedInvoiceData(error=error_str)
    
    def _parse_response(self, response_text: str) -> ExtractedInvoiceData:
        """Parseia a resposta do modelo em ExtractedInvoiceData."""
        
        try:
            # Limpar markdown se presente
            clean_text = response_text.strip()
            
            # Remover delimitadores de código markdown
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1]
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1]
                
            if "```" in clean_text:
                clean_text = clean_text.split("```")[0]
            
            # Remover comentários de linha (//)
            import re
            clean_text = re.sub(r'^\s*//.*$', '', clean_text, flags=re.MULTILINE)
                
            clean_text = clean_text.strip()
            
            data = json.loads(clean_text)
            
            # Helper para converter strings numéricas pt-BR (ex: "1.000,00" -> 1000.00)
            def parse_br_float(value):
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    # Remove pontos de milhar e troca vírgula decimal por ponto
                    clean = value.replace('.', '').replace(',', '.')
                    try:
                        return float(clean)
                    except ValueError:
                        return 0.0
                return 0.0

            # Normalizar chaves (suporte a variações do Gemini)
            nf_data = data.get('nota_fiscal') or data.get('documento') or data
            emit_data = data.get('emitente') or data.get('fornecedor') or data
            items_data = data.get('itens') or data.get('produtos') or data.get('products') or data.get('produtos_servicos') or []
            totals_data = data.get('valores_totais') or data.get('calculo_imposto') or data
            
            # Converter produtos
            products = []
            for p in items_data:
                products.append(InvoiceProduct(
                    code=str(p.get('codigo') or p.get('code') or ''),
                    description=str(p.get('descricao') or p.get('description') or ''),
                    quantity=parse_br_float(p.get('quantidade') or p.get('quantity')),
                    unit=str(p.get('unidade') or p.get('unit') or 'UN'),
                    unit_price=parse_br_float(p.get('valor_unitario') or p.get('unit_price')),
                    total_price=parse_br_float(p.get('valor_total') or p.get('total_price')),
                ))
            
            # Limpar CNPJ (apenas números)
            raw_cnpj = str(emit_data.get('cnpj') or emit_data.get('supplier_cnpj') or '')
            cnpj = re.sub(r'\D', '', raw_cnpj)
            
            # Limpar chave de acesso
            raw_key = str(nf_data.get('chave_acesso') or nf_data.get('chave_de_acesso') or nf_data.get('access_key') or '')
            access_key = re.sub(r'\D', '', raw_key)
            
            # Extrair observações
            observations = ""
            if 'dados_adicionais' in data:
                dados = data['dados_adicionais']
                if isinstance(dados, dict):
                    observations = dados.get('informacoes_complementares', '')
                elif isinstance(dados, str):
                    observations = dados

            # Extrair dados principais
            number = str(nf_data.get('numero') or nf_data.get('number') or '')
            series = str(nf_data.get('serie') or nf_data.get('series') or '')
            issue_date = str(nf_data.get('data_emissao') or nf_data.get('issue_date') or '')
            supplier_name = str(emit_data.get('razao_social') or emit_data.get('supplier_name') or '')
            
            # Valor total
            total_val = parse_br_float(totals_data.get('valor_total_nota') or totals_data.get('total_value') or data.get('total_value'))

            return ExtractedInvoiceData(
                number=number,
                series=series,
                access_key=access_key,
                issue_date=issue_date,
                supplier_name=supplier_name,
                supplier_cnpj=cnpj,
                total_value=total_val,
                products=products,
                observations=observations,
                confidence=float(data.get('confidence', 0) or 1.0),
                raw_text=response_text,
            )
            
        except json.JSONDecodeError as e:
            return ExtractedInvoiceData(
                error=f"Erro ao parsear resposta: {e}",
                raw_text=response_text
            )
        except Exception as e:
            return ExtractedInvoiceData(
                error=f"Erro inesperado: {e}",
                raw_text=response_text
            )


def find_similar_materials(product_description: str, supplier_id: int, limit: int = 5):
    """Busca materiais similares no banco de dados para um produto da nota."""
    from django.db.models import Q
    from bidding_procurement.models import MaterialBidding
    
    words = product_description.upper().split()
    words = [w for w in words if len(w) > 2]
    
    if not words:
        return MaterialBidding.objects.none()
    
    query = Q()
    for word in words[:5]:
        query |= Q(material__name__icontains=word)
    
    return MaterialBidding.objects.filter(
        query,
        supplier_id=supplier_id,
        status='1'
    ).select_related('material', 'bidding').distinct()[:limit]


def find_supplier_by_cnpj(cnpj: str):
    """Busca fornecedor pelo CNPJ."""
    from django.db.models import Q
    from bidding_supplier.models import Supplier
    
    cnpj_clean = re.sub(r'\D', '', cnpj)
    
    if len(cnpj_clean) != 14:
        return None
    
    return Supplier.objects.filter(
        Q(cnpj=cnpj_clean) | 
        Q(cnpj__contains=cnpj_clean)
    ).first()
