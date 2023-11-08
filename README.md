# Sistema de Gerenciamento de TI - SISInfo V2

Sistema para gerenciar a diretoria de TI da PMNH

Tecnologias usadas:
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
