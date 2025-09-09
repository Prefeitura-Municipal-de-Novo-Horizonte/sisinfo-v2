# TASK: Melhorias Iniciais de Configuração

## Objetivo
Refatorar as configurações do projeto para garantir uma separação clara entre ambientes de desenvolvimento e produção, aumentar a segurança e aplicar boas práticas de configuração do Django.

## Motivação
A aplicação está em produção e aprimorar a configuração base é crucial para a estabilidade, segurança e manutenibilidade do sistema.

## Plano de Ação

### 1. Estrutura de Configuração por Ambiente
- [x] Criar um novo diretório `core/settings/`.
- [x] Mover o conteúdo atual de `core/settings.py` para `core/settings/base.py`.
- [x] Criar `core/settings/development.py` para configurações específicas de desenvolvimento:
    - [x] `DEBUG = True`
    - [x] `SECRET_KEY` para desenvolvimento (pode ser uma string simples, mas segura para dev).
    - [x] `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`
    - [x] `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
    - [x] Configuração de banco de dados local (SQLite ou PostgreSQL via Docker).
- [x] Criar `core/settings/production.py` para configurações específicas de produção:
    - [x] `DEBUG = False`
    - [x] `SECRET_KEY` lida de forma segura (variável de ambiente robusta).
    - [x] `ALLOWED_HOSTS` configurado com os domínios de produção.
    - [x] Configuração de banco de dados de produção (PostgreSQL).
    - [x] Configuração de e-mail de produção.
    - [x] Adicionar configurações de segurança (ver item 2).
    - [ ] Adicionar configurações de logging (ver item 5).
- [x] Atualizar `manage.py` e `core/wsgi.py` para carregar as configurações corretas usando a variável de ambiente `DJANGO_SETTINGS_MODULE`.

### 2. Melhorias de Segurança
- [x] Em `production.py`, adicionar/revisar as seguintes configurações:
    - [x] `SECRET_KEY`: Garantir que seja lida de uma variável de ambiente segura e que seja uma string longa e aleatória.
    - [x] `SECURE_SSL_REDIRECT = True` (se o servidor web não estiver fazendo isso).
    - [x] `SECURE_HSTS_SECONDS = 31536000` (1 ano)
    - [x] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
    - [x] `SECURE_HSTS_PRELOAD = True`
    - [x] `SESSION_COOKIE_SECURE = True`
    - [x] `CSRF_COOKIE_SECURE = True`
    - [x] `SESSION_COOKIE_HTTPONLY = True`
    - [x] `CSRF_COOKIE_HTTPONLY = True`
    - [x] `X_FRAME_OPTIONS = 'DENY'` (já presente no middleware, mas bom ter explícito).
    - [x] `SECURE_BROWSER_XSS_FILTER = True`
    - [x] `SECURE_CONTENT_TYPE_NOSNIFF = True`

### 3. Configuração de Banco de Dados
- [x] Em `production.py`, garantir que a `DATABASE_URL` esteja configurada para o banco de dados de produção.
- [x] Adicionar `CONN_MAX_AGE = 600` (ou outro valor apropriado) para conexões persistentes em `production.py`.

### 4. Arquivos Estáticos e de Mídia
- [x] Em `base.py`, manter as configurações de `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_URL`, `MEDIA_ROOT`.
- [ ] Em `production.py`, considerar a configuração de `STATICFILES_STORAGE` e `DEFAULT_FILE_STORAGE` para serviços de armazenamento em nuvem (ex: S3, Cloudinary) se a aplicação for servir esses arquivos via CDN.

### 5. Configuração de Logging
- [ ] Em `production.py`, adicionar uma configuração de logging robusta para capturar erros e eventos importantes:
    - [ ] Configurar handlers para logs em arquivo (ex: `info.log`, `error.log`).
    - [ ] Configurar um handler para enviar e-mails aos administradores em caso de erros críticos (`AdminEmailHandler`).
    - [ ] Definir formatters e loggers apropriados.

### 6. Variáveis de Ambiente
- [x] Atualizar `contrib/.env-sample` para refletir as novas variáveis de ambiente necessárias (ex: `DJANGO_SETTINGS_MODULE`, variáveis para logging, etc.).
- [x] Reforçar a importância de não commitar o arquivo `.env` real.

## Verificação
- [ ] Testar a aplicação em ambiente de desenvolvimento para garantir que as novas configurações funcionem corretamente.
- [ ] Simular o ambiente de produção (se possível) para verificar as configurações de segurança, logging e e-mail.
- [ ] Executar `python manage.py check --deploy` para verificar problemas de configuração em produção.

## Status
- [x] Tarefa criada.
- [x] Estrutura de Configuração por Ambiente implementada.
- [x] Melhorias de segurança aplicadas.
- [x] Configuração de banco de dados ajustada.
- [x] Configuração de arquivos estáticos/mídia revisada.
- [ ] Configuração de logging adicionada.
- [x] Variáveis de ambiente atualizadas.
- [ ] Verificação concluída.
- [x] Implementação concluída.