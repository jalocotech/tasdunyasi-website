"""Taş Dünyası statik site üreticisi.

Girdi : data/urunler.csv, data/kategoriler.json, data/ozel.json, config.json, src/, assets/
Çıktı : docs/  (GitHub Pages bu klasörü yayınlar)
Kullanım: python3 build.py
"""
import csv, json, re, shutil
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
KAT = json.loads((ROOT / 'data' / 'kategoriler.json').read_text(encoding='utf-8'))
OZEL = json.loads((ROOT / 'data' / 'ozel.json').read_text(encoding='utf-8'))
CATS = dict(KAT['cats'])  # yol -> ad
IMG = CFG['gorsel_kaynagi']
DRAFT = CFG.get('taslak', True)
SHOW_PRICE = CFG.get('fiyat_goster', False)
PHONES = CFG['telefonlar']
SOLD = 'satilmis-urunler'

products = [r for r in csv.DictReader((ROOT / 'data' / 'urunler.csv').open(encoding='utf-8-sig')) if r['yayinda'].strip().lower() == 'evet' and r['kategori'] in CATS]
for p in products:
    p['imgs'] = p['gorseller'].split()
    tokens = [t.strip() for t in p['detay'].split(',') if t.strip()]
    if not SHOW_PRICE:
        tokens = [t for t in tokens if not re.search(r'TL|KDV', t, re.I)]
    p['tokens'] = tokens
    p['ozel'] = OZEL.get(p['id'], {})
by_cat = {}
for p in products:
    by_cat.setdefault(p['kategori'], []).append(p)


def children(path):
    return [c for c in CATS if c.startswith(path + '/') and c.count('/') == path.count('/') + 1]


def all_products(path):
    return [p for p in products if p['kategori'] == path or p['kategori'].startswith(path + '/')]


def rel(depth):
    return '../' * depth


def img_url(name):
    return IMG + name


def cat_thumb(path):
    ps = all_products(path)
    return ps[0]['imgs'][0] if ps and ps[0]['imgs'] else ''


TOP = [c for c in CATS if '/' not in c]
MAIN8 = ['tamburlanmis-peyzaj-taslari', 'cam-peyzaj-urunleri', 'doseme-ve-kaplama-taslari', 'dogal-kayaclar', 'el-yapimi-peyzaj-urunleri', 'dogal-tas-heykel-ve-sutunlar', 'akvaryum-taslari-ve-camlari', 'antik-taslar']
CAT_SUB = {
    'tamburlanmis-peyzaj-taslari': 'Dolomit, kalsit, mermer, dere çakılı, kalsedon',
    'cam-peyzaj-urunleri': 'Tamburlanmış ve kaya formu renkli camlar',
    'doseme-ve-kaplama-taslari': 'Traverten, kayrak, granit, bazalt, mermer',
    'dogal-kayaclar': 'Meteor, oniks, gnays, ağaç fosili, lav taşı',
    'el-yapimi-peyzaj-urunleri': 'Oturma grubu, çeşme, fıskiye, saksı',
    'dogal-tas-heykel-ve-sutunlar': 'Mermer heykel, aslan, sütun, kaide',
    'akvaryum-taslari-ve-camlari': 'Kalsedon, falez, meteor parça, cam',
    'antik-taslar': 'Değirmen taşı, dibek, kuyu ağzı, anfora',
}


def page(depth, title, body, desc='', active='', body_class='', canonical=''):
    r = rel(depth)
    robots = '<meta name="robots" content="noindex, nofollow">' if DRAFT else ''
    draft = '<div style="background:#FFF6D6;color:#6B5300;font-size:13px;text-align:center;padding:6px 12px">Taslak site: içerik ve görseller onay aşamasındadır.</div>' if DRAFT else ''
    nav = [('Ana Sayfa', '', 'home'), ('Hakkımızda', 'hakkimizda/', 'about'), ('Ürünler', 'urunler/', 'products'), ('Referanslar', 'referanslar/', 'refs'), ('İletişim', 'iletisim/', 'contact')]
    nav_html = ''.join(f'<a href="{r}{h}"{" class=on" if k == active else ""}>{t}</a>' for t, h, k in nav)
    tel = ''.join(f'<a href="tel:{re.sub(r"[^+0-9]", "", t)}" data-ev="phone_click">{t}</a>' for t in PHONES)
    canon = f'<link rel="canonical" href="{CFG["site_adresi"].rstrip("/")}/{canonical}">' if canonical is not None and not DRAFT else ''
    return f'''<!doctype html>
<html lang="tr" data-root="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or CFG["aciklama"])}">
{robots}{canon}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/site.css">
<link rel="icon" href="{r}assets/img/logo.jpg">
</head>
<body class="{body_class}">
{draft}
<div class="topbar"><div class="wrap"><div>{tel}</div><div><a href="{r}e-katalog/">E-Katalog</a><a href="{r}urun-kategori/antika-urunler/">Antik Eşya Mağazası</a><a href="{r}sanal-tur/">360° Sanal Tur</a></div></div></div>
<header class="header">
<div class="wrap">
<a class="logo" href="{r}" aria-label="Taş Dünyası ana sayfa"><img src="{CFG["eski_site"].rstrip("/")}/common/images/logo.png" onerror="this.onerror=null;this.src='{r}assets/img/logo.jpg'" width="280" height="68" alt="Taş Dünyası – Stone World"></a>
<nav class="nav" aria-label="Ana menü">{nav_html}</nav>
<div class="header-actions">
<form class="search" action="{r}urunler/" method="get"><label class="sr" for="q">Ürün ara</label><input id="q" name="q" type="search" placeholder="Ürün ara"><button type="submit">Ara</button></form>
<a class="btn btn-ghost" data-wa="">WhatsApp</a>
<a class="btn btn-cta" href="{r}iletisim/#teklif" data-ev="quote_click">Teklif İste</a>
</div>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menüyü aç"><span></span><span></span><span></span></button>
</div>
<div class="stripe" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="drawer" id="menu" hidden>
<form class="search" action="{r}urunler/" method="get" role="search"><input name="q" type="search" placeholder="Ürün ara" aria-label="Ürün ara"><button type="submit">Ara</button></form>
<nav class="drawer-nav" aria-label="Mobil menü">{nav_html}</nav>
<nav class="drawer-sub" aria-label="Diğer bağlantılar"><a href="{r}e-katalog/">E-Katalog</a><a href="{r}urun-kategori/antika-urunler/">Antik Eşya Mağazası</a><a href="{r}sanal-tur/">360° Sanal Tur</a></nav>
<div class="drawer-tel">{tel}</div>
<a class="btn btn-ghost" data-wa="">WhatsApp ile yazın</a>
</div>
</header>
<main>
{body}
</main>
<footer class="footer">
<div class="stripe" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="wrap cols">
<div><div class="brand">Taş Dünyası</div><div>1973'ten bu yana doğal taş, madencilik ve peyzaj.</div></div>
<div><strong>Ürünler</strong>{''.join(f'<a href="{r}urun-kategori/{c}/">{e(CATS[c])}</a>' for c in MAIN8[:5])}<a href="{r}urunler/">Tüm ürünler</a></div>
<div><strong>Kurumsal</strong><a href="{r}hakkimizda/">Hakkımızda</a><a href="{r}referanslar/">Referanslar</a><a href="{r}e-katalog/">E-Katalog</a><a href="{r}yasal-uyari/">Yasal uyarı ve KVKK</a></div>
<div><strong>İletişim</strong>{tel}<div>{e(CFG["adres"])}</div></div>
</div>
<div class="wrap legal">© {e(CFG["unvan"])} Tüm hakları saklıdır.</div>
</footer>
<script src="{r}assets/config.js"></script>
<script src="{r}assets/site.js"></script>
</body>
</html>
'''


def write(path, html):
    f = OUT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding='utf-8')


def product_card(p, r):
    img = f'<img loading="lazy" data-fallback src="{e(img_url(p["imgs"][0]))}" alt="{e(p["ad"])}">' if p['imgs'] else ''
    badge = '<span class="badge">Satıldı</span>' if p['kategori'].startswith(SOLD) else ''
    sub = p['tokens'][-1] if p['tokens'] and re.search(r'\d', p['tokens'][-1]) else CATS[p['kategori']]
    return f'<a class="card" href="{r}urun/{p["slug"]}/"><div class="card-img">{img}{badge}</div><div class="card-body"><span class="card-title">{e(p["ad"])}</span><span class="card-sub">{e(sub)}</span></div></a>'


def cat_card(c, r, sub=''):
    t = cat_thumb(c)
    img = f'<img loading="lazy" data-fallback src="{e(img_url(t))}" alt="{e(CATS[c])}">' if t else ''
    n = len(all_products(c))
    return f'<a class="card" href="{r}urun-kategori/{c}/"><div class="card-img">{img}</div><div class="card-body"><span class="card-title">{e(CATS[c])}</span><span class="card-sub">{e(sub or str(n) + " ürün")}</span></div></a>'


def quote_form(r, product=''):
    val = f' value="{e(product)}"' if product else ''
    return f'''<form class="form panel" data-quote-form action="#">
<label class="full">Ürün<input type="text" name="urun" data-form-product{val} placeholder="İlgilendiğiniz ürün"></label>
<label>Miktar<input type="text" name="miktar" placeholder="ör. 2 ton, 1 konteyner"></label>
<label>Teslim yeri / varış limanı<input type="text" name="teslimat" placeholder="ör. İstanbul"></label>
<label>Ad soyad<input type="text" name="ad" autocomplete="name" required></label>
<label>Firma<input type="text" name="firma" autocomplete="organization"></label>
<label>Telefon<input type="tel" name="telefon" autocomplete="tel" required></label>
<label>E-posta<input type="email" name="eposta" autocomplete="email"></label>
<label class="full">Notunuz<textarea name="mesaj" rows="3"></textarea></label>
<label class="full check"><input type="checkbox" required><span><a href="{r}yasal-uyari/">KVKK aydınlatma metnini</a> okudum, iletişime geçilmesini kabul ediyorum.</span></label>
<div class="full btns"><button class="btn btn-cta" type="button" data-send="wa">WhatsApp ile gönder</button><button class="btn btn-navy" type="button" data-send="mail">E-posta ile gönder</button><a class="btn btn-ghost" href="tel:{re.sub(r"[^+0-9]", "", PHONES[0])}" data-ev="phone_click">{PHONES[0]}</a></div>
<p class="form-msg">Bilgileriniz yalnızca teklif hazırlamak için kullanılır.</p>
</form>'''


def crumb(items):
    out = []
    for t, h in items:
        out.append(f'<a href="{h}">{e(t)}</a><span aria-hidden="true">›</span>' if h else f'<b>{e(t)}</b>')
    return '<nav class="crumb wrap" aria-label="Konum">' + ''.join(out) + '</nav>'


# ---------- Ana sayfa ----------
def build_home():
    r = ''
    feat = next((p for p in products if p['id'] == CFG['one_cikan_urun']), products[0])
    stats = [("1973'ten beri", 'İnşaat, madencilik ve doğal taşta aile şirketi', 'var(--blue)'), ('Kendi taş ocağı', 'Ruhsatlı sahadan doğrudan tedarik', 'var(--green)'), ('Kendi tamburlama tesisi', 'Ebat ve renk seçeneğiyle üretim', 'var(--orange)'), ('FOB Ambarlı', 'Big bag ve konteyner ile ihracat', '#16303F')]
    others = [c for c in TOP if c not in MAIN8 and c != SOLD]
    refs = CFG['referanslar'][:12]
    fo = feat['ozel']
    sizes = ''.join(f'<span class="chip">{e(s)}</span>' for s in fo.get('ebatlar', []))
    body = f'''
<section class="hero"><div class="wrap">
<div class="hero-text"><span class="kicker" lang="en">Natural stone solutions for a better tomorrow</span>
<h1>İstanbul'un içinde rengarenk bir dünya</h1>
<p>Peyzaj, döşeme ve dekorasyon için doğal taş, kayaç ve cam. Kendi ocağımızdan, kendi tamburlama tesisimizden; Türkiye'ye ve dünyaya.</p>
<div class="btns"><a class="btn btn-cta" href="iletisim/#teklif" data-ev="quote_click">Teklif İste</a><a class="btn btn-light" href="urunler/">Ürünleri İncele</a></div></div>
<div class="hero-img"><img src="assets/img/showroom.jpg" alt="Taş Dünyası açık hava sergi alanı: sütunlar, çakıl taşları ve dekoratif ürünler" width="941" height="1672"><a class="hero-tag" href="urun/{feat["slug"]}/"><small>Öne çıkan ürün</small><b>{e(feat["ad"])} →</b></a></div>
</div></section>
<section class="stats"><div class="wrap">{''.join(f'<div class="stat" style="border-color:{c}"><b>{e(b)}</b><span>{e(s)}</span></div>' for b, s, c in stats)}</div></section>
<section class="block"><div class="wrap">
<div class="block-head"><div><span class="kicker">Ürünler</span><h2>Ürün gruplarımız</h2></div><a class="more" href="urunler/">Tüm ürünler</a></div>
<div class="grid wide">{''.join(cat_card(c, r, CAT_SUB.get(c, '')) for c in MAIN8)}</div>
<div class="chips" style="margin-top:22px">{''.join(f'<a class="chip" href="urun-kategori/{c}/">{e(CATS[c])}</a>' for c in others)}</div>
</div></section>
<section class="block" style="padding-top:0"><div class="wrap"><div class="card" style="flex-direction:row;flex-wrap:wrap">
<div style="flex:1 1 360px;min-height:340px;position:relative"><img src="assets/img/stones.jpg" alt="{e(feat["ad"])}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></div>
<div style="flex:1 1 480px;padding:40px;display:flex;flex-direction:column;gap:14px"><span class="kicker">Öne çıkan ürün</span><h2 class="big">{e(feat["ad"])}</h2><span class="tagline">{e(fo.get("slogan", ""))}</span><p style="margin:0;color:#3C4B55">{e(fo.get("aciklama", ""))}</p><div class="chips">{sizes}</div><div class="btns"><a class="btn btn-navy" href="urun/{feat["slug"]}/">Ürün detayı</a><a class="btn btn-ghost" href="iletisim/#teklif">Teklif iste</a></div></div>
</div></div></section>
<section class="band"><div class="wrap split">
<div><span class="kicker">Toptan &amp; ihracat</span><h2 class="big" style="margin:6px 0 14px">Big bag'den konteynere, FOB Ambarlı</h2><p style="margin:0 0 18px">Tamburlanmış taş ve camları big bag ile ya da tam konteyner olarak yüklüyoruz. Miktar, ebat ve varış limanını yazın; fiyat ve yükleme planını gönderelim.</p><div class="btns"><a class="btn btn-cta" href="iletisim/#teklif">İhracat teklifi al</a></div></div>
<div class="tiles"><div class="tile"><small>1 Big Bag</small><b>1,2–1,3 t</b><span>ortalama ağırlık</span></div><div class="tile"><small>20 ft konteyner</small><b>24–26 t</b><span>20 big bag</span></div><div class="tile"><small>40 ft konteyner</small><b>48–52 t</b><span>40 big bag</span></div></div>
</div></section>
<section class="block"><div class="wrap">
<div class="block-head"><div><span class="kicker">Referanslar</span><h2>Bizimle çalışanlar</h2></div><a class="more" href="referanslar/">Tüm referanslar</a></div>
<div class="refs">{''.join(f'<div class="ref">{e(x)}</div>' for x in refs)}</div>
</div></section>
<section class="cta-row"><div class="wrap"><div style="flex:1 1 460px"><h2 class="big" style="font-size:32px">Projeniz için teklif alın</h2><p style="margin:8px 0 0;color:#3C4B55;max-width:560px">Ürünü, miktarı ve teslim yerini yazın; fiyat ve numune için size dönelim. Taşları Kemerburgaz'da yerinde de görebilirsiniz.</p></div><div class="btns"><a class="btn btn-cta" href="iletisim/#teklif">Teklif formu</a><a class="btn btn-ghost" data-wa="">WhatsApp'tan yaz</a><a class="btn btn-ghost" href="iletisim/">Yol tarifi</a></div></div></section>
'''
    write('index.html', page(0, 'Taş Dünyası | Doğal taş, peyzaj taşı ve cam – Kemerburgaz, İstanbul', body, active='home', canonical=''))


# ---------- Ürünler ve kategori sayfaları ----------
def build_listing():
    r = rel(1)
    body = f'''{crumb([('Ana Sayfa', r), ('Ürünler', '')])}
<div class="wrap page-head"><h1 data-search-head>Ürünler</h1><p data-hide-on-search>{len([p for p in products if not p["kategori"].startswith(SOLD)])} ürün, {len(TOP) - 1} ürün grubu. Aradığınızı bulamazsanız yazın, tedarik edelim.</p>
<form class="search" action="./" method="get" style="margin-top:14px"><label class="sr" for="q2">Ürün ara</label><input id="q2" name="q" type="search" data-search-input placeholder="Taş, renk ya da ürün adı" style="width:min(420px,60vw)"><button type="submit">Ara</button></form></div>
<section class="wrap" style="padding-bottom:64px"><div class="grid" data-search-results></div>
<div class="grid wide" data-hide-on-search>{''.join(cat_card(c, r, CAT_SUB.get(c, '')) for c in TOP)}</div></section>'''
    write('urunler/index.html', page(1, 'Ürünler | Taş Dünyası', body, active='products', canonical='urunler/'))

    for c in CATS:
        depth = 2 + c.count('/')
        r = rel(depth)
        parts = c.split('/')
        trail = [('Ana Sayfa', r), ('Ürünler', r + 'urunler/')]
        if len(parts) > 1:
            trail.append((CATS[parts[0]], f'{r}urun-kategori/{parts[0]}/'))
        trail.append((CATS[c], ''))
        subs = children(c)
        ps = by_cat.get(c, []) if subs else all_products(c)
        sub_html = f'<div class="chips subcats">{"".join(f"""<a class="chip" href="{r}urun-kategori/{s}/">{e(CATS[s])} ({len(all_products(s))})</a>""" for s in subs)}</div>' if subs else ''
        if subs and not ps:
            ps = all_products(c)
        grid = ''.join(product_card(p, r) for p in ps) or '<p class="note">Bu grupta henüz ürün yok.</p>'
        body = f'''{crumb(trail)}
<div class="wrap page-head"><h1>{e(CATS[c])}</h1><p>{e(CAT_SUB.get(c, ""))}</p></div>
<section class="wrap" style="padding-bottom:64px">{sub_html}<p class="count">{len(ps)} ürün</p><div class="grid">{grid}</div></section>
<section class="cta-row"><div class="wrap"><div style="flex:1 1 460px"><h2 class="big" style="font-size:28px">{e(CATS[c])} için teklif alın</h2></div><div class="btns"><a class="btn btn-cta" href="{r}iletisim/?urun={e(CATS[c])}#teklif">Teklif iste</a><a class="btn btn-ghost" data-wa="Merhaba, {e(CATS[c])} hakkında bilgi almak istiyorum.">WhatsApp</a></div></div></section>'''
        write(f'urun-kategori/{c}/index.html', page(depth, f'{CATS[c]} | Taş Dünyası', body, desc=f'{CATS[c]}: {CAT_SUB.get(c, "Taş Dünyası ürünleri")}. Fiyat ve numune için teklif isteyin.', active='products', canonical=f'urun-kategori/{c}/'))


# ---------- Ürün detay ----------
FEATS = [('%100 Doğal', 'Özgün, yüksek kaliteli doğal malzeme.', '<path d="M5 19c8 0 14-6 14-14C11 5 5 9 5 17v2z"/><path d="M5 19c3-4 6-7 10-10"/>'),
         ('Tamburlanmış yüzey', 'Pürüzsüz, yuvarlak kenarlar.', '<path d="M6 3h12l3 6-9 12L3 9z"/><path d="M3 9h18"/>'),
         ('Dayanıklı', 'Hava koşullarına dayanıklı, uzun ömürlü.', '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>'),
         ('Çok amaçlı', 'Peyzaj, bahçe, mimari ve dekoratif kullanım.', '<path d="M2 20l7-10 4 6 3-4 6 8z"/>')]


def build_products():
    r = rel(2)
    for p in products:
        o = p['ozel']
        cat = p['kategori']
        parts = cat.split('/')
        trail = [('Ana Sayfa', r), ('Ürünler', r + 'urunler/'), (CATS[parts[0]], f'{r}urun-kategori/{parts[0]}/')]
        if len(parts) > 1:
            trail.append((CATS[cat], f'{r}urun-kategori/{cat}/'))
        trail.append((p['ad'], ''))
        sold = cat.startswith(SOLD)
        local = o.get('gorseller_yerel', [])
        gallery = [r + g for g in local] + [img_url(i) for i in p['imgs']]
        main_img = f'<img data-main-img data-fallback src="{e(gallery[0])}" alt="{e(p["ad"])}">' if gallery else ''
        thumbs = ''
        if len(gallery) > 1:
            thumbs = '<div class="thumbs">' + ''.join(f'<button type="button" data-thumb="{e(g)}" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Görsel {i + 1}"><img loading="lazy" src="{e(g)}" alt=""></button>' for i, g in enumerate(gallery)) + '</div>'
        sizes = o.get('ebatlar') or ([t for t in p['tokens'] if re.search(r'\d\s*(x|X|-)\s*\d.*(cm|mm)$', t)] if len(p['tokens']) > 1 and parts[0] in ('tamburlanmis-peyzaj-taslari', 'cam-peyzaj-urunleri', 'akvaryum-taslari-ve-camlari') else [])
        size_html = ''
        if len(sizes) > 1:
            size_html = '<div><div class="label">Ebat seçenekleri <span class="note" style="text-transform:none;letter-spacing:0">· Seçili: <b data-size-label>—</b></span></div><div class="sizes">' + ''.join(f'<button type="button" data-size data-value="{e(s)}" aria-pressed="{"true" if i == 0 else "false"}">{e(s)}</button>' for i, s in enumerate(sizes)) + '</div></div>'
        desc = o.get('aciklama') or ''
        fob = o.get('fob_usd_ton')
        if SHOW_PRICE and fob:
            box = f'<div><span class="note">Fiyat</span><div><span class="price">${fob}</span> / ton</div><span class="note">FOB Ambarlı · KDV ve navlun hariç</span></div>'
        elif sold:
            box = '<div><b>Bu ürün satılmıştır</b><div class="note">Benzeri için özel üretim teklifi isteyebilirsiniz.</div></div>'
        else:
            box = '<div><b>Fiyat için teklif isteyin</b><div class="note">Miktar, ebat ve teslim yerine göre</div></div>'
        specs = [('Ürün grubu', CATS[cat])]
        if p['kod']:
            specs.append(('Ürün kodu', p['kod']))
        specs += o.get('ozellikler', [])
        rest = [t for t in p['tokens'] if t not in sizes] if not o.get('ozellikler') else []
        if sizes:
            specs.append(('Ebatlar', ' · '.join(sizes)))
        if rest:
            specs.append(('Özellikler', ', '.join(rest)))
        spec_html = '<table class="specs"><tbody>' + ''.join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in specs) + '</tbody></table>'
        feats = ''
        if parts[0] == 'tamburlanmis-peyzaj-taslari':
            feats = '<section class="feats"><div class="wrap">' + ''.join(f'<div class="feat"><svg aria-hidden="true" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#16303F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{s}</svg><div><b>{e(t)}</b><span>{e(d)}</span></div></div>' for t, d, s in FEATS) + '</div></section>'
        pack = ''
        if o.get('paketleme'):
            val = f'<div style="border-top:1px solid #2A4A5C;padding-top:10px"><span class="note" style="color:#9FC3D6">Tahmini FOB tutar</span><div style="font-family:var(--head);font-size:22px;font-weight:800" data-load-value data-price="{fob}"></div></div>' if SHOW_PRICE and fob else ''
            pack = f'''<section class="band"><div class="wrap"><span class="kicker">Paketleme &amp; yükleme</span><h2 class="big" style="margin:6px 0 24px">Big bag ve konteyner kapasitesi</h2>
<div class="pack"><figure><img loading="lazy" src="{r}assets/img/bigbag.jpg" alt="Dolu big bag"><figcaption><b>1 Big Bag</b> · 1.200–1.300 kg (ortalama)</figcaption></figure>
<figure style="flex:2 1 420px"><img loading="lazy" src="{r}assets/img/container.jpg" alt="20 ft konteynerde 20 big bag"><figcaption><b>20 ft konteyner · 20 big bag</b> · İç ölçü 5,90 × 2,35 × 2,35 m</figcaption></figure>
<div class="calc"><b style="font-family:var(--head);text-transform:uppercase">Yükleme hesapla</b><div class="seg" role="group" aria-label="Yükleme tipi"><button type="button" data-load data-value="1 Big Bag" data-bags="1" data-min="1.2" data-max="1.3" aria-pressed="false">1 Big Bag</button><button type="button" data-load data-value="20 ft konteyner" data-bags="20" data-min="24" data-max="26" aria-pressed="true">20 ft</button><button type="button" data-load data-value="40 ft konteyner" data-bags="40" data-min="48" data-max="52" aria-pressed="false">40 ft</button></div>
<div class="two"><div class="tile" style="background:var(--navy-2)"><small>Big bag</small><b data-load-bags>20</b></div><div class="tile" style="background:var(--navy-2)"><small>Yaklaşık ağırlık</small><b data-load-tons>24–26 t</b></div></div>{val}<a class="btn btn-cta" href="#teklif">Bu yükleme için teklif iste</a></div></div></div></section>'''
        related = [x for x in by_cat.get(cat, []) if x is not p][:4]
        rel_html = f'<section class="wrap" style="padding-bottom:64px"><h2 class="big" style="font-size:26px;margin-bottom:18px">Aynı gruptan</h2><div class="grid">{"".join(product_card(x, r) for x in related)}</div></section>' if related else ''
        wa_text = f'Merhaba, "{p["ad"]}" için fiyat ve numune bilgisi almak istiyorum.'
        body = f'''{crumb(trail)}
<div class="wrap product" data-product="{e(p["ad"])}">
<div class="product-media"><div class="product-main">{main_img}</div>{thumbs}</div>
<div class="product-info"><span class="kicker">{e(CATS[parts[0]])}</span><h1>{e(p["ad"])}</h1>{f'<span class="tagline">{e(o["slogan"])}</span>' if o.get("slogan") else ''}{f'<p style="margin:0;font-size:17px;color:#3C4B55">{e(desc)}</p>' if desc else ''}
{size_html}
<div class="quote-box">{box}<div class="note">Teslim: Kemerburgaz / FOB Ambarlı</div></div>
<div class="btns"><a class="btn btn-cta" href="#teklif" data-ev="quote_click" data-urun="{e(p["ad"])}">Bu ürün için teklif iste</a><a class="btn btn-ghost" data-wa="{e(wa_text)}" data-urun="{e(p["ad"])}">WhatsApp</a><a class="btn btn-ghost" href="tel:{re.sub(r"[^+0-9]", "", PHONES[0])}" data-ev="phone_click" data-urun="{e(p["ad"])}">{PHONES[0]}</a></div>
<span class="note">Numune ve Kemerburgaz'da yerinde görme için de yazabilirsiniz.</span></div>
</div>
{feats}
<section class="wrap" style="padding:48px 24px"><h2 class="big" style="font-size:26px;margin-bottom:16px">Ürün bilgileri</h2><div style="max-width:760px">{spec_html}</div></section>
{pack}
<section class="wrap split" id="teklif" style="padding:56px 24px;align-items:flex-start"><div style="flex:1 1 300px"><h2 class="big" style="font-size:30px">Teklif isteyin</h2><p style="color:#3C4B55">Ürün ve ebat seçiminiz forma eklenir. Miktarı ve teslim yerini yazın, size dönelim.</p></div><div style="flex:2 1 520px">{quote_form(r, p["ad"])}</div></section>
{rel_html}
<div class="sticky-quote"><a class="btn btn-cta" href="#teklif">Teklif iste</a><a class="btn btn-ghost" data-wa="{e(wa_text)}">WhatsApp</a></div>'''
        d = f'{p["ad"]} – {CATS[cat]}. {", ".join(p["tokens"][:3])}'.strip(' .')
        write(f'urun/{p["slug"]}/index.html', page(2, f'{p["ad"]} | {CATS[parts[0]]} | Taş Dünyası', body, desc=d + '. Fiyat ve numune için teklif isteyin.', active='products', body_class='has-sticky', canonical=f'urun/{p["slug"]}/'))


# ---------- Kurumsal sayfalar ----------
def simple(path, title, inner, active='', lead=''):
    r = rel(1)
    body = f'{crumb([("Ana Sayfa", r), (title, "")])}<div class="wrap page-head"><h1>{e(title)}</h1>{f"<p>{e(lead)}</p>" if lead else ""}</div><section class="wrap" style="padding-bottom:64px">{inner.replace("{r}", r)}</section>'
    write(f'{path}/index.html', page(1, f'{title} | Taş Dünyası', body, active=active, canonical=f'{path}/'))


def build_pages():
    simple('hakkimizda', 'Hakkımızda', '''<div class="prose">
<p>Taş Dünyası'nın da içinde yer aldığı şirketler grubunun temelleri, bugünkü aynı ortaklar tarafından 1973 yılında inşaat malzemeleri satışıyla atıldı. Grup; 1992'de ruhsatlı alanında agrega üretimine yönelik taş ocağı, 2003'te doğal taş ticareti, 2016'da inşaat ve 2017'de ruhsatlı taş ocağı sahasının işletmeye alınmasıyla bugünkü halini aldı.</p>
<h2>Biz ne yapıyoruz?</h2>
<p>Türkiye'nin her bölgesinden ve diğer ülkelerdeki tedarikçilerimizden temin ettiğimiz; inşaat, peyzaj, iç ve dış mekan dekorasyonu, döşeme ve kaplamada kullanılan doğal taşları, doğal kayaçları, peyzaj ve dekorasyon camlarını sunuyoruz. Kendi tesisimizde farklı ebatlarda taş ve cam tamburluyor; kadromuzdaki heykeltıraşlarla doğal taş, ağaç kökü, kütük ve metalden el yapımı ürünler üretiyoruz.</p>
<p><span class="todo">Düzenlenecek: Misyon &amp; vizyon, "Kimler bizimle neden çalışıyor?" ve "Taş hakkında" metinleri eski siteden aktarılacak.</span></p>
<div class="btns"><a class="btn btn-cta" href="{r}iletisim/#teklif">Teklif iste</a><a class="btn btn-ghost" href="{r}referanslar/">Referanslar</a></div></div>''', active='about', lead='1973\'ten bu yana doğal taş, madencilik, peyzaj ve inşaat.')
    refs = ''.join(f'<div class="ref">{e(x)}</div>' for x in CFG['referanslar'])
    simple('referanslar', 'Referanslar', f'''<div class="refs">{refs}</div>
<div class="panel" style="margin-top:24px;border-left:4px solid var(--blue)"><b>Sanat dünyasında:</b> Heykeltıraş Adrián Villar Rojas'ın İtalya ContemporaryArt Torino fuarındaki sergisinde kullanılan doğal kayaçların büyük bölümü Taş Dünyası'ndan temin edildi.</div>
<p class="note" style="margin-top:14px"><span class="todo">Düzenlenecek: referans logoları ve proje fotoğrafları eklenecek.</span></p>''', active='refs', lead='Kamu kurumları, inşaat ve peyzaj firmaları, mimarlık ofisleri.')
    tel = ''.join(f'<div><a href="tel:{re.sub(r"[^+0-9]", "", t)}" data-ev="phone_click">{t}</a></div>' for t in PHONES)
    maps = 'https://www.google.com/maps/search/?api=1&query=' + 'Ta%C5%9F+D%C3%BCnyas%C4%B1+Kemerburgaz'
    simple('iletisim', 'İletişim', f'''<div class="split" style="align-items:flex-start">
<div class="panel" style="flex:1 1 300px"><h2 style="font-size:22px;margin-bottom:10px">Bize ulaşın</h2><p style="margin:0 0 10px">{e(CFG["unvan"])}</p><p style="margin:0 0 10px">{e(CFG["adres"])}</p>{tel}<div class="btns" style="margin-top:16px"><a class="btn btn-navy" href="{maps}" target="_blank" rel="noopener">Yol tarifi</a><a class="btn btn-ghost" data-wa="">WhatsApp</a></div></div>
<div id="teklif" style="flex:2 1 520px"><h2 style="font-size:22px;margin-bottom:12px">Teklif formu</h2>{quote_form("{r}")}</div></div>''', active='contact', lead='Showroom ve stok sahamız Kemerburgaz\'da. Fiyat ve numune için yazın ya da arayın.')
    old = CFG['eski_site']
    simple('e-katalog', 'E-Katalog', f'''<div class="grid wide"><a class="card" href="{old}/Dogaltas-E-Katalog3/dogaltas_tr/" target="_blank" rel="noopener"><div class="card-body"><span class="card-title">Doğal Taş E-Katalog</span><span class="card-sub">Online katalog (eski sitede açılır)</span></div></a><a class="card" href="{old}/ekatalog/antika/" target="_blank" rel="noopener"><div class="card-body"><span class="card-title">Antik Eşya E-Katalog</span><span class="card-sub">Online katalog (eski sitede açılır)</span></div></a></div>
<p class="note" style="margin-top:14px"><span class="todo">Düzenlenecek: güncel PDF katalog bu depoya eklenecek.</span></p>''')
    simple('sanal-tur', '360° Sanal Tur', f'''<div class="panel"><p>Kemerburgaz'daki stok sahamızı ve showroom'umuzu ekrandan gezin.</p><a class="btn btn-navy" href="{old}/sanaltur" target="_blank" rel="noopener">Sanal turu başlat</a><p class="note" style="margin-top:12px"><span class="todo">Düzenlenecek: sanal tur dosyaları yeni siteye taşınacak.</span></p></div>''')
    simple('yasal-uyari', 'Yasal Uyarı ve KVKK', '''<div class="prose"><p><span class="todo">Düzenlenecek: yasal uyarı, kullanım koşulları ve KVKK aydınlatma metni hukuk danışmanının onayıyla eklenecek.</span></p><p>Teklif formunda paylaştığınız ad, telefon ve e-posta bilgileri yalnızca talebinize yanıt vermek amacıyla kullanılır.</p></div>''')


# ---------- 404 + eski adres yönlendirmesi, arama dizini, robots, sitemap ----------
def build_misc():
    legacy = {'tr': {}, 'en': {}, 'pages_tr': KAT['pages_tr'], 'pages_en': KAT['pages_en']}
    for k, v in KAT['tr'].items():
        legacy['tr'][k] = 'urun-kategori/' + v + '/'
    for k, v in KAT['en'].items():
        legacy['en'][k] = 'urun-kategori/' + v + '/'
    for p in products:
        legacy['tr'][p['id']] = 'urun/' + p['slug'] + '/'
    legacy['pages_tr']['referanslar'] = legacy['pages_en']['referances'] = '/referanslar/'
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    (OUT / 'assets' / 'legacy.json').write_text(json.dumps(legacy, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    base = CFG['taban_yol'].rstrip('/')
    body = f'''<div class="wrap page-head" style="padding:64px 24px"><h1>Sayfa bulunamadı</h1><p id="msg">Aradığınız sayfa taşınmış olabilir.</p><div class="btns" style="margin-top:18px"><a class="btn btn-navy" href="{base}/urunler/">Ürünlere git</a><a class="btn btn-ghost" href="{base}/">Ana sayfa</a></div></div>
<script>
(function(){{
  var base={json.dumps(base)}; var path=decodeURIComponent(location.pathname); if(base&&path.indexOf(base)===0) path=path.slice(base.length);
  var m=path.match(/^\\/(tr-TR|en-US)(?:\\/(.*))?$/i); var kat=/^\\/(dogaltas-e-katalog\\d*|ekatalog)(\\/|$)/i.test(path)?'e-katalog/':(/^\\/sanaltur\\/?$/i.test(path)?'sanal-tur/':null);
  function go(t){{ location.replace(base+'/'+String(t).replace(/^\\//,'')); }}
  if(kat) return go(kat);
  if(!m) return;
  document.getElementById('msg').textContent='Yeni adrese yönlendiriliyorsunuz…';
  fetch(base+'/assets/legacy.json').then(function(r){{return r.json()}}).then(function(L){{
    var lang=m[1].toLowerCase()==='tr-tr'?'tr':'en'; var segs=(m[2]||'').split('/').filter(Boolean); if(!segs.length) return go('');
    var ids=segs.slice(1).filter(function(s){{return /^\\d+$/.test(s)&&s.replace(/^0+/,'')!==''}}).map(function(s){{return s.replace(/^0+/,'')}}).reverse();
    for(var i=0;i<ids.length;i++) if(L[lang][ids[i]]) return go(L[lang][ids[i]]);
    var slug=segs[0].toLowerCase().replace(/ı/g,'i').replace(/ğ/g,'g').replace(/ü/g,'u').replace(/ş/g,'s').replace(/ö/g,'o').replace(/ç/g,'c').replace(/[^a-z0-9-]+/g,'');
    var pages=lang==='tr'?L.pages_tr:L.pages_en; if(pages[slug]) return go(pages[slug]);
    go(segs[1]==='3'||segs[1]==='1199'?'urunler/':'');
  }});
}})();
</script>'''
    html = page(0, 'Sayfa bulunamadı | Taş Dünyası', body, canonical=None)
    # 404 sayfası her derinlikten açılır: bağlantıları kök yoluna sabitle
    html = html.replace('data-root=""', f'data-root="{base}/"').replace('href="assets/', f'href="{base}/assets/').replace('src="assets/', f'src="{base}/assets/')
    html = re.sub(r'(href|action)="(?!https?:|tel:|#|/|mailto:)([^"]*)"', lambda m: f'{m.group(1)}="{base}/{m.group(2)}"', html)
    write('404.html', html)

    idx = [{'t': p['ad'], 'c': CATS[p['kategori']], 's': p['slug'], 'i': p['imgs'][0] if p['imgs'] else ''} for p in products]
    (OUT / 'search.json').write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    site = CFG['site_adresi'].rstrip('/')
    urls = ['', 'urunler/', 'hakkimizda/', 'referanslar/', 'iletisim/', 'e-katalog/', 'sanal-tur/', 'yasal-uyari/'] + [f'urun-kategori/{c}/' for c in CATS] + [f'urun/{p["slug"]}/' for p in products]
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{site}/{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n' if DRAFT else f'User-agent: *\nAllow: /\nSitemap: {site}/sitemap.xml\n', encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    js = {'whatsapp': CFG.get('whatsapp', ''), 'email': CFG.get('eposta', ''), 'imgBase': IMG}
    (OUT / 'assets' / 'config.js').write_text('window.TD = ' + json.dumps(js, ensure_ascii=False) + ';\n', encoding='utf-8')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets').mkdir(parents=True)
    shutil.copytree(ROOT / 'assets' / 'img', OUT / 'assets' / 'img')
    shutil.copy(ROOT / 'src' / 'site.css', OUT / 'assets' / 'site.css')
    shutil.copy(ROOT / 'src' / 'site.js', OUT / 'assets' / 'site.js')
    build_home(); build_listing(); build_products(); build_pages(); build_misc()
    n = sum(1 for _ in OUT.rglob('*.html'))
    print(f'{n} sayfa üretildi: {len(products)} ürün, {len(CATS)} kategori → {OUT}')


if __name__ == '__main__':
    main()
