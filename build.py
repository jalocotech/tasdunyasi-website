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
CATS_TR = dict(KAT['cats'])  # yol -> ad
CATS = dict(CATS_TR)
EN_CATS = json.loads((ROOT / 'data' / 'en_cats.json').read_text(encoding='utf-8'))
EN_NAMES = {}
for _f in sorted((ROOT / 'data').glob('en_names_*.txt')):
    for _l in _f.read_text(encoding='utf-8').splitlines():
        if ' = ' in _l:
            _k, _v = _l.split(' = ', 1)
            EN_NAMES[_k] = _v
EN_TOK = json.loads((ROOT / 'data' / 'en_tokens.json').read_text(encoding='utf-8'))
LANG = 'tr'
AR = ''  # dil klasöründen siteye kök yolu (assets için): en/ altında '../'
SEG = {
    'tr': {'products': 'urunler', 'cat': 'urun-kategori', 'item': 'urun', 'about': 'hakkimizda', 'refs': 'referanslar', 'contact': 'iletisim', 'catalog': 'e-katalog', 'tour': 'sanal-tur', 'legal': 'yasal-uyari'},
    'en': {'products': 'products', 'cat': 'category', 'item': 'product', 'about': 'about', 'refs': 'references', 'contact': 'contact', 'catalog': 'e-catalogue', 'tour': 'virtual-tour', 'legal': 'legal'},
}


def T(tr, en):
    return en if LANG == 'en' else tr


def S(k):
    return SEG[LANG][k]


def alt_path(canon, to):
    """Geçerli dildeki yol → diğer dildeki karşılığı (ilk bölüm çevrilir)."""
    frm = 'tr' if to == 'en' else 'en'
    inv = {v: k for k, v in SEG[frm].items()}
    segs = canon.split('/')
    if segs and segs[0] in inv:
        segs[0] = SEG[to][inv[segs[0]]]
    return '/'.join(segs)


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
    p['tokens_tr'] = tokens
    p['tokens'] = tokens
    p['ad_tr'] = p['ad']
    p['ozel_tr'] = OZEL.get(p['id'], {})
    p['ozel'] = p['ozel_tr']
by_cat = {}
for p in products:
    by_cat.setdefault(p['kategori'], []).append(p)


def tok_en(t):
    v = EN_TOK.get(t, t)
    return v


def set_lang(lang):
    """Ürün adlarını, kategori adlarını ve özel içeriği seçilen dile çevirir."""
    global LANG, AR, CATS, CAT_SUB
    LANG = lang
    AR = '../' if lang == 'en' else ''
    CATS = dict(EN_CATS['cats']) if lang == 'en' else dict(CATS_TR)
    CAT_SUB = dict(EN_CATS['sub']) if lang == 'en' else dict(CAT_SUB_TR)
    for p in products:
        if lang == 'en':
            p['ad'] = EN_NAMES.get(p['ad_tr'], p['ad_tr'])
            p['tokens'] = [x for x in (tok_en(t) for t in p['tokens_tr']) if x]
            o = dict(p['ozel_tr'])
            o.update(o.get('en', {}))
            p['ozel'] = o
        else:
            p['ad'] = p['ad_tr']
            p['tokens'] = p['tokens_tr']
            p['ozel'] = p['ozel_tr']


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
CAT_SUB_TR = {
    'tamburlanmis-peyzaj-taslari': 'Dolomit, kalsit, mermer, dere çakılı, kalsedon',
    'cam-peyzaj-urunleri': 'Tamburlanmış ve kaya formu renkli camlar',
    'doseme-ve-kaplama-taslari': 'Traverten, kayrak, granit, bazalt, mermer',
    'dogal-kayaclar': 'Meteor, oniks, gnays, ağaç fosili, lav taşı',
    'el-yapimi-peyzaj-urunleri': 'Oturma grubu, çeşme, fıskiye, saksı',
    'dogal-tas-heykel-ve-sutunlar': 'Mermer heykel, aslan, sütun, kaide',
    'akvaryum-taslari-ve-camlari': 'Kalsedon, falez, meteor parça, cam',
    'antik-taslar': 'Değirmen taşı, dibek, kuyu ağzı, anfora',
}
CAT_SUB = dict(CAT_SUB_TR)


def page(depth, title, body, desc='', active='', body_class='', canonical=''):
    r = rel(depth)
    ar = AR + r  # assets yolu
    robots = '<meta name="robots" content="noindex, nofollow">' if DRAFT else ''
    draft = f'<div style="background:#FFF6D6;color:#6B5300;font-size:13px;text-align:center;padding:6px 12px">{T("Taslak site: içerik ve görseller onay aşamasındadır.", "Draft site: content and images are pending approval.")}</div>' if DRAFT else ''
    nav = [(T('Ana Sayfa', 'Home'), '', 'home'), (T('Hakkımızda', 'About Us'), S('about') + '/', 'about'), (T('Ürünler', 'Products'), S('products') + '/', 'products'), (T('Referanslar', 'References'), S('refs') + '/', 'refs'), (T('İletişim', 'Contact'), S('contact') + '/', 'contact')]
    nav_html = ''.join(f'<a href="{r}{h}"{" class=on" if k == active else ""}>{t}</a>' for t, h, k in nav)
    tel = ''.join(f'<a href="tel:{re.sub(r"[^+0-9]", "", t)}" data-ev="phone_click">{t}</a>' for t in PHONES)
    site = CFG["site_adresi"].rstrip("/")
    other = 'tr' if LANG == 'en' else 'en'
    lang_link = ''
    canon = ''
    if canonical is not None:
        alt = alt_path(canonical, other)
        here = f'{site}/{"en/" if LANG == "en" else ""}{canonical}'
        tr_url = f'{site}/{canonical if LANG == "tr" else alt}'
        en_url = f'{site}/en/{canonical if LANG == "en" else alt}'
        if LANG == 'tr':
            href = f'{r}en/{alt}'
            lang_link = f'<a class="lang" href="{href}" hreflang="en" lang="en" title="English" data-ev="lang_switch">EN</a>'
        else:
            href = f'{r}../{alt}'
            lang_link = f'<a class="lang" href="{href}" hreflang="tr" lang="tr" title="Türkçe" data-ev="lang_switch">TR</a>'
        canon = f'<link rel="alternate" hreflang="tr" href="{tr_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{tr_url}">'
        if not DRAFT:
            canon = f'<link rel="canonical" href="{here}">' + canon
    cfgjs = 'config-en.js' if LANG == 'en' else 'config.js'
    return f'''<!doctype html>
<html lang="{LANG}" data-root="{r}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or T(CFG["aciklama"], CFG["aciklama_en"]))}">
{robots}{canon}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&family=Raleway:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{ar}assets/site.css">
<link rel="icon" href="{ar}assets/img/logo.jpg">
</head>
<body class="{body_class}">
{draft}
<div class="topbar"><div class="wrap"><div>{tel}</div><div><a href="{r}{S("catalog")}/">{T("E-Katalog", "E-Catalogue")}</a><a href="{r}{S("cat")}/antika-urunler/">{T("Antik Eşya Mağazası", "Antique Shop")}</a><a href="{r}{S("tour")}/">{T("360° Sanal Tur", "360° Virtual Tour")}</a></div></div></div>
<header class="header">
<div class="wrap">
<a class="logo" href="{r}" aria-label="{T("Taş Dünyası ana sayfa", "Taş Dünyası home page")}"><img src="{CFG["eski_site"].rstrip("/")}/common/images/logo.png" onerror="this.onerror=null;this.src='{ar}assets/img/logo.jpg'" width="280" height="68" alt="Taş Dünyası – Stone World"></a>
<nav class="nav" aria-label="{T("Ana menü", "Main menu")}">{nav_html}</nav>
<div class="header-actions">
<form class="search" action="{r}{S("products")}/" method="get"><label class="sr" for="q">{T("Ürün ara", "Search products")}</label><input id="q" name="q" type="search" placeholder="{T("Ürün ara", "Search products")}"><button type="submit">{T("Ara", "Search")}</button></form>
<a class="btn btn-ghost" data-wa="">WhatsApp</a>
<a class="btn btn-cta" href="{r}{S("contact")}/#teklif" data-ev="quote_click">{T("Teklif İste", "Request a Quote")}</a>
{lang_link}
</div>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="{T("Menüyü aç", "Open menu")}"><span></span><span></span><span></span></button>
</div>
<div class="stripe" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="drawer" id="menu" hidden>
<form class="search" action="{r}{S("products")}/" method="get" role="search"><input name="q" type="search" placeholder="{T("Ürün ara", "Search products")}" aria-label="{T("Ürün ara", "Search products")}"><button type="submit">{T("Ara", "Search")}</button></form>
<nav class="drawer-nav" aria-label="{T("Mobil menü", "Mobile menu")}">{nav_html}</nav>
<nav class="drawer-sub" aria-label="{T("Diğer bağlantılar", "Other links")}"><a href="{r}{S("catalog")}/">{T("E-Katalog", "E-Catalogue")}</a><a href="{r}{S("cat")}/antika-urunler/">{T("Antik Eşya Mağazası", "Antique Shop")}</a><a href="{r}{S("tour")}/">{T("360° Sanal Tur", "360° Virtual Tour")}</a>{lang_link}</nav>
<div class="drawer-tel">{tel}</div>
<a class="btn btn-ghost" data-wa="">{T("WhatsApp ile yazın", "Message us on WhatsApp")}</a>
</div>
</header>
<main>
{body}
</main>
<footer class="footer">
<div class="stripe" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="wrap cols">
<div><div class="brand">Taş Dünyası</div><div>{T("1973'ten bu yana doğal taş, madencilik ve peyzaj.", "Natural stone, mining and landscaping since 1973.")}</div></div>
<div><strong>{T("Ürünler", "Products")}</strong>{''.join(f'<a href="{r}{S("cat")}/{c}/">{e(CATS[c])}</a>' for c in MAIN8[:5])}<a href="{r}{S("products")}/">{T("Tüm ürünler", "All products")}</a></div>
<div><strong>{T("Kurumsal", "Company")}</strong><a href="{r}{S("about")}/">{T("Hakkımızda", "About Us")}</a><a href="{r}{S("refs")}/">{T("Referanslar", "References")}</a><a href="{r}{S("catalog")}/">{T("E-Katalog", "E-Catalogue")}</a><a href="{r}{S("legal")}/">{T("Yasal uyarı ve KVKK", "Legal notice and privacy")}</a></div>
<div><strong>{T("İletişim", "Contact")}</strong>{tel}<div>{e(T(CFG["adres"], CFG["adres_en"]))}</div></div>
</div>
<div class="wrap legal">© {e(CFG["unvan"])} {T("Tüm hakları saklıdır.", "All rights reserved.")}</div>
</footer>
<script src="{ar}assets/{cfgjs}"></script>
<script src="{ar}assets/site.js"></script>
</body>
</html>
'''


def write(path, html):
    f = OUT / ('en' if LANG == 'en' else '') / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding='utf-8')


def product_card(p, r):
    img = f'<img loading="lazy" data-fallback src="{e(img_url(p["imgs"][0]))}" alt="{e(p["ad"])}">' if p['imgs'] else ''
    badge = f'<span class="badge">{T("Satıldı", "Sold")}</span>' if p['kategori'].startswith(SOLD) else ''
    sub = p['tokens'][-1] if p['tokens'] and re.search(r'\d', p['tokens'][-1]) else CATS[p['kategori']]
    return f'<a class="card" href="{r}{S("item")}/{p["slug"]}/"><div class="card-img">{img}{badge}</div><div class="card-body"><span class="card-title">{e(p["ad"])}</span><span class="card-sub">{e(sub)}</span></div></a>'


def cat_card(c, r, sub=''):
    t = cat_thumb(c)
    img = f'<img loading="lazy" data-fallback src="{e(img_url(t))}" alt="{e(CATS[c])}">' if t else ''
    n = len(all_products(c))
    return f'<a class="card" href="{r}{S("cat")}/{c}/"><div class="card-img">{img}</div><div class="card-body"><span class="card-title">{e(CATS[c])}</span><span class="card-sub">{e(sub or str(n) + T(" ürün", " products"))}</span></div></a>'


def quote_form(r, product=''):
    val = f' value="{e(product)}"' if product else ''
    return f'''<form class="form panel" data-quote-form action="#">
<label class="full">{T("Ürün", "Product")}<input type="text" name="urun" data-form-product{val} placeholder="{T("İlgilendiğiniz ürün", "The product you are interested in")}"></label>
<label>{T("Miktar", "Quantity")}<input type="text" name="miktar" placeholder="{T("ör. 2 ton, 1 konteyner", "e.g. 2 tons, 1 container")}"></label>
<label>{T("Teslim yeri / varış limanı", "Delivery place / port of destination")}<input type="text" name="teslimat" placeholder="{T("ör. İstanbul", "e.g. Istanbul")}"></label>
<label>{T("Ad soyad", "Full name")}<input type="text" name="ad" autocomplete="name" required></label>
<label>{T("Firma", "Company")}<input type="text" name="firma" autocomplete="organization"></label>
<label>{T("Telefon", "Phone")}<input type="tel" name="telefon" autocomplete="tel" required></label>
<label>{T("E-posta", "E-mail")}<input type="email" name="eposta" autocomplete="email"></label>
<label class="full">{T("Notunuz", "Your note")}<textarea name="mesaj" rows="3"></textarea></label>
<label class="full check"><input type="checkbox" required><span>{T(f'<a href="{r}{S("legal")}/">KVKK aydınlatma metnini</a> okudum, iletişime geçilmesini kabul ediyorum.', f'I have read the <a href="{r}{S("legal")}/">privacy notice (KVKK)</a> and agree to be contacted.')}</span></label>
<div class="full btns"><button class="btn btn-cta" type="button" data-send="wa">{T("WhatsApp ile gönder", "Send via WhatsApp")}</button><button class="btn btn-navy" type="button" data-send="mail">{T("E-posta ile gönder", "Send by e-mail")}</button><a class="btn btn-ghost" href="tel:{re.sub(r"[^+0-9]", "", PHONES[0])}" data-ev="phone_click">{PHONES[0]}</a></div>
<p class="form-msg">{T("Bilgileriniz yalnızca teklif hazırlamak için kullanılır.", "Your details are used only to prepare a quote.")}</p>
</form>'''


def crumb(items):
    out = []
    for t, h in items:
        out.append(f'<a href="{h}">{e(t)}</a><span aria-hidden="true">›</span>' if h else f'<b>{e(t)}</b>')
    return f'<nav class="crumb wrap" aria-label="{T("Konum", "Breadcrumb")}">' + ''.join(out) + '</nav>'



# ---------- Ana sayfa ----------
def build_home():
    r = ''
    feat = next((p for p in products if p['id'] == CFG['one_cikan_urun']), products[0])
    stats = [(T("1973'ten beri", 'Since 1973'), T('İnşaat, madencilik ve doğal taşta aile şirketi', 'Family company in construction, mining and natural stone'), 'var(--blue)'), (T('Kendi taş ocağı', 'Own stone quarry'), T('Ruhsatlı sahadan doğrudan tedarik', 'Direct supply from a licensed site'), 'var(--green)'), (T('Kendi tamburlama tesisi', 'Own tumbling plant'), T('Ebat ve renk seçeneğiyle üretim', 'Production in your choice of size and color'), 'var(--orange)'), ('FOB Ambarlı', T('Big bag ve konteyner ile ihracat', 'Export by big bag and container'), '#16303F')]
    others = [c for c in TOP if c not in MAIN8 and c != SOLD]
    refs = CFG['referanslar'][:12]
    fo = feat['ozel']
    sizes = ''.join(f'<span class="chip">{e(s)}</span>' for s in fo.get('ebatlar', []))
    prod, cat_, contact = S('products'), S('cat'), S('contact')
    body = f'''
<section class="hero"><div class="wrap">
<div class="hero-text"><span class="kicker" lang="en">Natural stone solutions for a better tomorrow</span>
<h1>{T("İstanbul'un içinde rengarenk bir dünya", "A colorful world in the heart of Istanbul")}</h1>
<p>{T("Peyzaj, döşeme ve dekorasyon için doğal taş, kayaç ve cam. Kendi ocağımızdan, kendi tamburlama tesisimizden; Türkiye'ye ve dünyaya.", "Natural stone, rock and glass for landscaping, paving and decoration. From our own quarry and our own tumbling plant to Turkey and the world.")}</p>
<div class="btns"><a class="btn btn-cta" href="{contact}/#teklif" data-ev="quote_click">{T("Teklif İste", "Request a Quote")}</a><a class="btn btn-light" href="{prod}/">{T("Ürünleri İncele", "Browse Products")}</a></div></div>
<div class="hero-img"><img src="{AR}assets/img/showroom.jpg" alt="{T("Taş Dünyası açık hava sergi alanı: sütunlar, çakıl taşları ve dekoratif ürünler", "Taş Dünyası open-air showroom: columns, pebbles and decorative products")}" width="941" height="1672"><a class="hero-tag" href="https://www.google.com/maps/search/?api=1&amp;query=Ta%C5%9F+D%C3%BCnyas%C4%B1+Kemerburgaz" target="_blank" rel="noopener" data-ev="directions_click"><small>Kemerburgaz, Eyüpsultan</small><b>{T("Showroom'u ziyaret edin →", "Visit our showroom →")}</b></a></div>
</div></section>
<section class="stats"><div class="wrap">{''.join(f'<div class="stat" style="border-color:{c}"><b>{e(b)}</b><span>{e(s)}</span></div>' for b, s, c in stats)}</div></section>
<section class="block"><div class="wrap">
<div class="block-head"><div><span class="kicker">{T("Ürünler", "Products")}</span><h2>{T("Ürün gruplarımız", "Our product groups")}</h2></div><a class="more" href="{prod}/">{T("Tüm ürünler", "All products")}</a></div>
<div class="grid wide">{''.join(cat_card(c, r, CAT_SUB.get(c, '')) for c in MAIN8)}</div>
<div class="chips" style="margin-top:22px">{''.join(f'<a class="chip" href="{cat_}/{c}/">{e(CATS[c])}</a>' for c in others)}</div>
</div></section>
<section class="block" style="padding-top:0"><div class="wrap"><div class="card" style="flex-direction:row;flex-wrap:wrap">
<div style="flex:1 1 360px;min-height:340px;position:relative"><img src="{AR}assets/img/stones.jpg" alt="{e(feat["ad"])}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"></div>
<div style="flex:1 1 480px;padding:40px;display:flex;flex-direction:column;gap:14px"><span class="kicker">{T("Öne çıkan ürün", "Featured product")}</span><h2 class="big">{e(feat["ad"])}</h2><span class="tagline">{e(fo.get("slogan", ""))}</span><p style="margin:0;color:#3C4B55">{e(fo.get("aciklama", ""))}</p><div class="chips">{sizes}</div><div class="btns"><a class="btn btn-navy" href="{S("item")}/{feat["slug"]}/">{T("Ürün detayı", "Product details")}</a><a class="btn btn-ghost" href="{contact}/#teklif">{T("Teklif iste", "Request a quote")}</a></div></div>
</div></div></section>
<section class="band"><div class="wrap split">
<div><span class="kicker">{T("Toptan &amp; ihracat", "Wholesale &amp; export")}</span><h2 class="big" style="margin:6px 0 14px">{T("Big bag'den konteynere, FOB Ambarlı", "From big bags to containers, FOB Ambarlı")}</h2><p style="margin:0 0 18px">{T("Tamburlanmış taş ve camları big bag ile ya da tam konteyner olarak yüklüyoruz. Miktar, ebat ve varış limanını yazın; fiyat ve yükleme planını gönderelim.", "We load tumbled stone and glass in big bags or as full containers. Tell us the quantity, size and port of destination and we will send the price and loading plan.")}</p><div class="btns"><a class="btn btn-cta" href="{contact}/#teklif">{T("İhracat teklifi al", "Get an export quote")}</a></div></div>
<div class="tiles"><div class="tile"><small>1 Big Bag</small><b>{T("1,2–1,3 t", "1.2–1.3 t")}</b><span>{T("ortalama ağırlık", "average weight")}</span></div><div class="tile"><small>{T("20 ft konteyner", "20 ft container")}</small><b>24–26 t</b><span>{T("20 big bag", "20 big bags")}</span></div><div class="tile"><small>{T("40 ft konteyner", "40 ft container")}</small><b>48–52 t</b><span>{T("40 big bag", "40 big bags")}</span></div></div>
</div></section>
<section class="block"><div class="wrap">
<div class="block-head"><div><span class="kicker">{T("Referanslar", "References")}</span><h2>{T("Bizimle çalışanlar", "Who works with us")}</h2></div><a class="more" href="{S("refs")}/">{T("Tüm referanslar", "All references")}</a></div>
<div class="refs">{''.join(f'<div class="ref">{e(x)}</div>' for x in refs)}</div>
</div></section>
<section class="cta-row"><div class="wrap"><div style="flex:1 1 460px"><h2 class="big" style="font-size:32px">{T("Projeniz için teklif alın", "Get a quote for your project")}</h2><p style="margin:8px 0 0;color:#3C4B55;max-width:560px">{T("Ürünü, miktarı ve teslim yerini yazın; fiyat ve numune için size dönelim. Taşları Kemerburgaz'da yerinde de görebilirsiniz.", "Tell us the product, quantity and delivery place and we will get back to you with a price and samples. You can also see the stones in person in Kemerburgaz.")}</p></div><div class="btns"><a class="btn btn-cta" href="{contact}/#teklif">{T("Teklif formu", "Quote form")}</a><a class="btn btn-ghost" data-wa="">{T("WhatsApp'tan yaz", "Message on WhatsApp")}</a><a class="btn btn-ghost" href="{contact}/">{T("Yol tarifi", "Directions")}</a></div></div></section>
'''
    write('index.html', page(0, T('Taş Dünyası | Doğal taş, peyzaj taşı ve cam – Kemerburgaz, İstanbul', 'Taş Dünyası | Natural stone, landscape stone and glass – Kemerburgaz, Istanbul'), body, active='home', canonical=''))


# ---------- Ürünler ve kategori sayfaları ----------
def build_listing():
    r = rel(1)
    n_prod = len([p for p in products if not p["kategori"].startswith(SOLD)])
    body = f'''{crumb([(T('Ana Sayfa', 'Home'), r), (T('Ürünler', 'Products'), '')])}
<div class="wrap page-head"><h1 data-search-head>{T("Ürünler", "Products")}</h1><p data-hide-on-search>{T(f"{n_prod} ürün, {len(TOP) - 1} ürün grubu. Aradığınızı bulamazsanız yazın, tedarik edelim.", f"{n_prod} products in {len(TOP) - 1} product groups. If you cannot find what you need, write to us and we will source it.")}</p>
<form class="search" action="./" method="get" style="margin-top:14px"><label class="sr" for="q2">{T("Ürün ara", "Search products")}</label><input id="q2" name="q" type="search" data-search-input placeholder="{T("Taş, renk ya da ürün adı", "Stone, color or product name")}" style="width:min(420px,60vw)"><button type="submit">{T("Ara", "Search")}</button></form></div>
<section class="wrap" style="padding-bottom:64px"><div class="grid" data-search-results></div>
<div class="grid wide" data-hide-on-search>{''.join(cat_card(c, r, CAT_SUB.get(c, '')) for c in TOP)}</div></section>'''
    write(f'{S("products")}/index.html', page(1, T('Ürünler | Taş Dünyası', 'Products | Taş Dünyası'), body, active='products', canonical=f'{S("products")}/'))

    for c in CATS:
        depth = 2 + c.count('/')
        r = rel(depth)
        parts = c.split('/')
        trail = [(T('Ana Sayfa', 'Home'), r), (T('Ürünler', 'Products'), r + S('products') + '/')]
        if len(parts) > 1:
            trail.append((CATS[parts[0]], f'{r}{S("cat")}/{parts[0]}/'))
        trail.append((CATS[c], ''))
        subs = children(c)
        ps = by_cat.get(c, []) if subs else all_products(c)
        sub_html = f'<div class="chips subcats">{"".join(f"""<a class="chip" href="{r}{S("cat")}/{s}/">{e(CATS[s])} ({len(all_products(s))})</a>""" for s in subs)}</div>' if subs else ''
        if subs and not ps:
            ps = all_products(c)
        grid = ''.join(product_card(p, r) for p in ps) or f'<p class="note">{T("Bu grupta henüz ürün yok.", "There are no products in this group yet.")}</p>'
        wa = T(f'Merhaba, {CATS[c]} hakkında bilgi almak istiyorum.', f'Hello, I would like information about {CATS[c]}.')
        body = f'''{crumb(trail)}
<div class="wrap page-head"><h1>{e(CATS[c])}</h1><p>{e(CAT_SUB.get(c, ""))}</p></div>
<section class="wrap" style="padding-bottom:64px">{sub_html}<p class="count">{len(ps)} {T("ürün", "products")}</p><div class="grid">{grid}</div></section>
<section class="cta-row"><div class="wrap"><div style="flex:1 1 460px"><h2 class="big" style="font-size:28px">{T(f"{CATS[c]} için teklif alın", f"Get a quote for {CATS[c]}")}</h2></div><div class="btns"><a class="btn btn-cta" href="{r}{S("contact")}/?urun={e(CATS[c])}#teklif">{T("Teklif iste", "Request a quote")}</a><a class="btn btn-ghost" data-wa="{e(wa)}">WhatsApp</a></div></div></section>'''
        d = T(f'{CATS[c]}: {CAT_SUB.get(c, "Taş Dünyası ürünleri")}. Fiyat ve numune için teklif isteyin.', f'{CATS[c]}: {CAT_SUB.get(c, "Taş Dünyası products")}. Request a quote for prices and samples.')
        write(f'{S("cat")}/{c}/index.html', page(depth, f'{CATS[c]} | Taş Dünyası', body, desc=d, active='products', canonical=f'{S("cat")}/{c}/'))


# ---------- Ürün detay ----------
def feats_list():
    return [(T('%100 Doğal', '100% Natural'), T('Özgün, yüksek kaliteli doğal malzeme.', 'Authentic, high-quality natural material.'), '<path d="M5 19c8 0 14-6 14-14C11 5 5 9 5 17v2z"/><path d="M5 19c3-4 6-7 10-10"/>'),
            (T('Tamburlanmış yüzey', 'Tumbled surface'), T('Pürüzsüz, yuvarlak kenarlar.', 'Smooth, rounded edges.'), '<path d="M6 3h12l3 6-9 12L3 9z"/><path d="M3 9h18"/>'),
            (T('Dayanıklı', 'Durable'), T('Hava koşullarına dayanıklı, uzun ömürlü.', 'Weather-resistant and long-lasting.'), '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>'),
            (T('Çok amaçlı', 'Multi-purpose'), T('Peyzaj, bahçe, mimari ve dekoratif kullanım.', 'Landscape, garden, architectural and decorative use.'), '<path d="M2 20l7-10 4 6 3-4 6 8z"/>')]


def build_products():
    r = rel(2)
    ar = AR + r
    for p in products:
        o = p['ozel']
        cat = p['kategori']
        parts = cat.split('/')
        trail = [(T('Ana Sayfa', 'Home'), r), (T('Ürünler', 'Products'), r + S('products') + '/'), (CATS[parts[0]], f'{r}{S("cat")}/{parts[0]}/')]
        if len(parts) > 1:
            trail.append((CATS[cat], f'{r}{S("cat")}/{cat}/'))
        trail.append((p['ad'], ''))
        sold = cat.startswith(SOLD)
        local = o.get('gorseller_yerel', [])
        gallery = [ar + g for g in local] + [img_url(i) for i in p['imgs']]
        main_img = f'<img data-main-img data-fallback src="{e(gallery[0])}" alt="{e(p["ad"])}">' if gallery else ''
        multi = len(gallery) > 1
        arrows = f'<button type="button" class="gal-nav prev" data-prev aria-label="{T("Önceki görsel", "Previous image")}">&#8249;</button><button type="button" class="gal-nav next" data-next aria-label="{T("Sonraki görsel", "Next image")}">&#8250;</button><span class="gal-count"><b data-gal-i>1</b> / ' + str(len(gallery)) + '</span>' if multi else ''
        thumbs = ''
        if multi:
            caps = o.get('gorsel_etiketleri', [])
            thumbs = '<div class="thumbs">' + ''.join(f'<button type="button" data-thumb="{e(g)}" data-cap="{e(caps[i]) if i < len(caps) else ""}" aria-pressed="{"true" if i == 0 else "false"}" aria-label="{T("Görsel", "Image")} {i + 1}"><img loading="lazy" src="{e(g)}" alt=""></button>' for i, g in enumerate(gallery)) + '</div>'
        sizes = o.get('ebatlar') or ([t for t in p['tokens'] if re.search(r'\d\s*(x|X|-)\s*\d.*(cm|mm)$', t)] if len(p['tokens']) > 1 and parts[0] in ('tamburlanmis-peyzaj-taslari', 'cam-peyzaj-urunleri', 'akvaryum-taslari-ve-camlari') else [])
        size_html = ''
        if len(sizes) > 1:
            size_html = f'<div><div class="label">{T("Ebat seçenekleri", "Size options")} <span class="note" style="text-transform:none;letter-spacing:0">· {T("Seçili", "Selected")}: <b data-size-label>—</b></span></div><div class="sizes">' + ''.join(f'<button type="button" data-size data-value="{e(s)}" aria-pressed="{"true" if i == 0 else "false"}">{e(s)}</button>' for i, s in enumerate(sizes)) + '</div></div>'
        desc = o.get('aciklama') or ''
        fob = o.get('fob_usd_ton')
        if SHOW_PRICE and fob:
            box = f'<div><span class="note">{T("Fiyat", "Price")}</span><div><span class="price">${fob}</span> / {T("ton", "ton")}</div><span class="note">{T("FOB Ambarlı · KDV ve navlun hariç", "FOB Ambarlı · excluding VAT and freight")}</span></div>'
        elif sold:
            box = f'<div><b>{T("Bu ürün satılmıştır", "This product has been sold")}</b><div class="note">{T("Benzeri için özel üretim teklifi isteyebilirsiniz.", "You can request a custom-made alternative.")}</div></div>'
        else:
            box = f'<div><b>{T("Fiyat için teklif isteyin", "Request a quote for the price")}</b><div class="note">{T("Miktar, ebat ve teslim yerine göre", "Depending on quantity, size and delivery place")}</div></div>'
        specs = [(T('Ürün grubu', 'Product group'), CATS[cat])]
        if p['kod']:
            specs.append((T('Ürün kodu', 'Product code'), p['kod']))
        specs += o.get('ozellikler', [])
        rest = [t for t in p['tokens'] if t not in sizes] if not o.get('ozellikler') else []
        if sizes and not o.get('ozellikler'):
            specs.append((T('Ebatlar', 'Sizes'), ' · '.join(sizes)))
        if rest:
            specs.append((T('Özellikler', 'Features'), ', '.join(rest)))
        spec_html = '<dl class="spec-grid">' + ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in specs) + '</dl>'
        feats = ''
        if parts[0] == 'tamburlanmis-peyzaj-taslari':
            feats = '<section class="feats"><div class="wrap">' + ''.join(f'<div class="feat"><svg aria-hidden="true" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#16303F" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{s}</svg><div><b>{e(t)}</b><span>{e(d)}</span></div></div>' for t, d, s in feats_list()) + '</div></section>'
        pack = ''
        if o.get('paketleme'):
            val = f'<div style="border-top:1px solid #2A4A5C;padding-top:10px"><span class="note" style="color:#9FC3D6">{T("Tahmini FOB tutar", "Estimated FOB amount")}</span><div style="font-family:var(--head);font-size:22px;font-weight:800" data-load-value data-price="{fob}"></div></div>' if SHOW_PRICE and fob else ''
            c20, c40, bb = T('20 ft konteyner', '20 ft container'), T('40 ft konteyner', '40 ft container'), '1 Big Bag'
            pack = f'''<section class="band"><div class="wrap"><span class="kicker">{T("Paketleme &amp; yükleme", "Packing &amp; loading")}</span><h2 class="big" style="margin:6px 0 24px">{T("Big bag ve konteyner kapasitesi", "Big bag and container capacity")}</h2>
<div class="pack"><figure><img loading="lazy" src="{ar}assets/img/bigbag.jpg" alt="{T("Dolu big bag", "Filled big bag")}"><figcaption><b>1 Big Bag</b> · {T("1.200–1.300 kg (ortalama)", "1,200–1,300 kg (average)")}</figcaption></figure>
<figure style="flex:2 1 420px"><img loading="lazy" src="{ar}assets/img/container.jpg" alt="{T("20 ft konteynerde 20 big bag", "20 big bags in a 20 ft container")}"><figcaption><b>{T("20 ft konteyner · 20 big bag", "20 ft container · 20 big bags")}</b> · {T("İç ölçü 5,90 × 2,35 × 2,35 m", "Interior 5.90 × 2.35 × 2.35 m")}</figcaption></figure>
<div class="calc"><b style="font-family:var(--head);text-transform:uppercase">{T("Yükleme hesapla", "Loading calculator")}</b><div class="seg" role="group" aria-label="{T("Yükleme tipi", "Loading type")}"><button type="button" data-load data-value="{bb}" data-bags="1" data-min="1.2" data-max="1.3" aria-pressed="false">1 Big Bag</button><button type="button" data-load data-value="{c20}" data-bags="20" data-min="24" data-max="26" aria-pressed="true">20 ft</button><button type="button" data-load data-value="{c40}" data-bags="40" data-min="48" data-max="52" aria-pressed="false">40 ft</button></div>
<div class="two"><div class="tile" style="background:var(--navy-2)"><small>Big bag</small><b data-load-bags>20</b></div><div class="tile" style="background:var(--navy-2)"><small>{T("Yaklaşık ağırlık", "Approx. weight")}</small><b data-load-tons>{T("24–26 t", "24–26 t")}</b></div></div>{val}<a class="btn btn-cta" href="#teklif">{T("Bu yükleme için teklif iste", "Request a quote for this loading")}</a></div></div></div></section>'''
        related = [x for x in by_cat.get(cat, []) if x is not p][:4]
        rel_html = f'<section class="wrap" style="padding-bottom:64px"><h2 class="big" style="font-size:26px;margin-bottom:18px">{T("Aynı gruptan", "More from this group")}</h2><div class="grid">{"".join(product_card(x, r) for x in related)}</div></section>' if related else ''
        wa_text = T(f'Merhaba, "{p["ad"]}" için fiyat ve numune bilgisi almak istiyorum.', f'Hello, I would like price and sample information for "{p["ad"]}".')
        caps0 = o.get('gorsel_etiketleri', [''])[0] if multi else ''
        facts = o.get('ozet') or [(T('Teslim', 'Delivery'), 'Kemerburgaz / FOB Ambarlı'), (T('Fiyat', 'Price'), T('Teklif ile', 'On quote'))]
        facts_html = '<ul class="facts">' + ''.join(f'<li><span>{e(k)}</span><b>{e(v)}</b></li>' for k, v in facts) + '</ul>'
        opts = ''
        if o.get('paketleme_secenekleri'):
            gmap = {x['ad']: x for x in p['ozel_tr'].get('paketleme_secenekleri', [])}
            def gimg(i, x):
                return (p['ozel_tr']['paketleme_secenekleri'][i]['gorsel'])
            cards = ''.join(f'<article class="opt"><img loading="lazy" src="{ar}{gimg(i, x)}" alt="{e(x["ad"])}"><div><h3>{e(x["ad"])}</h3><ul>' + ''.join(f'<li>{e(s)}</li>' for s in x['satirlar']) + '</ul></div></article>' for i, x in enumerate(o['paketleme_secenekleri']))
            k = o.get('konteyner')
            plan = ''
            if k:
                plan = f'<h3 class="plan-h">{e(k["baslik"])}</h3><div class="plans">' + ''.join(f'<div class="plan"><b>{e(x["ad"])}</b><div class="bay">{"<span></span>" * x["adet"]}</div><em>{T("Toplam", "Total")}: {e(x["toplam"])}</em></div>' for x in k['planlar']) + f'</div><p class="note">{e(k["not"])}</p>'
            opts = f'<section class="pdp-sec"><div class="wrap"><span class="kicker">{T("Ambalaj", "Packaging")}</span><h2 class="sec-h">{T("Paketleme seçenekleri", "Packaging options")}</h2><div class="opts">{cards}</div>{plan}</div></section>'
        body = f'''{crumb(trail)}
<section class="pdp-hero" data-product="{e(p["ad"])}"><div class="wrap pdp-grid">
<div class="pdp-media"><div class="product-main">{main_img}{arrows}</div>{f'<div class="gal-cap" data-gal-cap>{e(caps0)}</div>' if multi else ''}{thumbs}</div>
<div class="pdp-summary"><span class="kicker">{e(CATS[parts[0]])}</span><h1>{e(p["ad"])}</h1>{f'<span class="tagline">{e(o["slogan"])}</span>' if o.get("slogan") else ''}{f'<p class="lead">{e(desc)}</p>' if desc else ''}
{size_html}
{facts_html}
<div class="quote-box">{box}</div>
<div class="btns"><a class="btn btn-cta" href="#teklif" data-ev="quote_click" data-urun="{e(p["ad"])}">{T("Bu ürün için teklif iste", "Request a quote for this product")}</a><a class="btn btn-light" data-wa="{e(wa_text)}" data-urun="{e(p["ad"])}">WhatsApp</a><a class="btn btn-light" href="tel:{re.sub(r"[^+0-9]", "", PHONES[0])}" data-ev="phone_click" data-urun="{e(p["ad"])}">{PHONES[0]}</a></div>
</div></div></section>
{feats}
<section class="pdp-sec"><div class="wrap"><span class="kicker">{T("Teknik", "Technical")}</span><h2 class="sec-h">{T("Ürün bilgileri", "Product information")}</h2>{spec_html}</div></section>
{opts}
{pack}
<section class="pdp-quote" id="teklif"><div class="wrap pq-grid">
<div class="pq-text"><span class="kicker">{T("Teklif", "Quote")}</span><h2>{T("Teklif isteyin", "Request a quote")}</h2><p>{T("Ürün ve ebat seçiminiz forma eklenir. Miktarı ve teslim yerini yazın, size dönelim.", "Your product and size selection are added to the form. Enter the quantity and delivery place and we will get back to you.")}</p>
<ul class="pq-contact">{''.join(f'<li><a href="tel:{re.sub(r"[^+0-9]", "", t)}" data-ev="phone_click">{t}</a></li>' for t in PHONES)}<li class="addr">{e(T(CFG["adres"], CFG["adres_en"]))}</li></ul>
<a class="btn btn-light" data-wa="{e(wa_text)}" data-urun="{e(p["ad"])}">{T("WhatsApp ile yazın", "Message us on WhatsApp")}</a></div>
<div class="pq-form">{quote_form(r, p["ad"])}</div>
</div></section>
{rel_html}
<div class="sticky-quote"><a class="btn btn-cta" href="#teklif">{T("Teklif iste", "Request a quote")}</a><a class="btn btn-ghost" data-wa="{e(wa_text)}">WhatsApp</a></div>'''
        d = f'{p["ad"]} – {CATS[cat]}. {", ".join(p["tokens"][:3])}'.strip(' .')
        write(f'{S("item")}/{p["slug"]}/index.html', page(2, f'{p["ad"]} | {CATS[parts[0]]} | Taş Dünyası', body, desc=d + T('. Fiyat ve numune için teklif isteyin.', '. Request a quote for prices and samples.'), active='products', body_class='has-sticky pdp', canonical=f'{S("item")}/{p["slug"]}/'))


# ---------- Kurumsal sayfalar ----------
def simple(key, title, inner, active='', lead=''):
    r = rel(1)
    body = f'{crumb([(T("Ana Sayfa", "Home"), r), (title, "")])}<div class="wrap page-head"><h1>{e(title)}</h1>{f"<p>{e(lead)}</p>" if lead else ""}</div><section class="wrap" style="padding-bottom:64px">{inner.replace("{r}", r)}</section>'
    write(f'{S(key)}/index.html', page(1, f'{title} | Taş Dünyası', body, active=active, canonical=f'{S(key)}/'))


def about_page():
    r = rel(1)
    ar = AR + r
    timeline = T([
        ('1973', 'Temeller atıldı', "Şirketler grubunun temelleri, bugünkü aynı ortaklar tarafından inşaat malzemeleri satışıyla atıldı. Kemerburgaz'daki Kemer Country villalarının inşaatında alt yüklenicilik de yapıldı."),
        ('1992', 'Taş ocağı', 'Ruhsatlı alanda agrega üretimine yönelik taş ocağı işletmeciliği başladı.'),
        ('2003', 'Taş Dünyası', "Doğal taş ticareti başladı. Taş Dünyası o günden bugüne aynı adreste, Kemerburgaz'da faaliyet gösteriyor."),
        ('2016', 'İnşaat', "Haziran 2016'da 24 daire ve 4 dükkândan oluşan ilk konut projesine başlandı."),
        ('2017', 'Yeni dönem', "Yakut Evleri (Arnavutköy / Bolluca) temmuzda teslim edildi. Taş Dünyası'nın ruhsatlı taş ocağı sahası rödovans sözleşmesiyle işletmeye alındı."),
    ], [
        ('1973', 'Foundations laid', "The foundations of the group were laid by the same partners of today with the sale of construction materials. They also worked as subcontractors on the construction of the Kemer Country villas in Kemerburgaz."),
        ('1992', 'Stone quarry', 'Quarry operations for aggregate production began on a licensed site.'),
        ('2003', 'Taş Dünyası', "Natural stone trading began. Taş Dünyası has operated at the same address in Kemerburgaz ever since."),
        ('2016', 'Construction', 'In June 2016 the first housing project, with 24 apartments and 4 shops, was started.'),
        ('2017', 'A new era', "Yakut Evleri (Arnavutköy / Bolluca) was delivered in July. Taş Dünyası's licensed quarry site was put into operation under a royalty (rödovans) agreement."),
    ])
    tl = ''.join(f'<li><b class="yr">{y}</b><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for y, t, d in timeline)
    mission = T([
        'Sattığımız inşaat, peyzaj ve dekorasyon amaçlı doğal taş, cam, taş-ağaç-metal art nouveau heykel-rölyef ve antika ürünlerde duyulan güveni korumak ve ürünlerimizle müşterilerimizin yaşamına değer katmak.',
        'Çalışmalarımızı kanunlara, sektör teamüllerine ve toplum geleneklerine uyumlu, yeniliklere açık yürütmeye özen göstermek.',
        'Hızlı ve kesintisiz hizmet kalitesiyle, istenen tonajda ürün tedarik ederek müşteri memnuniyetini ön planda tutmak.',
        'Çalışanlarımızın güvenliği için gereken tüm tedbirleri alarak daha sağlıklı ve güvenli bir ortamda çalışmalarını sağlamak.',
    ], [
        'To preserve the trust placed in the natural stone, glass, stone-wood-metal art nouveau sculptures and reliefs, and antiques we sell for construction, landscaping and decoration, and to add value to our customers\' lives with our products.',
        'To carry out our work in line with the law, industry practice and social customs, and open to innovation.',
        'To put customer satisfaction first through fast, uninterrupted service, supplying the tonnage requested.',
        'To take all necessary measures for the safety of our employees so that they work in a healthier and safer environment.',
    ])
    vision = T([
        'Ülkemizdeki doğal taşların ekonomiye kazandırılmasına ve insanların yaşamına sağlık ve değer katmasına hizmet etmek.',
        'Kalite standardı, uygun fiyat, kesintisiz ve istenen tonajda tedarik garantisiyle müşterileri memnun etmek.',
        'Tedarikçilerden kaliteli ve çok çeşitli ürünleri uygun fiyatla temin edip müşterilere sunmak.',
        'Yeniliklere açık ve yaratıcı olmak, en fazla çeşidi bir arada bulundurmak, doğal taş ve cam tamburlama tesisiyle marka bilinirliği ve itibarı yüksek şirket konumunu sürdürmek.',
        'Tamburlanmış doğal taş, cam ve el yapımı art nouveau heykel, rölyef, fonksiyonel peyzaj ürünleri ve antikada ilk akla gelen şirketlerden biri olmaya devam etmek.',
    ], [
        "To serve the bringing of our country's natural stones into the economy and to add health and value to people's lives.",
        'To satisfy customers with quality standards, fair prices, and uninterrupted supply guaranteed in the tonnage requested.',
        'To source high-quality, highly varied products from suppliers at fair prices and offer them to customers.',
        'To be open to innovation and creative, to keep the widest variety under one roof, and to remain a company with high brand awareness and reputation through our natural stone and glass tumbling plant.',
        'To remain one of the first companies that come to mind for tumbled natural stone, glass, hand-made art nouveau sculptures, reliefs, functional landscape products and antiques.',
    ])
    li = lambda xs: ''.join(f'<li>{e(x)}</li>' for x in xs)
    does = T([
        ('Doğal taşlar', 'Tamburlanmamış veya ebatlı, çok çeşitli doğal taşlar ve farklı boyutlarda doğal kayaçlar.'),
        ('Peyzaj camları', 'Kaya formu dahil, farklı ebatlarda tamburlanmamış peyzaj ve dekorasyon camları.'),
        ('Kendi tamburlama tesisimiz', 'Kendi tesislerimizde tamburlanan, farklı ebat ve çeşitlilikte doğal taş ve cam.'),
        ('Antik taş ve anforalar', 'Kullanılmış eski ve antik taşlar, anforalar.'),
        ('El yapımı heykel ve rölyef', "Kadromuzdaki heykeltıraşlarca doğal taş, ağaç kökü, masif kütük ve metalden; kurumsal yazı, logo, portre, hayvan, çiçek, eşya ve soyut temalı, aynısı olmayan tek üretim eserler."),
        ('Fonksiyonel peyzaj ürünleri', 'Bahçe oturma grubu, bank, saksı, çiçeklik, çeşme, havuz ve fıskiye gibi işlevsel ve yaratıcı ürünler.'),
        ('Antika ürünler', 'Büyük bölümü müzayedelerden alınmış, 400’den fazla çeşide ulaşan antika koleksiyon.'),
    ], [
        ('Natural stones', 'Untumbled or sized natural stones in great variety, and natural rocks in different sizes.'),
        ('Landscape glass', 'Untumbled landscape and decoration glass in various sizes, including rock-form pieces.'),
        ('Our own tumbling plant', 'Natural stone and glass tumbled in our own facilities, in different sizes and varieties.'),
        ('Antique stones and amphorae', 'Used old and antique stones, and amphorae.'),
        ('Hand-made sculptures and reliefs', 'Made by the sculptors on our staff from natural stone, tree roots, solid logs and metal: one-off works with corporate lettering, logos, portraits, animals, flowers, objects and abstract themes, never repeated.'),
        ('Functional landscape products', 'Functional and creative products such as garden seating sets, benches, planters, flower stands, fountains, pools and sprays.'),
        ('Antiques', 'An antique collection of more than 400 varieties, mostly bought at auctions.'),
    ])
    does_html = ''.join(f'<article class="do"><span class="no">{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, (t, d) in enumerate(does))
    stats = T([('1973', 'kuruluş, aile şirketi'), ('10.000 m²', 'açık ve kapalı alan'), ('500+', 'ürün çeşidi'), ('400+', 'antika ürün çeşidi')], [('1973', 'founded, family company'), ('10,000 m²', 'open and covered area'), ('500+', 'product varieties'), ('400+', 'antique varieties')])
    stats_html = ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in stats)
    body = T(f'''{crumb([("Ana Sayfa", r), ("Hakkımızda", "")])}
<section class="ab-hero"><div class="wrap ab-grid">
<div><span class="kicker">Hakkımızda</span><h1>1973'ten bu yana doğal taş, madencilik, peyzaj ve inşaat</h1>
<p class="lead">Taş Dünyası, aile şirketleri olan bir grubun parçası. Ortakların 40 yılı aşan ticaret hayatında madencilik, doğal taş, peyzaj ve inşaat sektörlerinde deneyim ile çok değerli bir müşteri ve tedarikçi çevresi oluştu.</p>
<p class="lead">2003'ten beri aynı adreste, İstanbul Kemerburgaz'da, Mimar Sinan'ın bugünkü hâlini verdiği tarihî Uzun Kemer'e bitişik 10.000 m² açık ve kapalı alanda faaliyet gösteriyoruz. Doğal taş ve cam tamburlama tesislerimiz, aynısı olmayan tek üretim art nouveau anlayışımız ve 500'ü aşan ürün çeşidimizle İstanbul'da tekiz.</p></div>
<div class="ab-photo"><img src="{ar}assets/img/showroom.jpg" alt="Taş Dünyası Kemerburgaz sergi alanı" loading="eager"></div>
</div></section>
<section class="ab-stats"><div class="wrap">{stats_html}</div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">Tarihçe</span><h2 class="sec-h">Yarım yüzyıla yaklaşan yolculuk</h2><ol class="timeline">{tl}</ol></div></section>
<section class="ab-mv"><div class="wrap mv-grid">
<div class="mv"><span class="kicker">Misyonumuz</span><h2>Güveni korumak, değer katmak</h2><ul>{li(mission)}</ul></div>
<div class="mv alt"><span class="kicker">Vizyonumuz</span><h2>Taşta ilk akla gelen şirket</h2><ul>{li(vision)}</ul></div>
</div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">Faaliyetlerimiz</span><h2 class="sec-h">Biz ne yapıyoruz?</h2>
<p class="ab-intro">Türkiye'nin her bölgesinden ve diğer ülkelerdeki tedarikçilerimizden temin ettiğimiz; inşaat, peyzaj, iç ve dış mekân dekorasyonu, döşeme ve kaplamada kullanılan ürünleri sunuyoruz.</p>
<div class="does">{does_html}</div>
<div class="ab-note"><b>Müşterilerimize sunduğumuz güvence:</b> Kesintisiz ve aynı kalitede tedarik, değişmeyen sözleşme fiyatı ve yüksek tonajda tedarik garantisi. Taş Dünyası uygulama yapmıyor; talep edilirse yıllardır birlikte çalıştığımız uygulamacı usta ve esnaf çözüm ortaklarımızı projenize yönlendiriyoruz.</div></div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">Grup şirketleri</span><h2 class="sec-h">Aynı çatı altında</h2>
<div class="group"><div><h3>Taş Dünyası İnşaat</h3><p>Konut projeleri. İlk proje Yakut Evleri (24 daire, 4 dükkân), temmuz 2017'de teslim edildi.</p></div>
<div><h3>Öztaş ve İlkdal</h3><p>1992'den bu yana Göktürk'teki ruhsatlı ocaklarında taş ocağı (agrega) işletmeciliği yapıyor.</p></div></div></div></section>
<section class="pdp-quote ab-cta"><div class="wrap" style="display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between"><div><h2 style="margin:0 0 6px">Projeniz için konuşalım</h2><p class="pq-text" style="margin:0;color:#DCE6EC">Showroom ve stok sahamızı Kemerburgaz'da gezebilir, fiyat ve numune için yazabilirsiniz.</p></div><div class="btns"><a class="btn btn-cta" href="{r}{S("contact")}/#teklif" data-ev="quote_click">Teklif iste</a><a class="btn btn-light" href="{r}{S("refs")}/">Referanslar</a></div></div></section>''',
    f'''{crumb([("Home", r), ("About Us", "")])}
<section class="ab-hero"><div class="wrap ab-grid">
<div><span class="kicker">About Us</span><h1>Natural stone, mining, landscaping and construction since 1973</h1>
<p class="lead">Taş Dünyası is part of a group of family-owned companies. Over more than 40 years of trading, our partners have built experience in mining, natural stone, landscaping and construction, and a valued circle of customers and suppliers.</p>
<p class="lead">Since 2003 we have operated at the same address in Kemerburgaz, Istanbul, on 10,000 m² of open and covered area next to the historic Uzun Kemer, the aqueduct given its present form by Mimar Sinan. With our natural stone and glass tumbling plants, our one-off art nouveau approach and more than 500 product varieties, we are unique in Istanbul.</p></div>
<div class="ab-photo"><img src="{ar}assets/img/showroom.jpg" alt="Taş Dünyası showroom in Kemerburgaz" loading="eager"></div>
</div></section>
<section class="ab-stats"><div class="wrap">{stats_html}</div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">History</span><h2 class="sec-h">A journey of nearly half a century</h2><ol class="timeline">{tl}</ol></div></section>
<section class="ab-mv"><div class="wrap mv-grid">
<div class="mv"><span class="kicker">Our Mission</span><h2>Keeping trust, adding value</h2><ul>{li(mission)}</ul></div>
<div class="mv alt"><span class="kicker">Our Vision</span><h2>The first name in stone</h2><ul>{li(vision)}</ul></div>
</div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">What we do</span><h2 class="sec-h">What do we do?</h2>
<p class="ab-intro">We supply products from every region of Turkey and from suppliers in other countries, for use in construction, landscaping, indoor and outdoor decoration, paving and cladding.</p>
<div class="does">{does_html}</div>
<div class="ab-note"><b>Our commitment to customers:</b> uninterrupted supply at consistent quality, a contract price that does not change, and a guarantee of supply in high tonnage. Taş Dünyası does not carry out installation; on request, we refer you to the installers and tradespeople we have worked with for years.</div></div></section>
<section class="ab-sec"><div class="wrap"><span class="kicker">Group companies</span><h2 class="sec-h">Under one roof</h2>
<div class="group"><div><h3>Taş Dünyası İnşaat</h3><p>Housing projects. The first project, Yakut Evleri (24 apartments, 4 shops), was delivered in July 2017.</p></div>
<div><h3>Öztaş and İlkdal</h3><p>Operating licensed quarries in Göktürk since 1992, producing aggregate.</p></div></div></div></section>
<section class="pdp-quote ab-cta"><div class="wrap" style="display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between"><div><h2 style="margin:0 0 6px">Let's talk about your project</h2><p class="pq-text" style="margin:0;color:#DCE6EC">Visit our showroom and stock yard in Kemerburgaz, or write to us for prices and samples.</p></div><div class="btns"><a class="btn btn-cta" href="{r}{S("contact")}/#teklif" data-ev="quote_click">Request a quote</a><a class="btn btn-light" href="{r}{S("refs")}/">References</a></div></div></section>''')
    write(f'{S("about")}/index.html', page(1, T('Hakkımızda | Taş Dünyası', 'About Us | Taş Dünyası'), body, desc=T("1973'ten bu yana doğal taş, madencilik, peyzaj ve inşaat. Taş Dünyası'nın tarihçesi, misyonu, vizyonu ve faaliyetleri.", "Natural stone, mining, landscaping and construction since 1973. The history, mission, vision and activities of Taş Dünyası."), active='about', body_class='about', canonical=f'{S("about")}/'))


def build_pages():
    about_page()
    refs = ''.join(f'<div class="ref">{e(x)}</div>' for x in CFG['referanslar'])
    simple('refs', T('Referanslar', 'References'), f'''<div class="refs">{refs}</div>
<div class="panel" style="margin-top:24px;border-left:4px solid var(--blue)">{T("<b>Sanat dünyasında:</b> Heykeltıraş Adrián Villar Rojas'ın İtalya ContemporaryArt Torino fuarındaki sergisinde kullanılan doğal kayaçların büyük bölümü Taş Dünyası'ndan temin edildi.", "<b>In the art world:</b> Most of the natural rocks used in sculptor Adrián Villar Rojas's exhibition at the ContemporaryArt Torino fair in Italy were supplied by Taş Dünyası.")}</div>
<p class="note" style="margin-top:14px"><span class="todo">{T("Düzenlenecek: referans logoları ve proje fotoğrafları eklenecek.", "To do: reference logos and project photos will be added.")}</span></p>''', active='refs', lead=T('Kamu kurumları, inşaat ve peyzaj firmaları, mimarlık ofisleri.', 'Public institutions, construction and landscaping companies, architecture offices.'))
    tel = ''.join(f'<div><a href="tel:{re.sub(r"[^+0-9]", "", t)}" data-ev="phone_click">{t}</a></div>' for t in PHONES)
    maps = 'https://www.google.com/maps/search/?api=1&query=' + 'Ta%C5%9F+D%C3%BCnyas%C4%B1+Kemerburgaz'
    simple('contact', T('İletişim', 'Contact'), f'''<div class="split" style="align-items:flex-start">
<div class="panel" style="flex:1 1 300px"><h2 style="font-size:22px;margin-bottom:10px">{T("Bize ulaşın", "Get in touch")}</h2><p style="margin:0 0 10px">{e(CFG["unvan"])}</p><p style="margin:0 0 10px">{e(T(CFG["adres"], CFG["adres_en"]))}</p>{tel}<div class="btns" style="margin-top:16px"><a class="btn btn-navy" href="{maps}" target="_blank" rel="noopener">{T("Yol tarifi", "Directions")}</a><a class="btn btn-ghost" data-wa="">WhatsApp</a></div></div>
<div id="teklif" style="flex:2 1 520px"><h2 style="font-size:22px;margin-bottom:12px">{T("Teklif formu", "Quote form")}</h2>{quote_form("{r}")}</div></div>''', active='contact', lead=T("Showroom ve stok sahamız Kemerburgaz'da. Fiyat ve numune için yazın ya da arayın.", 'Our showroom and stock yard are in Kemerburgaz. Write or call us for prices and samples.'))
    old = CFG['eski_site']
    simple('catalog', T('E-Katalog', 'E-Catalogue'), f'''<div class="grid wide"><a class="card" href="{old}/Dogaltas-E-Katalog3/dogaltas_tr/" target="_blank" rel="noopener"><div class="card-body"><span class="card-title">{T("Doğal Taş E-Katalog", "Natural Stone E-Catalogue")}</span><span class="card-sub">{T("Online katalog (eski sitede açılır)", "Online catalogue (opens on the old site)")}</span></div></a><a class="card" href="{old}/ekatalog/antika/" target="_blank" rel="noopener"><div class="card-body"><span class="card-title">{T("Antik Eşya E-Katalog", "Antique Items E-Catalogue")}</span><span class="card-sub">{T("Online katalog (eski sitede açılır)", "Online catalogue (opens on the old site)")}</span></div></a></div>
<p class="note" style="margin-top:14px"><span class="todo">{T("Düzenlenecek: güncel PDF katalog bu depoya eklenecek.", "To do: the current PDF catalogue will be added here.")}</span></p>''')
    simple('tour', T('360° Sanal Tur', '360° Virtual Tour'), f'''<div class="panel"><p>{T("Kemerburgaz'daki stok sahamızı ve showroom'umuzu ekrandan gezin.", "Tour our stock yard and showroom in Kemerburgaz on screen.")}</p><a class="btn btn-navy" href="{old}/sanaltur" target="_blank" rel="noopener">{T("Sanal turu başlat", "Start the virtual tour")}</a><p class="note" style="margin-top:12px"><span class="todo">{T("Düzenlenecek: sanal tur dosyaları yeni siteye taşınacak.", "To do: the virtual tour files will be moved to the new site.")}</span></p></div>''')
    simple('legal', T('Yasal Uyarı ve KVKK', 'Legal Notice and Privacy (KVKK)'), f'''<div class="prose"><p><span class="todo">{T("Düzenlenecek: yasal uyarı, kullanım koşulları ve KVKK aydınlatma metni hukuk danışmanının onayıyla eklenecek.", "To do: the legal notice, terms of use and the KVKK privacy notice will be added after approval by legal counsel.")}</span></p><p>{T("Teklif formunda paylaştığınız ad, telefon ve e-posta bilgileri yalnızca talebinize yanıt vermek amacıyla kullanılır.", "The name, phone number and e-mail address you share in the quote form are used only to respond to your request.")}</p></div>''')


# ---------- 404 + eski adres yönlendirmesi, arama dizini, robots, sitemap ----------
def build_search():
    idx = []
    for p in products:
        it = {'t': p['ad'], 'c': CATS[p['kategori']], 's': p['slug'], 'i': p['imgs'][0] if p['imgs'] else ''}
        if LANG == 'en':
            it['k'] = p['ad_tr'] + ' ' + CATS_TR[p['kategori']]  # Türkçe adla da bulunsun
        idx.append(it)
    write('search.json', json.dumps(idx, ensure_ascii=False, separators=(',', ':')))


def build_misc():
    legacy = {'tr': {}, 'en': {}, 'pages_tr': dict(KAT['pages_tr']), 'pages_en': {}}
    for k, v in KAT['tr'].items():
        legacy['tr'][k] = 'urun-kategori/' + v + '/'
    for k, v in KAT['en'].items():
        legacy['en'][k] = 'en/category/' + v + '/'
    for p in products:
        legacy['tr'][p['id']] = 'urun/' + p['slug'] + '/'
        legacy['en'].setdefault(p['id'], 'en/product/' + p['slug'] + '/')
    inv = {v: k for k, v in SEG['tr'].items()}
    for k, v in KAT['pages_en'].items():
        seg = v.strip('/').split('/')[0]
        legacy['pages_en'][k] = ('en/' + SEG['en'][inv[seg]] + '/') if seg in inv else 'en/'
    legacy['pages_tr']['referanslar'] = '/referanslar/'
    legacy['pages_en']['referances'] = 'en/references/'
    legacy['pages_en']['homepage'] = 'en/'
    (OUT / 'assets').mkdir(parents=True, exist_ok=True)
    (OUT / 'assets' / 'legacy.json').write_text(json.dumps(legacy, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    base = CFG['taban_yol'].rstrip('/')
    body = f'''<div class="wrap page-head" style="padding:64px 24px"><h1>Sayfa bulunamadı <small style="display:block;font-size:.55em;opacity:.7;margin-top:6px">Page not found</small></h1><p id="msg">Aradığınız sayfa taşınmış olabilir. / The page you are looking for may have moved.</p><div class="btns" style="margin-top:18px"><a class="btn btn-navy" href="{base}/urunler/">Ürünlere git</a><a class="btn btn-ghost" href="{base}/">Ana sayfa</a><a class="btn btn-ghost" href="{base}/en/">English site</a></div></div>
<script>
(function(){{
  var base={json.dumps(base)}; var path=decodeURIComponent(location.pathname); if(base&&path.indexOf(base)===0) path=path.slice(base.length);
  var m=path.match(/^\\/(tr-TR|en-US)(?:\\/(.*))?$/i); var kat=/^\\/(dogaltas-e-katalog\\d*|ekatalog)(\\/|$)/i.test(path)?'e-katalog/':(/^\\/sanaltur\\/?$/i.test(path)?'sanal-tur/':null);
  function go(t){{ location.replace(base+'/'+String(t).replace(/^\\//,'')); }}
  if(kat) return go(kat);
  if(!m) return;
  document.getElementById('msg').textContent='Yeni adrese yönlendiriliyorsunuz… / Redirecting…';
  fetch(base+'/assets/legacy.json').then(function(r){{return r.json()}}).then(function(L){{
    var lang=m[1].toLowerCase()==='tr-tr'?'tr':'en'; var segs=(m[2]||'').split('/').filter(Boolean); if(!segs.length) return go(lang==='tr'?'':'en/');
    var ids=segs.slice(1).filter(function(s){{return /^\\d+$/.test(s)&&s.replace(/^0+/,'')!==''}}).map(function(s){{return s.replace(/^0+/,'')}}).reverse();
    for(var i=0;i<ids.length;i++) if(L[lang][ids[i]]) return go(L[lang][ids[i]]);
    var slug=segs[0].toLowerCase().replace(/ı/g,'i').replace(/ğ/g,'g').replace(/ü/g,'u').replace(/ş/g,'s').replace(/ö/g,'o').replace(/ç/g,'c').replace(/[^a-z0-9-]+/g,'');
    var pages=lang==='tr'?L.pages_tr:L.pages_en; if(pages[slug]) return go(pages[slug]);
    go(segs[1]==='3'||segs[1]==='1199'?(lang==='tr'?'urunler/':'en/products/'):(lang==='tr'?'':'en/'));
  }});
}})();
</script>'''
    html = page(0, 'Sayfa bulunamadı | Taş Dünyası', body, canonical=None)
    # 404 sayfası her derinlikten açılır: bağlantıları kök yoluna sabitle
    html = html.replace('data-root=""', f'data-root="{base}/"').replace('href="assets/', f'href="{base}/assets/').replace('src="assets/', f'src="{base}/assets/')
    html = re.sub(r'(href|action)="(?!https?:|tel:|#|/|mailto:)([^"]*)"', lambda m: f'{m.group(1)}="{base}/{m.group(2)}"', html)
    write('404.html', html)

    site = CFG['site_adresi'].rstrip('/')
    base_pages = ['', 'products/', 'about/', 'references/', 'contact/', 'e-catalogue/', 'virtual-tour/', 'legal/']
    urls_tr = ['', 'urunler/', 'hakkimizda/', 'referanslar/', 'iletisim/', 'e-katalog/', 'sanal-tur/', 'yasal-uyari/'] + [f'urun-kategori/{c}/' for c in CATS_TR] + [f'urun/{p["slug"]}/' for p in products]
    urls = []
    for u in urls_tr:
        urls.append(u)
        urls.append('en/' + alt_path(u, 'en'))
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{site}/{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n' if DRAFT else f'User-agent: *\nAllow: /\nSitemap: {site}/sitemap.xml\n', encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    tr_strings = {'dec': ',', 'item': 'urun/', 'menuOpen': 'Menüyü aç', 'menuClose': 'Menüyü kapat', 'waDefault': 'Merhaba, ürünleriniz hakkında bilgi almak istiyorum.', 'draftMsg': 'Taslak: WhatsApp numarası ve e-posta adresi config.js dosyasına eklenince form çalışır. Şimdilik bizi telefonla arayabilirsiniz.', 'quoteReq': 'Teklif talebi', 'fProduct': 'Ürün', 'fQty': 'Miktar', 'fPlace': 'Teslim yeri', 'fName': 'Ad soyad', 'fCompany': 'Firma', 'fPhone': 'Telefon', 'fMail': 'E-posta', 'fNote': 'Not', 'quoteSubject': 'Teklif talebi', 'searchHead': '"{q}" için {n} ürün', 'noResult': 'Sonuç bulunamadı. Aradığınız ürünü bize yazın, tedarik edelim.', 'lang': 'tr'}
    en_strings = {'dec': '.', 'item': 'product/', 'menuOpen': 'Open menu', 'menuClose': 'Close menu', 'waDefault': 'Hello, I would like information about your products.', 'draftMsg': 'Draft: the form will work once the WhatsApp number and e-mail address are added to config.js. For now, please call us.', 'quoteReq': 'Quote request', 'fProduct': 'Product', 'fQty': 'Quantity', 'fPlace': 'Delivery place', 'fName': 'Full name', 'fCompany': 'Company', 'fPhone': 'Phone', 'fMail': 'E-mail', 'fNote': 'Note', 'quoteSubject': 'Quote request', 'searchHead': '{n} products for "{q}"', 'noResult': 'No results. Tell us what you are looking for and we will source it.', 'lang': 'en'}
    for name, st in (('config.js', tr_strings), ('config-en.js', en_strings)):
        js = {'whatsapp': CFG.get('whatsapp', ''), 'email': CFG.get('eposta', ''), 'imgBase': IMG, 't': st}
        (OUT / 'assets' / name).write_text('window.TD = ' + json.dumps(js, ensure_ascii=False) + ';\n', encoding='utf-8')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets').mkdir(parents=True)
    shutil.copytree(ROOT / 'assets' / 'img', OUT / 'assets' / 'img')
    shutil.copy(ROOT / 'src' / 'site.css', OUT / 'assets' / 'site.css')
    shutil.copy(ROOT / 'src' / 'site.js', OUT / 'assets' / 'site.js')
    for lang in ('tr', 'en'):
        set_lang(lang)
        build_home(); build_listing(); build_products(); build_pages(); build_search()
    set_lang('tr')
    build_misc()
    n = sum(1 for _ in OUT.rglob('*.html'))
    print(f'{n} sayfa üretildi (TR + EN): {len(products)} ürün, {len(CATS)} kategori → {OUT}')


if __name__ == '__main__':
    main()
