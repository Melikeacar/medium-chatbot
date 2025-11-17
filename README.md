# Medium Chatbot 🤖  
_Senin Makalelerin, Senin AI Editörün_

Medium Chatbot, Medium makalelerini otomatik olarak tarayan, başlık–yazar–link bilgisini çıkaran, içeriği analiz eden ve profesyonel bir kontrol listesine göre puanlayan yapay zekâ destekli bir analiz aracıdır.

Sistem; içerik yapısı, dil kalitesi, özgünlük, teknik doğruluk ve görsel kaynak uyumu gibi kritik noktaları değerlendirerek **0–100 arası final puan**, kategori ve kullanıcı dostu bir rapor üretir.

---

## 🧩 Teknik Mimari

Medium Chatbot’un mimarisi aşağıdaki bileşenlerden oluşur:

| Bileşen                | Teknoloji / Dil                  | Sorumluluklar                                                                 |
|------------------------|----------------------------------|-------------------------------------------------------------------------------|
| **Flask Backend**      | Python 3.13, Flask, Flask-CORS   | API uç noktaları, istek–yanıt akışı, analiz sonuçlarını frontend’e aktarma   |
| **Yerel LLM Servisi**  | Ollama, Llama 3.1 8B             | Prompt’ları işleme, JSON formatlı analiz çıktısı üretme                      |
| **Scraper**            | Requests, BeautifulSoup          | Medium makalesini HTML’den çekme ve sadeleştirme                             |
| **Frontend Arayüzü**   | HTML, CSS, JavaScript            | Link girişi, “Analiz Et” butonu, sonuçların gösterimi                       |
| **Checklist Sistemi**  | `config/checklist.json`          | Tüm içerik kalite kuralları, ağırlıklar, puanlama aralıkları                |
| **Prompt Yönetimi**    | `config/prompts.json`            | Sistem rolü, görev tanımı, JSON şeması                                       |

---

## ✨ Özellikler

### 🎯 Makale Analizi
- Başlık, yazar ve URL bilgisini otomatik çıkarır  
- İçerik özetleme (3000 karakter temiz metin)  
- Kural tabanlı denetim (checklist)  
- Her kural için durum: **uygun / kismen_uygun / uygun_degil / belirsiz**  
- Ağırlıklı final puan hesaplama  

### 🤖 Yapay Zekâ Destekli Analiz
- Ollama üzerinde **Llama 3.1:8B** modeli  
- Temiz JSON formatlı çıktı  
- JSON parse hatalarını otomatik düzeltme  
- Hatalı metinden doğru JSON çıkarma  

### 🔍 Scraper
- HTML tag temizleme  
- Gereksiz script/style kaldırma  
- Analiz için anlamlı gövde metni çıkarma  

### 📊 Sonuç Raporu
- Makale bilgisi (başlık, yazar, link)  
- Kural bazlı detaylı değerlendirme  
- Final puanı ve kategori etiketi  
- Okunabilir sade rapor  

---

## ⚙️ Kurulum

### 1. Depoyu Klonla

```bash
git clone https://github.com/Melikeacar/medium-chatbot.git
cd medium-chatbot
2. Sanal Ortam Oluştur
bash
Kodu kopyala
python -m venv venv
.\venv\Scripts\activate   # Windows
3. Bağımlılıkları Kur
bash
Kodu kopyala
pip install -r requirements.txt
4. Ollama Modelini İndir
bash
Kodu kopyala
ollama pull llama3.1:8b-instruct-q4_0
Ollama servisinin çalıştığını doğrulayın:

bash
Kodu kopyala
ollama serve
5. Backend’i Başlat
bash
Kodu kopyala
cd src
python main.py
Tarayıcıdan açın:

http://127.0.0.1:5000
