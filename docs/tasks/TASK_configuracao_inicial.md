# TASK: Melhorias Iniciais de Configuração

## Objetivo
Refatorar as configurações do projeto para garantir uma separação clara entre ambientes de desenvolvimento e produção, aumentar a segurança e aplicar boas práticas de configuração do Django.

## Motivação
A aplicação está em produção e aprimorar a configuração base é crucial para a estabilidade, segurança e manutenibilidade do sistema.

## Plano de Ação

### 1. Estrutura de Configuração por Ambiente
- [ ] Criar um novo diretório `core/settings/`.
- [ ] Mover o conteúdo atual de `core/settings.py` para `core/settings/base.py`.
- [ ] Criar `core/settings/development.py` para configurações específicas de desenvolvimento:
    - [ ] `DEBUG = True`
    - [ ] `SECRET_KEY` para desenvolvimento (pode ser uma string simples, mas segura para dev).
    - [ ] `ALLOWED_HOSTS = ['127.0.0.1', 'localhost']`
    - [ ] `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
    - [ ] Configuração de banco de dados local (SQLite ou PostgreSQL via Docker).
- [ ] Criar `core/settings/production.py` para configurações específicas de produção:
    - [ ] `DEBUG = False`
    - [ ] `SECRET_KEY` lida de forma segura (variável de ambiente robusta).
    - [ ] `ALLOWED_HOSTS` configurado com os domínios de produção.
    - [ ] Configuração de banco de dados de produção (PostgreSQL).
    - [ ] Configuração de e-mail de produção.
    - [ ] Adicionar configurações de segurança (ver item 2).
    - [ ] Adicionar configurações de logging (ver item 5).
- [ ] Atualizar `manage.py` e `core/wsgi.py` para carregar as configurações corretas usando a variável de ambiente `DJANGO_SETTINGS_MODULE`.

### 2. Melhorias de Segurança
- [ ] Em `production.py`, adicionar/revisar as seguintes configurações:
    - [ ] `SECRET_KEY`: Garantir que seja lida de uma variável de ambiente segura e que seja uma string longa e aleatória.
    - [ ] `SECURE_SSL_REDIRECT = True` (se o servidor web não estiver fazendo isso).
    - [ ] `SECURE_HSTS_SECONDS = 31536000` (1 ano)
    - [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
    - [ ] `SECURE_HSTS_PRELOAD = True`
    - [ ] `SESSION_COOKIE_SECURE = True`
    - [ ] `CSRF_COOKIE_SECURE = True`
    - [ ] `SESSION_COOKIE_HTTPONLY = True`
    - [ ] `CSRF_COOKIE_HTTPONLY = True`
    - [ ] `X_FRAME_OPTIONS = 'DENY'` (já presente no middleware, mas bom ter explícito).
    - [ ] `SECURE_BROWSER_XSS_FILTER = True`
    - [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True`

### 3. Configuração de Banco de Dados
- [ ] Em `production.py`, garantir que a `DATABASE_URL` esteja configurada para o banco de dados de produção.
- [ ] Adicionar `CONN_MAX_AGE = 600` (ou outro valor apropriado) para conexões persistentes em `production.py`.

### 4. Arquivos Estáticos e de Mídia
- [ ] Em `base.py`, manter as configurações de `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_URL`, `MEDIA_ROOT`.
- [ ] Em `production.py`, considerar a configuração de `STATICFILES_STORAGE` e `DEFAULT_FILE_STORAGE` para serviços de armazenamento em nuvem (ex: S3, Cloudinary) se a aplicação for servir esses arquivos via CDN.

### 5. Configuração de Logging

#### Pendentes:
- [ ] Adicionar configuração de logging robusta em `core/settings/production.py`:
    - [ ] Configurar handlers para logs em arquivo (`info.log`, `error.log`).
    - [ ] Configurar handler para envio de e-mails aos administradores em caso de erros críticos (`AdminEmailHandler`).
    - [ ] Definir formatters e loggers apropriados.


#### Pendentes:
- [ ] Adicionar configuração de storage em nuvem para arquivos estáticos e de mídia em `core/settings/production.py`:
    - [ ] Configurar `STATICFILES_STORAGE` e `DEFAULT_FILE_STORAGE` para uso de S3, Cloudinary ou similar.
    - [ ] Garantir que variáveis de ambiente estejam presentes no `.env-sample`.
- [ ] Atualizar `contrib/.env-sample` para refletir as novas variáveis de ambiente necessárias (ex: `DJANGO_SETTINGS_MODULE`, variáveis para logging, etc.).
- [ ] Reforçar a importância de não commitar o arquivo `.env` real.

## Verificação
- [ ] Testar a aplicação em ambiente de desenvolvimento para garantir que as novas configurações funcionem corretamente.
- [ ] Simular o ambiente de produção (se possível) para verificar as configurações de segurança, logging e e-mail.
- [ ] Executar `python manage.py check --deploy` para verificar problemas de configuração em produção.

## Status
- [ ] Tarefa criada.
- [ ] Estrutura de Configuração por Ambiente implementada.
- [ ] Melhorias de segurança aplicadas.
- [ ] Configuração de banco de dados ajustada.
- [ ] Configuração de arquivos estáticos/mídia revisada.
- [ ] Configuração de logging adicionada.
- [ ] Variáveis de ambiente atualizadas.
- [ ] Verificação concluída.
- [ ] Implementação concluída.
