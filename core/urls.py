from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from core.views import restore_backup_view

urlpatterns = [
    path("admin/restore-backup/", restore_backup_view, name="restore_backup"),
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("authenticate/", include(("authenticate.urls", "authenticate"))),
    path("suppliers/", include("bidding_supplier.urls")),
    path("reports/", include("reports.urls")),
    path("structure/", include("organizational_structure.urls")),
    path("procurement/", include("bidding_procurement.urls")),
    path("fiscal/", include("fiscal.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
