# Diretrizes de Contribuição

Bem-vindo(a) ao projeto SISInfo V2! Agradecemos o seu interesse em contribuir. Para garantir a consistência e a qualidade do código, por favor, siga as diretrizes abaixo.

## 1. Configuração do Ambiente de Desenvolvimento

Para configurar o ambiente de desenvolvimento local, siga os passos descritos no `README.md` do projeto. Em resumo:

1.  Clone o repositório: `git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git`
2.  Navegue até o diretório do projeto: `cd sisinfo-v2`
3.  Crie e ative um ambiente virtual Python:
    *   `python -m venv .venv`
    *   No Linux/Unix: `source .venv/bin/activate`
    *   No Windows: `.venv\Scripts\activate.bat`
4.  Instale as dependências Python: `pip install -r requirements.txt`
5.  Instale as dependências JavaScript: `npm install`
6.  Copie o arquivo de variáveis de ambiente e configure-o: `cp contrib/.env-sample .env` (preencha as variáveis necessárias).
7.  Inicie o observador do TailwindCSS: `npm run dev`
8.  Inicie o servidor Django: `python manage.py runserver`

## 2. Fluxo de Trabalho de Contribuição

1.  **Crie uma Branch:** Para cada nova funcionalidade ou correção de bug, crie uma nova branch a partir da `main` com um nome descritivo (ex: `feat/nova-funcionalidade`, `fix/correcao-bug-x`).
2.  **Desenvolva:** Implemente suas alterações.
3.  **Testes:** Certifique-se de que suas alterações não quebrem funcionalidades existentes e, se aplicável, adicione novos testes. Consulte `TESTING.md` para mais detalhes.
4.  **Commit:** Faça commits atômicos e com mensagens claras. Siga a convenção de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) (ex: `feat: adiciona autenticação de usuário`, `fix: corrige erro de login`).
5.  **Atualize sua Branch:** Antes de abrir um Pull Request, certifique-se de que sua branch está atualizada com a `main` (rebase ou merge).
6.  **Abra um Pull Request (PR):** Abra um PR para a branch `main`. Descreva suas alterações detalhadamente e referencie quaisquer issues relacionadas.
7.  **Revisão de Código:** Seu PR será revisado por outro(s) membro(s) da equipe. Esteja aberto(a) a feedback e faça as alterações solicitadas.

## 3. Estilo de Código e Formatação

*   **Python:** Siga as diretrizes da [PEP 8](https://www.python.org/dev/peps/pep-0008/). Utilize ferramentas de linting como `djlint` para templates Django.
*   **JavaScript/CSS:** Utilize `prettier` para formatação automática de código. O projeto já inclui `prettier-plugin-tailwind-css`. Certifique-se de que o comando `npm run dev` está rodando para o TailwindCSS.

## 4. Mensagens de Commit

Por favor, siga a especificação de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Isso ajuda a manter um histórico de commits limpo e facilita a geração automática de changelogs.

Exemplos:
*   `feat: adiciona funcionalidade de cadastro de usuários`
*   `fix: corrige bug de exibição na página inicial`
*   `docs: atualiza documentação de contribuição`
*   `refactor: refatora módulo de autenticação`
*   `test: adiciona testes para o modelo de usuário`
