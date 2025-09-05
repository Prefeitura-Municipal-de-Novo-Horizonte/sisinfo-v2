# Diretrizes de Teste

Este documento descreve como os testes são realizados e como você pode contribuir para a cobertura de testes do projeto SISInfo V2.

## 1. Executando Testes

O projeto utiliza o sistema de testes embutido do Django. Para executar todos os testes do projeto, navegue até o diretório raiz do projeto e execute o seguinte comando:

```bash
python manage.py test
```

Para executar testes de uma aplicação específica (ex: `authenticate`):

```bash
python manage.py test authenticate
```

## 2. Escrevendo Testes

*   **Localização:** Os testes devem ser escritos em arquivos `tests.py` dentro do diretório de cada aplicação Django (ex: `authenticate/tests.py`, `dashboard/tests.py`).
*   **Tipos de Teste:**
    *   **Testes de Unidade:** Focam em testar pequenas unidades de código (funções, métodos) isoladamente.
    *   **Testes de Integração:** Verificam a interação entre diferentes componentes do sistema.
    *   **Testes de Funcionalidade/End-to-End:** (Opcional, dependendo da complexidade) Simulam o comportamento do usuário para testar fluxos completos.
*   **Boas Práticas:**
    *   Mantenha os testes concisos e focados em um único aspecto.
    *   Utilize nomes descritivos para suas classes e métodos de teste.
    *   Garanta que seus testes sejam reproduzíveis e independentes.

## 3. Cobertura de Testes

É altamente recomendável que novas funcionalidades e correções de bugs sejam acompanhadas de testes correspondentes para garantir a estabilidade e prevenir regressões.
