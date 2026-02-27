# Teknoloji Radar

Siber güvenlik haberleri, CVE zafiyetleri, Kubernetes ekosistemi, SRE (Site Reliability Engineering) haberleri ve DevTools altyapı araçları güncellemelerini **27 farklı kaynaktan** toplayan, Türkçeye çeviren ve modern bir arayüzde sunan full-stack haber agregasyon uygulaması.

> Bu proje **Vibe Coding** yaklaşımıyla, Claude Code (claude-opus-4-6) ile birlikte geliştirilmiştir.

---

## Mimari

```
                         ┌──────────────────┐
                         │   React Frontend │
                         │   (Vite + BS5)   │
                         │   :3000          │
                         └────────┬─────────┘
                                  │ /api proxy
                         ┌────────▼─────────┐
                         │  Django REST API  │
                         │  (Gunicorn)       │
                         │  :8000            │
                         └──┬──────────┬────┘
                            │          │
                   ┌────────▼──┐  ┌────▼────────────┐
                   │   Redis   │  │  Celery Worker   │
                   │   :6379   │  │  + Beat Scheduler│
                   └───────────┘  └─────────────────┘
                                          │
                              ┌───────────▼───────────┐
                               │   Harici Kaynaklar     │
                               │   (27 kaynak)          │
                              │   + Google Translate    │
                              └─────────────────────────┘
```

## Özellikler

- **27 farklı kaynak** — 5 siber güvenlik, 5 CVE, 3 Kubernetes, 5 SRE, 9 DevTools
- **Tam makale çevirisi** — Kısaltma yok, tüm içerik Türkçeye çevrilir
- **Teknik terim koruması** — 60+ terim (CVE, CVSS, Kubernetes, Docker, vb.) çeviri sırasında bozulmaz
- **Parça tabanlı çeviri** — Uzun makaleler cümle sınırlarından 4500 karakterlik parçalara bölünerek çevrilir
- **Karanlık mod** — Koyu tonlarda arayüz
- **DevTools takibi** — MinIO, Seq, Ceph, MongoDB, PostgreSQL, RabbitMQ, Elasticsearch+Kibana, Redis, Moodle release güncellemeleri
- **Tarih filtresi** — 1-15 gün (haberler) / 1-60 gün (DevTools) slider ile filtreleme
- **CVSS şiddet filtresi** — Kritik / Yüksek / Orta / Düşük (CVE sayfası)
- **Docker Compose** — Tek komutla 5 container ayağa kalkar
- **Kubernetes** — Production-ready manifest'ler

---

## Veri Kaynakları

### Siber Güvenlik Haberleri (5 kaynak)

| Kaynak | Yöntem | Açıklama |
|--------|--------|----------|
| The Hacker News | HTML Scraping | Tam makale içeriği çekilir |
| Bleeping Computer | HTML Scraping | Sponsorlu içerik filtrelenir |
| SecurityWeek | HTML Scraping | Güvenlik odaklı haberler |
| Dark Reading | RSS Feed | HTML 403 döndüğü için RSS kullanılır |
| Krebs on Security | HTML Scraping | Brian Krebs'in güvenlik blogu |

### CVE Zafiyetleri (5 kaynak)

| Kaynak | Yöntem | Açıklama |
|--------|--------|----------|
| NVD (Yayınlanan) | REST API | Yeni yayınlanan CVE'ler |
| NVD (Güncel) | REST API | Son güncellenen CVE'ler |
| GitHub Advisory | REST API | CVSS, CWE, etkilenen paketler dahil |
| Tenable | HTML Scraping | Severity bilgisi dahil |
| CIRCL | REST API | Lüksemburg CERT |

### Kubernetes (3 kaynak)

| Kaynak | Yöntem | Açıklama |
|--------|--------|----------|
| Kubernetes Blog | HTML Scraping | Resmi Kubernetes blog yazıları |
| Kubernetes GitHub | REST API | Release notları, CHANGELOG formatında |
| CNCF Blog | WordPress API | Cloud Native Computing Foundation haberleri |

### SRE (5 kaynak)

| Kaynak | Yöntem | Açıklama |
|--------|--------|----------|
| SRE Weekly | RSS Feed | Haftalık bülten, bireysel makalelere ayrıştırılır |
| InfoQ SRE | HTML Scraping | SRE etiketli makaleler |
| PagerDuty Eng | RSS Feed | Incident management ve SRE makaleleri |
| Google Cloud SRE | RSS Feed | SRE anahtar kelime filtresiyle |
| DZone DevOps | RSS Feed | SRE/DevOps konulu makaleler |

### DevTools — Altyapı Araçları (9 kaynak)

| Kaynak | Yöntem | Açıklama |
|--------|--------|----------|
| MinIO | GitHub Releases API | S3 uyumlu object storage, detaylı changelog |
| Seq | Datalust Blog RSS | Yapılandırılmış log arama motoru, release filtreli |
| Ceph | GitHub Releases Atom | Dağıtık storage, version tag tabanlı |
| MongoDB | Blog RSS | Release ve güncelleme filtreli blog yazıları |
| PostgreSQL | Resmi News RSS | Resmi haberler, release notları, ekosistem |
| RabbitMQ | GitHub Releases API | Mesaj kuyruğu, tam changelog |
| Elasticsearch + Kibana | GitHub Releases API | ES ve Kibana sürümleri, deduplicate edilir |
| Redis | Blog RSS | Announcing/release filtreli blog yazıları |
| Moodle | GitHub Tags API | Stabil sürüm tag'leri, commit tarihinden date çıkarılır |

---

## Teknoloji Yığını

| Katman | Teknolojiler |
|--------|-------------|
| **Backend** | Python 3.11, Django 4.2, Django REST Framework 3.14, Celery 5.3, Gunicorn |
| **Frontend** | React 18, Vite 5, React Bootstrap 2.9, React Router DOM 6, Axios |
| **Veri** | SQLite (lokal), PostgreSQL 16 (K8s), Redis 7 (cache + broker) |
| **Scraping** | BeautifulSoup4, lxml, Requests |
| **Çeviri** | deep-translator (Google Translate) |
| **Altyapı** | Docker Compose, Kubernetes, Nginx 1.25, Whitenoise |

---

## Kurulum (Docker Compose)

### Gereksinimler

- Docker ve Docker Compose
- İnternet bağlantısı (kaynak sitelere ve Google Translate'e erişim)

### Hızlı Başlangıç

```bash
git clone https://github.com/KULLANICI_ADI/teknoloji-radar.git
cd teknoloji-radar/cybersecurity_news

docker compose up -d --build
```

| Servis | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/ |

### Container'lar

| Container | Image | Port | Görev |
|-----------|-------|------|-------|
| `teknoloji-api` | `teknoloji-haberleri-api:latest` | 8000 | Django REST API, scraping, çeviri, veritabanı |
| `teknoloji-frontend` | `node:18-alpine` | 3000 | React arayüz (Vite dev server, hot-reload) |
| `teknoloji-redis` | `redis:7-alpine` | 6379 | Cache + Celery message broker |
| `teknoloji-worker` | `teknoloji-haberleri-api:latest` | — | Arka plan scraping + çeviri |
| `teknoloji-scheduler` | `teknoloji-haberleri-api:latest` | — | Periyodik görev zamanlayıcı (Celery Beat) |

Container'lar `teknoloji-network` bridge network üzerinden haberleşir.

### Yönetim Komutları

```bash
# Başlat
docker compose up -d --build

# Durdur
docker compose down

# Logları izle
docker compose logs -f teknoloji-api
docker compose logs -f teknoloji-worker

# Redis cache temizle
docker compose exec teknoloji-redis redis-cli FLUSHDB

# Django shell
docker compose exec teknoloji-api python manage.py shell

# Sıfırdan başlat (volume'lar dahil)
docker compose down -v && docker compose up -d --build
```

---

## Kullanım

Her sayfa aynı düzeni takip eder:

1. Sol panelden **gün aralığını** (1-15) ve **kaynakları** seçin
2. **"Getir"** butonuna tıklayın
3. Haberler çekilir, Türkçeye çevrilir ve orta panelde listelenir
4. Bir habere tıklayarak sağ panelde detayını görüntüleyin

**Ek butonlar:**
- **Yenile** — Mevcut verileri yeniden yükler
- **Sıfırla** — Tüm verileri temizler
- **İndir** — JSON formatında dışa aktarır

---

## API Endpoints

Her bölüm (news, cve, k8s, sre, devtools) aynı endpoint yapısını kullanır:

| Method | Endpoint Deseni | Açıklama |
|--------|-----------------|----------|
| GET | `/api/{bölüm}/` | Kayıtlı verileri listele |
| POST | `/api/{bölüm}/fetch/` | Yeni verileri çek (body: `{"days": 7, "sources": [...]}`) |
| POST | `/api/{bölüm}/clear/` | Tüm verileri sil |
| GET | `/api/{bölüm}/stats/` | İstatistikleri getir |
| GET | `/api/{bölüm}/export/` | JSON olarak dışa aktar |

**Bölüm isimleri:** `news` (Siber Güvenlik, fetch endpoint: `/api/fetch/`), `cve`, `k8s`, `sre`, `devtools`

> **Not:** Siber güvenlik bölümünün fetch, clear, stats ve export endpoint'leri `/api/news/` altında değil, doğrudan `/api/` altındadır: `/api/fetch/`, `/api/clear/`, `/api/stats/`, `/api/export/`

---

## Proje Yapısı

```
cybersecurity_news/
├── cybernews/                  # Django proje ayarları
│   ├── settings.py             # Env-var tabanlı config (DB, Redis, CORS)
│   ├── urls.py                 # Root URL yapılandırması
│   ├── celery.py               # Celery yapılandırması
│   └── wsgi.py
│
├── news/                       # Ana Django uygulaması
│   ├── models.py               # NewsArticle, CVEEntry, KubernetesEntry, SREEntry, DevToolsEntry
│   ├── views.py                # API endpoint'leri (5 bölüm x 5 endpoint = 25)
│   ├── serializers.py          # DRF serializer'ları
│   ├── urls.py                 # API URL pattern'leri
│   ├── cve_scraper.py          # 5 CVE kaynağı scraper'ı
│   ├── k8s_scraper.py          # 3 Kubernetes kaynağı scraper'ı
│   ├── sre_scraper.py          # 5 SRE kaynağı scraper'ı
│   ├── devtools_scraper.py     # 9 DevTools kaynağı scraper'ı
│   └── admin.py                # Django admin kayıtları
│
├── scraper_multi.py            # 5 siber güvenlik kaynağı scraper'ı
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── App.jsx             # Router, Navbar, Karanlık Mod
│   │   ├── App.css             # Tema stilleri
│   │   ├── components/
│   │   │   ├── NewsComponent.jsx       # Siber güvenlik sayfası
│   │   │   ├── CVEComponent.jsx        # CVE sayfası
│   │   │   ├── KubernetesComponent.jsx # Kubernetes sayfası
│   │   │   ├── SREComponent.jsx        # SRE sayfası
│   │   │   └── DevToolsComponent.jsx   # DevTools sayfası
│   │   └── services/
│   │       └── api.js          # Axios API servisleri
│   ├── Dockerfile              # Production build: Node + Nginx
│   ├── nginx.conf              # SPA routing + /api proxy
│   ├── vite.config.js          # Dev proxy ayarları
│   ├── index.html
│   └── package.json
│
├── k8s/                        # Kubernetes manifest'leri
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml       # Uygulama ayarları
│   ├── 02-secret.yaml          # Gizli bilgiler (placeholder)
│   ├── 03-postgresql.yaml      # PostgreSQL (opsiyonel)
│   ├── 04-redis.yaml           # Redis (opsiyonel)
│   ├── 05-backend.yaml         # Django API Deployment + Service
│   ├── 06-frontend.yaml        # Nginx Frontend Deployment + Service
│   ├── 07-celery.yaml          # Worker + Beat Deployment
│   ├── 08-ingress.yaml         # Nginx Ingress kuralları
│   └── 09-migration-job.yaml   # DB migration Job
│
├── docker-compose.yml          # 5 servis (lokal geliştirme)
├── Dockerfile                  # Backend multi-stage build
├── entrypoint.sh               # Startup: wait-for-db + migrate
├── requirements.txt            # Python bağımlılıkları
├── .gitignore
├── .dockerignore
└── manage.py
```

---

## Çeviri Sistemi

1. **Teknik Terim Koruması** — 60+ terim çeviri öncesinde placeholder'larla değiştirilir, çeviri sonrası geri yerleştirilir
2. **Parça Tabanlı Çeviri** — Metin cümle sınırlarına göre 4500 karakterlik parçalara bölünür (Google Translate 5000 karakter limiti)
3. **Hata Yönetimi** — Başarısız çevirilerde retry mekanizması, rate limit'e karşı 0.3s bekleme

---

## Kubernetes'e Deploy Etme

### Ön Gereksinimler

- Kubernetes cluster (minikube, k3s, EKS, GKE, AKS, vb.)
- `kubectl` CLI kurulu ve cluster'a bağlı
- Docker image build ortamı
- Nginx Ingress Controller (opsiyonel)

### Mimari (Kubernetes)

```
                    ┌─────────────────────┐
                    │   Ingress (Nginx)   │
                    └──────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              │ /api,      │ /          │
              │ /admin,    │            │
              │ /static    │            │
              ▼            │            ▼
    ┌──────────────┐       │  ┌──────────────────┐
    │ teknoloji-api│       │  │teknoloji-frontend│
    │ replica: 2   │       │  │  replica: 2      │
    │ :8000        │       │  │  :3000 (nginx)   │
    └──────┬───────┘       │  └──────────────────┘
           │               │
    ┌──────┼───────────────┘
    │      │
    ▼      ▼
┌────────┐  ┌────────────────────┐
│ Redis  │  │    PostgreSQL      │
│ :6379  │  │    :5432           │
└────────┘  └────────────────────┘
    ▲
    │
┌───┴──────────────┐  ┌───────────────────┐
│ teknoloji-worker │  │teknoloji-scheduler│
│ (Celery Worker)  │  │ (Celery Beat)     │
└──────────────────┘  └───────────────────┘
```

Docker Compose'dan farklı olarak Kubernetes'te:
- **PostgreSQL** kullanılır (SQLite yerine — çoklu replica desteği)
- Frontend **Nginx** ile statik dosya olarak sunulur (Vite dev server yerine)
- Tüm konfigürasyon **ConfigMap** ve **Secret** ile yönetilir

### Adım 1 — Docker Image'larını Build Edin

```bash
# Backend
docker build -t teknoloji-haberleri-api:latest .

# Frontend (production Nginx build)
docker build -t teknoloji-haberleri-frontend:latest ./frontend
```

Private registry kullanıyorsanız tag'leyip push edin:

```bash
docker tag teknoloji-haberleri-api:latest REGISTRY/teknoloji-haberleri-api:latest
docker tag teknoloji-haberleri-frontend:latest REGISTRY/teknoloji-haberleri-frontend:latest
docker push REGISTRY/teknoloji-haberleri-api:latest
docker push REGISTRY/teknoloji-haberleri-frontend:latest
```

Registry kullandığınızda K8s manifest'lerindeki `image:` değerlerini ve `imagePullPolicy` satırını güncellemeyi unutmayın.

### Adım 2 — Secret'ları Oluşturun

`k8s/02-secret.yaml` dosyasındaki placeholder değerleri gerçek değerlerle değiştirin:

```yaml
stringData:
  SECRET_KEY: "min-50-karakter-rastgele-guclu-bir-key"
  DB_USER: "cybernews"
  DB_PASSWORD: "guclu-veritabani-sifresi"
  POSTGRES_PASSWORD: "guclu-veritabani-sifresi"
```

Veya doğrudan kubectl ile:

```bash
kubectl create namespace teknoloji-haberleri

kubectl create secret generic teknoloji-secret \
  --namespace=teknoloji-haberleri \
  --from-literal=SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=DB_USER=cybernews \
  --from-literal=DB_PASSWORD="$(openssl rand -hex 16)" \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -hex 16)"
```

### Adım 3 — ConfigMap'i Düzenleyin

`k8s/01-configmap.yaml` dosyasını ortamınıza göre düzenleyin:

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `DEBUG` | `"False"` | Django debug modu |
| `ALLOWED_HOSTS` | `"*"` | İzin verilen host'lar |
| `CORS_ALLOWED_ORIGINS` | `"http://localhost:3000,http://teknoloji-frontend:3000"` | CORS origin'leri |
| `DATABASE_URL` | `"postgresql"` | Boş olmayan herhangi bir değer PostgreSQL'i aktifler |
| `DB_NAME` | `"cybernews"` | Veritabanı adı |
| `DB_HOST` | `"teknoloji-postgresql"` | PostgreSQL adresi |
| `DB_PORT` | `"5432"` | PostgreSQL portu |
| `REDIS_URL` | `"redis://teknoloji-redis:6379/0"` | Redis bağlantısı (cache) |
| `CELERY_BROKER_URL` | `"redis://teknoloji-redis:6379/1"` | Redis bağlantısı (Celery) |

**Cluster'da mevcut PostgreSQL/Redis varsa** `DB_HOST` ve `REDIS_URL`/`CELERY_BROKER_URL` değerlerini mevcut servis adreslerine yönlendirin. Bu durumda `03-postgresql.yaml` ve `04-redis.yaml` dosyalarını uygulamayın.

```yaml
# Örnek: Farklı namespace'teki mevcut PostgreSQL
DB_HOST: "postgresql.database-namespace.svc.cluster.local"

# Örnek: Mevcut Redis
REDIS_URL: "redis://redis-master.cache-namespace.svc.cluster.local:6379/0"
CELERY_BROKER_URL: "redis://redis-master.cache-namespace.svc.cluster.local:6379/1"
```

### Adım 4 — Manifest'leri Uygulayın

```bash
# 1. Namespace
kubectl apply -f k8s/00-namespace.yaml

# 2. ConfigMap ve Secret
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml

# 3. Veritabanı ve Cache (mevcut varsa ATLAYIN)
kubectl apply -f k8s/03-postgresql.yaml
kubectl apply -f k8s/04-redis.yaml

# 4. PostgreSQL'in hazır olmasını bekleyin
kubectl wait --for=condition=ready pod \
  -l app.kubernetes.io/name=teknoloji-postgresql \
  -n teknoloji-haberleri --timeout=120s

# 5. DB migration
kubectl apply -f k8s/09-migration-job.yaml
kubectl wait --for=condition=complete job/teknoloji-migrate \
  -n teknoloji-haberleri --timeout=120s

# 6. Uygulama
kubectl apply -f k8s/05-backend.yaml
kubectl apply -f k8s/06-frontend.yaml
kubectl apply -f k8s/07-celery.yaml

# 7. Ingress (opsiyonel)
kubectl apply -f k8s/08-ingress.yaml
```

**Tek komutla hepsini uygulamak:**

```bash
kubectl apply -f k8s/
```

### Adım 5 — Doğrulama

```bash
# Pod durumları
kubectl get pods -n teknoloji-haberleri

# Beklenen:
# teknoloji-api-xxxxx          1/1     Running     0
# teknoloji-api-yyyyy          1/1     Running     0
# teknoloji-frontend-xxxxx     1/1     Running     0
# teknoloji-frontend-yyyyy     1/1     Running     0
# teknoloji-worker-xxxxx       1/1     Running     0
# teknoloji-scheduler-xxxxx    1/1     Running     0
# teknoloji-postgresql-xxxxx   1/1     Running     0
# teknoloji-redis-xxxxx        1/1     Running     0
# teknoloji-migrate-xxxxx      0/1     Completed   0

# Loglar
kubectl logs -f deployment/teknoloji-api -n teknoloji-haberleri
```

### Ingress Yoksa — Port Forward

```bash
kubectl port-forward svc/teknoloji-frontend 3000:3000 -n teknoloji-haberleri
kubectl port-forward svc/teknoloji-api 8000:8000 -n teknoloji-haberleri
```

Tarayıcıda `http://localhost:3000` adresine gidin.

### Güncelleme

```bash
# Yeni image build
docker build -t teknoloji-haberleri-api:v2 .
docker build -t teknoloji-haberleri-frontend:v2 ./frontend

# Migration (gerekiyorsa)
kubectl delete job teknoloji-migrate -n teknoloji-haberleri --ignore-not-found
kubectl apply -f k8s/09-migration-job.yaml

# Deployment güncelleme
kubectl set image deployment/teknoloji-api api=teknoloji-haberleri-api:v2 -n teknoloji-haberleri
kubectl set image deployment/teknoloji-frontend frontend=teknoloji-haberleri-frontend:v2 -n teknoloji-haberleri
kubectl set image deployment/teknoloji-worker worker=teknoloji-haberleri-api:v2 -n teknoloji-haberleri
kubectl set image deployment/teknoloji-scheduler scheduler=teknoloji-haberleri-api:v2 -n teknoloji-haberleri
```

### Kaldırma

```bash
kubectl delete namespace teknoloji-haberleri
```

---

## Ortam Değişkenleri

Uygulama tamamen ortam değişkenleri ile yapılandırılabilir. Docker Compose'da `docker-compose.yml` içinde, Kubernetes'te ConfigMap + Secret ile ayarlanır.

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `SECRET_KEY` | `django-insecure-...` | Django secret key (production'da mutlaka değiştirin) |
| `DEBUG` | `False` | Django debug modu |
| `ALLOWED_HOSTS` | `*` | Virgülle ayrılmış izinli host listesi |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | Frontend origin'leri |
| `DATABASE_URL` | _(boş)_ | Herhangi bir değer atanırsa PostgreSQL aktif olur, boşsa SQLite |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `cybernews` | Veritabanı adı |
| `DB_USER` | `cybernews` | Veritabanı kullanıcısı |
| `DB_PASSWORD` | _(boş)_ | Veritabanı şifresi |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Redis bağlantısı (cache) |
| `CELERY_BROKER_URL` | `redis://127.0.0.1:6379/1` | Redis bağlantısı (Celery broker) |

---

## Bilinen Kısıtlamalar

- Google Translate ücretsiz API rate limit'e takılabilir — çok sayıda makale çekildiğinde yavaşlama olabilir
- Dark Reading HTML scraping'e 403 döner, bu yüzden RSS feed kullanılır
- Gunicorn timeout 300 saniye — çok fazla kaynak seçilirse zaman aşımı olabilir
- Her fetch'te toplam makale sayısı **30 ile sınırlıdır** (Gunicorn timeout'undan kaçınmak için)

---

## Lisans

MIT License
