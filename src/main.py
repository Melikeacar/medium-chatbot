
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR) 


import analyzer as analyzer_module
print(f"[DEBUG] analyzer module path => {analyzer_module.__file__}")

from scraper import MediumScraper
from analyzer import ContentAnalyzer


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'your-secret-key-change-this' 
CORS(app)

scraper = MediumScraper()
analyzer = ContentAnalyzer()


analysis_history = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_article():
    """Makale analizi endpoint'i"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'URL gerekli'}), 400

        url = data['url'].strip()
        if not url:
            return jsonify({'success': False, 'error': 'Boş URL'}), 400

      
        session['analysis_status'] = 'scraping'
        scraping_result = scraper.extract_article_content(url)
        if not scraping_result['success']:
            return jsonify({
                'success': False,
                'error': f"Scraping Hatası: {scraping_result['error']}"
            }), 400

        
        session['analysis_status'] = 'analyzing'
        analysis_result = analyzer.analyze_article(scraping_result)

        if not analysis_result['success']:
            
            return jsonify({
                'success': False,
                'error': f"Analiz Hatası: {analysis_result.get('error', '')}",
                'raw_response': analysis_result.get('raw_response', '')
            }), 500

  
        session['analysis_status'] = 'formatting'
        formatted_result = format_analysis_for_api(analysis_result)

        add_to_history(formatted_result)
        session['analysis_status'] = 'completed'

        return jsonify({'success': True, 'data': formatted_result})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Beklenmeyen hata: {str(e)}'}), 500


@app.route('/status')
def get_status():
    return jsonify({'status': session.get('analysis_status', 'idle')})


@app.route('/history')
def get_history():
    return jsonify({'success': True, 'data': analysis_history[-10:]})


@app.route('/health')
def health_check():
    try:
        ollama_status = analyzer.test_ollama_connection()
        return jsonify({
            'status': 'healthy',
            'components': {
                'scraper': True,
                'analyzer': True,
                'ollama': ollama_status
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/quick-check', methods=['POST'])
def quick_check():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'valid': False, 'reason': 'Boş URL'})
        is_valid = scraper.is_valid_medium_url(url)
        return jsonify({
            'valid': is_valid,
            'reason': 'Geçerli Medium URL' if is_valid else 'Geçersiz Medium URL'
        })
    except Exception as e:
        return jsonify({'valid': False, 'reason': str(e)})


# Yardımcı fonksiyonlar
def format_analysis_for_api(analysis_result):
    try:
        makale = analysis_result['makale_bilgi']
        final = analysis_result['final_puanlama']
        detaylar = analysis_result['analiz_sonucu'].get('detaylar', [])

        emoji_map = {
            'mukemmel': '🏆',
            'iyi': '✅',
            'orta': '⚠️',
            'zayif': '❌',
            'basarisiz': '🚫'
        }

        uygun_kurallar = []
        uygun_olmayan_kurallar = []

        for detail in detaylar:
            rule_data = {
                'id': detail.get('kural_id', ''),
                'baslik': detail.get('kural_baslik', ''),
                'durum': detail.get('durum', ''),
                'puan': detail.get('puan', 0),
                'aciklama': detail.get('aciklama', ''),
                'ornekler': detail.get('ornek', '')
            }
            if detail.get('durum') == 'uygun':
                uygun_kurallar.append(rule_data)
            else:
                uygun_olmayan_kurallar.append(rule_data)

        return {
            'id': f"analysis_{int(time.time())}",
            'timestamp': analysis_result.get('timestamp'),
            'makale': makale,
            'puan': {
                'deger': final.get('puan', 0),
                'kategori': final.get('kategori', 'basarisiz'),
                'aciklama': final.get('aciklama', ''),
                'emoji': emoji_map.get(final.get('kategori', 'basarisiz'), '📊')
            },
            'kural_analizi': {
                'toplam_kural': len(detaylar),
                'uygun': len(uygun_kurallar),
                'uygun_olmayan': len(uygun_olmayan_kurallar),
                'uygun_kurallar': uygun_kurallar,
                'uygun_olmayan_kurallar': uygun_olmayan_kurallar
            },
            'oneri': analysis_result['analiz_sonucu'].get('oneriler', [])
        }
    except Exception as e:
        return {'error': f'Format hatası: {str(e)}', 'raw_data': analysis_result}


def add_to_history(analysis_data):
    if len(analysis_history) >= 50:
        analysis_history.pop(0)
    analysis_history.append(analysis_data)


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500


@app.route('/clear-history', methods=['POST'])
def clear_history():
    global analysis_history
    analysis_history.clear()
    return jsonify({'success': True, 'message': 'Analiz geçmişi temizlendi'})



if __name__ == '__main__':
    print("🚀 Medium Checker başlatılıyor...")
    print(f"📁 Çalışma dizini: {os.getcwd()}")

    if analyzer.test_ollama_connection():
        print("✅ Ollama bağlantısı başarılı")
    else:
        print("⚠️ Ollama bağlantısı kurulamadı. Lütfen 'ollama serve' komutunu çalıştırın.")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
