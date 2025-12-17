from django.urls import path

from reports.views import (
    ReportDetailView,
    ReportListView,
    create_sector_api,
    generate_pdf_report,
    material_report_delete,
    report_register,
    report_update,
)

from reports.views_invoice import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceUpdateView,
    InvoiceDeleteView,
    invoice_add_items,
    invoice_mark_delivered,
    invoice_upload,
    invoice_process,
    CommitmentListView,
    CommitmentCreateView,
    CommitmentDetailView,
    CommitmentUpdateView,
    api_materials_by_supplier,
)

from reports.views_delivery import (
    DeliveryNoteListView,
    DeliveryNoteDetailView,
    delivery_create,
    delivery_generate_pdf,
)

app_name = 'reports'

urlpatterns = [
    # Laudos
    path('', ReportListView.as_view(), name='reports'),
    path('new_register_report/', report_register, name='register_report'),
    path('report/<slug:slug>', ReportDetailView.as_view(), name='report_view'),
    path('report/<slug:slug>/update', report_update, name='report_update'),
    path('report/<slug:report_slug>/material/<int:pk>/delete',
         material_report_delete, name="material_report_delete"),
    path('report/<slug:slug>/download-pdf', generate_pdf_report, name='generate_pdf'),
    path('api/create-sector/', create_sector_api, name='create_sector_api'),
    
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
