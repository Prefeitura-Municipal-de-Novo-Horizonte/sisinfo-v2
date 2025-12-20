from django.urls import path
from fiscal.views import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceUpdateView,
    InvoiceDeleteView,
    invoice_add_items,
    invoice_mark_delivered,
    invoice_set_commitment,
    invoice_link_report,
    invoice_unlink_report,
    invoice_upload,
    invoice_process,
    CommitmentListView,
    CommitmentCreateView,
    CommitmentDetailView,
    CommitmentUpdateView,
    api_materials_by_supplier,
    DeliveryNoteListView,
    DeliveryNoteDetailView,
    delivery_create,
    delivery_generate_pdf,
    ocr_submit,
    ocr_status,
    ocr_cancel,
    ocr_callback,
)

app_name = 'fiscal'

urlpatterns = [
    # Notas Fiscais
    path('notas/', InvoiceListView.as_view(), name='invoices'),
    path('notas/upload/', invoice_upload, name='invoice_upload'),
    path('notas/processar/', invoice_process, name='invoice_process'),
    path('notas/nova/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('notas/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('notas/<int:pk>/editar/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('notas/<int:pk>/excluir/', InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('notas/<int:pk>/itens/', invoice_add_items, name='invoice_items'),
    path('notas/<int:pk>/entregar/', invoice_mark_delivered, name='invoice_deliver'),
    path('notas/<int:pk>/empenho/', invoice_set_commitment, name='invoice_set_commitment'),
    path('notas/<int:pk>/vincular-laudo/<int:report_pk>/', invoice_link_report, name='invoice_link_report'),
    path('notas/<int:pk>/desvincular-laudo/', invoice_unlink_report, name='invoice_unlink_report'),
    
    # OCR Assíncrono (polling)
    path('ocr/submit/', ocr_submit, name='ocr_submit'),
    path('ocr/status/<uuid:job_id>/', ocr_status, name='ocr_status'),
    path('ocr/cancel/<uuid:job_id>/', ocr_cancel, name='ocr_cancel'),
    path('ocr/callback/<uuid:job_id>/', ocr_callback, name='ocr_callback'),
    
    # Empenhos
    path('empenhos/', CommitmentListView.as_view(), name='commitments'),
    path('empenhos/novo/', CommitmentCreateView.as_view(), name='commitment_create'),
    path('empenhos/<int:pk>/', CommitmentDetailView.as_view(), name='commitment_detail'),
    path('empenhos/<int:pk>/editar/', CommitmentUpdateView.as_view(), name='commitment_update'),
    
    # Fichas de Entrega
    path('entregas/', DeliveryNoteListView.as_view(), name='deliveries'),
    path('entregas/nova/<int:invoice_pk>/', delivery_create, name='delivery_create'),
    path('entregas/<int:pk>/', DeliveryNoteDetailView.as_view(), name='delivery_detail'),
    path('entregas/<int:pk>/pdf/', delivery_generate_pdf, name='delivery_pdf'),
    
    # APIs
    path('api/materials-by-supplier/', api_materials_by_supplier, name='api_materials_by_supplier'),
]

