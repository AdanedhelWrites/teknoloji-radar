"""
DevTools Scraper Module — Altyapi Araclari Guncelleme Takibi
9 kaynak:
  - MinIO (GitHub Releases API)
  - Seq (Datalust Blog RSS)
  - Ceph (GitHub Releases Atom)
  - MongoDB (Blog RSS, filtreli)
  - PostgreSQL (Resmi News RSS)
  - RabbitMQ (GitHub Releases API)
  - Elasticsearch + Kibana (GitHub Releases API)
  - Redis (Blog RSS, filtreli)
  - Moodle (GitHub Tags API + Download page)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
from deep_translator import GoogleTranslator
import time
from email.utils import parsedate_to_datetime


class DevToolsScraper:
    """DevTools Scraper temel sinifi"""

    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='tr')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8',
        })

    PROTECTED_TERMS = [
        'MinIO', 'Seq', 'Ceph', 'MongoDB', 'PostgreSQL', 'RabbitMQ',
        'Elasticsearch', 'Kibana', 'Redis', 'Moodle',
        'RELEASE', 'LTS', 'GA', 'RC', 'Beta', 'Alpha',
        'API', 'REST', 'gRPC', 'GraphQL', 'HTTP', 'HTTPS', 'DNS', 'CDN',
        'S3', 'AMQP', 'MQTT', 'LDAP', 'SAML', 'OAuth', 'JWT', 'TLS', 'SSL',
        'Kubernetes', 'K8s', 'Docker', 'Helm', 'Terraform',
        'AWS', 'GCP', 'Azure',
        'CPU', 'RAM', 'SSD', 'I/O', 'IO', 'GB', 'TB', 'MB',
        'CVE', 'CVSS', 'XSS', 'SQL', 'NoSQL',
        'Linux', 'Ubuntu', 'CentOS', 'RHEL', 'Debian',
        'GitHub', 'GitLab',
        'RADOS', 'RGW', 'CephFS', 'BlueStore', 'OSD', 'MON', 'MDS',
        'PGPool', 'pgvector', 'VACUUM', 'WAL', 'MVCC',
        'Logstash', 'Beats', 'Filebeat', 'Metricbeat', 'Lucene',
        'SCORM', 'LTI', 'IMSCP',
        'Erasure Coding', 'Object Storage', 'Block Storage',
        'Replication', 'Sharding', 'Clustering', 'Failover',
        'CI/CD', 'DevOps', 'SRE',
    ]

    def _protect_terms(self, text: str) -> tuple:
        protected = text
        replacements = {}
        for i, term in enumerate(self.PROTECTED_TERMS):
            placeholder = f"__TERM{i:03d}__"
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            if pattern.search(protected):
                replacements[placeholder] = term
                protected = pattern.sub(placeholder, protected)
        return protected, replacements

    def _restore_terms(self, text: str, replacements: dict) -> str:
        restored = text
        for placeholder, original in replacements.items():
            restored = restored.replace(placeholder, original)
        return restored

    def translate_text(self, text: str, max_retries: int = 2) -> str:
        if not text or len(text.strip()) == 0:
            return ""
        protected, replacements = self._protect_terms(text)
        if len(protected) > 4500:
            protected = protected[:4500]
        for attempt in range(max_retries):
            try:
                translated = self.translator.translate(protected)
                time.sleep(0.3)
                return self._restore_terms(translated, replacements)
            except Exception:
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
        return text

    def translate_long_text(self, text: str, chunk_size: int = 4500) -> str:
        if not text or len(text.strip()) == 0:
            return ""
        if len(text) <= chunk_size:
            return self.translate_text(text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                current_chunk += (" " + sentence) if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk)
        translated_parts = []
        for chunk in chunks:
            try:
                translated_parts.append(self.translate_text(chunk))
                time.sleep(0.3)
            except Exception:
                translated_parts.append(chunk)
        return ' '.join(translated_parts)

    def _parse_rss_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass
        formats = [
            '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f%z',
            '%B %d, %Y', '%b %d, %Y', '%Y-%m-%d',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except Exception:
                continue
        return None

    def _html_to_text(self, html_content: str) -> str:
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _markdown_to_text(self, md: str) -> str:
        """Markdown'dan temiz metin cikarir"""
        if not md:
            return ""
        text = md
        # Link'leri temizle [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Bold/italic
        text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
        # Headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Fazla bosluklar
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


# ============================================================
# 1. MinIO — GitHub Releases API
# ============================================================
class MinIOScraper(DevToolsScraper):
    """MinIO GitHub Releases scraper"""

    API_URL = "https://api.github.com/repos/minio/minio/releases"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[MinIO] Son {days} gunun guncellemeleri cekiliyor...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.API_URL, params={'per_page': 15}, timeout=20)
            resp.raise_for_status()
            releases = resp.json()
            print(f"  [MinIO] {len(releases)} release bulundu")
            for rel in releases:
                pub_date = self._parse_rss_date(rel.get('published_at', ''))
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                title = rel.get('name', '') or rel.get('tag_name', '')
                body = self._markdown_to_text(rel.get('body', ''))
                link = rel.get('html_url', '')
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                entries.append({
                    'title': f"MinIO {title}",
                    'description': body[:4000] if body else title,
                    'link': link,
                    'date': date_str,
                    'source': 'MinIO',
                    'version': rel.get('tag_name', ''),
                    'entry_type': 'release',
                })
        except Exception as e:
            print(f"[MinIO] Hata: {e}")
        print(f"[MinIO] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 2. Seq — Datalust Blog RSS
# ============================================================
class SeqScraper(DevToolsScraper):
    """Seq (Datalust) Blog RSS scraper — release haberleri"""

    FEED_URL = "https://blog.datalust.co/rss/"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[Seq] Son {days} gunun guncellemeleri cekiliyor (RSS)...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.FEED_URL, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')
            print(f"  [Seq] RSS'te {len(items)} paylasim bulundu")
            for item in items:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ''
                if not title_text:
                    continue
                # Release ve update ile ilgili olanlari filtrele
                title_lower = title_text.lower()
                is_release = any(kw in title_lower for kw in [
                    'seq 20', 'release', 'update', 'announcing', 'preview',
                    'engineering update', 'what\'s new',
                ])
                if not is_release:
                    continue
                pub_tag = item.find('pubDate')
                pub_date = self._parse_rss_date(pub_tag.get_text(strip=True)) if pub_tag else None
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                link_tag = item.find('link')
                link = link_tag.get_text(strip=True) if link_tag else ''
                if link and link.startswith('/'):
                    link = f"https://blog.datalust.co{link}"
                content_tag = item.find('content:encoded') or item.find('encoded')
                description = ''
                if content_tag:
                    description = self._html_to_text(content_tag.get_text())
                if not description:
                    desc_tag = item.find('description')
                    description = self._html_to_text(desc_tag.get_text()) if desc_tag else title_text
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                # Versiyon cikarma
                version_match = re.search(r'Seq\s+(\d{4}\.\d+)', title_text)
                version = version_match.group(1) if version_match else ''
                entries.append({
                    'title': title_text,
                    'description': description[:4000],
                    'link': link,
                    'date': date_str,
                    'source': 'Seq',
                    'version': version,
                    'entry_type': 'release' if 'release' in title_lower else 'blog',
                })
        except Exception as e:
            print(f"[Seq] RSS hatasi: {e}")
        print(f"[Seq] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 3. Ceph — GitHub Releases Atom
# ============================================================
class CephScraper(DevToolsScraper):
    """Ceph GitHub Releases Atom feed scraper"""

    ATOM_URL = "https://github.com/ceph/ceph/releases.atom"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[Ceph] Son {days} gunun guncellemeleri cekiliyor (Atom)...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.ATOM_URL, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            atom_entries = soup.find_all('entry')
            print(f"  [Ceph] Atom feed'de {len(atom_entries)} release bulundu")
            for entry in atom_entries:
                title_tag = entry.find('title')
                title = title_tag.get_text(strip=True) if title_tag else ''
                if not title:
                    continue
                updated_tag = entry.find('updated')
                pub_date = self._parse_rss_date(updated_tag.get_text(strip=True)) if updated_tag else None
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                link_tag = entry.find('link')
                link = link_tag.get('href', '') if link_tag else ''
                content_tag = entry.find('content')
                description = self._html_to_text(content_tag.get_text()) if content_tag else title
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                entries.append({
                    'title': f"Ceph {title}",
                    'description': description[:4000] if description else f"Ceph {title} released",
                    'link': link,
                    'date': date_str,
                    'source': 'Ceph',
                    'version': title,
                    'entry_type': 'release',
                })
        except Exception as e:
            print(f"[Ceph] Atom hatasi: {e}")
        print(f"[Ceph] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 4. MongoDB — Blog RSS (filtreli)
# ============================================================
class MongoDBScraper(DevToolsScraper):
    """MongoDB Blog RSS scraper — release filtreli"""

    FEED_URL = "https://www.mongodb.com/blog/rss"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[MongoDB] Son {days} gunun guncellemeleri cekiliyor (RSS)...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.FEED_URL, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')
            print(f"  [MongoDB] RSS'te {len(items)} paylasim bulundu")
            for item in items:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ''
                if not title_text:
                    continue
                title_lower = title_text.lower()
                is_relevant = any(kw in title_lower for kw in [
                    'release', 'released', 'update', 'mongodb',
                    'what\'s new', 'announcing', 'launch',
                    'security', 'patch', 'upgrade',
                ])
                if not is_relevant:
                    continue
                pub_tag = item.find('pubDate')
                pub_date = self._parse_rss_date(pub_tag.get_text(strip=True)) if pub_tag else None
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                link_tag = item.find('link')
                link = link_tag.get_text(strip=True) if link_tag else ''
                desc_tag = item.find('description')
                description = self._html_to_text(desc_tag.get_text()) if desc_tag else title_text
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', title_text)
                version = version_match.group(1) if version_match else ''
                entries.append({
                    'title': title_text,
                    'description': description[:4000],
                    'link': link,
                    'date': date_str,
                    'source': 'MongoDB',
                    'version': version,
                    'entry_type': 'release' if 'release' in title_lower else 'blog',
                })
        except Exception as e:
            print(f"[MongoDB] RSS hatasi: {e}")
        print(f"[MongoDB] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 5. PostgreSQL — Resmi News RSS
# ============================================================
class PostgreSQLScraper(DevToolsScraper):
    """PostgreSQL resmi news RSS scraper"""

    FEED_URL = "https://www.postgresql.org/news.rss"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[PostgreSQL] Son {days} gunun guncellemeleri cekiliyor (RSS)...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.FEED_URL, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')
            print(f"  [PostgreSQL] RSS'te {len(items)} haber bulundu")
            for item in items:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ''
                if not title_text:
                    continue
                pub_tag = item.find('pubDate')
                pub_date = self._parse_rss_date(pub_tag.get_text(strip=True)) if pub_tag else None
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                link_tag = item.find('link')
                link = link_tag.get_text(strip=True) if link_tag else ''
                desc_tag = item.find('description')
                description = self._html_to_text(desc_tag.get_text()) if desc_tag else title_text
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', title_text)
                version = version_match.group(1) if version_match else ''
                title_lower = title_text.lower()
                entry_type = 'release' if any(kw in title_lower for kw in ['released', 'release', 'update']) else 'news'
                entries.append({
                    'title': title_text,
                    'description': description[:4000],
                    'link': link,
                    'date': date_str,
                    'source': 'PostgreSQL',
                    'version': version,
                    'entry_type': entry_type,
                })
        except Exception as e:
            print(f"[PostgreSQL] RSS hatasi: {e}")
        print(f"[PostgreSQL] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 6. RabbitMQ — GitHub Releases API
# ============================================================
class RabbitMQScraper(DevToolsScraper):
    """RabbitMQ GitHub Releases scraper"""

    API_URL = "https://api.github.com/repos/rabbitmq/rabbitmq-server/releases"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[RabbitMQ] Son {days} gunun guncellemeleri cekiliyor...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.API_URL, params={'per_page': 15}, timeout=20)
            resp.raise_for_status()
            releases = resp.json()
            print(f"  [RabbitMQ] {len(releases)} release bulundu")
            for rel in releases:
                if rel.get('prerelease', False):
                    continue
                pub_date = self._parse_rss_date(rel.get('published_at', ''))
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                title = rel.get('name', '') or rel.get('tag_name', '')
                body = self._markdown_to_text(rel.get('body', ''))
                link = rel.get('html_url', '')
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                entries.append({
                    'title': f"RabbitMQ {title}",
                    'description': body[:4000] if body else f"RabbitMQ {title} released",
                    'link': link,
                    'date': date_str,
                    'source': 'RabbitMQ',
                    'version': rel.get('tag_name', ''),
                    'entry_type': 'release',
                })
        except Exception as e:
            print(f"[RabbitMQ] Hata: {e}")
        print(f"[RabbitMQ] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 7. Elasticsearch + Kibana — GitHub Releases API
# ============================================================
class ElasticScraper(DevToolsScraper):
    """Elasticsearch + Kibana GitHub Releases scraper"""

    ES_API = "https://api.github.com/repos/elastic/elasticsearch/releases"
    KIBANA_API = "https://api.github.com/repos/elastic/kibana/releases"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[Elastic] Son {days} gunun guncellemeleri cekiliyor...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)

        # Elasticsearch releases
        try:
            resp = self.session.get(self.ES_API, params={'per_page': 10}, timeout=20)
            resp.raise_for_status()
            releases = resp.json()
            print(f"  [Elasticsearch] {len(releases)} release bulundu")
            for rel in releases:
                pub_date = self._parse_rss_date(rel.get('published_at', ''))
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                title = rel.get('name', '') or rel.get('tag_name', '')
                body = self._markdown_to_text(rel.get('body', ''))
                link = rel.get('html_url', '')
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                entries.append({
                    'title': f"Elasticsearch {title}",
                    'description': body[:4000] if body else f"Elasticsearch {title} released",
                    'link': link,
                    'date': date_str,
                    'source': 'Elastic',
                    'version': rel.get('tag_name', ''),
                    'entry_type': 'release',
                })
        except Exception as e:
            print(f"[Elasticsearch] Hata: {e}")

        # Kibana releases (sadece ES'te olmayanlari ekle)
        es_versions = {e['version'] for e in entries}
        try:
            resp = self.session.get(self.KIBANA_API, params={'per_page': 10}, timeout=20)
            resp.raise_for_status()
            releases = resp.json()
            print(f"  [Kibana] {len(releases)} release bulundu")
            for rel in releases:
                tag = rel.get('tag_name', '')
                if tag in es_versions:
                    continue  # ES ile ayni versiyon, tekrar ekleme
                pub_date = self._parse_rss_date(rel.get('published_at', ''))
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                title = rel.get('name', '') or tag
                body = self._markdown_to_text(rel.get('body', ''))
                link = rel.get('html_url', '')
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                entries.append({
                    'title': f"Kibana {title}",
                    'description': body[:4000] if body else f"Kibana {title} released",
                    'link': link,
                    'date': date_str,
                    'source': 'Elastic',
                    'version': tag,
                    'entry_type': 'release',
                })
        except Exception as e:
            print(f"[Kibana] Hata: {e}")

        print(f"[Elastic] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 8. Redis — Blog RSS (filtreli)
# ============================================================
class RedisScraper(DevToolsScraper):
    """Redis Blog RSS scraper — release filtreli"""

    FEED_URL = "https://redis.io/blog/feed"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[Redis] Son {days} gunun guncellemeleri cekiliyor (RSS)...")
        entries = []
        cutoff = datetime.now() - timedelta(days=days)
        try:
            resp = self.session.get(self.FEED_URL, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')
            print(f"  [Redis] RSS'te {len(items)} paylasim bulundu")
            for item in items:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ''
                if not title_text:
                    continue
                title_lower = title_text.lower()
                is_relevant = any(kw in title_lower for kw in [
                    'announcing redis', 'redis', 'release', 'update',
                    'what\'s new', 'security', 'patch',
                ])
                if not is_relevant:
                    continue
                pub_tag = item.find('pubDate')
                pub_date = self._parse_rss_date(pub_tag.get_text(strip=True)) if pub_tag else None
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue
                link_tag = item.find('link')
                link = link_tag.get_text(strip=True) if link_tag else ''
                desc_tag = item.find('description')
                description = self._html_to_text(desc_tag.get_text()) if desc_tag else title_text
                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                version_match = re.search(r'Redis\s+(\d+\.\d+(?:\.\d+)?)', title_text, re.IGNORECASE)
                version = version_match.group(1) if version_match else ''
                entries.append({
                    'title': title_text,
                    'description': description[:4000],
                    'link': link,
                    'date': date_str,
                    'source': 'Redis',
                    'version': version,
                    'entry_type': 'release' if 'announcing' in title_lower or 'release' in title_lower else 'blog',
                })
        except Exception as e:
            print(f"[Redis] RSS hatasi: {e}")
        print(f"[Redis] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# 9. Moodle — GitHub Tags API
# ============================================================
class MoodleScraper(DevToolsScraper):
    """Moodle GitHub Tags + download page scraper"""

    TAGS_API = "https://api.github.com/repos/moodle/moodle/tags"
    DOWNLOAD_URL = "https://download.moodle.org/releases/latest/"

    def fetch_entries(self, days: int = 60) -> List[Dict]:
        print(f"[Moodle] Son {days} gunun guncellemeleri cekiliyor...")
        entries = []

        # GitHub Tags — son stabil versiyonlar
        try:
            resp = self.session.get(self.TAGS_API, params={'per_page': 20}, timeout=20)
            resp.raise_for_status()
            tags = resp.json()
            print(f"  [Moodle] {len(tags)} tag bulundu")

            stable_tags = []
            for tag in tags:
                name = tag.get('name', '')
                # Sadece stabil versiyonlar (beta, rc, dev, weekly haric)
                if re.match(r'^v\d+\.\d+\.\d+$', name):
                    stable_tags.append(name)

            # Son 5 stabil tag
            for tag_name in stable_tags[:5]:
                # Tag commit tarihini cek
                commit_url = None
                for tag in tags:
                    if tag.get('name') == tag_name:
                        commit_url = tag.get('commit', {}).get('url', '')
                        break

                pub_date = None
                if commit_url:
                    try:
                        commit_resp = self.session.get(commit_url, timeout=10)
                        if commit_resp.ok:
                            commit_data = commit_resp.json()
                            date_str = commit_data.get('commit', {}).get('committer', {}).get('date', '')
                            pub_date = self._parse_rss_date(date_str)
                    except Exception:
                        pass

                cutoff = datetime.now() - timedelta(days=days)
                if pub_date and pub_date.replace(tzinfo=None) < cutoff:
                    continue

                date_str = pub_date.strftime('%Y-%m-%d') if pub_date else datetime.now().strftime('%Y-%m-%d')
                version = tag_name.lstrip('v')

                entries.append({
                    'title': f"Moodle {version} Released",
                    'description': f"Moodle {version} has been released. Visit the Moodle download page for details, changelog, and system requirements.",
                    'link': f"https://github.com/moodle/moodle/releases/tag/{tag_name}",
                    'date': date_str,
                    'source': 'Moodle',
                    'version': version,
                    'entry_type': 'release',
                })

        except Exception as e:
            print(f"[Moodle] Tags hatasi: {e}")

        print(f"[Moodle] {len(entries)} guncelleme bulundu")
        return entries


# ============================================================
# Multi DevTools Scraper — Tum kaynaklari birlestiren sinif
# ============================================================
class MultiDevToolsScraper(DevToolsScraper):
    """Tum DevTools kaynaklarini birlestiren scraper"""

    def __init__(self):
        super().__init__()
        self.scrapers = {
            'MinIO': MinIOScraper(),
            'Seq': SeqScraper(),
            'Ceph': CephScraper(),
            'MongoDB': MongoDBScraper(),
            'PostgreSQL': PostgreSQLScraper(),
            'RabbitMQ': RabbitMQScraper(),
            'Elastic': ElasticScraper(),
            'Redis': RedisScraper(),
            'Moodle': MoodleScraper(),
        }

    def fetch_all(self, days: int = 60, selected_sources: list = None, max_total: int = 30) -> List[Dict]:
        all_entries = []
        print("=" * 80)
        print(f"TUM DEVTOOLS KAYNAKLARINDAN GUNCELLEME CEKILIYOR ({days} gun, maks {max_total})")
        print("=" * 80)

        sources = dict(self.scrapers)
        if selected_sources:
            sources = {k: v for k, v in sources.items() if k in selected_sources}

        per_source_limit = max(5, max_total // max(len(sources), 1))

        for source_name, scraper in sources.items():
            try:
                entries = scraper.fetch_entries(days=days)
                if len(entries) > per_source_limit:
                    entries = entries[:per_source_limit]
                    print(f"  -> {source_name}: {per_source_limit} guncelleme (sinirlandirildi)")
                else:
                    print(f"  -> {source_name}: {len(entries)} guncelleme")
                all_entries.extend(entries)
            except Exception as e:
                print(f"  -> {source_name}: HATA - {e}")

        all_entries.sort(key=lambda x: x['date'], reverse=True)

        if len(all_entries) > max_total:
            all_entries = all_entries[:max_total]

        # Duplicate link kontrolu
        seen_links = set()
        unique = []
        for entry in all_entries:
            if entry['link'] not in seen_links:
                seen_links.add(entry['link'])
                unique.append(entry)

        print("=" * 80)
        print(f"TOPLAM {len(unique)} DEVTOOLS GUNCELLEMESI CEKILDI")
        print("=" * 80)
        return unique

    def process_entries(self, entries: List[Dict]) -> List[Dict]:
        """DevTools haberlerini Turkceye cevirir"""
        processed = []
        total = len(entries)
        print(f"\nDevTools guncellemeleri cevriliyor ({total} adet)...")

        for i, entry in enumerate(entries, 1):
            try:
                if i % 10 == 0:
                    print(f"  Cevriliyor: {i}/{total}")
                try:
                    translated_title = self.translate_text(entry['title'])
                except Exception:
                    translated_title = entry['title']
                translated_desc = self.translate_long_text(entry['description'])
                processed.append({
                    'original_title': entry['title'],
                    'turkish_title': translated_title,
                    'original_description': entry['description'],
                    'turkish_description': translated_desc,
                    'link': entry['link'],
                    'published_date': entry['date'],
                    'source': entry['source'],
                    'version': entry.get('version', ''),
                    'entry_type': entry.get('entry_type', 'release'),
                })
            except Exception as e:
                print(f"  DevTools haber isleme hatasi: {e}")
                processed.append({
                    'original_title': entry['title'],
                    'turkish_title': entry['title'],
                    'original_description': entry['description'],
                    'turkish_description': entry['description'],
                    'link': entry['link'],
                    'published_date': entry['date'],
                    'source': entry['source'],
                    'version': entry.get('version', ''),
                    'entry_type': entry.get('entry_type', 'release'),
                })

        print(f"Ceviri tamamlandi: {len(processed)} DevTools guncellemesi islendi")
        return processed


if __name__ == "__main__":
    scraper = MultiDevToolsScraper()
    entries = scraper.fetch_all(days=60)
    print(f"\nToplam {len(entries)} DevTools guncellemesi cekildi")
    for e in entries[:15]:
        print(f"  [{e['source']:12s}] {e['date']} | {e.get('version',''):15s} | {e['title'][:55]}")
