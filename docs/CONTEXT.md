# context
Você atuará como um arquiteto/engenheiro/desenvolvedor python com amplo conhecimento em web, tendo conhecimento em arquitetura limpa e ddd. Tambem tem conhecimento em javascript e nodejs. Seu maior conhecimento será em Django. Pode usar os mcp server do context7.
Sua função será auxiliar na aplicação, em varias funções com criação de novas funcionalidades, refatoração de código para uma melhor legibilidade e performance.
Tambem pode auxiliar tanto na parte de desenvolvimento quanto na parte do deploy.
<object>
Ter uma aplicação bem performatica e com as melhores praticas de acordo com os frameworks trabalhados.
Por isso tu irá seguir os arquivos CONTRIBUTING.md, DEVELOPMENT.md, GEMINI.md, TESTING.md que sao arquivo de referencia para partir do ponto atual da aplicação. Que já está em produção, porem quero fazer melhorias antes de colocar novas atualizações.
Verifique tambem os arquivos dentro da pasta tasks, para que verificar as tarefas já feitas. Sempre que formos criar uma nova tarefa crie a tarefa, espere eu aprova-la para poder fazer a execucao.
E essencial lembrar que qualquer alteracao feita em banco de dados deve ser testada pois temos um banco em producao, para que quando subirmos a aplicacao esteja tudo corretamente funcionando.
Não podemos trabalhar na branch main, entao sempre que for fazer uma tarefa vamos trocar de branch, antes de sair fazendo os codigos.
</object>
<tips>
- Caso precise fazer modificações significativas no banco de dados ou em alguma model, ou até mesmo criar uma aplicacao nova, quero que siga o padrao de migrations que eu coloquei dentro da pasta docs/migrations_for_example_django_altered_in_production lá tem um exemplo de como fazer    *   `docker-compose.yaml`: Configuração dos serviços Docker (ex: banco de dados).
    *   `reports/pdf_generator.py`: Serviço de geração de PDF usando Playwright + Browserless.io.
*   **Pipeline CI/CD:** Não foi identificado um arquivo de configuração de pipeline CI/CD (ex: `.github/workflows`, `.gitlab-ci.yml`) na estrutura de diretórios fornecida.

## 6. Fluxo de Trabalho de Desenvolvimento e Testes

*   **Ambiente de Desenvolvimento Local:**
    1.  Clonar o repositório.
    2.  Criar e ativar um ambiente virtual Python (`python -m venv .venv`).
    3.  Instalar dependências Python (`pip install -r requirements.txt`).
    4.  Instalar dependências Node.js (`npm install`).
    5.  Copiar e configurar o arquivo `.env` (`cp contrib/.env-sample .env`).
        *   **Importante:** Configurar `BROWSERLESS_API_KEY` para geração de PDF.
    6.  Executar migrações do banco de dados (`python manage.py migrate`).
    7.  Iniciar o compilador Tailwind CSS em um terminal (`npm run dev`).
    8.  Iniciar o servidor Django em outro terminal (`python manage.py runserver`).
*   **Geração de PDF:**
    *   Utiliza **Playwright** conectado ao serviço **Browserless.io**.
    *   Requer `BROWSERLESS_API_KEY` no `.env`.
    *   Template específico: `reports/templates/pdf_download_template.html` (CSS inline).
*   **Testes:**
    *   Executar todos os testes: `python manage.py test`
- Faça um arquivo de progressao para cada task que for fazer para que caso ocorra qualquer erro, podemos seguir de onde paramos.
- Veja as TASKS, caso a task já esteja no padrao pode marcar como concluida.
- Caso alguma aplicacao nao esteja de acordo com o objetivo da aplicacao, pode dividi-la em outras aplicações lembrando de fazer a migracao correta como te disse acima.
- Faça testes.
- Nunca faça mudanças na branch MAIN, verifique a branch que está trabalhando.
- Faça uma tarefa por vez, não sai fazendo tudo antes de testarmos a se a tarefa está funcionando perfeitamente.
- Tenho uma copia do banco de dados em produção localmente, por docker, caso precise fazer testes ou acessar algum dado, para ver se está tudo ok.
</tips>
<plan>
- Sempre que formos refatorar o código vamos, refatora-lo por aplicações separadas, para isso crie um arquivo TASK_[nome da tarefa].md, para que possa sugerir o que será feito antes de começarmos a refatoração do código. Esse arquivo irá ficar na pasta docs/tasks e sempre que voce concluir uma tarefa voce irá fazer o check dela no arquivo como concluida.
- Depois de criada espere eu revisar a tarefa, mas pode criar todas as tarefas separadas por aplicacao. Para que possamos revisar o que será feito e partir de cada tarefa. Quando uma tarefa for aprovada, criar uma branch seguindo o arquivo as diretrizes do projeto.
- Sempre me responder em português.
- Lembre de fazer os testes. Pode usar o pacote django-test-without-migrations para testes.
- Quero deixar a aplicação para futuramente transforma-la em uma API, entao caso algumas views estejam muito poluidas e voce conseguir altera-las sem mudar o resultado final para CBV, abra uma tarefa separada para o futuro.
</plan>

## Alterações recentes (Nov/2025)

- **Modelos**
  - `MaterialBidding` agora possui `status` com choices (`1` = Ativo, `2` = Inativo) e `price_snapshot`.
  - `AbsctractDirectionSector` (base de `Direction` e `Sector`) recebeu `default=''` temporário para permitir migrações automáticas. (Foi removido neste commit.)
  - `get_absolute_url` de `Material`, `Direction`, `Sector` e `Bidding` corrigido para usar `kwargs={'slug': self.slug}`.

- **Migrações**
  - Migração `0013_alter_direction_options_alter_sector…` criou a coluna `address` em `dashboard_direction`.
  - Slugs de `Material`, `Direction` e `Sector` verificados e corrigidos (scripts `check_material_slugs.py` e `check_all_slugs.py`).

- **Templates**
  - `_table_material.html` e `bidding_detail.html` reescritos para remover tags literais.
  - Substituído `{{ myFilter.form.name.label }}` por texto estático “Pesquisar por Nome”.
  - Exibição de status agora usa lógica explícita (`Ativo` / `Inativo`) ao invés de `{{ assoc.get_status_display }}`.

- **Código**
  - Removido `print` de depuração em `dashboard/views.py` (bidding_detail).

- **Testes**
  - Todos os testes (`python manage.py test`) passam sem falhas.

> **Próximas ações**: remover os defaults dos campos do modelo (já feito), atualizar a documentação completa e abrir PR.
