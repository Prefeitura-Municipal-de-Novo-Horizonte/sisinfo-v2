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
    Copie o arquivo de exemplo e preencha com suas credenciais locais (banco de dados, secret key, etc.).
    ```bash
    cp contrib/.env-sample .env
    ```

5.  **Execute as migrações do banco de dados:**
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
