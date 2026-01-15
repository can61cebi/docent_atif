# Doçentlik Atıf Dosyası Oluşturma Aracı

Akademik personelin doçentlik başvuruları için gerekli atıf dosyalarını otomatik olarak hazırlayan web tabanlı bir uygulamadır. 2025 YÖK kriterlerine uygun formatta doküman üretir.

## Özellikler

- Web of Science export dosyalarından atıf bilgilerini otomatik ayrıştırma
- PDF tam metinlerinden atıf sayfalarını tespit etme
- Atıf cümleleri ve kaynak referanslarını sarı ile vurgulama
- Kapak ve ünvan sayfaları ekleme desteği
- YÖK formatına uygun PDF doküman oluşturma
- Excel raporu oluşturma
- Doküman arşivi yönetimi

## Sistem Gereksinimleri

- Python 3.10 veya üzeri
- Node.js 18 veya üzeri
- Windows 10/11

## Kurulum

### 1. Python Bağımlılıkları

```bash
pip install -r requirements.txt
```

### 2. Web Arayüzü

```bash
cd web
npm install
```

## Çalıştırma

### Geliştirme Modu

**Python Backend (Terminal 1):**
```bash
python main.py
```

**Web Arayüzü (Terminal 2):**
```bash
cd web
npm run dev
```

Tarayıcınızda `http://localhost:3000` adresini açın.

## Kullanım

### Adım 1: Aday Bilgileri
Kişisel bilgilerinizi ve kaynak makale bilgilerini girin.

![Aday Bilgileri](screenshots/01-aday-bilgileri.png)

### Adım 2: WoS Dosyası Yükleme
Web of Science'tan export ettiğiniz `savedrecs.txt` dosyasını yükleyin.

![WoS Import](screenshots/02-wos-import.png)

### Adım 3: PDF Dosyaları
Atıf yapan makalelerin tam metin PDF dosyalarını yükleyin. Sistem otomatik olarak eşleşme yapar.

![PDF Yükleme](screenshots/03-pdf-yukleme.png)

### Adım 4: Kapak Sayfaları
Her makale için dergi kapak/ünvan sayfalarını ekleyin (PNG, JPG veya PDF).

### Adım 5: Doküman Oluşturma
Tüm veriler tamamlandığında "Dokümanları Oluştur" butonuna tıklayın.

![Doküman Oluşturma](screenshots/04-dokuman-olusturma.png)

### Adım 6: Doküman Arşivi
Oluşturulan tüm dokümanlar arşivde saklanır.

![Doküman Arşivi](screenshots/05-dokuman-arsivi.png)

## Proje Yapısı

```
docentlikatif/
├── config.py              # Yapılandırma ve veri sınıfları
├── document_builder.py    # PDF doküman oluşturucu
├── pdf_processor.py       # PDF işleme ve atıf bulucu
├── check_citation_cli.py  # Atıf kontrol CLI aracı
├── import_utils.py        # WoS dosya ayrıştırıcı
├── main.py               # Ana CLI uygulaması
├── requirements.txt      # Python bağımlılıkları
├── fonts/                # PDF için font dosyaları
├── downloads/            # Yüklenen PDF dosyaları
├── output/               # Oluşturulan dokümanlar
└── web/                  # Nuxt.js web arayüzü
    ├── app/              # Vue bileşenleri ve sayfalar
    ├── server/           # API endpointleri
    └── public/           # Statik dosyalar
```

## Oluşturulan Doküman Formatı

Her atıf için aşağıdaki bölümleri içerir:

1. **Atıf Listesi** - Tüm atıf yapan makalelerin künye bilgileri
2. **Yayının Ünvan Sayfası** - Dergi kapak/ünvan sayfası (kullanıcı tarafından yüklenir)
3. **Eserin Başlık Sayfası** - Atıf yapan makalenin ilk sayfası
4. **Atıf Yapılan Sayfalar** - Kaynak makalenin referans verildiği sayfalar (sarı ile vurgulu)
5. **Kaynak Sayfası** - References bölümü (atıf numarası vurgulu)

## Lisans

Bu proje GPL v3 lisansı altında yayınlanmıştır.

## İletişim

Sorularınız için GitHub Issues bölümünü kullanabilirsiniz.