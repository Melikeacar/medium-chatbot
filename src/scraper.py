import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
import json
import unicodedata
import html


class MediumScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/123.0.0.0 Safari/537.36'),
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        })

    def is_valid_medium_url(self, url):
        try:
            parsed = urlparse(url)
            host = (parsed.netloc or '').lower()
            return ('medium.com' in host) or host.endswith('.medium.com')
        except:
            return False

    def clean_text(self, text: str) -> str:
        """Metni normalize eder ve gereksiz boşlukları kaldırır"""
        if not text:
            return ""
        # HTML entity decode
        text = html.unescape(text)
        # Unicode normalizasyonu (Türkçe karakterler için güvenli)
        text = unicodedata.normalize("NFC", text)
        # Sabit boşlukları temizle
        text = text.replace('\u00a0', ' ')
        # Fazla boşlukları teke indir
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_from_ldjson(self, soup):
        """script[type=application/ld+json] içinden başlık/yazar yakalamaya çalışır"""
        try:
            for tag in soup.find_all("script", {"type": "application/ld+json"}):
                if not tag.string:
                    continue
                obj = json.loads(tag.string)
                items = obj if isinstance(obj, list) else [obj]
                for it in items:
                    t = it.get("@type") or it.get("type")
                    if t in ("Article", "NewsArticle", "BlogPosting"):
                        headline = it.get("headline") or it.get("name") or ""
                        # author dict ya da liste olabilir
                        auth = it.get("author")
                        author = ""
                        if isinstance(auth, dict):
                            author = auth.get("name", "")
                        elif isinstance(auth, list) and auth:
                            if isinstance(auth[0], dict):
                                author = auth[0].get("name", "")
                            else:
                                author = str(auth[0])
                        return {
                            "title": self.clean_text(headline),
                            "author": self.clean_text(author)
                        }
        except Exception:
            pass
        return None

    def _extract_title(self, soup):
        """Çeşitli fallback’larla başlık yakala"""
        selectors = [
            'h1[data-testid="storyTitle"]',
            'h1.graf--title',
            'h1',
            '.graf--title',
            'meta[property="og:title"]',
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                if el.name == 'meta':
                    return self.clean_text(el.get('content', ''))
                return self.clean_text(el.get_text())
        t = soup.find('title')
        if t:
            return self.clean_text(t.get_text())
        return ""

    def _extract_author(self, soup):
        """Çeşitli fallback’larla yazar yakala"""
        selectors = [
            '[data-testid="authorName"]',
            '.author-name',
            '.js-authorName',
            'meta[name="author"]',
            'a[rel="author"]',
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                if el.name == 'meta':
                    return self.clean_text(el.get('content', ''))
                return self.clean_text(el.get_text())
        return ""

    def _extract_content(self, soup):
        """İçeriği mümkün olduğunca kapsamlı yakala"""
        content_selectors = [
            '[data-testid="storyContent"]',
            'article section',
            'article',
            '.postArticle-content',
            '.section-content',
            'section[tabindex]',
            'div[data-field="body"]',
        ]

        paragraphs = []
        for sel in content_selectors:
            nodes = soup.select(sel)
            if not nodes:
                continue
            for el in nodes:
                for para in el.find_all(['p', 'li', 'pre', 'code', 'h2', 'h3', 'h4']):
                    text = self.clean_text(para.get_text())
                    if text and len(text) > 5:
                        paragraphs.append(text)
            if paragraphs:
                break

        if not paragraphs:
            for p in soup.find_all('p'):
                text = self.clean_text(p.get_text())
                if text and len(text) > 10:
                    paragraphs.append(text)

        return '\n\n'.join(paragraphs)

    def extract_article_content(self, url):
        """Medium makalesinin içeriğini çeker"""
        try:
            if not self.is_valid_medium_url(url):
                return {'success': False, 'error': 'Geçerli bir Medium URL\'si değil'}

            last_exc = None
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    last_exc = e
                    if attempt == 2:
                        raise
                    time.sleep(1.2 * (attempt + 1))

            if response is None:
                raise last_exc or Exception("Bilinmeyen istek hatası")

            # Türkçe karakterler bozulmasın diye UTF-8’e sabitliyoruz
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, 'html.parser')

            # ld+json
            title = ""
            author = ""
            ld = self._extract_from_ldjson(soup)
            if ld:
                title = ld.get("title") or ""
                author = ld.get("author") or ""

            if not title:
                title = self._extract_title(soup)

            content = self._extract_content(soup)

            if not author:
                author = self._extract_author(soup)

            if not title and not content:
                return {'success': False, 'error': 'Makale içeriği çekilemedi. Sayfa yapısı tanınmıyor.'}

            return {
                'success': True,
                'title': title,
                'content': content,
                'author': author,
                'url': url,
                'word_count': len(content.split()) if content else 0
            }

        except requests.RequestException as e:
            return {'success': False, 'error': f'HTTP Hatası: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Genel Hata: {str(e)}'}

    def test_scraper(self):
        test_urls = [
            "https://medium.com/@example/test-article",  # buraya gerçek URL gir
        ]
        for url in test_urls:
            print(f"Test ediliyor: {url}")
            result = self.extract_article_content(url)
            if result['success']:
                print(f"✓ Başarılı: {result['title'][:80]}...")
                print(f"  Kelime sayısı: {result['word_count']}")
                print(f"  Yazar: {result['author']}")
            else:
                print(f"✗ Hata: {result['error']}")
            print("-" * 50)


if __name__ == "__main__":
    scraper = MediumScraper()
    scraper.test_scraper()
