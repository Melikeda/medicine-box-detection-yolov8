"""Türkçe Düzce Üniversitesi CE499 staj raporu (Word)."""

from __future__ import annotations

import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_internship_report_docx import (  # noqa: E402
    ASSETS,
    DUZCE_LOGO,
    FIGURES,
    ROOT,
    SAMPLES,
    Report,
    prepare_figures,
    restart_page_number,
    set_page_border,
    set_run_font,
    setup_body_footer,
    setup_empty_footer,
)

OUT_DOCS = ROOT / "docs" / "Staj_Raporu_Yolocilin.docx"
OUT_DOWNLOADS = Path.home() / "Downloads" / "Staj_Raporu_Yolocilin.docx"


def build() -> None:
    prepare_figures(lang="tr")
    rep = Report()
    doc = rep.doc

    if DUZCE_LOGO.exists():
        p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, indent=False, space_before=6, space_after=8)
        p.add_run().add_picture(str(DUZCE_LOGO), width=Cm(4.6))

    for line in (
        "DÜZCE ÜNİVERSİTESİ",
        "MÜHENDİSLİK FAKÜLTESİ",
        "BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ",
    ):
        p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=0, space_after=0)
        r = p.add_run(line)
        set_run_font(r, size=16, bold=True)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=24, space_after=12)
    r = p.add_run("Staj Raporu")
    set_run_font(r, size=18, bold=True)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=6, space_after=18)
    r = p.add_run("Yolocilin — İlaç Kutusu Tespit, Tanıma ve Bilgilendirme Sistemi")
    set_run_font(r, size=14, bold=True)

    cover_fields = [
        ("Öğrenci No:", "221015057"),
        ("Ad Soyad:", "Melike Eda Külahcı"),
        ("Bölüm:", "Bilgisayar Mühendisliği"),
        ("Ders Kodu:", "CE499"),
        ("Staj Tarihleri:", "29.07.2026 – 03.08.2026"),
        ("Staj Yeri:", "Cerebrum Tech"),
    ]
    for label, value in cover_fields:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.LEFT, indent=False, space_before=4, space_after=4)
        p.paragraph_format.left_indent = Cm(2.5)
        r = p.add_run(f"{label}  ")
        set_run_font(r, size=12, bold=True)
        r2 = p.add_run(value)
        set_run_font(r2, size=12)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=36)
    r = p.add_run("Düzce, 2026")
    set_run_font(r, size=12)

    rep.add_section_break()
    setup_empty_footer(doc.sections[-1])

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=0, space_after=12)
    r = p.add_run("İÇİNDEKİLER")
    set_run_font(r, size=16, bold=True)

    toc = [
        (14, "1. GİRİŞ", True),
        (14, "2. ŞİRKET HAKKINDA BİLGİLER", True),
        (12, "    2.1 Ad, Adres ve Faaliyet Alanı", False),
        (12, "    2.2 Personel ve Organizasyon", False),
        (12, "    2.3 İletişim Kişisi", False),
        (14, "3. PROJE VE YAPILACAK İŞİN TANIMI", True),
        (12, "    3.1 Problem Tanımı", False),
        (12, "    3.2 Planlanan İş", False),
        (12, "    3.3 Kullanılan Teknolojiler", False),
        (12, "    3.4 Kapsam Dışı Kalanlar", False),
        (14, "4. PROJE VE YAPILAN İŞLER", True),
        (12, "    4.1 Stajdaki Görev ve Yapılan İşler", False),
        (12, "    4.2 Proje Amacı ve Analiz", False),
        (12, "    4.3 Gereksinimler", False),
        (12, "    4.4 Tasarım ve Mimari", False),
        (12, "    4.5 Veri Seti ve YOLOv8 Eğitimi", False),
        (12, "    4.6 Nesne Tespiti", False),
        (12, "    4.7 Görüntü Ön İşleme ve OCR", False),
        (12, "    4.8 Eşleme Algoritmaları ve İş Kuralları", False),
        (12, "    4.9 Veritabanı", False),
        (12, "    4.10 Backend API", False),
        (12, "    4.11 Kimlik Doğrulama ve Yetkilendirme", False),
        (12, "    4.12 Mobil Uygulama", False),
        (12, "    4.13 Doğrulama, Test ve Performans", False),
        (12, "    4.14 Güvenlik ve DevOps", False),
        (12, "    4.15 Karşılaşılan Problemler ve Çözümler", False),
        (12, "    4.16 Belgeleme ve Yayım (GitHub, Kaggle, Medium)", False),
        (14, "5. SONUÇ", True),
        (14, "EKLER", True),
        (12, "    Ek A  OpenCV Ön İşleme (CLAHE ve keskinleştirme)", False),
        (12, "    Ek B  YOLO Güven Eşiği Yedekleme", False),
        (12, "    Ek C  Hızlı OCR Varyantları", False),
        (12, "    Ek D  RapidFuzz Eşleme", False),
        (12, "    Ek E  Analyze Yükleme Yolu", False),
        (12, "    Ek F  Güvenlik Başlıkları", False),
        (12, "    Ek G  Örnek fotoğraflar (bkz. Bölüm 4)", False),
        (14, "KAYNAKLAR", True),
    ]
    for size, title, bold in toc:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0, indent=False, space_before=2, space_after=2)
        r = p.add_run(title)
        set_run_font(r, size=size, bold=bold)

    rep.add_section_break()
    restart_page_number(doc.sections[-1], 1)
    setup_body_footer(doc.sections[-1], lang="tr")

    rep.h1("1. GİRİŞ")
    rep.body(
        "Bu rapor, Düzce Üniversitesi Mühendislik Fakültesi Bilgisayar Mühendisliği "
        "Bölümü CE499 staj dersi kapsamında hazırlanmıştır. Staj, 29.07.2026–03.08.2026 "
        "tarihleri arasında Ankara Cyberpark’taki Cerebrum Tech ofisinde tamamlanmıştır. "
        "Şirket yapay zekâ, bilgisayarlı görü, doğal dil işleme ve tahmine dayalı "
        "analitik alanlarında çalışmaktadır [1], [2].",
        first=True,
    )
    rep.body(
        "Stajda uçtan uca çalışan bir yazılım ürünü geliştirilmiştir. Ürünün adı "
        "Yolocilin’dir. Aynı ad Android uygulamasında, GitHub deposunda, GitHub Projects "
        "tahtasında ve Kaggle veri setinde kullanılır. Kullanıcı, uygulamayla bir veya "
        "daha fazla ilaç kutusunun fotoğrafını çeker. FastAPI arkaplanı her kutuyu "
        "YOLOv8n ile tespit eder, OpenCV ön işleme ve EasyOCR ile baskı metnini okur, "
        "gürültülü metni RapidFuzz ile 1163 ilaçlık katalogla eşler. Sonuçlar uygulamada "
        "gösterilir. Başarılı eşlemeden sonra Google Gemini ile kısa bir açıklama "
        "istenebilir. Tarama geçmişi cihazda tutulur; sunucu erişilebilirse JSON olarak "
        "arkaplana da kopyalanır."
    )
    rep.body(
        "Yolocilin klinik karar aracı değildir. API yanıtı ve sonuç ekranı, çıktının "
        "tıbbi tavsiye olmadığını; kesin bilgi için prospektüse veya eczacıya bakılması "
        "gerektiğini belirtir. Dil modeli bu nedenle ayrı bir uç noktada tutulmuş, istem "
        "ise yalnızca katalog alanlarıyla sınırlanmıştır."
    )
    rep.body(
        "Çalışma veri seti ve model eğitiminden başlamış; ön işleme, OCR, eşleme, REST "
        "API, SQLite, Docker, GitHub Actions ve Flutter istemcisiyle sürdürülmüştür. "
        "Sonraki aşamalarda üretim tarafı kontrolleri, TİTCK SKRS katalog genişletmesi, "
        "isteğe bağlı Gemini açıklamaları, kamera çekimi ve tarama geçmişi eklenmiştir. "
        "Geliştirme sırasında öğrenilen yöntemler, projenin katmanlarına paralel üç "
        "Medium dizisinde de kayda geçirilmiştir [30], [31], [32]."
    )
    rep.body(
        "Bölüm 2 şirket bilgilerini verir. Bölüm 3 projeyi ve planlanan işi tanımlar. "
        "Bölüm 4 sistemin nasıl kurulduğunu, denendiğini ve gerçek fotoğraflardaki "
        "hataların nasıl giderildiğini anlatır. Bölüm 5 sonuçları toplar. Tam kaynak kod "
        "GitHub deposundadır [33]. Ekler’de yalnızca anlatılan kararları gösteren kısa "
        "alıntılar yer alır."
    )

    rep.h1("2. ŞİRKET HAKKINDA BİLGİLER")
    rep.body(
        "Bu bölümdeki bilgiler staj işyeri formundan ve şirketin kamuya açık web "
        "sayfalarından derlenmiştir [1], [2].",
        first=True,
    )

    rep.h2("2.1 Ad, Adres ve Faaliyet Alanı")
    rep.body(
        "Staj yeri Cerebrum Tech’tir. Adres: Ankara Teknoloji Geliştirme Bölgesi, "
        "Üniversiteler Mahallesi, 1606. Cadde, Kapı No: 4/A, Cyberpark A Blok, "
        "7. Kat No: 707, 06800 Bilkent, Çankaya / Ankara. Üretim ve hizmet alanı yazılım "
        "geliştirmedir. Staj Ar-Ge biriminde yapılmıştır."
    )
    rep.body(
        "Şirket, bilgisayarlı görü, doğal dil işleme ve tahmine dayalı analitik "
        "üzerinde çalışan bir yapay zekâ firmasıdır [1]. Kamuya açık sayfalarda orman "
        "yangını tespiti ve akıllı tarım çözümleri de yer alır [3]. Yolocilin, staj "
        "döneminde geliştirilen ilaç kutusu tespit, tanıma ve bilgilendirme sistemidir; şirketin yayımlanmış "
        "ürün hatlarından bağımsız, kendi başına teslim edilen bir Ar-Ge çalışmasıdır."
    )
    rep.body(
        "Şirket Ankara’dadır. Ekip sayfasında Dr. R. Erdem Erkul Kurucu ve Yönetim "
        "Kurulu Başkanı olarak yer alır [4]."
    )

    rep.h2("2.2 Personel ve Organizasyon")
    rep.body(
        "İşyeri formuna göre şirkette 10 mühendis, 3 finansman elemanı ve 17 diğer "
        "personel çalışmaktadır; toplam 30 kişidir. Stajyer, Ar-Ge Takım Lideri "
        "Ahmet Mert Özdemir’e bağlı çalışmıştır."
    )
    rep.caption(
        "Tablo 2.1 Raporda kullanılan işyeri bilgileri.",
        above=True,
    )
    rep.table(
        ["Madde", "Değer"],
        [
            ["Şirket adı", "Cerebrum Tech"],
            ["Birim", "Ar-Ge"],
            ["Mühendis", "10"],
            ["Finansman elemanı", "3"],
            ["Diğer", "17"],
            ["Toplam personel", "30"],
            ["Şirket danışmanı", "Ahmet Mert Özdemir"],
            ["Unvan", "Ar-Ge Takım Lideri"],
            ["Stajyer konumu", "Stajyer, Ar-Ge birimi"],
        ],
    )

    rep.h2("2.3 İletişim Kişisi")
    rep.caption("Tablo 2.2 Staj işyeri formundaki iletişim kişisi.", above=True)
    rep.table(
        ["Madde", "Değer"],
        [
            ["Ad soyad", "Ahmet Mert Özdemir"],
            ["Görevi", "Ar-Ge Takım Lideri"],
            ["Telefon", "0312 544 50 50"],
            ["E-posta", "info@cerebrumtechnologies.co"],
            ["Web", "https://www.cerebrumtechnologies.com"],
        ],
    )

    rep.h1("3. PROJE VE YAPILACAK İŞİN TANIMI")
    rep.h2("3.1 Problem Tanımı")
    rep.body(
        "İlaç kutusunu telefon fotoğrafından yalnızca görsel tahmine dayanarak tanımak "
        "güvenilir değildir. Ambalaj dönük, kadraj dışı veya Türkçe-İngilizce karışık "
        "basılmış olabilir. Tek karede birden fazla kutu bulunabilir. Ham görüntüde OCR "
        "afern, fen, ibucold € veya 250 mo / j0o mo tablot gibi gürültülü diziler üretir. "
        "Bu dizileri ek kontrol olmadan marka listesine bağlamak yanlış ilaç döndürebilir; "
        "yanlış eşleme, bulunamadı sonucundan daha risklidir.",
        first=True,
    )
    rep.body("Staj projesi aşağıdaki işleri yapan çalışan bir sistem olarak tanımlandı:")
    rep.numbered(
        [
            "fotoğraftaki her ilaç kutusunu tespit etmek,",
            "her kırpımdaki baskıyı okumak,",
            "metni tohum katalogla eşlemek,",
            "yapılandırılmış JSON sonucu Android uygulamaya dönmek,",
            "isteğe bağlı olarak eşleşen ilaç için kısa Türkçe veya İngilizce açıklama üretmek,",
            "başarılı taramaların geçmişini tutmak.",
        ]
    )

    rep.h2("3.2 Planlanan İş")
    rep.body(
        "İş, sıralı evrelere bölündü. Her evre bir Git özellik dalı ve bir GitHub "
        "issue ile yürütüldü. Sıra şöyleydi: depo ve ortam; veri seti ve Roboflow "
        "etiketleme; YOLOv8n eğitimi; OpenCV ön işleme ve EasyOCR; CSV katalog üzerinde "
        "RapidFuzz; birleşik servis katmanı; FastAPI (health, analyze, ardından medicines, "
        "explain, scans); çalışma anı katalog olarak SQLite; otomatik test, Docker ve "
        "GitHub Actions; Flutter Android istemcisi (galeri, sonra kamera); TİTCK SKRS "
        "ile katalog genişletme; CPU performansı, üretim sertleştirmesi, Gemini "
        "açıklamaları, tarama geçmişi ve uçtan uca araçlar."
    )
    rep.body(
        "Erken dönemde düşünülen Streamlit arayüzü bırakıldı. GitHub #7 kapatıldı; "
        "teslimatın defter demosu değil, HTTP sözleşmeli bir mobil ürün olması için "
        "Flutter ve FastAPI seçildi."
    )

    rep.h2("3.3 Kullanılan Teknolojiler")
    rep.body(
        "Tablo 3.1, depoda fiilen kullanılan teknolojileri listeler. PostgreSQL, iOS "
        "istemci, genel HTTPS barındırma ve kullanıcı hesapları yol haritasında kalmış "
        "olup bu raporda uygulanmış gibi sunulmaz."
    )
    rep.caption(
        "Tablo 3.1 Yolocilin’de fiilen kullanılan teknolojiler ve katman rolleri.",
        above=True,
    )
    rep.table(
        ["Katman", "Teknoloji", "Rol"],
        [
            ["Dil (YZ ve API)", "Python 3.11+ (CI 3.11, Docker 3.12)", "Hat ve FastAPI"],
            ["Tespit", "YOLOv8n, Ultralytics 8.4.87, PyTorch 2.12.1", "Tek sınıflı ilaç kutusu detektörü"],
            ["Görüntü işleme", "OpenCV, Pillow", "Kırpma, ölçek, CLAHE, eşik, OCR varyantları"],
            ["OCR", "EasyOCR 1.7.2 (tr, en)", "Kırpılmış kutudan metin"],
            ["Eşleme", "RapidFuzz 3.14.5 (fuzz.WRatio)", "Gürültülü OCR → katalog satırı"],
            ["Katalog tohumu", "CSV (medicines.csv)", "Kaynak gerçek, 1163 satır"],
            ["Çalışma anı DB", "SQLite / SQLAlchemy 2.0.46", "medicines ve scans tabloları"],
            ["Resmî zenginleştirme", "TİTCK SKRS XLSX (pandas, openpyxl)", "Doz, form, etken madde, marka"],
            ["Arkaplan", "FastAPI 0.140.0, Uvicorn, Pydantic Settings", "REST API"],
            ["LLM (isteğe bağlı)", "google-genai 1.16.1, Gemini Flash", "POST /api/v1/explain"],
            ["Mobil", "Flutter 3.19+, Dart SDK ≥ 3.3", "Android istemci Yolocilin"],
            ["Mobil depolama", "sqflite, shared_preferences", "Yerel geçmiş ve OCR kip tercihi"],
            ["Mobil HTTP / kamera", "http, image_picker", "Çok parçalı yükleme, galeri ve kamera"],
            ["Test", "pytest 8.4.2, httpx, Flutter test", "Arkaplan ve widget testleri"],
            ["Konteyner", "Docker, docker-compose", "API imajı python:3.12-slim-bookworm"],
            ["CI", "GitHub Actions", "Arkaplan test, mobil test, Docker derleme"],
            ["Veri seti aracı", "Roboflow", "Etiketleme ve YOLO dışa aktarma"],
            ["Veri seti yayını", "Kaggle, CC BY 4.0", "395 gizlilik temizliği yapılmış görüntü"],
        ],
    )

    rep.h2("3.4 Kapsam Dışı Kalanlar")
    rep.body(
        "Kodda ve yol haritasında yapılmamış olanlar: kullanıcı girişi, JWT veya kişiye "
        "özel tarama listesi (sunucu taramaları genel listedir); yönetim paneli; iOS "
        "istemci; PostgreSQL; barkod / karekod yolu; genel bulut HTTPS yayını; WAF veya "
        "DDoS koruması; Gemini anahtarı için bulut gizli yöneticisi. Giriş ekranı yoktur. "
        "Mobil akış: açılış, ana sayfa (karşılama / tara / geçmiş), önizleme, sonuç."
    )
    rep.image(ASSETS / "yolocilin-banner.png", 14.0)
    rep.caption(
        "Şekil 3.1 Yolocilin ürün görseli. Aynı ad Android uygulamasında, GitHub "
        "deposunda (github.com/Melikeda/yolocilin) ve Kaggle veri setinde kullanılır."
    )

    rep.h1("4. PROJE VE YAPILAN İŞLER")
    rep.body(
        "Bu bölüm stajın teknik kaydıdır. Eşikler ve sayılar güncel kaynaktan "
        "alınmıştır (src/services/config.py, backend/app/config.py, katalog README).",
        first=True,
    )

    rep.h2("4.1 Stajdaki Görev ve Yapılan İşler")
    rep.body(
        "Stajyer Ar-Ge biriminde, Ar-Ge Takım Lideri Ahmet Mert Özdemir’e bağlı "
        "çalıştı. Günlük iş özellik dalı iş akışına göre yürüdü: odaklı değişiklik, "
        "ayrı dal, çekme isteği, main’e birleştirme. Görevler GitHub Projects tahtasında "
        "Todo, In Progress ve Done sütunlarıyla izlendi. Yapılan işler arasında ilaç "
        "kutusu görüntüsü toplama ve etiketleme; YOLOv8n eğitimi; OpenCV ve EasyOCR "
        "modülleri; RapidFuzz eşleme ve güvenilirlik kontrolleri; FastAPI analyze, "
        "medicines, explain ve scans uçları; CSV’den SQLite tohumlama; TİTCK SKRS ile "
        "katalog genişletme; pytest ve Flutter testleri; Docker paketleme; GitHub "
        "Actions; Android istemci (galeri, kamera, iki dilli arayüz, geçmiş); üretim "
        "ayarlarının sertleştirilmesi (CORS, hız sınırı, sihirli bayt kontrolü) vardır. "
        "İlgili kod bu bölümde değil Ekler’dedir."
    )

    rep.h2("4.2 Proje Amacı ve Analiz")
    rep.body(
        "Yolocilin pratik bir soruya cevap verir: bir veya daha fazla ilaç kutusunun "
        "telefon fotoğrafı verildiğinde, katalogda hangi kayıtlar (varsa) bu kutulara "
        "karşılık gelir? Sistem üç parçadan oluşur. src paketi tespit, ön işleme, OCR, "
        "eşleme ve SQLAlchemy modellerini tutar. backend/app paketinde FastAPI yönlendiricileri, "
        "doğrulama, hız sınırları, LLM ve tarama servisleri vardır. mobile paketi Flutter "
        "Android arayüzüdür. examples ağacı öğrenme betikleridir; üretim kodu bunları içe aktarmaz."
    )
    rep.body(
        "Analiz hattın sırasını izledi. İlaç kutusu fotoğrafları Roboflow’da tek sınıf "
        "medicine-box olarak etiketlendi. İçerideki erken bölünmede 478 görüntü vardı. "
        "Kaggle yayını öncesi üçüncü taraf ekran görüntüleri ve el yazısı notlu kareler "
        "çıkarıldı. Yayımlanan set 395 görüntüdür: eğitim 363, doğrulama 15, test 17, "
        "lisans CC BY 4.0 [5]. Eğitim src/train.py ile yapıldı: Ultralytics YOLOv8n, "
        "yolov8n.pt, 50 epok, 640 piksel, yığın 8, CPU [6], [7], [8]. Net test karelerinde "
        "kutu güvenleri genelde 0,80–0,93 arasındaydı. Başarısızlıklar düşük ışık ve "
        "kısmen görünen kutularda toplandı; bu da 0,40 / 0,25 güven yedeklemesini doğurdu."
    )
    rep.body(
        "Tek ham kırpımda EasyOCR yetmedi. Kırpım başına birkaç ön işlenmiş varyant "
        "üretildi. Emülatörde CPU gecikmesi kullanılmaz hale gelince fast kipi eklendi. "
        "RapidFuzz WRatio kısa çöp metne yüksek puan veriyor, doz satırlarını etken "
        "madde alanıyla karıştırıyordu. Katalog büyüdükten sonra eksik bir marka komşu "
        "satıra düşebiliyordu. Bu yüzden tek bir kesit yerine bir dizi koruma eklendi [11]."
    )

    rep.h2("4.3 Gereksinimler")
    rep.body(
        "Gereksinimler GitHub issue’larında, yol haritasında ve API şemalarında tutuldu."
    )
    p = rep._p(indent=False)
    r = p.add_run("İşlevsel gereksinimler.")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        " Yüklenen JPEG, PNG, WebP veya BMP dosyasında (en fazla 10 MB) tüm ilaç "
        "kutularını tespit et. Aynı karede birden fazla kutuyu destekle. Türkçe ve "
        "İngilizce baskıyı oku. medicine_name, brand_name ve güvenliyse active_ingredient "
        "ile eşle. Kutu durumu olarak matched, not_found, not_medicine_box veya error "
        "dön. Katalog araması sun. Eşleşen medicine_id için isteğe bağlı açıklama üret. "
        "Galeri ve kameralı, iki dilli, sonuç kartlı Android istemci ver; yerel geçmiş "
        "(en fazla 50) ve olanaklar ölçüsünde sunucu eşlemesi (en fazla 200) olsun. "
        "Modellerin yüklenip yüklenmediğini bildiren sağlık ucu olsun."
    )
    set_run_font(r2)
    p = rep._p(indent=False)
    r = p.add_run("İşlevsel olmayan gereksinimler.")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        " YOLO ve EasyOCR’ı süreç başında bir kez yükle. Bloke eden hattı asyncio.to_thread "
        "içinde çalıştır. Varsayılan OCR kipi fast olsun; accurate sorgu bayrağıyla açılsın. "
        "Üretimde joker CORS’u reddet, /docs’u kapat, 500 ayrıntısını gizle, hız sınırlarını "
        "açık tut. Gizli bilgileri commit etme. Analyze yanıtında ve sonuç ekranında tıbbi "
        "uyarı göster."
    )
    set_run_font(r2)

    rep.h2("4.4 Tasarım ve Mimari")
    rep.body(
        "Asıl tasarım kuralı tek orkestrasyon noktasıyla modülerlikti. "
        "PipelineManager.load() bir YOLO modeli, bir EasyOCR okuyucu ve bir eşleme "
        "servisi oluşturur. analyze_all(image_path) tespit, OCR ve eşlemeyi çalıştırır; "
        "aşama sürelerini (yolo_ms, ocr_ms, matching_ms, total_ms) ekler. FastAPI yaşam "
        "döngüsü bu servisleri açılışta yükler, kapanışta boşaltır; testler durumu "
        "ayırabilir [12], [13]."
    )
    rep.mono(
        "Yolocilin (Flutter, Android)\n"
        "        |  galeri veya kamera\n"
        "        v\n"
        "POST /api/v1/analyze?mode=fast|accurate\n"
        "        |\n"
        "        v\n"
        "FastAPI  ->  PipelineManager (YOLO + EasyOCR bir kez yüklenir)\n"
        "        |\n"
        "        v\n"
        "YOLOv8 tespit -> kırp -> OpenCV varyantları -> EasyOCR\n"
        "        -> normalize -> RapidFuzz -> SQLite katalog (1163)\n"
        "        |\n"
        "        v\n"
        "JSON (kutu durumu + özet + süre + uyarı)\n"
        "        |-- yerel sqflite geçmiş + POST /api/v1/scans (olanaklar ölçüsünde)\n"
        "        +-- isteğe bağlı POST /api/v1/explain -> Gemini"
    )
    rep.caption(
        "Şekil 4.1 Android istemciden analyze hattına çalışma yolu. Modeller API "
        "açılışında yüklenir, istek başına değil. Explain ayrı çağrıdır; Gemini OCR "
        "süresine eklenmesin diye."
    )
    rep.mono(
        "mobile/lib  (ekranlar, servisler, modeller)\n"
        "        | HTTP çok parçalı / JSON\n"
        "        v\n"
        "backend/app  (yönlendiriciler, ara katman, servisler)\n"
        "        |\n"
        "        v\n"
        "src/services  PipelineManager -> Tespit / OCR / Eşleme\n"
        "        |\n"
        "        v\n"
        "SQLite medicines.db (medicines + scans)\n"
        "CSV     medicines.csv (tohum; açılışta işlenir)"
    )
    rep.caption(
        "Şekil 4.2 Bileşen sınırları. Mobil uygulama kataloğu gömmez. Yerel "
        "scan_history.db analyze JSON’unu ve fotoğraf kopyasını tutar. Sunucu scans "
        "tablosu yalnızca JSON saklar, görüntü saklamaz."
    )
    rep.image(FIGURES / "pipeline_architecture_tr.png", 15.5)
    rep.caption(
        "Şekil 4.3 Uygulanan modüllerden çizilen sistem mimarisi. Flutter istemci "
        "fotoğrafı FastAPI’ye gönderir; hat YOLOv8, OCR ve RapidFuzz’ı 1163 ilaçlık "
        "SQLite katalog üzerinde çalıştırır."
    )

    rep.h2("4.5 Veri Seti ve YOLOv8 Eğitimi")
    rep.body(
        "Görüntüler önce sınırlayıcı kutu tablosu olarak tutuldu: dosya adı, genişlik, "
        "yükseklik, sınıf ve xmin / ymin / xmax / ymax köşeleri. Bu tablo, etiketleme "
        "sürecinin ara biçimidir. Marka adı (örneğin Aferin, Parol) detektör sınıfı "
        "değildir; marka OCR ve katalog eşlemesiyle bulunur. Eğitim için kayıtlar "
        "Roboflow’da tek sınıf medicine-box olarak birleştirilmiş, YOLO biçimine "
        "dönüştürülmüştür: görüntü başına bir metin dosyası, sınıf no 0, normalize "
        "merkez ve boyut. data/dataset/data.yaml nc: 1 ve sınıf adı medicine-box olarak "
        "ayarlar [22]."
    )
    rep.caption(
        "Tablo 4.1 Sınırlayıcı kutu etiket tablosunun alanları. Bu tablo medicines.csv "
        "katalog genişletmesinden ayrıdır.",
        above=True,
    )
    rep.table(
        ["Alan", "Anlamı"],
        [
            ["filename", "Görüntü dosya adı"],
            ["width, height", "Görüntü boyutu (piksel)"],
            ["class", "Nesne sınıfı; eğitimde medicine-box"],
            ["xmin, ymin", "Kutunun sol üst köşesi"],
            ["xmax, ymax", "Kutunun sağ alt köşesi"],
        ],
    )
    rep.body(
        "İçerideki erken bölünmede 478 görüntü vardı. Kaggle yayını öncesi üçüncü taraf "
        "ekran görüntüleri ve el yazısı notlu kareler çıkarıldı. Temizlenen set, "
        "Yolocilin Medicine Box Detection adı altında Kaggle’a yüklendi: 395 görüntü "
        "(eğitim 363, doğrulama 15, test 17), lisans CC BY 4.0 [5]. Amaç, eğitim "
        "görüntülerini Git deposuna koymadan yeniden üretilebilir bir indirme kaynağı "
        "vermekti."
    )
    rep.body(
        "Eğitim src/train.py ile yapıldı: Ultralytics YOLOv8n, yolov8n.pt, 50 epok, "
        "640 piksel, yığın 8, CPU [6], [7], [8]. YOLOv8 Nano seçildi çünkü staj "
        "makinesi CPU çıkarımı yaptı ve görev tek, büyük bir nesne sınıfıdır. Ağırlıklar "
        "commit edilmez. API best.pt dosyasını yaygın runs/detect düzenlerinden, "
        "models/best.pt veya YOLO_MODEL_PATH ile bulur. Net test karelerinde kutu "
        "güvenleri genelde 0,80–0,93 arasındaydı. Düşük ışık ve kısmen görünen kutularda "
        "başarısızlıklar, 0,40 / 0,25 güven yedeklemesini doğurdu."
    )
    rep.caption("Tablo 4.2 src/train.py içindeki YOLOv8n eğitim ayarı.", above=True)
    rep.table(
        ["Parametre", "Değer"],
        [
            ["Model", "YOLOv8n (yolov8n.pt, aktarım öğrenmesi)"],
            ["Epok", "50"],
            ["Görüntü boyutu", "640 x 640"],
            ["Yığın", "8"],
            ["Aygıt", "CPU"],
            ["Yayımlanan görüntüler (Kaggle)", "395 (eğitim 363, doğrulama 15, test 17)"],
            ["Lisans", "CC BY 4.0"],
        ],
    )
    rep.image(SAMPLES / "aferin_forte.jpg", 10.5)
    rep.caption(
        "Şekil 4.4 Staj testlerinde kullanılan tek kutu örneği (A-Ferin Forte). "
        "Ambalaj yazısı okunur; detektör ve OCR yolu bu tür girdiyle denendi."
    )
    rep.image(SAMPLES / "imunol_defence.jpg", 10.0)
    rep.caption(
        "Şekil 4.5 İkinci tek kutu örneği (İmunol Defence). Farklı düzen ve renk, "
        "eşlemenin tek markaya kilitlenmediğini kontrol etmek için kullanışlıydı."
    )
    rep.image(SAMPLES / "2li_ornek.png", 10.5)
    rep.caption(
        "Şekil 4.6 İki kutu örneği (Aferin ve Dolorex). Detektör kutu başına bir kırpım "
        "dönmelidir; her kırpım ayrı eşlenir."
    )

    rep.h2("4.6 Nesne Tespiti")
    rep.body(
        "DetectionService.detect_all gerektiğinde YOLO’yu iki kez çalıştırır. Birincil "
        "güven 0,40’tır. Bu geçiş boşsa, veya en iyi skor 0,55’in altındaysa ve 0,25 "
        "geçişi daha fazla kutu bulursa yedek sonuç tutulur. Bulanık çoklu kutu "
        "fotoğrafında staj ölçümü eski 0,60 eşiğinde 0 kutu, yedekten sonra 3 kutu "
        "kaydetti. YOLO yanlış pozitifleri detektörde silinmez. OCR ve eşleme inandırıcı "
        "görünmezse (skor minimum_plausible_match_score 65’in altında, boş/çöp metin "
        "veya geçerli ad adayı olmayan metin) kutu not_medicine_box olur. İlgili kod "
        "Ek B’dedir."
    )
    rep.caption("Tablo 4.3 PipelineConfig’teki tespit eşikleri.", above=True)
    rep.table(
        ["Ayar", "Değer", "Anlamı"],
        [
            ["Birincil güven", "0,40", "İlk geçiş"],
            ["Yedek güven", "0,25", "İlk geçiş boş veya zayıfsa yeniden dene"],
            ["Zayıf tespit kuralı", "en yüksek güven < 0,55", "Daha fazla kutu varsa yedeği kullan"],
        ],
    )

    rep.h2("4.7 Görüntü Ön İşleme ve OCR")
    rep.body(
        "İki ön işleme katmanı vardır. src/preprocessing yeniden kullanılabilir OpenCV "
        "katmanıdır: gri ton, ölçek, kırpma, medyan bulanıklaştırma, CLAHE, uyarlamalı "
        "eşik, açma ve kapama [9]. OCR çalışma anı bu tek ikili hatta durmaz. "
        "src/ocr/ocr_pipeline.py kırpım başına varyant sözlüğü üretir: 0, 90, 180, 270 "
        "derece döndürme; kübik büyütme (fast’te 1,75 kat, accurate’de 2,0 kat); fast’te "
        "yalnızca orijinal renk ve keskinleştirme; accurate’de unsharp, CLAHE, CLAHE+keskin, "
        "Otsu ve Laplacian varyansı 80’in altındaysa ek bulanıklık varyantları [10]."
    )
    rep.body(
        "Hat başlamadan sunucu yüklemeyi uzun kenarı en fazla 1280 piksel olacak şekilde "
        "küçültür. Flutter galeri seçici de en fazla 1280 piksel, kalite %65 sıkıştırır. "
        "Sonraki analyze sürelerinin ilk emülatör ölçümü olan yaklaşık 255 saniyeden "
        "CPU’da bir-üç dakikaya inmesinin asıl nedeni bu iki küçültmedir."
    )
    rep.caption("Tablo 4.4 Güncel PipelineConfig OCR kipleri.", above=True)
    rep.table(
        ["Kip", "Davranış"],
        [
            [
                "fast (API varsayılanı)",
                "Ölçek 1,75x, dört dönüş, açı başına 2 varyant (en fazla 8 OCR geçişi), erken çıkış açık",
            ],
            [
                "accurate",
                "Ölçek 2,0x, dört dönüş, tam varyant kümesi (zor kırpımlarda yaklaşık 52 geçiş), erken çıkış yok",
            ],
        ],
    )
    rep.body(
        "EasyOCR diller tr ve en ile bir kez oluşturulur. GPU varsayılan kapalıdır. "
        "Yan yana OCR parçaları birleştirilir; ibucold ve €, ibucold c olabilir. Genel "
        "ifadeler ve yalnızca doz satırları RapidFuzz’tan önce düşer. CLAHE ve "
        "keskinleştirme alıntısı Ek A’dadır; hızlı kip varyantları Ek C’dedir."
    )

    rep.h2("4.8 Eşleme Algoritmaları ve İş Kuralları")
    rep.body(
        "Gerçek fotoğraflardan sonra en çok değişen kısım eşleme oldu. Çekirdek skor "
        "normalize dizeler üzerinde RapidFuzz fuzz.WRatio’dur, aralık 0–100 [11]. "
        "Normalizasyon küçük harfe çevirir, boşlukları sıkıştırır ve Ibucold C kutusunun "
        "ibucold € okunması yüzünden €, ©, ¢ karakterlerini c yapar. Her OCR adayı "
        "medicine_name, brand_name ve active_ingredient ile karşılaştırılır; en yüksek "
        "skor tutulur. Birkaç kural bu kazananı eler."
    )
    rep.caption(
        "Tablo 4.5 Eşleme korumaları. Son kabul kesiti 88’dir. OCR erken çıkışı 80 "
        "alt kapısını kullanabilir.",
        above=True,
    )
    rep.table(
        ["Kural", "Eşik veya davranış", "Nedeni"],
        [
            ["En düşük eşleme skoru", "88", "Katalog büyüdükten sonra 80 hâlâ yanlış komşuyu kabul ediyordu"],
            ["Ad kapsama oranı", "0,55", "Tek harfli yanlış pozitifleri keser"],
            ["Kısmi marka kapsaması", "sorgu markanın içinde, kapsama 0,50, skor ≥ 88", "Bulanık baskıda fen → Nurofen"],
            ["Genel tek sözcükler", "forte, plus, tablet, şurup, …", "Bu parçalar birçok kutuda vardır"],
            ["Genel etken maddeler", "yalnızca ibuprofen, paracetamol, …", "Nurofen ile Brufen ayırt edilemez"],
            ["Yalnızca etken madde eşlemesi", "ad/marka skorları 65’in altındaysa elenir", "Parafon, etken madde üzerinden Nurofen oluyordu"],
            ["Yalnızca doz/form", "mg, ml, tablet, tablot, … marka benzeri parça yok", "250 mo / j0o mo tablot marka değildir"],
            ["Etiket parça örtüşmesi", "en az 4 harflik ortak parça", "Katalogda olmayan OCR not_found dönmeli"],
            ["Yabancı marka parçası", "aday etiketlerinde olmayan uzun OCR parçası", "Endofer benzeri metin Coldaway C olmamalı"],
            ["Marka ailesi ayırımı", "Plus / Forte / Jel / Gargara parçaları", "Aynı skorda daha uzun SKU adı kazanmamalı"],
        ],
    )
    rep.body(
        "Kutu durumları: matched (güvenilir skor ve korumalar geçti), not_found "
        "(ambalaj ilaç kutusuna benziyor ama güvenli katalog satırı yok), "
        "not_medicine_box (YOLO kırpımı inandırıcılık kontrolünü geçmedi), error "
        "(o kırpımda istisna). Marka ailesi mantığı src/matching/brand_disambiguation.py "
        "içindedir. Parol ile Parol Plus, OCR’da plus geçip geçmediğine bakılarak "
        "seçilir; daha uzun ad kazanmaz. İlgili kod Ek D’dedir."
    )

    rep.h2("4.9 Veritabanı")
    rep.body(
        "Projede iki ayrı tablo ailesi vardır. İlki görüntü etiketleridir (Bölüm 4.5, "
        "Tablo 4.1). İkincisi ilaç kataloğudur: data/database/medicines.csv. Katalog, "
        "OCR çıktısının eşleneceği kaynaktır; etiket CSV’si değildir. Çalışma anında "
        "SQLAlchemy medicines.db içinde iki tablo eşler [14], [15]. ensure_database_seeded() "
        "açılışta CSV’yi SQLite’a işler. SQLite’ı elle düzenlemek yanlıştır; sonraki "
        "tohum üzerine yazar. 06.08.2026 tarihli TİTCK SKRS indirmesinde 7948 aktif "
        "ürün satırı vardı [21]. Staj kataloğu seçilmiş bir alt kümedir: sık kullanılan "
        "markalar, ATC grubu doldurma ve Mucosolvan, Redoxon, Strepsils gibi elle "
        "eklenen OTC satırları. Doz / form / etken madde yer tutucu oranı yaklaşık "
        "%7–11’dir; CI eşiği %15’in altıdır. pytest en az 900 satır ve sıfır yinelenen "
        "kimlik ister."
    )
    rep.caption(
        "Tablo 4.6 Staj süresince katalog büyümesi (commit edilen CSV; tam SKRS dökümü değil).",
        above=True,
    )
    rep.table(
        ["Aşama", "Satır"],
        [
            ["İlk eşleme denemeleri", "38"],
            ["İlk TİTCK zenginleştirme (Issue #41)", "107"],
            ["Son parlatma yenilemesi (06.08.2026)", "131"],
            ["Denetimli ek markalar (Ferrum, Buscopan, …)", "153"],
            ["Popüler TR / ATC genişletme (PR #59)", "1163"],
        ],
    )
    rep.image(FIGURES / "catalog_growth_tr.png", 14.0)
    rep.caption(
        "Şekil 4.7 Her genişletme adımından sonra katalog boyutu. Son çubuk eşleme "
        "servisinin kullandığı commit edilmiş tohumdur (1163 satır)."
    )
    rep.caption("Tablo 4.7 Çalışma anı SQLite tablosu medicines.", above=True)
    rep.table(
        ["Sütun", "Tür", "Not"],
        [
            ["medicine_id", "String(32), PK", "MED001 … MED1163"],
            ["medicine_name", "String(255)", "Ana gösterim ve eşleme hedefi"],
            ["brand_name", "String(255)", "Kısmi / bulanık marka eşlemesi"],
            ["active_ingredient", "String(512)", "Yer tutucuysa atlanır"],
            ["dosage", "String(128)", "VERIFY_FROM_OFFICIAL_LEAFLET olabilir"],
            ["form", "String(128)", "Tablet, Şurup, Kapsül, …"],
            ["category", "String(128)", "Örneğin Ağrı Kesici"],
        ],
    )
    rep.caption(
        "Tablo 4.8 Çalışma anı SQLite tablosu scans (kullanıcı tablosu ve hesap yabancı anahtarı yok).",
        above=True,
    )
    rep.table(
        ["Sütun", "Tür", "Not"],
        [
            ["id", "Integer, PK", "Otomatik artan"],
            ["created_at", "DateTime TZ", "İndeksli"],
            ["detection_count, matched_count", "Integer", "Analyze özetinden kopyalanır"],
            ["preview_label", "String(255)", "Liste arayüzü"],
            ["filename", "String(512), boş olabilir", "Orijinal yükleme adı"],
            ["ocr_mode", "String(32)", "fast / accurate"],
            ["client_device_id", "String(128), boş olabilir", "İsteğe bağlı; giriş kimliği değil"],
            ["response_json", "JSON", "Tam analyze yükü"],
        ],
    )
    rep.body(
        "Mobil geçmiş ayrı bir dosyadır: scan_history.db, sqflite, 50 satırda budanır "
        "[19]. Sunucu geçmişi 200 satırla sınırlıdır."
    )

    rep.h2("4.10 Backend API")
    rep.body(
        "Giriş noktası run_api.py’dir. Varsayılan dinleme adresi 127.0.0.1:8000, önek "
        "/api/v1’dir [12], [26]. Analyze sırası: gövde okunmadan Content-Length "
        "MAX_UPLOAD_SIZE_MB (varsayılan 10) üstündeyse reddet; uzantı ve içerik türünü "
        "doğrula, Android galeri application/octet-stream gönderdiği için bunu uzantı "
        "MIME’sine çevir; sihirli baytları kontrol et (JPEG, PNG, WebP, BMP); isteğe "
        "bağlı uzun kenar 1280 piksel; geçici dosya yaz; PipelineManager.analyze_all’ı "
        "işçi iş parçacığında çalıştır; geçici dosyayı sil; özet, süre, image_resized, "
        "processing_time_ms ve tıbbi uyarıyı ekle. OpenAPI belgesi yalnızca ENVIRONMENT "
        "production değilken sunulur. İlgili kod Ek E’dedir."
    )
    rep.caption("Tablo 4.9 backend/app/routers içinde uygulanan REST uçları.", above=True)
    rep.table(
        ["Yöntem", "Yol", "Amaç"],
        [
            ["GET", "/health", "status ok/degraded, models_loaded, medicine_count"],
            ["GET", "/api/v1/analyze/info", "Yükleme sınırları, OCR kipleri, durumlar"],
            ["POST", "/api/v1/analyze", "Çok parçalı dosya, sorgu mode=fast|accurate"],
            ["GET", "/api/v1/medicines", "Liste / arama (search, category, limit, offset)"],
            ["GET", "/api/v1/medicines/categories", "Ayırtık kategoriler"],
            ["GET", "/api/v1/medicines/{id}", "Ayrıntı veya 404"],
            ["GET", "/api/v1/explain/info", "LLM hazır bayrağı"],
            ["POST", "/api/v1/explain", "Eşleşen medicine_id için kısa Gemini metni"],
            ["GET", "/api/v1/scans/info", "Tarama geçmişi üst verisi"],
            ["GET / POST", "/api/v1/scans", "Listele veya analyze JSON’unu sakla"],
            ["GET / DELETE", "/api/v1/scans/{id}", "Ayrıntı veya sil"],
        ],
    )
    rep.body(
        "Explain bilerek ayrı POST’tur. Analyze CPU’da zaten bir-üç dakika sürer. Sonuç "
        "ekranı İlaç hakkında kartını kullanıcı açınca yükler. Birincil Gemini modeli "
        "gemini-flash-latest, yedek gemini-flash-lite-latest [20]. Önbellek anahtarı "
        "medicine_id + yerel ayardır. Explain hız sınırı varsayılan dakikada IP başına "
        "5 istektir. LLM_ENABLED varsayılan false’tur. İstem katalog alanlarıyla sınırlıdır."
    )

    rep.h2("4.11 Kimlik Doğrulama ve Yetkilendirme")
    rep.body(
        "Üründe kayıt, parola, oturum veya JWT yoktur. Bu bilinçli bir MVP sınırıdır. "
        "Mevcut tasarıma yetkilendirme demek abartı olur. Tarama satırlarının sahibi "
        "bir kullanıcı değildir. client_device_id isteğe bağlı bir dizidir, doğrulanmış "
        "kimlik değildir."
    )
    rep.body(
        "Bunun yerine şunlar vardır. Analyze, medicines, explain ve tarama POST/GET’te "
        "son kullanıcı girişi yoktur; asıl kötüye kullanım kontrolü hız sınırıdır. "
        "Üretimde DELETE /api/v1/scans/{id}, SCANS_API_KEY tanımlıysa X-API-Key ister; "
        "anahtar yoksa DELETE 403 döner. Geliştirmede DELETE açıktır. Gemini anahtarı "
        "sunucuda kalır. Yer tutucu dizeler ve 20 karakterden kısa anahtarlar reddedilir. "
        "Android yayın derlemeleri yalnızca HTTPS kullanır. Hata ayıklama derlemeleri "
        "emülatör için http://10.0.2.2 açık metnine izin verir."
    )

    rep.h2("4.12 Mobil Uygulama")
    rep.body(
        "Flutter modülü medicine_box_app, sürüm 0.1.0+1’dir [16], [17], [18]. Giriş, "
        "gösterge paneli veya yönetim paneli yoktur. Var olan ekranlar: açılış; karşılama / "
        "tara / geçmiş sekmeli ana sayfa; OCR kip seçicili ve Analiz Et düğmeli önizleme; "
        "özet çipleri, kutu kartları, uyarı ve açılır açıklama bölümü olan sonuç; kaydırarak "
        "silmeli geçmiş. AnalyzeApiService 300 saniye zaman aşımıyla çok parçalı POST "
        "gönderir. Analyze öncesi istemci GET /health çağırır; modeller yüklenmemişse "
        "SnackBar ile durur. OCR kipi SharedPreferences’ta saklanır. Dil Türkçe veya İngilizce’dir."
    )
    rep.image(ASSETS / "yolocilin-logo.png", 4.4)
    rep.caption(
        "Şekil 4.8 Uygulama logosu. Aynı görsel Android başlatıcı ön planıdır. "
        "Uygulamada giriş ekranı yoktur."
    )
    rep.mono(
        "Açılış -> Ana sayfa\n"
        "           |- Karşılama sekmesi\n"
        "           |- Tara sekmesi -> galeri veya kamera -> Önizleme -> sağlık kontrolü -> Sonuç\n"
        "           +- Geçmiş sekmesi -> kayıtlı Sonuç\n"
        "Sonuç -> açılır İlaç hakkında -> POST /explain"
    )
    rep.caption(
        "Şekil 4.9 Mobil dolaşım. Başarılı analyze sonrası geçmiş kaydı arka planda "
        "çalışır; OCR bekleme süresine eklenmez. Sunucu eşlemesi olanaklar ölçüsündedir. "
        "CSV yer tutucuları arayüzde VERIFY_FROM_OFFICIAL_LEAFLET olarak "
        "gösterilmez, insan cümlesine çevrilir."
    )
    rep.body(
        "Emülatör API adresi http://10.0.2.2:8000’dir. Fiziksel aygıtlar dart-define "
        "API_BASE_URL kullanır. Galeri sıkıştırması en fazla 1280 piksel, kalite %65’tir."
    )

    rep.h2("4.13 Doğrulama, Test ve Performans")
    rep.body(
        "Doğrulama dört katmandadır. Yükleme boyut, uzantı, MIME, sihirli bayt ve boş "
        "dosyayı kontrol eder. Hat yapılandırması en az 3 karakter OCR metni ve Tablo 4.5 "
        "eşleme kapılarını uygular. Katalog doğrulaması en az 900 satır, benzersiz kimlik "
        "ve %15’in altında yer tutucu oranı ister. Üretim CORS_ORIGINS=* değerini reddeder. "
        "LLM_ENABLED üretimde gerçek anahtar veya mock kip olmadan true ise açılış hata verir."
    )
    rep.body(
        "Arkaplan testleri CI’da Python 3.11 ile çalışır [25]. Tam YOLO + EasyOCR CI’da "
        "çalıştırılmaz; tek CPU fotoğrafı GitHub koşucuları için çok yavaştır, bu yüzden "
        "uçtan uca duman testinde analyze sahtelenir. Test modülleri eşleme, veritabanı, "
        "octet-stream yükleme, explain, LLM yapılandırması, taramalar, güvenlik (CORS, "
        "üretimde docs kapalı, başlıklar, HTTP 429), performans bayrakları, model yolları, "
        "CSV doğrulama, TİTCK eşleme ve marka ayırımını kapsar. Flutter CI flutter analyze "
        "ve flutter test çalıştırır. Canlı betikler scripts/e2e_api_flow.py ve "
        "scripts/benchmark_analyze.py yerel makine içindir."
    )
    rep.caption(
        "Tablo 4.10 Stajda kaydedilen performans sayıları. 255 saniye ilk emülatör "
        "tabanıdır, sonraki tipik süre değildir.",
        above=True,
    )
    rep.table(
        ["Ölçüm", "Değer"],
        [
            ["İlk emülatör analyze (fast, CPU, bir kutu)", "yaklaşık 255 s"],
            ["Sonraki tipik fast CPU analyze", "fotoğraf başına yaklaşık 1–3 dakika"],
            ["O ilk koşuda A-Ferin Forte eşlemesi", "yaklaşık %85,7, OCR metni a ferin"],
            ["Mobil analyze HTTP zaman aşımı", "300 s"],
            ["E2E pytest OCR dışı adımlar", "her biri 5 s altı"],
            ["Medicines / scans CRUD (gözlenen)", "2 s altı"],
            ["Docker sağlık kontrolü start-period", "180 s (EasyOCR ve YOLO yükü)"],
            ["Analyze hız sınırı (varsayılan)", "dakikada IP başına 20"],
            ["Explain hız sınırı (varsayılan)", "dakikada IP başına 5"],
            ["Scans hız sınırı (varsayılan)", "dakikada IP başına 30"],
        ],
    )
    rep.body(
        "Performans işi fast kipinde OCR arama uzayını kesti, erken çıkış ekledi, "
        "yüklemeleri küçülttü, modelleri bir kez yükledi, geçmiş G/Ç’sini analyze "
        "bekleme yolundan çıkardı ve explain’i analyze içine gömmedi. accurate kipi "
        "bilerek daha yavaştır. GPU isteğe bağlıdır (USE_GPU=true) ve staj varsayılanı değildi."
    )

    rep.h2("4.14 Güvenlik ve DevOps")
    rep.body(
        "Uygulanan kontroller: sihirli bayt yükleme denetimi (kullanımdan kalkan imghdr "
        "kaldırıldı), erken Content-Length reddi ile 10 MB tavan, IP başına hız sınırları, "
        "güvenlik başlıkları (X-Content-Type-Options nosniff, X-Frame-Options DENY, "
        "Referrer-Policy, API yanıtlarında kamera/mikrofon/konum kapalı Permissions-Policy), "
        "üretimde hata gizleme, üretimde açık CORS listesi, üretimde OpenAPI kapalı, "
        "üretimde tarama DELETE korumalı veya kapalı, gitignore edilmiş gizliler ve tıbbi "
        "uyarılar. Kullanıcı kimliği, WAF ve bulut gizli yöneticisi uygulanmadı. İlgili "
        "kod Ek F’dedir."
    )
    rep.body(
        "Dockerfile python:3.12-slim-bookworm kullanır; OpenCV ve EasyOCR için libgl1, "
        "libglib2.0-0 ve libgomp1 kurar [23]. Compose 8000 portunu açar, ağırlıkları ve "
        "data/database’i bağlar, EasyOCR modellerini adlı birimde önbellekler. GitHub "
        "Actions arkaplan pytest, Flutter analyze/test, Docker imaj derlemesi ve isteğe "
        "bağlı Firebase App Distribution çalıştırır [24]. Git iş akışı özellik dalı, "
        "odaklı çekme isteği, main’e birleştirmedir."
    )

    rep.h2("4.15 Karşılaşılan Problemler ve Çözümler")
    rep.body("Aşağıdaki hatalar gerçek fotoğraflarda veya Android emülatöründe çıktı, sonra kodda düzeltildi.")
    p = rep._p()
    r = p.add_run("Bulanık telefon fotoğrafında sıfır YOLO kutusu. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Varsayılan güven 0,60 fazla katıydı. Birincil eşik 0,40’a indi; boş veya zayıf "
        "sonuçlar 0,25’te yeniden denenir. Ölçülen örnek: bulanık çoklu kutu karesinde "
        "0 kutu, 3 kutu oldu."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Kısmi marka OCR (fen) not_found verdi. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Kapsama kontrolleri kısa dizileri reddediyordu. Kısmi marka eşlemesi eklendi: "
        "sorgu brand_name içinde alt dizi olmalı, yeterli harf kapsamı ve yüksek RapidFuzz "
        "skoru gerekir. Tek harfler hâlâ reddedilir."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Doz OCR’ı yanlış ilaç seçti. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "250 mo / j0o mo tablot satırı active_ingredient üzerinden Parafon kutusuna "
        "Nurofen Cold and Flu döndürdü. Yalnızca doz metni artık elenir; bu sorgularda "
        "etken madde karşılaştırması atlanır."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Ibucold C’de C yerine euro işareti. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Normalleştirici para birimi ve telif benzerlerini c yapar. Yan yana OCR "
        "parçaları birleştirilir. Düzeltme sonrası bildirilen eşleme: Ibucold C, skor 100."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("CSV’de ilaç yok. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "38 satırlık katalogda Parafon yoktu. Eklendi; sonraki TİTCK genişletmesi sistematik "
        "cevap oldu. Marka hâlâ yoksa parça örtüşme kuralları komşu satır yerine not_found "
        "tercih eder. 153 satırlık genişletmede kesit 80’den 88’e çıktı (Ferrum Pharmaton olmamalı)."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Beraberlikte daha uzun SKU adının kazanması. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "OCR plus görmeden Parol Plus, Parol’u geçebiliyordu. Ayırım artık OCR kanıtındaki "
        "varyant parçalarını kullanır; bu parçalar yoksa temel SKU tercih edilir."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Android HTTP 415 Unsupported Media Type. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Galeri yüklemeleri application/octet-stream geliyordu. Arkaplan bunu uzantıdan "
        "MIME’ye çevirir; istemci de MIME’yi sonekten yazar."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Analyze birkaç dakika sürdüğü için bozuk sanıldı. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Zaman aşımı 300 saniyeye çıkarıldı, yükleme metni değiştirildi, galeri ve sunucu "
        "küçültmesi eklendi, fast OCR arama uzayı kesildi. Taban yaklaşık 255 saniye, "
        "sonraki tipik fast CPU süreleri yaklaşık 1–3 dakika."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Yer tutucu dizelerin arayüze sızması. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Gösterim yardımcısı VERIFY_FROM_OFFICIAL_LEAFLET ifadesini insan cümlesine çevirir."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Kutu etiketlerinde bir fazla sayma. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "API zaten 1 tabanlı box_index kullanıyordu. Arayüz bir kez daha +1 ekliyordu. "
        "Fazla artış kaldırıldı."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Üretime yakın boşluklar. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Joker CORS, açık /docs, 500’de yığın izi, sınırsız analyze POST ve yayın "
        "derlemesinde açık metin, ortam değişkenli ayarlar ve tests/test_security.py ile "
        "kapatıldı. Üretimde tarama DELETE, SCANS_API_KEY eklenene kadar fazla açıktı. "
        "Streamlit Flutter lehine bırakıldı. Soğuk Docker açılışı varsayılan sağlık "
        "penceresini kaçırıyordu; start-period 180 saniye yapıldı."
    )
    set_run_font(r2)

    rep.caption("Tablo 4.11 Teslim edilenlerin sayısal özeti.", above=True)
    rep.table(
        ["Nicelik", "Değer"],
        [
            ["Katalog boyutu", "1163 ilaç"],
            ["Referans TİTCK SKRS aktif satır", "7948 (bildirim 06.08.2026)"],
            ["Yayımlanan YOLO görüntüsü", "395"],
            ["YOLO sınıf sayısı", "1 (medicine-box)"],
            ["Son eşleme kesiti", "88"],
            ["Yükleme tavanı", "10 MB"],
            ["Yerel geçmiş tavanı", "50"],
            ["Sunucu geçmiş tavanı", "200"],
            ["Arkaplan pytest modülü", "tests/ altında 14"],
            ["Flutter test dosyası", "mobile/test/ altında 10"],
        ],
    )

    rep.h2("4.16 Belgeleme ve Yayım")
    rep.body(
        "Ürün adı Yolocilin’dir. GitHub deposu, GitHub Projects tahtası, Android "
        "uygulama ve Kaggle veri seti aynı adı kullanır [5], [33]. İş takibi issue ve "
        "çekme istekleriyle yürütülmüştür."
    )
    rep.body(
        "Eğitim görüntüleri Git deposuna konmamıştır. Gizlilik temizliği yapılan 395 "
        "görüntülük YOLO seti, Yolocilin Medicine Box Detection başlığıyla Kaggle’da "
        "yayımlanmıştır; lisans CC BY 4.0’tır [5]."
    )
    rep.body(
        "Staj süresince geliştirme ile paralel olarak teknik notlar Medium’da üç dizide "
        "tutulmuştur. Diziler projenin katmanlarına karşılık gelir: Computer Vision "
        "(YOLOv8, OpenCV, OCR) [30], Learning REST APIs with FastAPI [31] ve Database "
        "(CSV, SQLite, katalog) [32]. Bu yazılar ürünün yerine geçmez; stajda öğrenilen "
        "yöntemlerin kamuya açık kısa kaydıdır. Dizinin geri kalan başlıkları staj "
        "raporunun tesliminden sonra aynı ad altında sürdürülebilir."
    )

    rep.h1("5. SONUÇ")
    rep.body(
        "Staj, çalışan bir ürün bıraktı: eğitilmiş tek sınıflı detektör, hata durumlu "
        "OCR ve eşleme hattı, FastAPI servisi, TİTCK ile zenginleştirilmiş 1163 satırlık "
        "katalog, Android istemci, Docker paketleme ve CI. İş GitHub issue’larına karşı "
        "özellik dallarında yürüdü. Veri seti Kaggle’da, teknik notlar ise Medium "
        "dizilerinde yayımlanmıştır.",
        first=True,
    )
    rep.body(
        "Teknik olarak işe yarayan ders şuydu: temiz Roboflow görüntülerinde tespit "
        "doğruluğu, mutfak masası fotoğrafında tanıma ile aynı problem değildir. İlk "
        "best.pt’den sonraki sürenin çoğu OCR varyantlarına, RapidFuzz korumalarına, "
        "katalog kalitesine ve üç dakikalık CPU çağrısını mobil arayüzde kullanılabilir "
        "kılmaya gitti. Eşleme kesitini yükseltmek ve yabancı marka parçalarını reddetmek, "
        "başka bir YOLO ölçeği eklemekten daha çok güven verdi. İlk yanlış eşlemelerden "
        "sonra hedef, sistemin yanlış markadan çok not_found ile düşmesiydi."
    )
    rep.body(
        "Sınırlar da sonucun parçasıdır. Kullanıcı kimliği yoktur; sunucu tarama geçmişi "
        "geneldir. Çıkarım CPU’ya bağlıdır, gerçek zamanlı değildir. Katalog tam TİTCK "
        "listesi değildir. iOS, PostgreSQL, barkod ve genel HTTPS yayını sonraya bırakıldı. "
        "Gemini açıklamaları isteğe bağlıdır ve prospektüs yerine okunmamalıdır."
    )
    rep.body(
        "Bir bilgisayar mühendisliği stajı için teslimat çalışan bir dikey dilimdir: "
        "görü modeli, veri hattı, HTTP API, mobil istemci, testler ve sistemi başka "
        "bir makinede yeniden çalıştırmak için gereken işletme dosyaları. Bölüm "
        "kılavuzunun istediği gibi her iç sayfada sol altta öğrenci imzası, sağ altta "
        "sorumlu mühendis imzası ve şirket kaşesi bulunmalıdır."
    )

    rep.h1("EKLER")
    rep.body(
        "Staj yazım kuralları gereği kodlar metin içinde değil, yalnızca bu bölümdedir. "
        "Buradaki listeler dosyaların tamamı değildir; ilgili fonksiyonlardan kısaltılmış "
        "alıntılardır. Tüm proje kaynak kodu Yolocilin GitHub deposundadır [33]. Ayrı bir "
        "kod raporu veya tüm dosyaların Word’e kopyalanması gerekmez. Bu bölümde satır "
        "aralığı tektir.",
        first=True,
    )
    rep.caption("Tablo EK.1 Eklerdeki alıntıların kaynak dosyaları. Tam kod [33].", above=True)
    rep.table(
        ["Ek", "Dosya", "Ne gösterilir"],
        [
            ["A", "src/preprocessing/color_operations.py, src/ocr/ocr_pipeline.py", "CLAHE ve keskinleştirme"],
            ["B", "src/services/detection_service.py", "YOLO güven yedeklemesi"],
            ["C", "src/ocr/ocr_pipeline.py, src/services/config.py", "Hızlı OCR varyantları"],
            ["D", "src/matching/medicine_matcher.py", "RapidFuzz eşleme"],
            ["E", "backend/app/services/analyze_service.py", "Yükleme ve küçültme"],
            ["F", "backend/app/middleware/security_headers.py", "Güvenlik başlıkları"],
            ["G", "data/samples/", "Örnek fotoğraflar Bölüm 4’tedir"],
        ],
    )

    rep.h2("Ek A  OpenCV Ön İşleme (CLAHE ve keskinleştirme)")
    rep.body(
        "Kaynak: src/preprocessing/color_operations.py ve src/ocr/ocr_pipeline.py. "
        "CLAHE yerel kontrastı artırır; keskinleştirme çekirdeği yazı kenarlarını "
        "belirginleştirir. Bu iki işlem, OCR öncesi üretilen varyantların temelidir [9]."
    )
    rep.code(
        "def convert_to_grayscale(image):\n"
        "    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "\n"
        "def apply_clahe(grayscale_image, clip_limit=2.0, tile_grid_size=(8, 8)):\n"
        "    clahe = cv2.createCLAHE(\n"
        "        clipLimit=clip_limit,\n"
        "        tileGridSize=tile_grid_size,\n"
        "    )\n"
        "    return clahe.apply(grayscale_image)\n"
        "\n"
        "def apply_sharpening(image):\n"
        "    kernel = np.array(\n"
        "        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],\n"
        "        dtype=np.float32,\n"
        "    )\n"
        "    return cv2.filter2D(image, ddepth=-1, kernel=kernel)"
    )

    rep.h2("Ek B  YOLO Güven Eşiği Yedekleme")
    rep.body(
        "Kaynak: src/services/detection_service.py (detect_all). Birincil eşik 0,40. "
        "Kutu yoksa, veya en iyi skor 0,55’in altındaysa ve 0,25 geçişi daha fazla kutu "
        "bulursa yedek sonuç tutulur."
    )
    rep.code(
        "primary_threshold = self.config.confidence_threshold          # 0.40\n"
        "fallback_threshold = self.config.fallback_confidence_threshold  # 0.25\n"
        "detected_boxes = self._detect_at_threshold(image_path, primary_threshold)\n"
        "should_use_fallback = not detected_boxes\n"
        "if detected_boxes and max(box.confidence for box in detected_boxes) < 0.55:\n"
        "    fallback_boxes = self._detect_at_threshold(image_path, fallback_threshold)\n"
        "    if len(fallback_boxes) > len(detected_boxes):\n"
        "        detected_boxes = fallback_boxes\n"
        "        should_use_fallback = True\n"
        "if not detected_boxes:\n"
        "    detected_boxes = self._detect_at_threshold(image_path, fallback_threshold)"
    )

    rep.h2("Ek C  Hızlı OCR Varyantları")
    rep.body(
        "Kaynak: src/ocr/ocr_pipeline.py (add_minimal_variants) ve src/services/config.py. "
        "fast kipi dönüş başına orijinal ve keskinleştirilmiş tutar, erken durabilir."
    )
    rep.code(
        "def add_minimal_variants(variants, prefix, image) -> None:\n"
        '    """Fast OCR mode: 2 variants per angle."""\n'
        '    variants[f"{prefix}_original_color"] = image\n'
        '    variants[f"{prefix}_sharpened_color"] = apply_sharpening(image)\n'
        "\n"
        "# PipelineConfig (excerpt)\n"
        "confidence_threshold: float = 0.40\n"
        "fallback_confidence_threshold: float = 0.25\n"
        "ocr_scale_factor_fast: float = 1.75\n"
        "max_image_dimension: int = 1280\n"
        "minimum_match_score: float = 88.0\n"
        'ocr_languages: tuple[str, ...] = ("tr", "en")\n'
        'ocr_mode: OCRMode = "fast"\n'
        "# ocr_rotation_angles -> (0, 90, 180, 270)\n"
        "# ocr_early_exit -> True when ocr_mode == fast"
    )

    rep.h2("Ek D  RapidFuzz Eşleme")
    rep.body(
        "Kaynak: src/matching/medicine_matcher.py ve src/matching/text_normalizer.py. "
        "Benzerlik, normalize_ocr_text sonrası fuzz.WRatio’dur [11]."
    )
    rep.code(
        "def calculate_text_similarity(query_text: str, medicine_name: str) -> float:\n"
        "    cleaned_query = normalize_text(query_text)\n"
        "    cleaned_medicine_name = normalize_text(medicine_name)\n"
        "    if not cleaned_query or not cleaned_medicine_name:\n"
        "        return 0.0\n"
        "    return float(fuzz.WRatio(cleaned_query, cleaned_medicine_name))\n"
        "\n"
        "OCR_CONFUSABLE_TRANSLATION = str.maketrans(\n"
        '    {"€": "c", "©": "c", "¢": "c"}\n'
        ")"
    )

    rep.h2("Ek E  Analyze Yükleme Yolu")
    rep.body(
        "Kaynak: backend/app/services/analyze_service.py. Doğrulama ve küçültme "
        "asyncio.to_thread’den önce yapılır."
    )
    rep.code(
        "suffix = validate_upload_metadata(\n"
        "    filename=filename,\n"
        "    content_type=content_type,\n"
        "    allowed_extensions=self.settings.allowed_extensions,\n"
        ")\n"
        "validate_image_bytes(file_bytes, suffix=suffix)\n"
        "file_bytes, resized = resize_image_bytes_if_large(\n"
        "    file_bytes,\n"
        "    max_dimension=self.manager.config.max_image_dimension,\n"
        "    suffix=suffix,\n"
        ")\n"
        "result = await asyncio.to_thread(\n"
        "    _run_analysis, self.manager, temp_path, ocr_mode=selected_mode,\n"
        ")"
    )

    rep.h2("Ek F  Güvenlik Başlıkları")
    rep.body("Kaynak: backend/app/middleware/security_headers.py.")
    rep.code(
        'response.headers.setdefault("X-Content-Type-Options", "nosniff")\n'
        'response.headers.setdefault("X-Frame-Options", "DENY")\n'
        'response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")\n'
        "response.headers.setdefault(\n"
        '    "Permissions-Policy", "camera=(), microphone=(), geolocation=()",\n'
        ")"
    )

    rep.h2("Ek G  Örnek Fotoğraflar")
    rep.body(
        "Raporda kullanılan daha net ambalaj fotoğrafları tespit ve OCR anlatısının "
        "yanında durması için Bölüm 4’e konmuştur (Şekil 4.4–4.6). Bulanık el çekimleri "
        "ve ev eşyası görünen kareler basılı şekillere alınmamıştır."
    )

    rep.h1("KAYNAKLAR")
    refs = [
        "[1] Cerebrum Technologies, “Cerebrum Technologies” (ana sayfa: misyon, YZ tanımı, Ankara ofis adresi), erişim 13 Ağustos 2026. https://www.cerebrumtechnologies.com",
        "[2] Cerebrum Tech, “Hakkımızda” (misyon metni; R. Erdem Erkul, PhD mesajı), erişim 13 Ağustos 2026. https://www.cerebrumtechnologies.com/en/hakkımızda",
        "[3] Cerebrum Tech, “Sürdürülebilirlik” (orman yangını tespiti; arıcılık ve akıllı tarım), erişim 13 Ağustos 2026. https://www.cerebrumtechnologies.com/en/copy-of-vizyonumuz",
        "[4] Cerebrum Tech, “Ekibimiz” (yayımlanan kurucu ve yönetim unvanları), erişim 13 Ağustos 2026. https://www.cerebrumtechnologies.com/en/ekibimiz-ile-tanisin",
        "[5] Kaggle, “Yolocilin Medicine Box Detection” (veri seti etiketi melikeklahc/yolocilin-medicine-box-detection), CC BY 4.0, erişim 13 Ağustos 2026. https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection",
        "[6] Ultralytics, YOLOv8 Docs, erişim 13 Ağustos 2026. https://docs.ultralytics.com",
        "[7] Jocher, G., Chaurasia, A., Qiu, J., Ultralytics YOLO, 2023. https://github.com/ultralytics/ultralytics",
        "[8] Redmon, J., Divvala, S., Girshick, R., Farhadi, A., “You Only Look Once: Unified, Real-Time Object Detection,” Proc. IEEE Conference on Computer Vision and Pattern Recognition, 2016, ss. 779–788.",
        "[9] OpenCV, OpenCV Documentation, erişim 13 Ağustos 2026. https://docs.opencv.org",
        "[10] JaidedAI, EasyOCR, erişim 13 Ağustos 2026. https://github.com/JaidedAI/EasyOCR",
        "[11] RapidFuzz, RapidFuzz Documentation (fuzz.WRatio), erişim 13 Ağustos 2026. https://rapidfuzz.github.io/RapidFuzz",
        "[12] FastAPI, FastAPI Documentation, erişim 13 Ağustos 2026. https://fastapi.tiangolo.com",
        "[13] Pydantic, Pydantic Documentation, erişim 13 Ağustos 2026. https://docs.pydantic.dev",
        "[14] SQLAlchemy, SQLAlchemy 2.0 Documentation, erişim 13 Ağustos 2026. https://docs.sqlalchemy.org",
        "[15] SQLite, SQLite Documentation, erişim 13 Ağustos 2026. https://www.sqlite.org/docs.html",
        "[16] Flutter, Flutter Documentation, erişim 13 Ağustos 2026. https://docs.flutter.dev",
        "[17] Dart, http paketi, erişim 13 Ağustos 2026. https://pub.dev/packages/http",
        "[18] Flutter, image_picker paketi, erişim 13 Ağustos 2026. https://pub.dev/packages/image_picker",
        "[19] Flutter, sqflite paketi, erişim 13 Ağustos 2026. https://pub.dev/packages/sqflite",
        "[20] Google, Gemini API / Google GenAI Python SDK, erişim 13 Ağustos 2026. https://ai.google.dev",
        "[21] T.C. Sağlık Bakanlığı, Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK), “SKRS E-Reçete İlaç ve Diğer Farmasötik Ürünler Listesi,” erişim 13 Ağustos 2026. https://www.titck.gov.tr/dinamikmodul/43",
        "[22] Roboflow, Roboflow Documentation, erişim 13 Ağustos 2026. https://docs.roboflow.com",
        "[23] Docker, Docker Documentation, erişim 13 Ağustos 2026. https://docs.docker.com",
        "[24] GitHub, GitHub Actions Documentation, erişim 13 Ağustos 2026. https://docs.github.com/en/actions",
        "[25] pytest, pytest Documentation, erişim 13 Ağustos 2026. https://docs.pytest.org",
        "[26] Uvicorn, Uvicorn Documentation, erişim 13 Ağustos 2026. https://www.uvicorn.org",
        "[27] Creative Commons, Attribution 4.0 International (CC BY 4.0), erişim 13 Ağustos 2026. https://creativecommons.org/licenses/by/4.0/",
        "[28] PyTorch, PyTorch Documentation, erişim 13 Ağustos 2026. https://pytorch.org/docs/stable/index.html",
        "[29] Düzce Üniversitesi Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü, Staj Raporu Hazırlama Kılavuzu (StajRaporuİngilizce), t.y.",
        "[30] Külahcı, M. E., “Computer Vision” (Medium dizisi; Yolocilin görü, OpenCV ve OCR notları), erişim 13 Ağustos 2026. https://medium.com/@m.edakulahci/list/computer-vision-d0f63fcdf7d2",
        "[31] Külahcı, M. E., “Learning REST APIs with FastAPI” (Medium dizisi; Yolocilin arkaplan notları), erişim 13 Ağustos 2026. https://medium.com/@m.edakulahci/list/learning-rest-apis-with-fastapi-ad9c2442f9d6",
        "[32] Külahcı, M. E., “Database” (Medium dizisi; CSV, SQLite ve katalog notları), erişim 13 Ağustos 2026. https://medium.com/@m.edakulahci/list/database-25184640519a",
        "[33] Külahcı, M. E., Yolocilin (GitHub deposu), erişim 13 Ağustos 2026. https://github.com/Melikeda/yolocilin",
    ]
    for item in refs:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.0, indent=False, space_before=0, space_after=6)
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        r = p.add_run(item)
        set_run_font(r, size=12)

    for section in doc.sections:
        set_page_border(section)

    OUT_DOCS.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DOCS))
    try:
        OUT_DOWNLOADS.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(OUT_DOWNLOADS))
    except OSError:
        pass
    print(f"Wrote {OUT_DOCS}")
    if OUT_DOWNLOADS.exists():
        print(f"Wrote {OUT_DOWNLOADS}")


if __name__ == "__main__":
    build()
