import google.generativeai as genai
import json
import os
from datetime import datetime

# Türkçe tarih
aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
         "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
bugun = datetime.now()
tarih_tr = f"{bugun.day} {aylar[bugun.month-1]} {bugun.year}"
gun_tr = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"][bugun.weekday()]

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT = f"""Bugün {gun_tr}, {tarih_tr}. 

Aşağıdaki kategorilerde bugünün en önemli, gerçek ve güncel haberlerini topla. Yalnızca şu kaynaklardan seç: The Guardian, MIT Technology Review, Nature, Science, Reuters, BBC, AP, NPR, The Atlantic, Wired, NEJM, The Economist, Lancet, New Scientist.

KATEGORİLER:
- Dünyadan: 3 haber
- Teknoloji & Yapay Zeka: 3 haber  
- Bilim & Sağlık: 2 haber
- Kültür & Kitap: 2 haber

SADECE JSON döndür, başka hiçbir şey yazma, markdown kullanma:
{{
  "tarih": "{tarih_tr}",
  "gun": "{gun_tr}",
  "kategoriler": [
    {{
      "baslik": "Dünyadan",
      "emoji": "🌍",
      "renk": "#c0392b",
      "haberler": [
        {{
          "baslik": "Ana bilgi — sonuç veya önemli bağlam",
          "kaynak": "The Guardian",
          "link": "https://theguardian.com",
          "etiket": "Politika"
        }}
      ]
    }},
    {{
      "baslik": "Teknoloji & Yapay Zeka",
      "emoji": "⚡",
      "renk": "#2471a3",
      "haberler": []
    }},
    {{
      "baslik": "Bilim & Sağlık",
      "emoji": "🔬",
      "renk": "#1e8449",
      "haberler": []
    }},
    {{
      "baslik": "Kültür & Kitap",
      "emoji": "📚",
      "renk": "#7d3c98",
      "haberler": []
    }}
  ]
}}

Kurallar:
- Türkçe yaz
- Em dash (—) kullan ayraç olarak
- Gerçek, doğrulanabilir haberler seç
- Etiket kısa: Politika, Sağlık, Uzay, AI, Kitap vb.
- link alanına o kaynağın ana URL'sini yaz"""

print("Gemini API'ye bağlanılıyor...")

response = model.generate_content(PROMPT)
raw = response.text.strip()

# JSON temizle
if "```json" in raw:
    raw = raw.split("```json")[1].split("```")[0].strip()
elif "```" in raw:
    raw = raw.split("```")[1].split("```")[0].strip()

data = json.loads(raw)
print(f"Haberler alındı: {data['tarih']}")

# HTML oluştur
kategoriler_html = ""
for kat in data["kategoriler"]:
    haberler_html = ""
    for i, haber in enumerate(kat["haberler"]):
        delay = i * 80
        haberler_html += f"""
        <div class="haber" style="animation-delay:{delay}ms">
          <span class="nokta" style="background:{kat['renk']}"></span>
          <span class="haber-metin">{haber['baslik']}</span>
          <div class="haber-meta">
            <span class="etiket" style="background:{kat['renk']}">{haber['etiket']}</span>
            <a href="{haber['link']}" target="_blank" rel="noopener" class="kaynak-link" style="color:{kat['renk']}">{haber['kaynak']} →</a>
          </div>
        </div>"""

    kategoriler_html += f"""
    <section class="kategori">
      <div class="kat-baslik" style="color:{kat['renk']};border-bottom-color:{kat['renk']}">
        <span>{kat['emoji']}</span>
        <h2>{kat['baslik']}</h2>
      </div>
      <div class="haberler">{haberler_html}</div>
    </section>"""

html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Günün Akışı — {data['tarih']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&display=swap" rel="stylesheet">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#f5f0e8;font-family:'Source Serif 4',Georgia,serif;color:#1a1a1a;min-height:100vh}}
    .masthead{{background:#1a1a1a;color:#f5f0e8;border-bottom:4px solid #c0392b}}
    .masthead-ust{{display:flex;justify-content:space-between;align-items:center;padding:8px 40px;border-bottom:1px solid #333;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#888}}
    .masthead-orta{{text-align:center;padding:20px 40px 16px}}
    .masthead-orta h1{{font-family:'Playfair Display',serif;font-size:clamp(36px,7vw,80px);font-weight:900;letter-spacing:-.02em;line-height:1}}
    .masthead-orta p{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#666;margin-top:8px}}
    .icerik{{max-width:860px;margin:0 auto;padding:48px 20px 80px}}
    .tarih-bant{{text-align:center;padding-bottom:32px;margin-bottom:40px;border-bottom:1px solid #ccc}}
    .tarih-bant span{{font-size:12px;letter-spacing:.15em;text-transform:uppercase;color:#888}}
    .kategori{{margin-bottom:48px}}
    .kat-baslik{{display:flex;align-items:center;gap:10px;margin-bottom:20px;padding-bottom:10px;border-bottom:3px solid}}
    .kat-baslik h2{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700}}
    .haber{{display:flex;align-items:baseline;gap:12px;padding:14px 0;border-bottom:1px solid #ddd;animation:belir .4s ease forwards;opacity:0}}
    .haber:last-child{{border-bottom:none}}
    @keyframes belir{{to{{opacity:1}}}}
    .nokta{{width:6px;height:6px;border-radius:50%;flex-shrink:0;margin-top:8px}}
    .haber-metin{{flex:1;font-size:15px;line-height:1.65;color:#1a1a1a}}
    .haber-meta{{display:flex;align-items:center;gap:8px;flex-shrink:0}}
    .etiket{{font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;padding:2px 7px;color:#f5f0e8}}
    .kaynak-link{{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-bottom:1px solid transparent;transition:border-color .2s;white-space:nowrap}}
    .kaynak-link:hover{{border-bottom-color:currentColor}}
    footer{{background:#1a1a1a;color:#555;text-align:center;padding:20px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;margin-top:40px}}
    @media(max-width:600px){{
      .masthead-ust{{padding:8px 16px;font-size:9px}}
      .masthead-orta{{padding:16px}}
      .icerik{{padding:24px 16px 60px}}
      .haber-meta{{flex-direction:column;align-items:flex-end;gap:4px}}
    }}
  </style>
</head>
<body>
  <header class="masthead">
    <div class="masthead-ust">
      <span>📍 Küresel Haber Özeti</span>
      <span>{data['gun']}, {data['tarih']}</span>
      <span>AI Destekli</span>
    </div>
    <div class="masthead-orta">
      <h1>GÜNÜN AKIŞI</h1>
      <p>Güvenilir Kaynaklardan · Her Sabah Otomatik Güncellenir</p>
    </div>
  </header>
  <main class="icerik">
    <div class="tarih-bant">
      <span>{data['gun']}, {data['tarih']} Bülteni</span>
    </div>
    {kategoriler_html}
  </main>
  <footer>
    <p>Günün Akışı · The Guardian · MIT · Reuters · BBC · Nature · NPR ve daha fazlası</p>
  </footer>
</body>
</html>"""

with open("haberler.html", "w", encoding="utf-8") as f:
    f.write(html)

print("haberler.html başarıyla oluşturuldu!")
