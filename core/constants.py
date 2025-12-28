"""
Constantes compartilhadas do projeto.

Este módulo centraliza:
- Classes CSS para formulários
- Choices de status para models
- Outras constantes reutilizáveis
"""

# =============================================================================
# CSS CLASSES (Tailwind)
# =============================================================================

STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"

TEXTAREA_CLASS = "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"


# =============================================================================
# STATUS CHOICES COMUNS
# =============================================================================

STATUS_ACTIVE_INACTIVE = (
    ("1", "Ativo"),
    ("2", "Inativo"),
)

STATUS_OPEN_CLOSED = (
    ("1", "Aberto"),
    ("3", "Finalizado"),
)

STATUS_PENDING_COMPLETED = (
    ("P", "Pendente"),
    ("C", "Concluído"),
)


# =============================================================================
# INVOICE STATUS
# =============================================================================

INVOICE_STATUS = (
    ("P", "Pendente"),      # Nota recebida, aguardando processamento
    ("R", "Recebida"),      # Materiais conferidos
    ("E", "Entregue"),      # Entregue ao setor de compras
)


# =============================================================================
# DELIVERY STATUS
# =============================================================================

DELIVERY_STATUS = (
    ("P", "Pendente"),      # Aguardando entrega
    ("A", "A Caminho"),     # Em trânsito
    ("C", "Concluída"),     # Entregue com sucesso
    ("X", "Cancelada"),     # Cancelada
)


# =============================================================================
# OCR JOB STATUS
# =============================================================================

OCR_JOB_STATUS = (
    ("pending", "Pendente"),
    ("processing", "Processando"),
    ("completed", "Concluído"),
    ("failed", "Falhou"),
)


# =============================================================================
# FILE/CONTACT TYPES
# =============================================================================

DOCUMENT_FILE_TYPES = (
    ("L", "Laudo Escaneado"),
    ("O", "Outro"),
)

CONTACT_TYPES = (
    ("E", "Email"),
    ("P", "Telefone"),
)
