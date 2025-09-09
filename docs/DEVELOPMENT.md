# Guia de Desenvolvimento

Este documento descreve como configurar e executar o ambiente de desenvolvimento local para o SISInfo V2.

## Pré-requisitos

| Tecnologia | Versão   | Obrigatório |
| :--------- | :------- | :---------- |
| `python`   | `3.12.x` | Preferível  |
| `nodejs`   | `20.9.0+`| Sim         |
| `pip`      | `latest` | Sim         |

## 1. Configuração Inicial

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git
    cd sisinfo-v2
    ```

2.  **Crie e ative o ambiente virtual Python:**
    ```bash
    # Crie o ambiente
    python -m venv .venv

    # Ative no Linux/macOS
    source .venv/bin/activate

    # Ative no Windows (PowerShell/CMD)
    .venv\Scripts\activate
    ```

3.  **Instale as dependências (Python e Node.js):**
    ```bash
    pip install -r requirements.txt
    npm install
    ```

4.  **Configure as variáveis de ambiente:**
    Copie o arquivo de exemplo `.env-sample` para `.env` e preencha com suas credenciais locais (banco de dados, secret key, etc.). Este arquivo também controlará qual conjunto de configurações do Django será carregado.
    ```bash
    cp contrib/.env-sample .env
    ```

5.  **Entenda as configurações do Django (`DJANGO_SETTINGS_MODULE`):**
    O projeto agora utiliza uma estrutura de configurações separada por ambiente (`core/settings/`). A variável de ambiente `DJANGO_SETTINGS_MODULE` define qual arquivo de configuração será carregado.
    *   Para **desenvolvimento local**, o valor padrão é `core.settings.development`. Este arquivo configura o `DEBUG=True`, uma `SECRET_KEY` para desenvolvimento e o backend de e-mail para console.
    *   Para **produção**, o valor deve ser `core.settings.production`. Este arquivo contém configurações de segurança aprimoradas, `DEBUG=False` e outras otimizações para o ambiente de produção.
    Você pode sobrescrever o padrão definindo a variável de ambiente antes de executar comandos Django, por exemplo:
    ```bash
    DJANGO_SETTINGS_MODULE=core.settings.production python manage.py check --deploy
    ```

6.  **Execute as migrações do banco de dados:**
    Este comando prepara o banco de dados com o schema necessário para a aplicação.
    ```bash
    python manage.py migrate
    ```

## 2. Executando o Projeto

Para desenvolver, você precisará de dois terminais abertos.

*   **Terminal 1: Compilador Tailwind CSS**
    Este comando irá observar as alterações nos seus arquivos de template e CSS e recompilar o arquivo de estilo principal.
    ```bash
    npm run dev
    ```

*   **Terminal 2: Servidor Django**
    Este comando irá iniciar o servidor de desenvolvimento do Django.
    ```bash
    python manage.py runserver
    ```

Agora você pode acessar o projeto em `http://127.0.0.1:8000`.

## 3. Executando Testes

O projeto utiliza o `django-test-without-migrations` para otimizar a execução de testes durante o desenvolvimento.

### Abordagem Híbrida

Adotamos uma abordagem híbrida para garantir tanto agilidade quanto segurança:

*   **Para Desenvolvimento Rápido (Local):**
    Use o comando a seguir para rodar os testes **sem** aplicar as migrações. É muito mais rápido e ideal para o dia a dia, ao validar a lógica de negócio.
    ```bash
    python manage.py test --nomigrations
    ```

*   **Para Validação Completa (Obrigatório antes de Merges/Deploys):**
    Use o comando padrão para rodar a suíte de testes completa, incluindo a aplicação de todas as migrações. Isso garante que o ambiente de teste é fiel ao de produção e que as migrações estão saudáveis.
    ```bash
    python manage.py test
    ```
