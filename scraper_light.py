"""
Cybersecurity Haber Çekici (Hafif Versiyon)
The Hacker News'tan haftalık haberleri çeker, 
Türkçeye çevirir ve basit özetleme yapar.
"""

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json
from datetime import datetime, timedelta
import re


class CyberNewsScraperLight:
    def __init__(self):
        self.base_url = "https://thehackernews.com"
        self.translator = GoogleTranslator(source='auto', target='tr')
        print("Uygulama başlatıldı! (Hafif versiyon)")
    
    def fetch_news(self, days=7):
        """Son X günün haberlerini çeker"""
        print(f"Son {days} günün haberleri çekiliyor...")
        
        try:
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Hata: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        story_divs = soup.find_all('div', class_='body-post')
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for story in story_divs:
            try:
                title_tag = story.find('h2', class_='home-title')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                
                link_tag = story.find('a', class_='story-link')
                link = link_tag.get('href', '') if link_tag else ""
                
                date_tag = story.find('span', class_='h-datetime')
                date_str = ""
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    pub_date = self._parse_date(date_str)
                else:
                    pub_date = datetime.now()
                
                if pub_date >= cutoff_date:
                    desc_tag = story.find('div', class_='home-desc')
                    description = desc_tag.get_text(strip=True) if desc_tag else ""
                    
                    articles.append({
                        'title': title,
                        'description': description,
                        'link': link,
                        'date': pub_date.strftime('%Y-%m-%d'),
                        'original_date': date_str
                    })
                    
            except Exception as e:
                print(f"Haber işlenirken hata: {e}")
                continue
        
        print(f"{len(articles)} haber bulundu.")
        return articles
    
    def _parse_date(self, date_str):
        """Tarih stringini datetime objesine çevirir"""
        try:
            return datetime.strptime(date_str, '%B %d, %Y')
        except:
            try:
                return datetime.strptime(date_str, '%b %d, %Y')
            except:
                return datetime.now()
    
    def translate_text(self, text, dest='tr'):
        """Metni Türkçeye çevirir"""
        if not text or len(text.strip()) == 0:
            return ""
        
        try:
            if len(text) > 4500:
                text = text[:4500]
            return self.translator.translate(text)
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return text
    
    def simple_summarize(self, text, sentences=3):
        """Basit cümle bazlı özetleme"""
        if not text or len(text) < 200:
            return text
        
        # Cümleleri ayır
        sentences_list = re.split(r'(?<=[.!?])\s+', text)
        
        # İlk birkaç cümleyi al
        if len(sentences_list) <= sentences:
            return text
        
        summary = ' '.join(sentences_list[:sentences])
        return summary
    
    def process_news(self, articles):
        """Haberleri çevirir ve özetler"""
        processed = []
        
        for i, article in enumerate(articles):
            print(f"İşleniyor: {i+1}/{len(articles)} - {article['title'][:50]}...")
            
            translated_title = self.translate_text(article['title'])
            translated_desc = self.translate_text(article['description'])
            
            # Basit özetleme
            summary = self.simple_summarize(article['description'])
            translated_summary = self.translate_text(summary)
            
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
        """Haberleri JSON olarak kaydeder"""
        if not filename:
            filename = f"cybersecurity_news_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"Haberler {filename} dosyasına kaydedildi.")
    
    def save_to_txt(self, articles, filename=None):
        """Haberleri TXT olarak kaydeder"""
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
        """Ana çalıştırma fonksiyonu"""
        print("="*80)
        print("SİBER GÜVENLİK HABER ÇEKİCİ BAŞLATILIYOR (Hafif Versiyon)")
        print("="*80)
        
        articles = self.fetch_news(days=days)
        
        if not articles:
            print("Haber bulunamadı!")
            return
        
        processed = self.process_news(articles)
        self.save_to_json(processed)
        self.save_to_txt(processed)
        
        print("\n" + "="*80)
        print("İŞLEM TAMAMLANDI!")
        print(f"Toplam {len(processed)} haber işlendi.")
        print("="*80)


if __name__ == "__main__":
    scraper = CyberNewsScraperLight()
    scraper.run(days=7)
