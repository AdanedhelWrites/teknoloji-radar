"""
Cybersecurity Haber Çekici
The Hacker News'tan haftalık haberleri çeker, 
Türkçeye çevirir ve özetler.
"""

import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from transformers import pipeline
import json
from datetime import datetime, timedelta
import re


class CyberNewsScraper:
    def __init__(self):
        self.base_url = "https://thehackernews.com"
        self.translator = Translator()
        # Özetleme modeli
        print("Özetleme modeli yükleniyor...")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        print("Model yüklendi!")
    
    def fetch_news(self, days=7):
        """
        Son X günün haberlerini çeker
        """
        print(f"Son {days} günün haberleri çekiliyor...")
        
        try:
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Hata: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Haber kartlarını bul
        story_divs = soup.find_all('div', class_='body-post')
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for story in story_divs:
            try:
                # Başlık
                title_tag = story.find('h2', class_='home-title')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                
                # Link
                link_tag = story.find('a', class_='story-link')
                if link_tag:
                    link = link_tag.get('href', '')
                else:
                    link = ""
                
                # Tarih
                date_tag = story.find('span', class_='h-datetime')
                date_str = ""
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    pub_date = self._parse_date(date_str)
                else:
                    pub_date = datetime.now()
                
                # Sadece belirlenen tarih aralığındaki haberler
                if pub_date >= cutoff_date:
                    # Özet
                    desc_tag = story.find('div', class_='home-desc')
                    description = desc_tag.get_text(strip=True) if desc_tag else ""
                    
                    articles.append({
                        'title': title,
                        'description': description,
                        'link': link,
                        'date': pub_date.strftime('%Y-%m-%d'),
                        'original_date': date_str if date_tag else ""
                    })
                    
            except Exception as e:
                print(f"Haber işlenirken hata: {e}")
                continue
        
        print(f"{len(articles)} haber bulundu.")
        return articles
    
    def _parse_date(self, date_str):
        """
        Tarih stringini datetime objesine çevirir
        """
        try:
            # Format: "January 05, 2025"
            return datetime.strptime(date_str, '%B %d, %Y')
        except:
            try:
                return datetime.strptime(date_str, '%b %d, %Y')
            except:
                return datetime.now()
    
    def translate_text(self, text, dest='tr'):
        """
        Metni Türkçeye çevirir
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        try:
            # Google Translate API limitleri için metni böl
            if len(text) > 4500:
                text = text[:4500]
            
            result = self.translator.translate(text, dest=dest)
            return result.text
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return text
    
    def summarize_text(self, text, max_length=150, min_length=40):
        """
        Metni özetler
        """
        if not text or len(text.strip()) < 100:
            return text
        
        try:
            # Model için metni temizle ve kısalt
            text = text.replace('\n', ' ').strip()
            if len(text) > 1024:
                text = text[:1024]
            
            summary = self.summarizer(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Özetleme hatası: {e}")
            return text[:200] + "..."
    
    def process_news(self, articles):
        """
        Haberleri çevirir ve özetler
        """
        processed = []
        
        for i, article in enumerate(articles):
            print(f"İşleniyor: {i+1}/{len(articles)} - {article['title'][:50]}...")
            
            # Başlığı çevir
            translated_title = self.translate_text(article['title'])
            
            # Açıklamayı çevir
            translated_desc = self.translate_text(article['description'])
            
            # Açıklamayı özetle (isteğe bağlı)
            summarized = self.summarize_text(article['description'])
            translated_summary = self.translate_text(summarized)
            
            processed.append({
                'original_title': article['title'],
                'turkish_title': translated_title,
                'turkish_description': translated_desc,
                'turkish_summary': translated_summary,
                'link': article['link'],
                'date': article['date'],
                'original_date': article['original_date']
            })
        
        return processed
    
    def save_to_json(self, articles, filename=None):
        """
        Haberleri JSON olarak kaydeder
        """
        if not filename:
            filename = f"cybersecurity_news_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"Haberler {filename} dosyasına kaydedildi.")
    
    def save_to_txt(self, articles, filename=None):
        """
        Haberleri TXT olarak kaydeder (okunabilir format)
        """
        if not filename:
            filename = f"cybersecurity_news_{datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("HAFTALIK SİBER GÜVENLİK HABERLERİ\n")
            f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*80 + "\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"{i}. HABER\n")
                f.write("-"*80 + "\n")
                f.write(f"Başlık: {article['turkish_title']}\n")
                f.write(f"Tarih: {article['original_date']}\n")
                f.write(f"Link: {article['link']}\n\n")
                f.write(f"ÖZET:\n{article['turkish_summary']}\n\n")
                f.write(f"DETAYLI AÇIKLAMA:\n{article['turkish_description']}\n\n")
                f.write("="*80 + "\n\n")
        
        print(f"Haberler {filename} dosyasına kaydedildi.")
    
    def run(self, days=7):
        """
        Ana çalıştırma fonksiyonu
        """
        print("="*80)
        print("SİBER GÜVENLİK HABER ÇEKİCİ BAŞLATILIYOR")
        print("="*80)
        
        # Haberleri çek
        articles = self.fetch_news(days=days)
        
        if not articles:
            print("Haber bulunamadı!")
            return
        
        # Haberleri işle
        processed = self.process_news(articles)
        
        # Kaydet
        self.save_to_json(processed)
        self.save_to_txt(processed)
        
        print("\n" + "="*80)
        print("İŞLEM TAMAMLANDI!")
        print(f"Toplam {len(processed)} haber işlendi.")
        print("="*80)


if __name__ == "__main__":
    scraper = CyberNewsScraper()
    scraper.run(days=7)
