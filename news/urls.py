from django.urls import path
from . import views

urlpatterns = [
    # Haber API endpoints
    path('api/news/', views.get_news, name='get_news'),
    path('api/fetch/', views.fetch_news, name='fetch_news'),
    path('api/clear/', views.clear_cache, name='clear_cache'),
    path('api/stats/', views.get_stats, name='get_stats'),
    path('api/export/', views.export_news, name='export_news'),
    
    # CVE API endpoints
    path('api/cve/', views.get_cves, name='get_cves'),
    path('api/cve/fetch/', views.fetch_cves, name='fetch_cves'),
    path('api/cve/clear/', views.clear_cve_cache, name='clear_cve_cache'),
    path('api/cve/stats/', views.get_cve_stats, name='get_cve_stats'),
    path('api/cve/export/', views.export_cves, name='export_cves'),

    # Kubernetes API endpoints
    path('api/k8s/', views.get_k8s, name='get_k8s'),
    path('api/k8s/fetch/', views.fetch_k8s, name='fetch_k8s'),
    path('api/k8s/clear/', views.clear_k8s_cache, name='clear_k8s_cache'),
    path('api/k8s/stats/', views.get_k8s_stats, name='get_k8s_stats'),
    path('api/k8s/export/', views.export_k8s, name='export_k8s'),

    # SRE API endpoints
    path('api/sre/', views.get_sre, name='get_sre'),
    path('api/sre/fetch/', views.fetch_sre, name='fetch_sre'),
    path('api/sre/clear/', views.clear_sre_cache, name='clear_sre_cache'),
    path('api/sre/stats/', views.get_sre_stats, name='get_sre_stats'),
    path('api/sre/export/', views.export_sre, name='export_sre'),
]
