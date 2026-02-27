from django.contrib import admin
from .models import NewsArticle, CVEEntry, KubernetesEntry, SREEntry

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('turkish_title', 'source', 'date', 'created_at')
    list_filter = ('source', 'date', 'created_at')
    search_fields = ('turkish_title', 'original_title', 'turkish_description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'


@admin.register(CVEEntry)
class CVEEntryAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'source', 'severity', 'cvss_score', 'published_date', 'created_at')
    list_filter = ('source', 'severity', 'published_date', 'created_at')
    search_fields = ('cve_id', 'turkish_title', 'original_title', 'turkish_description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'published_date'


@admin.register(KubernetesEntry)
class KubernetesEntryAdmin(admin.ModelAdmin):
    list_display = ('turkish_title', 'source', 'category', 'version', 'published_date', 'created_at')
    list_filter = ('source', 'category', 'published_date', 'created_at')
    search_fields = ('turkish_title', 'original_title', 'turkish_description', 'version')
    readonly_fields = ('created_at',)
    date_hierarchy = 'published_date'


@admin.register(SREEntry)
class SREEntryAdmin(admin.ModelAdmin):
    list_display = ('turkish_title', 'source', 'published_date', 'created_at')
    list_filter = ('source', 'published_date', 'created_at')
    search_fields = ('turkish_title', 'original_title', 'turkish_description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'published_date'
