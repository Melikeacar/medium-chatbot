import json
import requests
import re
from typing import Dict
from datetime import datetime
import unicodedata
import os


class ContentAnalyzer:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = os.getenv("OLLAMA_URL", ollama_url)
        self.model_name = "llama3.1:8b-instruct-q4_0"
        
       
        self.checklist = self.load_json('config/checklist.json')
        self.prompts = self.load_json('config/prompts.json')
    
    def load_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON yükleme hatası ({file_path}): {e}")
            return {}
        
    
    def test_ollama_connection(self):
        """Ollama bağlantısını test eder"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def call_ollama(self, prompt: str, temperature=0.1) -> Dict:
        """Ollama API'sine istek gönderir (JSON çıktısını zorlar)"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
                "format": "json",   
                "options": {
                    "num_predict": 2048,
                    "top_k": 10,
                    "top_p": 0.9
                }
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=180
            )
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result.get('response', ''),  # JSON string bekliyoruz
                    'done': result.get('done', False)
                }
            else:
                return {'success': False, 'error': f"API Hatası: {response.status_code}"}
        except requests.RequestException as e:
            return {'success': False, 'error': f"Bağlantı Hatası: {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': f"Genel Hata: {str(e)}"}
    
    def build_analysis_prompt(self, article_data: Dict) -> str:
        """Analiz için prompt oluşturur"""
        # Checklist metni
        lines = []
        for i, rule in enumerate(self.checklist.get('kontrol_maddeleri', []), 1):
            kw = ', '.join(rule.get('anahtar_kelimeler', [])[:5])
            lines.append(
                f"{i}. {rule['baslik']} (ID: {rule['id']})\n"
                f"   - Açıklama: {rule['aciklama']}\n"
                f"   - Ağırlık: {rule['agirlik']}/10\n"
                f"   - Anahtar Kelimeler: {kw}\n"
            )
        checklist_text = "\n".join(lines)

        json_template = json.dumps(
           self.prompts.get('ana_analiz_prompt', {}).get('json_sablonu', {}),
           ensure_ascii=False, indent=2
        )

        title   = article_data.get('title', '')
        author  = article_data.get('author', '')
        url     = article_data.get('url', '')
        content = (article_data.get('content', '') or '')[:3000]

        sistem_rolu     = self.prompts['ana_analiz_prompt']['sistem_rolu']
        gorev_tanimi    = self.prompts['ana_analiz_prompt']['gorev_tanimi']
        format_talimati = self.prompts['ana_analiz_prompt']['format_talimati']

        return (
            f"{sistem_rolu}\n\n"
            f"Görev: {gorev_tanimi}\n\n"
            f"Format Talimatı: {format_talimati}\n\n"
            f"Makale Bilgileri:\n- Başlık: {title}\n- Yazar: {author}\n- Link: {url}\n\n"
            f"İçerik (özet):\n{content}\n\n"
            f"DEĞERLENDİRİLECEK KONTROL LİSTESİ:\n{checklist_text}\n\n"
            f"SADECE AŞAĞIDAKİ JSON ŞEMASINA UYAN TEK BİR JSON NESNESİ DÖN:\n{json_template}\n\n"
            "JSON DIŞI TEK KARAKTER YAZMA. Bilinmeyen alanları boş string ('') bırak."
        )  


    def extract_json_from_response(self, response_text: str) -> Dict:
        """LLM yanıtından JSON'ı güvenli şekilde çıkarır."""
        try:
            text = response_text if isinstance(response_text, str) else str(response_text)

            # 0) Ollama format:"json" ise genelde direkt parse edilebilir
            try:
                return json.loads(text)
            except Exception:
                pass

            # 1) ```json ... ``` bloğu varsa onu al
            fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
            if fence_match:
                candidate = fence_match.group(1).strip()
            else:
                # 2) İlk { ile son } arası (greedy) — serbest metinden JSON'ı ayıkla
                start = text.find('{')
                end = text.rfind('}')
                if start == -1 or end == -1 or end <= start:
                    print("JSON nesnesi bulunamadı.")
                    print("Gelen yanıt:", text[:300])
                    return None
                candidate = text[start:end+1]

            # 3) Temizlik
            json_str = candidate.strip().strip('`').strip()
            json_str = re.sub(r',\s*}', '}', json_str)   # ",}" -> "}"
            json_str = re.sub(r',\s*]', ']', json_str)   # ",]" -> "]"
            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)  # // yorum
            json_str = re.sub(r'/\*[\s\S]*?\*/', '', json_str)              # /* ... */ yorum

            # 4) Parse et
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse hatası: {e}")
            try:
                print("Hata konumu:", json_str[max(0, e.pos-30): e.pos+30])  # type: ignore
            except Exception:
                pass
            return None
        except Exception as e:
            print(f"Genel hata: {e}")
            return None
    
    def calculate_final_score(self, analysis_result: Dict) -> Dict:
        """Final puanlamayı hesaplar (0–100 ölçeği)"""
        try:
            if not analysis_result or 'detaylar' not in analysis_result:
                return {'puan': 0, 'kategori': 'basarisiz', 'aciklama': 'Analiz başarısız'}
            
            total_weight = 0
            weighted_score = 0
            
            for detail in analysis_result['detaylar']:
                rule_id = detail.get('kural_id', '')
                rule_score = detail.get('puan', 0)  # 0–10 bekleniyor
                
                weight = 5
                for rule in self.checklist.get('kontrol_maddeleri', []):
                    if rule['id'] == rule_id:
                        weight = rule['agirlik']
                        break
                
                total_weight += weight
                weighted_score += rule_score * weight
            
            final_score = int((weighted_score / total_weight) * 10) if total_weight > 0 else 0  # 0–100

            # Kategori eşlemesi (kullanıcının checklist.json'ına uygun)
            category = 'basarisiz'
            description = ''
            for cat_name, cat_info in self.checklist['puanlama_sistemi']['araliklar'].items():
                if cat_info['min'] <= final_score <= cat_info['max']:
                    category = cat_name
                    description = self.checklist['puanlama_sistemi']['araliklar'][cat_name]['aciklama']
                    break
            
            return {'puan': final_score, 'kategori': category, 'aciklama': description}
        except Exception as e:
            print(f"Puan hesaplama hatası: {e}")
            return {'puan': 0, 'kategori': 'basarisiz', 'aciklama': 'Hesaplama hatası'}
    
    def analyze_article(self, article_data: Dict) -> Dict:
        """Makaleyi analiz eder"""
        if not self.test_ollama_connection():
            return {
                'success': False,
                'error': 'Ollama bağlantısı kurulamadı. Ollama çalışıyor mu?'
            }
        
        prompt = self.build_analysis_prompt(article_data)
        llm_response = self.call_ollama(prompt)
        
        if not llm_response['success']:
            return {'success': False, 'error': llm_response['error']}
        
        analysis_json = self.extract_json_from_response(llm_response['content'])
        
        if not analysis_json:
            return {
                'success': False,
                'error': 'LLM yanıtından JSON çıkarılamadı',
                'raw_response': llm_response.get('content', '')[:500]
            }
        
        final_scoring = self.calculate_final_score(analysis_json)
        
        result = {
            'success': True,
            'makale_bilgi': {
                'baslik': article_data.get('title', ''),
                'yazar': article_data.get('author', ''),
                'url': article_data.get('url', ''),
                'kelime_sayisi': article_data.get('word_count', 0)
            },
            'analiz_sonucu': analysis_json,
            'final_puanlama': final_scoring,
            'timestamp': self.get_timestamp()
        }
        return result
    
    def get_timestamp(self):
        """Zaman damgası üretir"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def format_result_for_user(self, analysis_result: Dict) -> str:
        """Sonuçları kullanıcı dostu formatta döndürür"""
        if not analysis_result['success']:
            return f"❌ Analiz Hatası: {analysis_result['error']}"

        makale = analysis_result['makale_bilgi']
        final = analysis_result['final_puanlama']

        analiz_sonucu = analysis_result.get('analiz_sonucu', {})
        detaylar = analiz_sonucu.get('detaylar', [])

        emoji_map = {
            'mukemmel': '🏆',
            'iyi': '✅',
            'orta': '⚠️',
            'zayif': '❌',
            'basarisiz': '🚫'
        }
        emoji = emoji_map.get(final['kategori'], '📊')

        result_text = f"""
{emoji} **Analiz Raporu**

📄 **Makale:** {makale.get('baslik','')[:50]}...
👤 **Yazar:** {makale.get('yazar','')}
📊 **Final Puan:** {final.get('puan',0)}/100 - {final.get('kategori','').upper()}
📝 **Durum:** {final.get('aciklama','')}

🔍 **Detay Analiz:**
"""
        if not detaylar:
            result_text += "\n⚠️ Detaylı analiz verisi bulunamadı."
        else:
            for detail in detaylar:
                durum = detail.get('durum', '')
                status_emoji = "✅" if durum == 'uygun' else ("⚠️" if durum == 'kismen_uygun' else "❌")
                baslik = detail.get('kural_baslik', '(başlık yok)')
                acik = detail.get('aciklama', '')
                result_text += f"\n{status_emoji} **{baslik}**: {acik[:100]}..."

        return result_text


# Test fonksiyonu
def quick_test():
    analyzer = ContentAnalyzer()
    
    test_article = {
        'title': 'Test Makale',
        'content': 'Bu basit bir test içeriğidir.',
        'author': 'Test Yazar',
        'url': 'https://test.com',
        'word_count': 5
    }
    
    result = analyzer.analyze_article(test_article)
    
    if not result['success']:
        print(f"HATA: {result['error']}")
        if 'raw_response' in result:
            print("RAW:", result['raw_response'])
    else:
        print("BAŞARILI!")
        print(analyzer.format_result_for_user(result))

if __name__ == "__main__":
    quick_test()
