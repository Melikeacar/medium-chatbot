📄 Medium Chatbot
"Medium makalelerini profesyonel editör gibi analiz eden yapay zekâ asistanı"

Medium Chatbot, Medium makalelerinin içeriğini otomatik olarak tarayan, başlık-yazar-link bilgisini çıkaran, metni analiz eden ve profesyonel bir içerik denetim checklist’ine göre puanlayan bir yapay zekâ destekli analiz platformudur.

Sistem; içerik yapısı, özgünlük, dil kalitesi, teknik doğruluk, konu bütünlüğü ve görsel kaynak uyumu gibi kritik noktaları değerlendirerek 0–100 arası final puan, kategori sınıfı ve kullanıcı dostu detay raporu üretir.

🎥 Demo (Yerel Çalışma)

Flask tabanlı backend’i çalıştırdıktan sonra tarayıcıdan:

http://127.0.0.1:5000


Arayüzden Medium linki girerek anında analiz yapabilirsiniz.

🧩 Teknik Mimari

Medium Chatbot’un mimarisi aşağıdaki bileşenlerden oluşur:

Bileşen	Teknoloji / Dil	Sorumluluk
Flask Backend	Python 3.13, Flask, Flask-CORS	API uç noktaları, AI çağrıları, skor hesaplama
Yerel LLM Servisi	Ollama + Llama 3.1 8B	JSON formatlı analiz çıktısı üretme
Scraper Servisi	BeautifulSoup, Requests	Medium makalelerini HTML’den temiz formatta çekme
Frontend Arayüzü	HTML, CSS, JavaScript	Analiz ekranı, sonuçların görselleştirilmesi
Checklist Sistemi	JSON	Kural bazlı analiz, ağırlıklandırma
Prompt Yönetimi	JSON	Sistem rolü, görev tanımı, analiz formatı
✨ Özellikler
🎯 Makale Kalite Analizi

Başlık, yazar, url çıkarma

İçerik özetleme

Kural tabanlı denetim (checklist)

Özgünlük kontrolü (anahtar kelime eşleşmeleri)

Görsel kaynak uyumu

Ağırlıklı final puanı

🤖 Yapay Zekâ Destekli İşleme

Ollama üzerinde çalışan Llama 3.1 modeli

Tanımlı JSON şeması

Hatalı JSON’u otomatik düzeltme

0–100 skor hesaplama

🔍 Web Scraper

HTML tag temizleme

Gereksiz script/style kaldırma

3000 karakterlik içerik özeti

📊 Kullanıcıya Gösterilen Sonuç

Makale bilgisi

Detaylı kural değerlendirmeleri

Uygun / Kısmen Uygun / Uygun Değil durumları

0–100 final puanı

Kategori etiketi (mükemmel / iyi / orta / zayıf / başarısız)

⚙️ Kurulum
1️⃣ Depoyu Klonla
git clone https://github.com/Melikeacar/medium-chatbot.git
cd medium-chatbot

2️⃣ Sanal Ortam Oluştur
python -m venv venv
.\venv\Scripts\activate   # Windows

3️⃣ Gereksinimleri Yükle
pip install -r requirements.txt

4️⃣ Ollama İçin Modeli İndir
ollama pull llama3.1:8b-instruct-q4_0

5️⃣ Backend’i Başlat
cd src
python main.py


Tarayıcıdan:

http://127.0.0.1:5000

📁 Proje Yapısı
medium-chatbot/
│
├── config/
│   ├── checklist.json        # Kurallar & ağırlıklar
│   └── prompts.json          # Prompt yönetimi
│
├── src/
│   ├── main.py               # Flask backend
│   ├── analyzer.py           # AI analiz motoru
│   ├── scraper.py            # Medium scraper
│   └── templates/
│       └── index.html        # Web arayüzü
│
├── requirements.txt
├── Dockerfile
└── README.md

🧠 Analiz Süreci

Medium linki frontend’e girilir

Backend → scraper ile makaleyi indirir

Analyzer → prompt'u oluşturur

Ollama → JSON output gönderir

Sistem → JSON’dan skor hesaplar

Sonuç kullanıcıya sunulur

📦 Kullanılan Teknolojiler
Backend

Python 3.13

Flask

Requests

JSON

AI

Ollama

Llama 3.1 8B

Prompt Engineering

Frontend

HTML

CSS

JavaScript

🤝 Katkıda Bulunma

Fork yap

Branch oluştur

Commit gönder

Pull request aç

📝 Lisans

Bu proje MIT lisansı ile sunulmuştur.
