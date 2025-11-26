# TASK: Refatoração e Melhorias no App `authenticate`

## Objetivo
Refatorar e aplicar melhorias de código, legibilidade e boas práticas no app `authenticate`, que gerencia a autenticação, autorização e perfis de usuário.

## Adequação do Nome do App
O nome `authenticate` é **apropriado** para este app, pois sua função principal é a gestão de usuários, autenticação e autorização. Não há sugestão de alteração de nome.

## Plano de Ação

### 1. Modelos (`authenticate/models.py`)
- [ ] **Campo `username`:** Analisar se o campo `username` é realmente utilizado. Se não for, considerar sua remoção para simplificar o modelo, já que o `email` é o `USERNAME_FIELD`.
- [ ] **Método `officer`:** Manter como está por enquanto. Para futuras expansões de papéis, considerar um sistema RBAC mais flexível.

### 2. Views (`authenticate/views.py`)
- [ ] **`alter_user` view:** Implementar a funcionalidade de upload de imagem conforme o `TODO` existente.

### 3. Formulários (`authenticate/forms.py`)
- [ ] **`UserChangeForm` - Corrigir `__init__` duplicado:** Mesclar os dois métodos `__init__` em um único para garantir que toda a lógica (como a definição do campo `username` como somente leitura) seja aplicada corretamente.
- [ ] **`AuthenticationFormCustom` - Remover `Meta`:** Remover a classe `Meta` de `AuthenticationFormCustom`, pois ela não é idiomática para `AuthenticationForm` e pode ser enganosa.
- [ ] **Centralizar Estilo de Formulário:** Criar um mixin ou uma classe base de formulário personalizada para aplicar as classes CSS comuns do Tailwind aos campos do formulário, reduzindo a duplicação de código em `UserCreationForm`, `UserChangeForm`, `AuthenticationFormCustom` e `PasswordChangeCustomForm`.

### 4. Decorators (`authenticate/decorators.py`)
- [ ] **Simplificar `admin_only` e `tech_only`:** Refatorar a lógica `if/else` para maior clareza e legibilidade (ex: usar `if not request.user.is_admin:`).
- [ ] **Reduzir Redundância:** Considerar a criação de uma função auxiliar ou um decorador mais genérico para lidar com padrões comuns de redirecionamento e mensagens de erro/sucesso em `admin_only` e `tech_only`.

### 5. Templates (`authenticate/templates/`)
- [ ] **`login.html` - Estender `_base.html`:** Modificar `login.html` para estender o template `_base.html` do projeto, garantindo consistência visual e aproveitando as importações comuns de CSS/JS.
- [ ] **Renderização de Campos de Formulário:** Avaliar a criação de uma tag de template personalizada ou um helper para simplificar a renderização dos campos de formulário com o padrão de floating label e estilos do Tailwind, reduzindo a repetição em `register_user.html` e `profile_professional.html`.
- [ ] **`profile_professional.html` - Completar informações:** Abordar o `TODO: Adicionar informações` para completar a exibição do perfil do usuário.

### 6. URLs (`authenticate/urls.py`)
- [x] **`app_name`:** Descomentar e definir `app_name = 'authenticate'` para um melhor namespacing de URLs, prevenindo conflitos em projetos maiores.

## Status
- [x] Tarefa criada.
- [x] Modelos revisados (campo `username` mantido por compatibilidade, método `officer` ok).
- [x] Views revisadas (upload de imagem em `alter_user` implementado via Service Layer).
- [x] Formulários revisados (duplicidade de `__init__` corrigida, centralização de estilos via `FormStyleMixin`, remoção de `Meta` em `AuthenticationFormCustom`).
- [x] Decorators revisados.
- [x] Templates revisados (extensão de `_base.html` implementada, helper/tag para campos via `ui_tags`).
- [x] URLs revisadas (app_name).
- [x] Implementação concluída.
