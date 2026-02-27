# Celery tasks
from celery import shared_task
from django.core.cache import cache
from scraper_multi import MultiSourceScraper
from .models import NewsArticle

@shared_task
def fetch_news_task(days=7, selected_sources=None, clear_existing=True):
    """Celery task: Haberleri çek ve kaydet"""
    try:
        # Önce mevcut haberleri temizle (isteğe bağlı)
        if clear_existing:
            NewsArticle.objects.all().delete()
            cache.delete('cybersecurity_news')
            print(f"[TASK] Mevcut haberler temizlendi")
        
        scraper = MultiSourceScraper()
        articles = scraper.fetch_all_news(days=days, selected_sources=selected_sources)
        
        if articles:
            processed = scraper.process_news(articles)
            
            # Database'e kaydet
            saved_count = 0
            for article in processed:
                # Aynı link varsa güncelle, yoksa oluştur
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
            
            # Cache'i güncelle
            cached_data = []
            for article in NewsArticle.objects.all().order_by('-date')[:100]:
                cached_data.append({
                    'id': article.id,
                    'source': article.source,
                    'original_title': article.original_title,
                    'turkish_title': article.turkish_title,
                    'original_description': article.original_description,
                    'turkish_description': article.turkish_description,
                    'turkish_summary': article.turkish_summary,
                    'link': article.link,
                    'date': article.date.strftime('%Y-%m-%d'),
                    'original_date': article.original_date,
                })
            
            cache.set('cybersecurity_news', cached_data, 3600)
            cache.set('last_update', datetime.now().isoformat(), 3600)
            
            return {
                'success': True,
                'count': saved_count,
                'message': f'{saved_count} haber başarıyla kaydedildi'
            }
        else:
            return {
                'success': False,
                'count': 0,
                'message': 'Haber bulunamadı'
            }
            
    except Exception as e:
        return {
            'success': False,
            'count': 0,
            'message': str(e)
        }

from datetime import datetime
