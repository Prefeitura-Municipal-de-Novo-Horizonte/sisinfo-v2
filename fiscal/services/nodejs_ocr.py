"""
Cliente para chamar a API Node.js de OCR.
"""
import base64
import requests
from decouple import config


def call_nodejs_ocr(image_bytes: bytes, mime_type: str = 'image/jpeg') -> dict:
    """
    Chama a API Node.js de OCR para processar uma nota fiscal.
    
    Args:
        image_bytes: Bytes da imagem
        mime_type: Tipo MIME da imagem
        
    Returns:
        dict com dados extraídos ou erro
    """
    # Configurações
    api_secret = config('INTERNAL_API_SECRET', default=None)
    vercel_url = config('VERCEL_URL', default='http://localhost:3000')
    
    if not api_secret:
        return {'success': False, 'error': 'INTERNAL_API_SECRET não configurada'}
    
    # Converter para base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # Determinar URL da API
    # Em produção, usa VERCEL_URL; em desenvolvimento, usa localhost
    if vercel_url.startswith('http'):
        api_url = f"{vercel_url}/api/ocr"
    else:
        api_url = f"https://{vercel_url}/api/ocr"
    
    try:
        response = requests.post(
            api_url,
            json={
                'image': base64_image,
                'mimeType': mime_type
            },
            headers={
                'X-API-Key': api_secret,
                'Content-Type': 'application/json'
            },
            timeout=15  # 15 segundos de timeout
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            return {
                'success': True,
                'data': data.get('data', {}),
                'meta': data.get('meta', {})
            }
        else:
            return {
                'success': False,
                'error': data.get('error', 'Erro desconhecido')
            }
            
    except requests.Timeout:
        return {
            'success': False,
            'error': 'Timeout: O processamento demorou muito. Tente novamente ou cadastre manualmente.'
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Erro de conexão: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro inesperado: {str(e)}'
        }


def parse_nodejs_ocr_response(data: dict) -> dict:
    """
    Converte a resposta da API Node.js para o formato esperado pelo Django.
    
    Args:
        data: Dados retornados pela API Node.js
        
    Returns:
        dict no formato esperado pelas views do Django
    """
    nf = data.get('nota_fiscal', {})
    emit = data.get('emitente', {})
    items = data.get('itens', [])
    totals = data.get('valores_totais', {})
    
    # Limpar CNPJ
    cnpj = emit.get('cnpj', '')
    cnpj_clean = ''.join(c for c in cnpj if c.isdigit())
    
    # Limpar chave de acesso
    access_key = nf.get('chave_acesso', '')
    access_key_clean = ''.join(c for c in access_key if c.isdigit())
    
    # Converter produtos
    products = []
    for item in items:
        products.append({
            'code': item.get('codigo', ''),
            'description': item.get('descricao', ''),
            'quantity': _parse_float(item.get('quantidade', 0)),
            'unit': item.get('unidade', 'UN'),
            'unit_price': _parse_float(item.get('valor_unitario', 0)),
            'total_price': _parse_float(item.get('valor_total', 0)),
        })
    
    return {
        'number': nf.get('numero', ''),
        'series': nf.get('serie', ''),
        'access_key': access_key_clean,
        'issue_date': nf.get('data_emissao', ''),
        'supplier_name': emit.get('razao_social', ''),
        'supplier_cnpj': cnpj_clean,
        'total_value': _parse_float(totals.get('valor_total_nota', 0)),
        'products': products,
        'observations': data.get('dados_adicionais', {}).get('informacoes_complementares', ''),
    }


def _parse_float(value) -> float:
    """Converte valor para float, tratando formatos brasileiros."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove pontos de milhar e troca vírgula por ponto
        clean = value.replace('.', '').replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return 0.0
    return 0.0
