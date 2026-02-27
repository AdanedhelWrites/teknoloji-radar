from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from datetime import datetime
from .models import NewsArticle, CVEEntry, KubernetesEntry, SREEntry, DevToolsEntry
from .serializers import (
    NewsArticleSerializer, CVEEntrySerializer, KubernetesEntrySerializer,
    SREEntrySerializer, DevToolsEntrySerializer,
    FetchNewsRequestSerializer, FetchCVERequestSerializer, FetchK8sRequestSerializer,
    FetchSRERequestSerializer, FetchDevToolsRequestSerializer,
    StatsSerializer
)
from scraper_multi import MultiSourceScraper
from .cve_scraper import MultiCVEScraper
from .k8s_scraper import MultiK8sScraper
from .sre_scraper import MultiSREScraper
from .devtools_scraper import MultiDevToolsScraper


@api_view(['GET'])
@permission_classes([AllowAny])
def get_news(request):
    """Haberleri getir (cache veya database'den)"""
    # Once cache'den dene
    cached_news = cache.get('cybersecurity_news')
    if cached_news:
        return Response({
            'success': True,
            'data': cached_news,
            'cached': True,
            'count': len(cached_news)
        })
    
    # Cache yoksa database'den cek
    articles = NewsArticle.objects.all().order_by('-date')[:100]
    serializer = NewsArticleSerializer(articles, many=True)
    data = serializer.data
    
    # Cache'e kaydet
    if data:
        cache.set('cybersecurity_news', data, 3600)
    
    return Response({
        'success': True,
        'data': data,
        'cached': False,
        'count': len(data)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_news(request):
    """Yeni haberleri cek - SENKRON"""
    serializer = FetchNewsRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Gecersiz istek',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        days = serializer.validated_data.get('days', 7)
        selected_sources = serializer.validated_data.get('sources', None)
        
        # Senkron olarak cek (Celery yok)
        scraper = MultiSourceScraper()
        articles = scraper.fetch_all_news(days=days, selected_sources=selected_sources)
        
        if articles:
            processed = scraper.process_news(articles)
            
            # Database'e kaydet
            saved_count = 0
            for article in processed:
                obj, created = NewsArticle.objects.update_or_create(
                    link=article['link'],
                    defaults={
                        'source': article['source'],
                        'original_title': article['original_title'],
                        'turkish_title': article['turkish_title'],
                        'original_description': article.get('turkish_description', ''),
                        'turkish_description': article.get('turkish_description', ''),
                        'turkish_summary': article.get('turkish_summary', ''),
                        'date': article['date'],
                        'original_date': article.get('original_date', ''),
                    }
                )
                saved_count += 1
            
            # Cache'i guncelle
            all_articles = NewsArticle.objects.all().order_by('-date')[:100]
            cached_data = NewsArticleSerializer(all_articles, many=True).data
            
            cache.set('cybersecurity_news', cached_data, 3600)
            cache.set('last_update', datetime.now().isoformat(), 3600)
            
            return Response({
                'success': True,
                'message': f'{saved_count} haber basariyla cekildi ve kaydedildi',
                'count': saved_count,
                'data': cached_data
            })
        else:
            return Response({
                'success': False,
                'message': 'Haber bulunamadi',
                'count': 0,
                'data': []
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_cache(request):
    """Cache ve database'i temizle"""
    try:
        # Cache temizle
        cache.delete('cybersecurity_news')
        cache.delete('last_update')
        
        # Database temizle
        NewsArticle.objects.all().delete()
        
        return Response({
            'success': True,
            'message': 'Cache ve veritabani temizlendi'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stats(request):
    """Istatistikleri getir"""
    total = NewsArticle.objects.count()
    
    # Kaynaklara gore dagilim
    from django.db.models import Count
    source_stats = NewsArticle.objects.values('source').annotate(
        count=Count('source')
    ).order_by('-count')
    
    by_source = {item['source']: item['count'] for item in source_stats}
    
    # Son guncelleme
    last_article = NewsArticle.objects.order_by('-created_at').first()
    last_update = last_article.created_at.isoformat() if last_article else None
    
    return Response({
        'success': True,
        'total': total,
        'by_source': by_source,
        'last_update': last_update,
        'cached': cache.get('cybersecurity_news') is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_news(request):
    """Haberleri JSON olarak disari aktar"""
    articles = NewsArticle.objects.all().order_by('-date')
    serializer = NewsArticleSerializer(articles, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'exported_at': datetime.now().isoformat(),
        'count': len(serializer.data)
    })


# ==================== CVE ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cves(request):
    """CVE'leri getir (cache veya database'den)"""
    # Once cache'den dene
    cached_cves = cache.get('cve_entries')
    if cached_cves:
        return Response({
            'success': True,
            'data': cached_cves,
            'cached': True,
            'count': len(cached_cves)
        })
    
    # Cache yoksa database'den cek
    cves = CVEEntry.objects.all().order_by('-published_date')[:100]
    serializer = CVEEntrySerializer(cves, many=True)
    data = serializer.data
    
    # Cache'e kaydet
    if data:
        cache.set('cve_entries', data, 3600)
    
    return Response({
        'success': True,
        'data': data,
        'cached': False,
        'count': len(data)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_cves(request):
    """Yeni CVE'leri cek - SENKRON"""
    serializer = FetchCVERequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Gecersiz istek',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        days = serializer.validated_data.get('days', 30)
        selected_sources = serializer.validated_data.get('sources', None)
        
        # CVE'leri cek
        scraper = MultiCVEScraper()
        cves = scraper.fetch_all_cves(days=days, selected_sources=selected_sources)
        
        if cves:
            processed = scraper.process_cves(cves)
            
            # Database'e kaydet
            saved_count = 0
            for cve in processed:
                obj, created = CVEEntry.objects.update_or_create(
                    cve_id=cve['cve_id'],
                    defaults={
                        'source': cve['source'],
                        'original_title': cve['original_title'],
                        'turkish_title': cve.get('turkish_title', ''),
                        'original_description': cve['original_description'],
                        'turkish_description': cve.get('turkish_description', ''),
                        'severity': cve.get('severity', 'Bilinmiyor'),
                        'cvss_score': cve.get('cvss_score'),
                        'published_date': cve['published_date'],
                        'modified_date': cve.get('modified_date'),
                        'link': cve['link'],
                        'cwe_ids': cve.get('cwe_ids', []),
                        'references': cve.get('references', []),
                        'affected_products': cve.get('affected_products', ''),
                    }
                )
                saved_count += 1
            
            # Cache'i guncelle
            all_cves = CVEEntry.objects.all().order_by('-published_date')[:100]
            cached_data = CVEEntrySerializer(all_cves, many=True).data
            
            cache.set('cve_entries', cached_data, 3600)
            cache.set('cve_last_update', datetime.now().isoformat(), 3600)
            
            return Response({
                'success': True,
                'message': f'{saved_count} CVE basariyla cekildi ve kaydedildi',
                'count': saved_count,
                'data': cached_data
            })
        else:
            return Response({
                'success': False,
                'message': 'CVE bulunamadi',
                'count': 0,
                'data': []
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_cve_cache(request):
    """CVE cache ve database'i temizle"""
    try:
        # Cache temizle
        cache.delete('cve_entries')
        cache.delete('cve_last_update')
        
        # Database temizle
        CVEEntry.objects.all().delete()
        
        return Response({
            'success': True,
            'message': 'CVE cache ve veritabani temizlendi'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cve_stats(request):
    """CVE istatistiklerini getir"""
    total = CVEEntry.objects.count()
    
    # Kaynaklara gore dagilim
    from django.db.models import Count
    source_stats = CVEEntry.objects.values('source').annotate(
        count=Count('source')
    ).order_by('-count')
    
    by_source = {item['source']: item['count'] for item in source_stats}
    
    # Siddet seviyesine gore dagilim
    severity_stats = CVEEntry.objects.values('severity').annotate(
        count=Count('severity')
    ).order_by('-count')
    
    by_severity = {item['severity']: item['count'] for item in severity_stats}
    
    # Son guncelleme
    last_cve = CVEEntry.objects.order_by('-created_at').first()
    last_update = last_cve.created_at.isoformat() if last_cve else None
    
    return Response({
        'success': True,
        'total': total,
        'by_source': by_source,
        'by_severity': by_severity,
        'last_update': last_update,
        'cached': cache.get('cve_entries') is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_cves(request):
    """CVE'leri JSON olarak disari aktar"""
    cves = CVEEntry.objects.all().order_by('-published_date')
    serializer = CVEEntrySerializer(cves, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'exported_at': datetime.now().isoformat(),
        'count': len(serializer.data)
    })


# ==================== KUBERNETES ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_k8s(request):
    """Kubernetes haberlerini getir (cache veya database'den)"""
    cached_k8s = cache.get('k8s_entries')
    if cached_k8s:
        return Response({
            'success': True,
            'data': cached_k8s,
            'cached': True,
            'count': len(cached_k8s)
        })

    entries = KubernetesEntry.objects.all().order_by('-published_date')[:100]
    serializer = KubernetesEntrySerializer(entries, many=True)
    data = serializer.data

    if data:
        cache.set('k8s_entries', data, 3600)

    return Response({
        'success': True,
        'data': data,
        'cached': False,
        'count': len(data)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_k8s(request):
    """Yeni Kubernetes haberlerini cek - SENKRON"""
    serializer = FetchK8sRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Gecersiz istek',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        days = serializer.validated_data.get('days', 30)
        selected_sources = serializer.validated_data.get('sources', None)

        scraper = MultiK8sScraper()
        entries = scraper.fetch_all(days=days, selected_sources=selected_sources)

        if entries:
            processed = scraper.process_entries(entries)

            saved_count = 0
            for entry in processed:
                obj, created = KubernetesEntry.objects.update_or_create(
                    link=entry['link'],
                    defaults={
                        'source': entry['source'],
                        'original_title': entry['original_title'],
                        'turkish_title': entry.get('turkish_title', ''),
                        'original_description': entry['original_description'],
                        'turkish_description': entry.get('turkish_description', ''),
                        'published_date': entry['published_date'],
                        'category': entry.get('category', 'blog'),
                        'version': entry.get('version', ''),
                    }
                )
                saved_count += 1

            all_entries = KubernetesEntry.objects.all().order_by('-published_date')[:100]
            cached_data = KubernetesEntrySerializer(all_entries, many=True).data

            cache.set('k8s_entries', cached_data, 3600)
            cache.set('k8s_last_update', datetime.now().isoformat(), 3600)

            return Response({
                'success': True,
                'message': f'{saved_count} Kubernetes haberi basariyla cekildi ve kaydedildi',
                'count': saved_count,
                'data': cached_data
            })
        else:
            return Response({
                'success': False,
                'message': 'Kubernetes haberi bulunamadi',
                'count': 0,
                'data': []
            })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_k8s_cache(request):
    """Kubernetes cache ve database'i temizle"""
    try:
        cache.delete('k8s_entries')
        cache.delete('k8s_last_update')

        KubernetesEntry.objects.all().delete()

        return Response({
            'success': True,
            'message': 'Kubernetes cache ve veritabani temizlendi'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_k8s_stats(request):
    """Kubernetes istatistiklerini getir"""
    total = KubernetesEntry.objects.count()

    from django.db.models import Count
    source_stats = KubernetesEntry.objects.values('source').annotate(
        count=Count('source')
    ).order_by('-count')

    by_source = {item['source']: item['count'] for item in source_stats}

    category_stats = KubernetesEntry.objects.values('category').annotate(
        count=Count('category')
    ).order_by('-count')

    by_category = {item['category']: item['count'] for item in category_stats}

    last_entry = KubernetesEntry.objects.order_by('-created_at').first()
    last_update = last_entry.created_at.isoformat() if last_entry else None

    return Response({
        'success': True,
        'total': total,
        'by_source': by_source,
        'by_category': by_category,
        'last_update': last_update,
        'cached': cache.get('k8s_entries') is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_k8s(request):
    """Kubernetes haberlerini JSON olarak disari aktar"""
    entries = KubernetesEntry.objects.all().order_by('-published_date')
    serializer = KubernetesEntrySerializer(entries, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'exported_at': datetime.now().isoformat(),
        'count': len(serializer.data)
    })


# ==================== SRE ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sre(request):
    """SRE haberlerini getir (cache veya database'den)"""
    cached_sre = cache.get('sre_entries')
    if cached_sre:
        return Response({
            'success': True,
            'data': cached_sre,
            'cached': True,
            'count': len(cached_sre)
        })

    entries = SREEntry.objects.all().order_by('-published_date')[:100]
    serializer = SREEntrySerializer(entries, many=True)
    data = serializer.data

    if data:
        cache.set('sre_entries', data, 3600)

    return Response({
        'success': True,
        'data': data,
        'cached': False,
        'count': len(data)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_sre(request):
    """Yeni SRE haberlerini cek - SENKRON"""
    serializer = FetchSRERequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Gecersiz istek',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        days = serializer.validated_data.get('days', 30)
        selected_sources = serializer.validated_data.get('sources', None)

        scraper = MultiSREScraper()
        entries = scraper.fetch_all(days=days, selected_sources=selected_sources)

        if entries:
            processed = scraper.process_entries(entries)

            saved_count = 0
            for entry in processed:
                obj, created = SREEntry.objects.update_or_create(
                    link=entry['link'],
                    defaults={
                        'source': entry['source'],
                        'original_title': entry['original_title'],
                        'turkish_title': entry.get('turkish_title', ''),
                        'original_description': entry['original_description'],
                        'turkish_description': entry.get('turkish_description', ''),
                        'published_date': entry['published_date'],
                    }
                )
                saved_count += 1

            all_entries = SREEntry.objects.all().order_by('-published_date')[:100]
            cached_data = SREEntrySerializer(all_entries, many=True).data

            cache.set('sre_entries', cached_data, 3600)
            cache.set('sre_last_update', datetime.now().isoformat(), 3600)

            return Response({
                'success': True,
                'message': f'{saved_count} SRE haberi basariyla cekildi ve kaydedildi',
                'count': saved_count,
                'data': cached_data
            })
        else:
            return Response({
                'success': False,
                'message': 'SRE haberi bulunamadi',
                'count': 0,
                'data': []
            })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_sre_cache(request):
    """SRE cache ve database'i temizle"""
    try:
        cache.delete('sre_entries')
        cache.delete('sre_last_update')

        SREEntry.objects.all().delete()

        return Response({
            'success': True,
            'message': 'SRE cache ve veritabani temizlendi'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sre_stats(request):
    """SRE istatistiklerini getir"""
    total = SREEntry.objects.count()

    from django.db.models import Count
    source_stats = SREEntry.objects.values('source').annotate(
        count=Count('source')
    ).order_by('-count')

    by_source = {item['source']: item['count'] for item in source_stats}

    last_entry = SREEntry.objects.order_by('-created_at').first()
    last_update = last_entry.created_at.isoformat() if last_entry else None

    return Response({
        'success': True,
        'total': total,
        'by_source': by_source,
        'last_update': last_update,
        'cached': cache.get('sre_entries') is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_sre(request):
    """SRE haberlerini JSON olarak disari aktar"""
    entries = SREEntry.objects.all().order_by('-published_date')
    serializer = SREEntrySerializer(entries, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'exported_at': datetime.now().isoformat(),
        'count': len(serializer.data)
    })


# ==================== DEVTOOLS ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_devtools(request):
    """DevTools guncellemelerini getir (cache veya database'den)"""
    cached_devtools = cache.get('devtools_entries')
    if cached_devtools:
        return Response({
            'success': True,
            'data': cached_devtools,
            'cached': True,
            'count': len(cached_devtools)
        })

    entries = DevToolsEntry.objects.all().order_by('-published_date')[:100]
    serializer = DevToolsEntrySerializer(entries, many=True)
    data = serializer.data

    if data:
        cache.set('devtools_entries', data, 3600)

    return Response({
        'success': True,
        'data': data,
        'cached': False,
        'count': len(data)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def fetch_devtools(request):
    """Yeni DevTools guncellemelerini cek - SENKRON"""
    serializer = FetchDevToolsRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': 'Gecersiz istek',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        days = serializer.validated_data.get('days', 60)
        selected_sources = serializer.validated_data.get('sources', None)

        scraper = MultiDevToolsScraper()
        entries = scraper.fetch_all(days=days, selected_sources=selected_sources)

        if entries:
            processed = scraper.process_entries(entries)

            saved_count = 0
            for entry in processed:
                obj, created = DevToolsEntry.objects.update_or_create(
                    link=entry['link'],
                    defaults={
                        'source': entry['source'],
                        'original_title': entry['original_title'],
                        'turkish_title': entry.get('turkish_title', ''),
                        'original_description': entry['original_description'],
                        'turkish_description': entry.get('turkish_description', ''),
                        'published_date': entry['published_date'],
                        'version': entry.get('version', ''),
                        'entry_type': entry.get('entry_type', 'release'),
                    }
                )
                saved_count += 1

            all_entries = DevToolsEntry.objects.all().order_by('-published_date')[:100]
            cached_data = DevToolsEntrySerializer(all_entries, many=True).data

            cache.set('devtools_entries', cached_data, 3600)
            cache.set('devtools_last_update', datetime.now().isoformat(), 3600)

            return Response({
                'success': True,
                'message': f'{saved_count} DevTools guncellemesi basariyla cekildi ve kaydedildi',
                'count': saved_count,
                'data': cached_data
            })
        else:
            return Response({
                'success': False,
                'message': 'DevTools guncellemesi bulunamadi',
                'count': 0,
                'data': []
            })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'count': 0,
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_devtools_cache(request):
    """DevTools cache ve database'i temizle"""
    try:
        cache.delete('devtools_entries')
        cache.delete('devtools_last_update')

        DevToolsEntry.objects.all().delete()

        return Response({
            'success': True,
            'message': 'DevTools cache ve veritabani temizlendi'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_devtools_stats(request):
    """DevTools istatistiklerini getir"""
    total = DevToolsEntry.objects.count()

    from django.db.models import Count
    source_stats = DevToolsEntry.objects.values('source').annotate(
        count=Count('source')
    ).order_by('-count')

    by_source = {item['source']: item['count'] for item in source_stats}

    type_stats = DevToolsEntry.objects.values('entry_type').annotate(
        count=Count('entry_type')
    ).order_by('-count')

    by_type = {item['entry_type']: item['count'] for item in type_stats}

    last_entry = DevToolsEntry.objects.order_by('-created_at').first()
    last_update = last_entry.created_at.isoformat() if last_entry else None

    return Response({
        'success': True,
        'total': total,
        'by_source': by_source,
        'by_type': by_type,
        'last_update': last_update,
        'cached': cache.get('devtools_entries') is not None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_devtools(request):
    """DevTools guncellemelerini JSON olarak disari aktar"""
    entries = DevToolsEntry.objects.all().order_by('-published_date')
    serializer = DevToolsEntrySerializer(entries, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'exported_at': datetime.now().isoformat(),
        'count': len(serializer.data)
    })
