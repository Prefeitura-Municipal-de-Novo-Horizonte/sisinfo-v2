# Sistema de Gerenciamento de TI - SISInfo V2 💻⚙️

\u003cdiv align="center"\u003e
\u003cimg src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/capa.png" width="350" /\u003e

\u003cdiv data-badges\u003e
    \u003cimg src="https://img.shields.io/github/stars/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub stars" /\u003e
    \u003cimg src="https://img.shields.io/github/forks/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub forks" /\u003e
    \u003cimg src="https://img.shields.io/github/issues/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub issues" /\u003e
\u003c/div\u003e

\u003cdiv data-badges\u003e
    \u003cimg src="https://img.shields.io/badge/python-3670A0?style=for-the-badge\u0026logo=python\u0026logoColor=ffdd54" alt="Python" /\u003e
    \u003cimg src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge\u0026logo=django\u0026logoColor=white" alt="Django" /\u003e
    \u003cimg src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge\u0026logo=tailwind-css\u0026logoColor=white" alt="Tailwind CSS" /\u003e
    \u003cimg src="https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge\u0026logo=vercel\u0026logoColor=white" alt="Vercel" /\u003e
    \u003cimg src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge\u0026logo=postgresql\u0026logoColor=white" alt="Postgres" /\u003e
    \u003cimg src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge\u0026logo=javascript\u0026logoColor=%23F7DF1E" alt="Postgres" /\u003e
    \u003cimg src="https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge\u0026logo=gnu-bash\u0026logoColor=white" alt="Postgres" /\u003e

\u003c/div\u003e
\u003c/div\u003e

\u003ch3\u003e🖥️ SISInfo: Sistema de Gerenciamento da Diretoria de TI 🖥️\u003c/h3\u003e
O SISInfo é uma plataforma completa e intuitiva desenvolvida para otimizar e centralizar a gestão da Diretoria de Tecnologia da Informação da Prefeitura de Novo Horizonte. Com foco em eficiência e organização, o sistema oferece um conjunto de ferramentas robustas para simplificar o dia a dia dos profissionais de TI e garantir o funcionamento eficaz dos serviços tecnológicos do município.

### 📋 Funcionalidades Principais 📋
#### Gerenciamento de Ativos de TI:
- Cadastro e controle detalhado de todos os equipamentos, softwares e licenças utilizados pela prefeitura.
 - Monitoramento do ciclo de vida dos ativos, desde a aquisição até o descarte.
 - Geração de relatórios sobre a utilização e o estado dos ativos.
#### Central de Serviços de Helpdesk:
 - Registro e acompanhamento de chamados e solicitações de suporte técnico.
 - Categorização e priorização de incidentes para garantir atendimento eficiente.
 - Base de conhecimento para soluções rápidas e autônomas.
#### Gestão de Projetos de TI:
 - Planejamento e controle de projetos de desenvolvimento e implementação de sistemas.
 - Acompanhamento de prazos, custos e recursos envolvidos em cada projeto.
 - Ferramentas de colaboração para facilitar a comunicação entre os membros da equipe.
#### Relatórios e Análises:
 - Geração de relatórios personalizados sobre o desempenho da equipe, a utilização de recursos e a eficiência dos serviços de TI.
 - Painéis de controle com indicadores-chave de desempenho (KPIs) para facilitar a tomada de decisões estratégicas.
 - Análises preditivas para identificar tendências e antecipar necessidades futuras.

O SISInfo é a solução ideal para a Prefeitura de Novo Horizonte otimizar seus processos de TI, reduzir custos e garantir a qualidade dos serviços tecnológicos prestados à comunidade.

## Tecnologias usadas: 🚀⚙️
| Tecnologia | Versão | Descrição |
| :---------- | :--------- | :---------------------------------- |
| `Python` | `3.12.x` | **Recomendado**. Python 3.11.x também compatível |
| `Django` | `5.2.6` | Framework web principal |
| `Node.js` | `20.9.0+` | **Obrigatório**. Usado para TailwindCSS e Flowbite |
| `PostgreSQL` | `Latest` | Banco de dados (via Supabase) |
| `TailwindCSS` | `3.3.5` | Framework CSS |
| `Flowbite` | `2.0.0` | Componentes UI |

## 🚀 Setup Local

### 1. Clonar o repositório

```bash
git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git
cd sisinfo-v2
```

### 2. Criar ambiente virtual Python

```bash
python -m venv .venv
```

**Linux/Unix:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\\Scripts\\activate.bat
```

### 3. Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalar dependências Node.js

```bash
npm install
```

### 5. Configurar variáveis de ambiente

```bash
cp contrib/.env-sample .env
```

Edite o arquivo `.env` e configure:
- `SECRET_KEY`: Chave secreta do Django
- `DATABASE_URL`: URL de conexão com PostgreSQL (Supabase)
- `DEBUG`: `True` para desenvolvimento, `False` para produção
- `ALLOWED_HOSTS`: Hosts permitidos (ex: `localhost,127.0.0.1,.vercel.app`)

### 6. Executar migrações

```bash
python manage.py migrate
```

### 7. Rodar em desenvolvimento

Em um terminal:
```bash
npm run dev
```

Em outro terminal:
```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000`

## 📦 Deploy na Vercel

O projeto está configurado para deploy automático na Vercel.

### Configuração

1. **Conecte o repositório** no dashboard da Vercel
2. **Configure as variáveis de ambiente** no Vercel:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.vercel.app`

3. **Deploy automático**: Cada push para `main` faz deploy automático

### Arquivos de configuração

- `vercel.json`: Configuração do Vercel (Python 3.12, região sfo1)
- `build.sh`: Script de build (instala deps, roda migrações, coleta statics)

## 🐛 Troubleshooting

### Erro 504 (Gateway Timeout)
- Verifique se a região do Vercel (`sfo1`) está próxima do banco Supabase
- Otimize queries lentas com `select_related()` e `prefetch_related()`

### Migrações não aplicadas
- Rode localmente: `python manage.py migrate`
- Commit as migrações: `git add dashboard/migrations/ && git commit`
- Push para aplicar em produção

### Erro de slug vazio
- Certifique-se de que todos os objetos têm slugs válidos
- Rode: `python manage.py shell` e execute a migração de dados manualmente

## 📸 Screenshots

![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/2.jpg)
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/3.jpg)