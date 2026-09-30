
## Özet

| | |
|---|---|
| Başlangıç | 19:20 |
| Bitiş | 00.04
| Toplam süre |Yaklaşık 4 saat
| Kullandığım araç | Claude (sohbet arayüzü). Başka AI aracı kullanmadım.|

## Görev dağılımı

**AI'dan aldığım yardım**
- 24 saatlik yol haritası ve teknoloji önerisi (FastAPI, Neon Postgres, Render)
- `app/main.py`: kayıt endpoint'i, Pydantic doğrulaması, korumalı kayıt listesi
- `static/index.html` ve `static/admin.html`: Bootstrap arayüzü, form durumları
- `tests/test_api.py` ve README taslağı
- Git, PowerShell ve Render kurulumunda hata ayıklama yönlendirmeleri

**Kendi yaptıklarım**
- GitHub reposu, sanal ortam, paketler, Neon veritabanı ve `.env` kurulumu
- Render'da servis oluşturma ve ortam değişkenlerini girme
- Kodu yerelde ve canlıda çalıştırıp denemek, hata mesajlarını takip etmek
- Git çakışmasını ve push hatasını çözmek
- Testleri çalıştırmak, README ve bu dosyayı doldurmak

## Adım adım kayıt

### 1. Kurulum, planlama ve veritabanı bağlantısı
- Claude'dan görev metnine göre yol haritası istedim. Ürün fikri olarak önerilen "mesajları görev kartına çeviren servis" fikrini kabul ettim ve **Kartla** adıyla kurgusal ürün yaptım.
- Teknoloji önerisini kabul ettim: FastAPI + Neon Postgres + Render. Gerekçe: bazı ücretsiz hostinglerde disk kalıcı olmayabiliyor, Postgres bu riski ortadan kaldırıyor.
- Yerelde `/health` ve `POST /api/requests` ile kaydın Neon'a yazıldığını gördüm (ilk kayıt numarası 1 döndü).

### 2. Arayüz, form ve admin sayfası
- Claude'dan Bootstrap ile basit bir landing page ve form istedim. İsim, e-posta, hizmet seçimi, açıklama alanları; istemci ve sunucu doğrulaması; gönderiliyor, başarı ve hata durumları kodlandı.
- Başarı mesajı yalnızca HTTP 201 ve gövdede sayısal `id` varsa gösteriliyor.
- Kayıtları tarayıcıdan görmek için `admin.html` sayfasını ekledik.
- **Karşılaştığım sorun:** Admin sayfası 401 verdi. Sebep, `.env` değişince çalışan sunucunun yeniden başlatılmamasıydı. Sunucuyu yeniden başlatınca kayıtlar listelendi.
- **Veri kuralı:** Formda denediğim bir kayıtta gerçek e-posta adresimi kullanmıştım. Görevin "yalnızca kurgusal veri" kuralı nedeniyle sildim`. Sonraki denemelerde uydurma veri kullandım.

### 3. Canlıya alma ve canlıda test
- Render'da Web Service oluşturdum. Claude'un önerdiği başlatma komutunu (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`) girdim, Render'ın varsayılan `gunicorn` komutunu değiştirdim.
- `DATABASE_URL` ve `ADMIN_TOKEN` değerlerini Render ortam değişkenlerine girdim, `.env` dosyası repoya eklenmedi (`git status` ile kontrol ettim).
- **Git sorunu:** `git push` reddedildi, `AI_LOG.md` için çakışma çıktı. `git pull --rebase` ile çakışmayı elle çözüp push ettim.
- Canlı adreste form gönderimini ve admin sayfasını denedim, telefon ile test ettim  bir sorun görmedim.

### 4. Testler
- Claude pytest testlerini yazdı. Testler sahte bir veritabanı bağlantısı kullanır, gerçek veritabanına dokunmaz.
- İlk çalıştırmada pytest 0 test topladı. Dosya yerleşimini düzelttikten sonra **14 test geçti**.
- Kapsam: geçerli kayıt, veri kırpma, eksik ve geçersiz alanlar (geçersizse kayıt yazılmıyor), bot tuzağı, veritabanı hatasında 500 ve gövdede `id` olmaması, admin token koruması, `/health`.


## Kabul ettiğim ve değiştirdiğim öneriler

| Öneri | Kararım | Gerekçe |
|---|---|---|
| Postgres (Neon), SQLite değil | Kabul | Yeniden başlatmada veri kaybı riski yok |
| Başarı mesajı yalnızca 201 + `id` ile | Kabul | Sunucu hatasında yanlışlıkla başarı göstermemek |
| Admin sayfası ve token korumalı kayıt listesi | Kabul | Kalıcı kaydı canlıda göstermek için |
| Render'ın varsayılan `gunicorn` başlatma komutu | Değiştirdim | Uygulama FastAPI, `uvicorn` ile çalışıyor |
| |



## Bu çalışmada bulduğum hatalar
- Admin 401: sunucunun `.env` değişikliğinden sonra yeniden başlatılması gerekiyordu.
- Git çakışması: hem GitHub'daki hem yereldeki commit `AI_LOG.md`'yi değiştirmişti.
- pytest ilk çalıştırmada 0 test topladı (dosya yerleşimi).



## Doğrulama özeti
- Yerelde: geçerli kayıt Neon'a yazıldı, admin sayfasında göründü, yanlış token 401 verdi.
- Canlıda: Boş form doldurma , Doldurulan formlar kayıt edilip edilmemesi , Hatalı eposta formatı girilmesi , mobil uyumluluk testleri yapıldı.
- Otomatik testler: 14 test geçti.

## Bilinen sınırlar
IP başına hız sınırı yok, e-posta doğrulanmıyor, admin koruması tek paylaşılan token. Ayrıntı için README'deki "Bilinen eksikler" bölümüne bak.