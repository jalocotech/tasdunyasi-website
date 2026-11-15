# Taş Dünyası – yeni web sitesi

Statik site. E-ticaret yok: ürünler katalog olarak listelenir, ziyaretçi teklif formu, WhatsApp ya da telefona yönlendirilir.

- Taslak adresi: https://jalocotech.github.io/tasdunyasi-website/
- Yapılacaklar: [YAPILACAKLAR.md](YAPILACAKLAR.md)

## Nasıl güncellenir

1. `data/urunler.csv` dosyasını düzenleyin (Excel ile açılır). Sütunlar: `ad`, `kategori`, `detay`, `gorseller`, `yayinda` (evet/hayir). `slug` ürünün adresidir; yayından sonra değiştirmeyin.
2. Ayarlar `config.json` içinde: WhatsApp, e-posta, telefonlar, adres, `fiyat_goster`, `taslak`.
3. Bir ürüne özel açıklama, ebat ve paketleme bilgisi `data/ozel.json` içinde, ürün `id`'siyle.
4. `python3 build.py` komutu `docs/` klasörünü yeniden üretir. Değişiklikler `main` dalına gönderilince site güncellenir.

## Klasörler

| Yol | İçerik |
|---|---|
| `data/urunler.csv` | Ürün tablosu (kaynak) |
| `data/kategoriler.json` | Kategori ağacı ve eski site kimlik eşlemesi |
| `data/ozel.json` | Ürüne özel içerik |
| `data/crawl.json` | Eski siteden taranan ham veri (15.11.2026) |
| `src/`, `assets/` | Stil, betik, görseller |
| `build.py` | Site üretici |
| `tools/import_crawl.py` | Ham veriyi `urunler.csv`'ye çevirir (bir kez çalıştırıldı) |
| `docs/` | Üretilen site (elle düzenlemeyin) |

## Notlar

- Ürün fotoğrafları şimdilik eski siteden (`gorsel_kaynagi`) yükleniyor.
- Eski `/tr-TR/...` ve `/en-US/...` adresleri `404.html` içindeki betikle yeni adreslere yönlenir (`docs/assets/legacy.json`).
- `taslak: true` iken tüm sayfalar arama motorlarına kapalıdır (noindex + robots.txt).
