# Sistema de Gerenciamento de TI - SISInfo V2 💻⚙️

<div align="center">
<img src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/capa.png" width="350" />

<div data-badges>
    <img src="https://img.shields.io/github/stars/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub stars" />
    <img src="https://img.shields.io/github/forks/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub forks" />
    <img src="https://img.shields.io/github/issues/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub issues" />
</div>

<div data-badges>
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python" />
    <img src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
    <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres" />
    <img src="https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E" alt="Postgres" />
    <img src="https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white" alt="Postgres" />

</div>
</div>

<h3>🖥️ SISInfo: Sistema de Gerenciamento da Diretoria de TI 🖥️</h3>
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
| Tecnologia | Version | Descrição |
| :---------- | :--------- | :---------------------------------- |
| `python` | `3.12` | **Opcional**. Preferivél, porem pode se trabalhar no python 3.11.x |
| `nodejs` | `20.9.0` | **Obrigatório**. Usado para utilizando do TailwindCSS e Flowbite |

Como utilizar:

```bash
git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git

cd sisinfo-v2

python -m venv .venv
```

Caso esteja no linux ou unix:

```bash
source .venv/bin/activate
```

Caso esteja no windows:

```bash
.venv\Scripts\activate.bat
```

Proximo passo instalar as dependências:

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

Instalando as dependências para o frontend:

```bash
npm install
```

Arquivo de secret key:

```bash
cp contrib/.env-sample .env
```

Feito isso, adicionar as senhas no arquivo .env

----------------------------------------------------------------

## Para desenvolvimento

rodar no terminal

```bash
npm run dev

python manage.py runserver
```

![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/2.jpg)
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/3.jpg)