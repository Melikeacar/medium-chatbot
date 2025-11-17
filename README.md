# Medium Chatbot 🤖  

_Senin Makalelerin, Senin AI Editörün_

Medium Chatbot, Medium makalelerini otomatik olarak tarayan, başlık–yazar–link bilgisini çıkaran, içeriği analiz eden ve profesyonel bir kontrol listesine göre puanlayan yapay zekâ destekli bir analiz aracıdır.  

Sistem; içerik yapısı, dil kalitesi, özgünlük, teknik doğruluk ve görsel kaynak uyumu gibi kritik noktaları değerlendirerek **0–100 arası final puan**, kategori ve kullanıcı dostu bir rapor üretir.

---

## 🎥 Demo (Yerel Çalışma)

Flask backend’i çalıştırdıktan sonra tarayıcıdan:

`http://127.0.0.1:5000`

adresine giderek Medium linklerini analiz edebilirsin.

---

## 🧩 Teknik Mimari

Medium Chatbot’un mimarisi aşağıdaki bileşenlerden oluşur:

| Bileşen                | Teknoloji / Dil                  | Sorumluluklar                                                                 |
|------------------------|----------------------------------|-------------------------------------------------------------------------------|
| **Flask Backend**      | Python 3.13, Flask, Flask-CORS   | API uç noktaları, istek–yanıt akışı, analiz sonuçlarını frontend’e aktarma   |
| **Yerel LLM Servisi**  | Ollama, Llama 3.1 8B             | Prompt’ları işleme, JSON formatlı analiz çıktısı üretme                      |
| **Scraper**            | Requests, BeautifulSoup          | Medium makalesini HTML’den çekme ve sadeleştirme                             |
| **Frontend Arayüzü**   | HTML, CSS, JavaScript            | Link girişi, “Analiz Et” butonu, sonuçların tablo/karte olarak gösterimi     |
| **Checklist Sistemi**  | `config/checklist.json`          | Kural ID’leri, açıklamalar, ağırlıklar, puanlama aralıkları                  |
| **Prompt Yönetimi**    | `config/prompts.json`            | Sistem rolü, görev tanımı, JSON şeması ve örnek analiz prompt’ları           |

---

## ✨ Özellikler

### 🎯 Makale Analizi
- Başlık, yazar ve URL bilgisini otomatik çıkarır  
- İçerikten özet üretir (sınırlı karakterle)  
- Checklist kurallarına göre her maddeyi değerlendirir  
- Her kural için durum: **uygun / kismen_uygun / uygun_degil / belirsiz**  
- 0–10 arası puan verip ağırlıklarla **0–100 final skor** hesaplar  

### 🤖 Yapay Zekâ Destekli Süreç
- Ollama üzerinde çalışan **Llama 3.1 8B** modeli kullanılır  
- Çıktı formatı sıkı bir JSON şemasına zorlanır  
- Gelen yanıt içinden JSON’ı otomatik ayıklar ve temizler  
- JSON parse hataları için ek kontrol adımları içerir  

### 🔍 Scraper
- Medium makalesinin HTML içeriğini indirir  
- Gereksiz script/style tag’lerini temizler  
- Analiz için anlamlı gövde metnini çıkarır  

### 📊 Sonuç Çıktısı
- Makalenin temel bilgileri (başlık, yazar, link, kelime sayısı)  
- Kurallara göre detaylı değerlendirme listesi  
- Final puan ve kategori (mükemmel / iyi / orta / zayıf / başarısız)  
- Kullanıcıya okunabilir kısa özet rapor  

---

## ⚙️ Kurulum

 1️⃣ Depoyu Klonla

```bash
git clone https://github.com/Melikeacar/medium-chatbot.git
cd medium-chatbot


2️⃣ Sanal Ortam Oluştur
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows


3️⃣ Bağımlılıkları Kur
```bash
pip install -r requirements.txt


4️⃣ Ollama Modelini İndir
```bash
ollama pull llama3.1:8b-instruct-q4_0

Ollama servisinin çalıştığından emin ol:
```bash
ollama serve

5️⃣ Backend’i Başlat
```bash
cd src
python main.py


medium-chatbot/
│
├── config/
│   ├── checklist.json        # Kural ve ağırlık sistemi
│   └── prompts.json          # AI prompt yapılandırması
│
├── src/
│   ├── main.py               # Flask uygulama girişi
│   ├── analyzer.py           # Analiz ve puanlama mantığı
│   ├── scraper.py            # Medium içerik çekici
│   └── templates/
│       └── index.html        # Web arayüzü
│
├── requirements.txt
├── Dockerfile
└── README.md


🧠 Analiz Akışı

Kullanıcı Medium linkini arayüze girer

Backend, scraper.py ile makaleyi indirir

analyzer.py, checklist ve prompt’ları yükler

Prompt hazırlanıp Ollama’ya gönderilir

LLM yanıtından JSON analiz sonucu çıkarılır

Ağırlıklı puan hesaplanır ve kullanıcıya gösterilir



📦 Kullanılan Teknolojiler

Backend

Python 3.13
Flask
Flask-CORS
Requests

AI

Ollama
Llama 3.1 8B
JSON tabanlı prompt tasarımı

Frontend
HTML
CSS
Vanilla JavaScript


