from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apis.urls")),
]

admin.site.index_title = "Epic Events"
admin.site.site_header = "Epic Events Admin"
admin.site.site_title = "Site d'administration de Epic Events"
