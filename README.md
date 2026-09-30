# Kartla

Kartla, e-posta ve WhatsApp mesajlarındaki işleri sahipli görev kartlarına çeviren kurgusal bir servistir. Bu repo, bir değerlendirme çalışması için hazırlanmış landing page ve talep formunu içerir. Ticari amaçla kullanılmaz, yalnızca kurgusal test verisi girilmelidir.

- **Canlı URL:** https://enteksis-mulakat.onrender.com/
- **Kayıt listesi (token gerekir):** https://enteksis-mulakat.onrender.com/admin.html
- **Harcanan süre:** Yaklaşık 4 saat harcadım

## Neler var
- Mobil ve masaüstü uyumlu landing page (Bootstrap 5)
- Talep formu: isim, e-posta, hizmet seçimi, açıklama
- İstemci ve sunucu tarafında alan doğrulaması
- Gönderiliyor, başarı ve hata durumları
- Kayıtlar Neon Postgres'te kalıcı saklanır
- Başarı mesajı yalnızca sunucu HTTP 201 ve kayıt numarası döndürdüğünde gösterilir

## Teknoloji
| Katman | Seçim |
|---|---|
| Backend | FastAPI, Uvicorn, Pydantic |
| Veritabanı | Neon Postgres (psycopg) |
| Frontend | HTML, Bootstrap 5 (CDN), vanilla JS |
| Test | pytest, httpx |
| Hosting | Render (ücretsiz plan) |

Postgres'i, bazı ücretsiz hostinglerde dosya diskinin yeniden başlatmada silinebilmesi nedeniyle seçtim (SQLite yerine).

## Yerelde çalıştırma
```powershell
git clone https://github.com/EnesEmek26/Enteksis_mulakat.git
cd Enteksis_mulakat
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env     # sonra .env içindeki değerleri doldur
python -m uvicorn app.main:app --reload
```
Uygulama `http://127.0.0.1:8000/` adresinde açılır.

## Ortam değişkenleri
| Değişken | Açıklama |
|---|---|
| `DATABASE_URL` | Postgres bağlantı adresi (örnek: `.env.example`) |
| `ADMIN_TOKEN` | `/api/requests` (GET) ve `/admin.html` için gizli token |

`.env` dosyası repoya eklenmez.

## API
- `POST /api/requests` — 201 `{"id": N}`, 422 `{"errors": {alan: mesaj}}`, 400 (bot tuzağı), 500 genel hata
- `GET /api/requests` — `X-Admin-Token` başlığı gerekir, son 50 kaydı döndürür
- `GET /health` — veritabanı bağlantısını ve kayıt sayısını döndürür

## Testler
```powershell
python -m pytest -v
```
Testler sahte bir veritabanı bağlantısı kullanır, gerçek veritabanına dokunmaz. Kapsam: geçerli kayıt, eksik ve geçersiz alanlar, bot tuzağı, veritabanı hatasında 500, admin yetkilendirmesi.

## Bilinen eksikler
- IP başına hız sınırı yok, koruma olarak yalnızca bot tuzağı alanı var.
- E-posta adresleri doğrulanmıyor (sadece biçim kontrolü).
- Admin koruması tek bir paylaşılan token ile yapılıyor, kullanıcı hesabı yok.
- Her istekte yeni veritabanı bağlantısı açılıyor (bağlantı havuzu yok).
- Ücretsiz Render planında servis uyur, ilk istek yavaş olabilir.
- Bootstrap CDN'den yüklenir, çevrimdışı çalışmaz.


## Kaynaklar ve kullanılan hazır parçalar
- Bootstrap 5.3 (CDN), FastAPI, Pydantic, psycopg, pytest
- Hazır şablon kullanılmadı.
- Kodun bir kısmı AI yardımıyla yazıldı, ayrıntılar için `AI_LOG.md` dosyasına bakın.