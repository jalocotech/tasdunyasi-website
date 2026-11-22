# Taş Dünyası – Yapılacaklar

Durum: 15 Kasım 2026. Yeni site taslağı bu depoda; eski site (tasdunyasi.com.tr) yayında kalıyor.

## A. Yeni site (bu depo)

### Yayına almadan önce şart
- [ ] `config.json`: WhatsApp numarası ve e-posta adresi girilecek (teklif formu bunlar olmadan çalışmaz)
- [ ] Kapı numarası doğrulanacak (eski sitede 161, 163/1 ve "161 34075" olarak üç farklı yazılmış)
- [ ] Ürün fotoğrafları eski sunucudan alınıp bu depoya taşınacak (şu an eski siteden bağlantıyla geliyor; eski sunucu kapanırsa görseller kaybolur)
- [ ] Eski sitede de açılmayan ürün fotoğrafları var (ör. Tamburlanmış Dolomit, Kalsit, Mermer); yeni fotoğraf gerekli
- [ ] `data/urunler.csv` gözden geçirilecek: yayından kalkacak ürünlerde `yayinda` sütunu `hayir` yapılacak, tekrarlanan ürünler (ör. 29 ayrı "Paşabahçe") birleştirilecek
- [ ] Fiyat kararı: sitede fiyat görünecek mi? (`fiyat_goster`; şu an kapalı. Eski ürün açıklamalarındaki TL fiyatları da gizleniyor)
- [ ] "Satılmış Ürünler" grubu (136 ürün) kalacak mı?
- [ ] Yasal uyarı ve KVKK aydınlatma metni (hukuk onayıyla)
- [x] Hakkımızda: tarihçe, misyon, vizyon, biz ne yapıyoruz eski siteden aktarıldı
- [ ] "Kimler bizimle neden çalışıyor?" ve "Taş hakkında" (Neden taş / Taşla neler yapılabilir / Taşın tarihi) metinleri aktarılacak
- [ ] Logo dosyasının aslı (vektör/yüksek çözünürlük) eklenecek; şu anki görsel broşürden kırpıldı

### İyileştirme
- [ ] Diğer ihracat ürünleri için `data/ozel.json` kayıtları (ebat, ambalaj, açıklama; dolomit örnek olarak hazır)
- [ ] Referans logoları ve proje fotoğrafları
- [ ] Güncel PDF katalog ve sanal tur dosyalarının taşınması
- [x] İngilizce sürüm yapıldı (/en/). Çeviriler taslaktır; site sahibi veya çevirmen gözden geçirmeli, özellikle ürün adları ve hakkımızda metinleri
- [ ] GA4 ölçüm kodu (site olayları göndermeye hazır: quote_click, whatsapp_click, phone_click, generate_lead)

### Yayına alma
- [ ] Kalıcı hosting kararı (GitHub Pages ücretsiz; alan adı bağlanabilir. Sunucu taraflı form ve gerçek 301 yönlendirme için cPanel hosting gerekir)
- [ ] `config.json`: `taslak: false`, `site_adresi` ve `taban_yol` güncellenecek
- [ ] DNS'te alan adı yeni siteye yönlendirilecek; Search Console'a site haritası gönderilecek
- [ ] Eski adres yönlendirmeleri canlıda test edilecek (`/tr-TR/...` ve `/en-US/...`)

## B. Mevcut sunucu (acil, yeni siteden bağımsız)
- [ ] **Web shell**: `httpdocs/brute.asp` ve `httpdocs/image.cer` (03.06.2021) web dışına alınacak; Webkur'a bildirim ve tam tarama
- [ ] Tüm şifreler değişecek: Plesk, FTP, e-posta hesapları, site yönetim paneli (`testgrimor` dahil)
- [ ] Yönetim panelindeki admin e-postası eski çalışana ait; şirket adresiyle değiştirilecek
- [ ] Sunucunun tam yedeği / snapshot (şu an yedek yok; 11,6 GB e-posta risk altında)
- [ ] Plesk lisansı (anahtar boş görünüyordu) ve SSL otomatik yenilemesi doğrulanacak
- [ ] robots.txt ve sitemap.xml 500 hatası veriyor (`GoogleAyarSabit.asp`)
- [ ] Gereksiz dosyalar: `test.asp`, `YukluBilesenler.asp`, `sayfalar.asp-s` ve benzeri yedek kopyalar
- [ ] 2018 sonrası IIS/posta loglarının nerede tutulduğu Webkur'a sorulacak
- [ ] KVKK: olası veri ihlali için hukuk danışmanıyla değerlendirme

## C. Alan adı, e-posta, hosting
- [ ] tasdunyasi.com.tr hangi firmada kayıtlı, bitiş tarihi ne? (Webkur panelinde görünmüyor)
- [ ] tasdunyasiinsaat.com.tr'nin süresi dolmuş görünüyor; gerekiyorsa yeniden tescil, dosyalarının yedeği
- [ ] E-posta taşıma planı (11,6 GB): yeni hosting ya da Google Workspace / Microsoft 365; kaç hesap var?
- [ ] DNS kayıtlarının (SPF, DKIM, DMARC dahil) yeni yere taşınması
- [ ] Webkur ile görüşme: VDS'in kalan süresinin (24.07.2027'ye kadar ödenmiş, 12.500 TL/yıl) mahsubu ya da iadesi
- [ ] Temmuz 2027'den önce VDS'in kapatılması
