"""
Cybersecurity Haber Çekici - GUI Arayüz
Tkinter ile yapilmis kullanici arayuzu
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from scraper_light import CyberNewsScraperLight
import json
from datetime import datetime
import os
import glob


class CyberNewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cybersecurity Haber Cekici")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.news_data = []
        self.scraper = None
        
        self.setup_ui()
        self.load_saved_news()
    
    def setup_ui(self):
        # Baslik
        header = tk.Frame(self.root, bg='#2c3e50', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header, 
            text="Cybersecurity Haber Cekici", 
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Ana icerik alani
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sol panel - Kontroller
        left_panel = tk.Frame(main_frame, bg='#f0f0f0', width=280)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Kontrol butonlari
        control_frame = tk.LabelFrame(
            left_panel, 
            text="Kontroller", 
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Gun sayisi secimi
        tk.Label(
            control_frame, 
            text="Kac gunluk haber:",
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(0, 5))
        
        self.days_var = tk.StringVar(value="7")
        days_spinbox = ttk.Spinbox(
            control_frame, 
            from_=1, 
            to=30, 
            textvariable=self.days_var,
            width=10
        )
        days_spinbox.pack(anchor='w', pady=(0, 10))
        
        # Cek butonu
        self.fetch_btn = tk.Button(
            control_frame,
            text="Haberleri Cek",
            command=self.fetch_news,
            bg='#3498db',
            fg='white',
            font=('Arial', 11, 'bold'),
            height=2,
            cursor='hand2'
        )
        self.fetch_btn.pack(fill='x', pady=(0, 10))
        
        # Yenile butonu
        self.refresh_btn = tk.Button(
            control_frame,
            text="Kayitli Haberleri Yuke",
            command=self.load_saved_news,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10),
            cursor='hand2'
        )
        self.refresh_btn.pack(fill='x', pady=(0, 5))
        
        # Durum gostergesi
        self.status_frame = tk.LabelFrame(
            left_panel,
            text="Durum",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        self.status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Hazir",
            bg='#f0f0f0',
            font=('Arial', 9),
            wraplength=230
        )
        self.status_label.pack()
        
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=230
        )
        
        # Istatistikler
        self.stats_frame = tk.LabelFrame(
            left_panel,
            text="Istatistikler",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        self.stats_frame.pack(fill='x')
        
        self.total_label = tk.Label(
            self.stats_frame,
            text="Toplam Haber: 0",
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.total_label.pack(anchor='w')
        
        self.date_label = tk.Label(
            self.stats_frame,
            text="Son Guncelleme: -",
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.date_label.pack(anchor='w')
        
        # Sag panel - Haber listesi ve detay
        right_panel = tk.Frame(main_frame, bg='#f0f0f0')
        right_panel.pack(side='left', fill='both', expand=True)
        
        # Ust kisim - Haber listesi
        list_frame = tk.LabelFrame(
            right_panel,
            text="Haber Listesi",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        list_frame.pack(fill='both', expand=False, pady=(0, 10))
        
        # Treeview (tablo)
        columns = ('no', 'title', 'date')
        self.tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show='headings',
            height=8
        )
        
        self.tree.heading('no', text='No')
        self.tree.heading('title', text='Baslik')
        self.tree.heading('date', text='Tarih')
        
        self.tree.column('no', width=40, anchor='center')
        self.tree.column('title', width=600)
        self.tree.column('date', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Secim olayini bagla
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Alt kisim - Detaylar
        detail_frame = tk.LabelFrame(
            right_panel,
            text="Haber Detaylari",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        detail_frame.pack(fill='both', expand=True)
        
        # Baslik
        tk.Label(
            detail_frame,
            text="Baslik:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill='x', padx=5, pady=(5, 0))
        
        self.detail_title = tk.Label(
            detail_frame,
            text="Bir haber secin...",
            font=('Arial', 10),
            bg='#f0f0f0',
            anchor='w',
            wraplength=800
        )
        self.detail_title.pack(fill='x', padx=5, pady=(0, 5))
        
        # Link
        tk.Label(
            detail_frame,
            text="Link:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill='x', padx=5)
        
        self.detail_link = tk.Label(
            detail_frame,
            text="-",
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='blue',
            anchor='w',
            cursor='hand2'
        )
        self.detail_link.pack(fill='x', padx=5, pady=(0, 5))
        self.detail_link.bind('<Button-1>', self.open_link)
        
        # Ozet
        tk.Label(
            detail_frame,
            text="Ozet:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill='x', padx=5)
        
        self.detail_summary = scrolledtext.ScrolledText(
            detail_frame,
            wrap=tk.WORD,
            font=('Arial', 9),
            height=5,
            padx=5,
            pady=5
        )
        self.detail_summary.pack(fill='x', padx=5, pady=(0, 5))
        
        # Detayli aciklama
        tk.Label(
            detail_frame,
            text="Detayli Aciklama:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill='x', padx=5)
        
        self.detail_desc = scrolledtext.ScrolledText(
            detail_frame,
            wrap=tk.WORD,
            font=('Arial', 9),
            height=8,
            padx=5,
            pady=5
        )
        self.detail_desc.pack(fill='both', expand=True, padx=5, pady=(0, 5))
    
    def fetch_news(self):
        self.fetch_btn.config(state='disabled')
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start()
        self.status_label.config(text="Haberler cekiliyor...")
        
        thread = threading.Thread(target=self._fetch_thread)
        thread.daemon = True
        thread.start()
    
    def _fetch_thread(self):
        try:
            days = int(self.days_var.get())
            scraper = CyberNewsScraperLight()
            articles = scraper.fetch_news(days=days)
            
            if articles:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"{len(articles)} haber bulundu. Ceviriliyor..."
                ))
                
                processed = scraper.process_news(articles)
                scraper.save_to_json(processed)
                scraper.save_to_txt(processed)
                
                self.news_data = processed
                self.root.after(0, self.update_ui)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Basarili", 
                    f"{len(processed)} haber basariyla cekildi!"
                ))
            else:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Uyari", 
                    "Haber bulunamadi!"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Hata", 
                f"Bir hata olustu: {str(e)}"
            ))
        finally:
            self.root.after(0, self._reset_ui)
    
    def _reset_ui(self):
        self.fetch_btn.config(state='normal')
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Hazir")
    
    def load_saved_news(self):
        try:
            # En son json dosyasini bul
            json_files = glob.glob("cybersecurity_news_*.json")
            
            if json_files:
                # En yeniyi al
                latest_file = max(json_files, key=os.path.getctime)
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.news_data = json.load(f)
                
                self.update_ui()
                self.status_label.config(text=f"{len(self.news_data)} haber yuklendi")
            else:
                self.status_label.config(text="Kayitli haber bulunamadi")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yuklenirken hata: {str(e)}")
    
    def update_ui(self):
        # Treeview'i temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Yeni haberleri ekle
        for i, article in enumerate(self.news_data, 1):
            title = article['turkish_title'][:70] + "..." if len(article['turkish_title']) > 70 else article['turkish_title']
            self.tree.insert('', 'end', values=(
                i,
                title,
                article['date']
            ))
        
        # Istatistikleri guncelle
        self.total_label.config(text=f"Toplam Haber: {len(self.news_data)}")
        self.date_label.config(text=f"Son Guncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        index = int(item['values'][0]) - 1
        
        if 0 <= index < len(self.news_data):
            article = self.news_data[index]
            
            self.detail_title.config(text=article['turkish_title'])
            self.detail_link.config(text=article['link'])
            
            self.detail_summary.delete(1.0, tk.END)
            self.detail_summary.insert(1.0, article['turkish_summary'])
            
            self.detail_desc.delete(1.0, tk.END)
            self.detail_desc.insert(1.0, article['turkish_description'])
    
    def open_link(self, event):
        import webbrowser
        link = self.detail_link.cget("text")
        if link and link != "-":
            webbrowser.open(link)


if __name__ == "__main__":
    root = tk.Tk()
    app = CyberNewsGUI(root)
    root.mainloop()
