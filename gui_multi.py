"""
Cybersecurity Haber Cekici - Gelistirilmis GUI
Coklu kaynak destegi ve ozellestirilebilir gun sayisi
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from scraper_multi import MultiSourceScraper
import json
from datetime import datetime
import os
import glob


class CyberNewsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cybersecurity Haber Cekici - Multi-Source")
        self.root.geometry("1400x850")
        self.root.configure(bg='#f0f0f0')
        
        self.news_data = []
        self.scraper = MultiSourceScraper()
        
        self.setup_ui()
        self.load_saved_news()
    
    def setup_ui(self):
        # Baslik
        header = tk.Frame(self.root, bg='#2c3e50', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header, 
            text="Cybersecurity Haber Cekici - Multi Source", 
            font=('Arial', 22, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=18)
        
        # Ana icerik alani
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Sol panel - Kontroller
        left_panel = tk.Frame(main_frame, bg='#f0f0f0', width=320)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # Kaynaklar bolumu
        sources_frame = tk.LabelFrame(
            left_panel,
            text="Haber Kaynaklari",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        sources_frame.pack(fill='x', pady=(0, 10))
        
        self.source_vars = {}
        sources = [
            ("The Hacker News", True),
            ("Bleeping Computer", True),
            ("SecurityWeek", True),
            ("Dark Reading", True),
            ("Krebs on Security", True)
        ]
        
        for source, default in sources:
            var = tk.BooleanVar(value=default)
            self.source_vars[source] = var
            cb = tk.Checkbutton(
                sources_frame,
                text=source,
                variable=var,
                bg='#f0f0f0',
                font=('Arial', 10),
                anchor='w'
            )
            cb.pack(fill='x', pady=2)
        
        # Ayarlar bolumu
        settings_frame = tk.LabelFrame(
            left_panel,
            text="Ayarlar",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        settings_frame.pack(fill='x', pady=(0, 10))
        
        # Gun sayisi
        tk.Label(
            settings_frame,
            text="Kac gunluk haber cekilsin?",
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        self.days_var = tk.IntVar(value=7)
        days_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        days_frame.pack(fill='x', pady=(0, 10))
        
        days_scale = tk.Scale(
            days_frame,
            from_=1,
            to=30,
            orient='horizontal',
            variable=self.days_var,
            bg='#f0f0f0',
            length=200
        )
        days_scale.pack(side='left')
        
        days_entry = tk.Entry(
            days_frame,
            textvariable=self.days_var,
            width=5,
            font=('Arial', 11, 'bold'),
            justify='center'
        )
        days_entry.pack(side='left', padx=(10, 0))
        
        # Butonlar
        buttons_frame = tk.LabelFrame(
            left_panel,
            text="Kontroller",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        self.fetch_btn = tk.Button(
            buttons_frame,
            text="Tum Kaynaklardan Cek",
            command=self.fetch_news,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            cursor='hand2'
        )
        self.fetch_btn.pack(fill='x', pady=(0, 10))
        
        self.selected_fetch_btn = tk.Button(
            buttons_frame,
            text="Secili Kaynaklardan Cek",
            command=self.fetch_selected_news,
            bg='#2980b9',
            fg='white',
            font=('Arial', 11, 'bold'),
            height=2,
            cursor='hand2'
        )
        self.selected_fetch_btn.pack(fill='x', pady=(0, 10))
        
        self.refresh_btn = tk.Button(
            buttons_frame,
            text="Son Kayitlari Yuke",
            command=self.load_saved_news,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10),
            height=2,
            cursor='hand2'
        )
        self.refresh_btn.pack(fill='x', pady=(0, 5))
        
        # Durum
        self.status_frame = tk.LabelFrame(
            left_panel,
            text="Durum",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        self.status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Hazir",
            bg='#f0f0f0',
            font=('Arial', 10),
            wraplength=270
        )
        self.status_label.pack()
        
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=270
        )
        
        # Istatistikler
        self.stats_frame = tk.LabelFrame(
            left_panel,
            text="Istatistikler",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        self.stats_frame.pack(fill='x')
        
        self.total_label = tk.Label(
            self.stats_frame,
            text="Toplam Haber: 0",
            bg='#f0f0f0',
            font=('Arial', 10, 'bold')
        )
        self.total_label.pack(anchor='w', pady=(0, 5))
        
        self.by_source_label = tk.Label(
            self.stats_frame,
            text="Kaynaklara gore dagilim:\n-",
            bg='#f0f0f0',
            font=('Arial', 9),
            justify='left'
        )
        self.by_source_label.pack(anchor='w', pady=(0, 5))
        
        self.date_label = tk.Label(
            self.stats_frame,
            text="Son Guncelleme: -",
            bg='#f0f0f0',
            font=('Arial', 9)
        )
        self.date_label.pack(anchor='w')
        
        # Sag panel
        right_panel = tk.Frame(main_frame, bg='#f0f0f0')
        right_panel.pack(side='left', fill='both', expand=True)
        
        # Filtreleme
        filter_frame = tk.Frame(right_panel, bg='#f0f0f0')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            filter_frame,
            text="Kaynak Filtresi:",
            bg='#f0f0f0',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="Tumu")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["Tumu", "The Hacker News", "Bleeping Computer", 
                   "SecurityWeek", "Dark Reading", "Krebs on Security"],
            state='readonly',
            width=25,
            font=('Arial', 10)
        )
        self.filter_combo.pack(side='left')
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_news)
        
        # Haber listesi
        list_frame = tk.LabelFrame(
            right_panel,
            text="Haber Listesi",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        list_frame.pack(fill='both', expand=False, pady=(0, 10))
        
        columns = ('no', 'title', 'source', 'date')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        self.tree.heading('no', text='No')
        self.tree.heading('title', text='Baslik')
        self.tree.heading('source', text='Kaynak')
        self.tree.heading('date', text='Tarih')
        
        self.tree.column('no', width=50, anchor='center')
        self.tree.column('title', width=650)
        self.tree.column('source', width=150, anchor='center')
        self.tree.column('date', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Detay paneli
        detail_frame = tk.LabelFrame(
            right_panel,
            text="Haber Detaylari",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        )
        detail_frame.pack(fill='both', expand=True)
        
        # Kaynak bilgisi
        self.detail_source_frame = tk.Frame(detail_frame, bg='#e74c3c', height=30)
        self.detail_source_frame.pack(fill='x', padx=5, pady=(5, 10))
        self.detail_source_frame.pack_propagate(False)
        
        self.detail_source = tk.Label(
            self.detail_source_frame,
            text="Kaynak: -",
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        self.detail_source.pack(pady=5)
        
        # Baslik
        tk.Label(
            detail_frame,
            text="Baslik:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            anchor='w'
        ).pack(fill='x', padx=5)
        
        self.detail_title = tk.Label(
            detail_frame,
            text="Bir haber secin...",
            font=('Arial', 11),
            bg='#f0f0f0',
            anchor='w',
            wraplength=900,
            justify='left'
        )
        self.detail_title.pack(fill='x', padx=5, pady=(0, 10))
        
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
        self.detail_link.pack(fill='x', padx=5, pady=(0, 10))
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
            font=('Arial', 10),
            height=4,
            padx=5,
            pady=5
        )
        self.detail_summary.pack(fill='x', padx=5, pady=(0, 10))
        
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
            font=('Arial', 10),
            height=6,
            padx=5,
            pady=5
        )
        self.detail_desc.pack(fill='both', expand=True, padx=5, pady=(0, 5))
    
    def fetch_news(self):
        self._fetch_news(selected_only=False)
    
    def fetch_selected_news(self):
        self._fetch_news(selected_only=True)
    
    def _fetch_news(self, selected_only=False):
        self.fetch_btn.config(state='disabled')
        self.selected_fetch_btn.config(state='disabled')
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start()
        
        days = int(self.days_var.get())
        self.status_label.config(text=f"{days} gunluk haberler cekiliyor...")
        
        selected_sources = None
        if selected_only:
            selected_sources = [name for name, var in self.source_vars.items() if var.get()]
            self.status_label.config(text=f"Secili kaynaklardan {days} gunluk haberler cekiliyor...")
        
        thread = threading.Thread(target=self._fetch_thread, args=(days, selected_sources))
        thread.daemon = True
        thread.start()
    
    def _fetch_thread(self, days, selected_sources):
        try:
            articles = self.scraper.fetch_all_news(days=days)
            
            # Secili kaynaklari filtrele
            if selected_sources:
                articles = [a for a in articles if a['source'] in selected_sources]
            
            if articles:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"{len(articles)} haber bulundu. Ceviriliyor..."
                ))
                
                processed = self.scraper.process_news(articles)
                json_file = self.scraper.save_to_json(processed)
                self.scraper.save_to_txt(processed)
                
                self.news_data = processed
                self.root.after(0, self.update_ui)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Basarili",
                    f"{len(processed)} haber basariyla cekildi ve kaydedildi!\n\nDosya: {json_file}"
                ))
            else:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Uyari",
                    "Secili kriterlere uygun haber bulunamadi!"
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
        self.selected_fetch_btn.config(state='normal')
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Hazir")
    
    def filter_news(self, event):
        filter_source = self.filter_var.get()
        self.update_treeview(filter_source)
    
    def update_treeview(self, filter_source="Tumu"):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered_data = self.news_data
        if filter_source != "Tumu":
            filtered_data = [a for a in self.news_data if a['source'] == filter_source]
        
        for i, article in enumerate(filtered_data, 1):
            title = article['turkish_title'][:80] + "..." if len(article['turkish_title']) > 80 else article['turkish_title']
            self.tree.insert('', 'end', values=(
                i,
                title,
                article['source'],
                article['date']
            ))
    
    def load_saved_news(self):
        try:
            json_files = glob.glob("cybersecurity_news_multi_*.json")
            
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.news_data = json.load(f)
                
                self.update_ui()
                self.status_label.config(text=f"{len(self.news_data)} haber yuklendi")
                messagebox.showinfo("Basarili", f"Son kaydedilen haberler yuklendi!\nDosya: {latest_file}")
            else:
                # Tek kaynakli dosyalari dene
                json_files = glob.glob("cybersecurity_news_*.json")
                if json_files:
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
        self.update_treeview(self.filter_var.get())
        
        self.total_label.config(text=f"Toplam Haber: {len(self.news_data)}")
        
        # Kaynak dagilimi
        source_count = {}
        for article in self.news_data:
            source = article.get('source', 'Bilinmiyor')
            source_count[source] = source_count.get(source, 0) + 1
        
        source_text = "Kaynaklara gore dagilim:\n"
        for source, count in sorted(source_count.items(), key=lambda x: x[1], reverse=True):
            source_text += f"  {source}: {count}\n"
        
        self.by_source_label.config(text=source_text)
        self.date_label.config(text=f"Son Guncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        index = int(item['values'][0]) - 1
        
        # Filtrelenmis listede dogru indeksi bul
        filter_source = self.filter_var.get()
        filtered_data = self.news_data
        if filter_source != "Tumu":
            filtered_data = [a for a in self.news_data if a['source'] == filter_source]
        
        if 0 <= index < len(filtered_data):
            article = filtered_data[index]
            
            # Kaynak rengini degistir
            source_colors = {
                "The Hacker News": "#e74c3c",
                "Bleeping Computer": "#3498db",
                "SecurityWeek": "#2ecc71",
                "Dark Reading": "#9b59b6",
                "Krebs on Security": "#f39c12"
            }
            color = source_colors.get(article['source'], '#95a5a6')
            self.detail_source_frame.config(bg=color)
            self.detail_source.config(bg=color)
            
            self.detail_source.config(text=f"Kaynak: {article['source']}")
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
