# AI_POLICY_LGPD.md
## Política de Uso de IA — Recorte LGPD (MVP)

### 1. Objetivo
Estabelecer diretrizes mínimas para uso de Inteligência Artificial em conformidade com a LGPD (Lei nº 13.709/2018),
garantindo proteção de dados pessoais em ambientes experimentais (MVP).

### 2. Escopo
Aplica-se a todos os sistemas, APIs, pipelines e interações com IA que tratem dados pessoais ou potencialmente identificáveis.

### 3. Princípios LGPD Aplicados à IA
- Finalidade
- Necessidade (minimização de dados)
- Adequação
- Segurança
- Prevenção
- Responsabilização

### 4. Dados Pessoais
- Evitar processamento de dados pessoais sempre que possível.
- Preferir dados anonimizados ou sintéticos.
- Dados sensíveis **não devem** ser processados por IA no MVP.

### 5. Logs e Observabilidade
- Logs não devem conter PII.
- Logs devem ser temporários e com retenção mínima.
- Debug com dados reais é proibido.

### 6. Retenção e Exclusão
- Dados utilizados por IA não devem ser armazenados permanentemente.
- Exclusão automática após uso.

### 7. Responsabilidades
- Desenvolvedores: garantir anonimização.
- Tech Lead: validar conformidade.
- Produto: garantir base legal.

### 8. Status do Documento
Documento MVP — sujeito a evolução para versão auditável.