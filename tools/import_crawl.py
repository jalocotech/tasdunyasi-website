"""Eski siteden taranan veriyi (data/crawl.json) düzenlenebilir ürün tablosuna (data/urunler.csv) çevirir.

Bir kez çalıştırılır. Sonrasında kaynak data/urunler.csv dosyasıdır; elle ya da Excel ile düzenlenir.
Kullanım: python3 tools/import_crawl.py [--force]
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'urunler.csv'

# ASCII yazılmış Türkçe kelimelerin düzeltmeleri (küçük harf → doğru yazım)
FIX = {
 'tas': 'taş', 'tasi': 'taşı', 'taslari': 'taşları', 'taslar': 'taşlar', 'tasindan': 'taşından', 'tamburlanmis': 'tamburlanmış',
 'tamburlanmamis': 'tamburlanmamış', 'dogal': 'doğal', 'agac': 'ağaç', 'agaç': 'ağaç', 'agaci': 'ağacı', 'çakil': 'çakıl', 'çakili': 'çakılı',
 'kayragi': 'kayrağı', 'yassi': 'yassı', 'yassy': 'yassı', 'kirmizi': 'kırmızı', 'sari': 'sarı', 'yesil': 'yeşil', 'yesili': 'yeşili', 'açik': 'açık',
 'karisik': 'karışık', 'çesitleri': 'çeşitleri', 'çesme': 'çeşme', 'çesmesi': 'çeşmesi', 'fiskiye': 'fıskiye', 'saksi': 'saksı',
 'baykus': 'baykuş', 'kusu': 'kuşu', 'balik': 'balık', 'baligi': 'balığı', 'ayi': 'ayı', 'kiz': 'kız', 'çocugu': 'çocuğu', 'tavsan': 'tavşan',
 'tavsanli': 'tavşanlı', 'günes': 'güneş', 'ahsap': 'ahşap', 'kapi': 'kapı', 'kanatli': 'kanatlı', 'makinasi': 'makinası', 'dikis': 'dikiş',
 'ayakli': 'ayaklı', 'kapakli': 'kapaklı', 'bakir': 'bakır', 'gümüs': 'gümüş', 'takimi': 'takımı', 'takim': 'takım', 'sobasi': 'sobası',
 'sömine': 'şömine', 'askili': 'askılı', 'sirketi': 'şirketi', 'tabelasi': 'tabelası', 'yapim': 'yapım', 'yapimi': 'yapımı', 'sarap': 'şarap',
 'fiçilari': 'fıçıları', 'fiçisi': 'fıçısı', 'fiçisindan': 'fıçısından', 'kagni': 'kağnı', 'arabasi': 'arabası', 'islenmis': 'işlenmiş',
 'islemeli': 'işlemeli', 'islenmemis': 'işlenmemiş', 'yeldegirmeni': 'yeldeğirmeni', 'degirmeni': 'değirmeni', 'degirmen': 'değirmen',
 'oymasi': 'oyması', 'oymali': 'oymalı', 'sapka': 'şapka', 'sort': 'şort', 'lambasi': 'lambası', 'basi': 'başı', 'basli': 'başlı',
 'kösesi': 'köşesi', 'köse': 'köşe', 'kaplumbagasi': 'kaplumbağası', 'kaplumbaga': 'kaplumbağa', 'ugur': 'uğur', 'böcegi': 'böceği',
 'iki': 'iki', 'içinde': 'içinde', 'için': 'için', 'izi': 'izi', 'ithal': 'ithal', 'ibrik': 'ibrik', 'ip': 'ip', 'iskeleti': 'iskeleti',
 'parlatilmis': 'parlatılmış', 'yakilmis': 'yakılmış', 'ebatli': 'ebatlı', 'dag': 'dağ', 'masasi': 'masası', 'çalisma': 'çalışma',
 'koltugu': 'koltuğu', 'açilir': 'açılır', 'kapanir': 'kapanır', 'sandigi': 'sandığı', 'aynali': 'aynalı', 'dolapli': 'dolaplı',
 'kapli': 'kaplı', 'kadin': 'kadın', 'savasçi': 'savaşçı', 'bugday': 'buğday', 'çaydanlik': 'çaydanlık', 'duymadim': 'duymadım',
 'samdan': 'şamdan', 'asyali': 'asyalı', 'yogurt': 'yoğurt', 'bakraci': 'bakracı', 'sarayli': 'saraylı', 'serbet': 'şerbet',
 'ibrigi': 'ibriği', 'çamasir': 'çamaşır', 'hizari': 'hızarı', 'matkabi': 'matkabı', 'genisletme': 'genişletme', 'tulumbasi': 'tulumbası',
 'tirmigi': 'tırmığı', 'taslama': 'taşlama', 'sikma': 'sıkma', 'egirme': 'eğirme', 'ögütme': 'öğütme', 'tabancasi': 'tabancası',
 'gida': 'gıda', 'kati': 'katı', 'bas': 'baş', 'arkasi': 'arkası', 'saksida': 'saksıda', 'disi': 'dişi', 'dis': 'dişi', 'kugu': 'kuğu',
 'anahtari': 'anahtarı', 'sirt': 'sırt', 'sirta': 'sırta', 'karsilikli': 'karşılıklı', 'ayakkabi': 'ayakkabı', 'çantasi': 'çantası',
 'agzi': 'ağzı', 'kayasi': 'kayası', 'dali': 'dalı', 'katli': 'katlı', 'pasabahçe': 'paşabahçe', 'kornasi': 'kornası', 'havali': 'havalı',
 'diregi': 'direği', 'çani': 'çanı', 'çipa': 'çıpa', 'babalari': 'babaları', 'sehpasi': 'sehpası', 'yuvasi': 'yuvası', 'tugla': 'tuğla',
 'çikma': 'çıkma', 'uygulamasy': 'uygulaması', 'uygulamamyz': 'uygulamamız', 'isi': 'ısı', 'köpegi': 'köpeği', 'ögesi': 'öğesi',
 'kiyafetli': 'kıyafetli', 'denizanasi': 'denizanası', 'anasi': 'anası', 'yüzlü': 'yüzlü', 'baligi': 'balığı', 'kafasi': 'kafası',
 'boga': 'boğa', 'aslani': 'aslanı', 'mermeri': 'mermeri', 'islemeli': 'işlemeli', 'ölçegi': 'ölçeği', 'elegi': 'eleği', 'tahil': 'tahıl',
 'ilaçlama': 'ilaçlama', 'kizilderili': 'kızılderili', 'yusufçuk': 'yusufçuk', 'sehpali': 'sehpalı', 'kollu': 'kollu', 'çeyiz': 'çeyiz',
}
UP = {'i': 'İ', 'ı': 'I'}
LOW = {'I': 'ı', 'İ': 'i'}


def tr_lower(s):
    return ''.join(LOW.get(c, c) for c in s).lower()


def fix_word(w):
    if len(w) > 1 and w.isupper():
        return w  # marka adları (SINGER, AEG) aynen kalır
    key = w.replace('İ', 'i').lower()
    if key not in FIX:
        return w
    out = FIX[key]
    if w[0].isupper():
        out = UP.get(out[0], out[0].upper()) + out[1:]
    return out


def fix_text(s):
    return re.sub(r"[^\W\d_]+", lambda m: fix_word(m.group(0)), s)


TRMAP = str.maketrans('çğıöşüÇĞİÖŞÜâîûéÉ', 'cgiosuCGIOSUaiuee')


def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.translate(TRMAP).lower())
    return re.sub(r'-+', '-', s).strip('-')


def main():
    if OUT.exists() and '--force' not in sys.argv:
        sys.exit(f'{OUT} zaten var. Üzerine yazmak için --force ekleyin (elle yapılan düzenlemeler silinir).')
    cats = json.loads((ROOT / 'data' / 'kategoriler.json').read_text(encoding='utf-8'))
    tr = cats['tr']
    crawl = json.loads((ROOT / 'data' / 'crawl.json').read_text(encoding='utf-8'))
    used, rows = {}, []
    for x in sorted(crawl, key=lambda x: [int(i) for i in x['c'].split('/')]):
        ids = x['c'].split('/')[1:]
        pid = ids[-1].lstrip('0') or '0'
        cat = next((tr[i] for i in reversed(ids[:-1]) if i in tr), 'cam-peyzaj-urunleri' if pid == '3044' else '')
        if not cat:
            continue
        name = x['n'].strip()
        code = ''
        m = re.search(r'\s*Ürün Kodu\s*:\s*(\S+)\s*$', name)
        if m:
            code, name = m.group(1), name[:m.start()].strip()
        raw = x['n'].strip()
        detail = x['d'].strip()
        for prefix in (raw, name):
            if detail.startswith(prefix):
                detail = detail[len(prefix):]
                break
        detail = re.sub(r'^[\s,]+', '', detail)
        detail = re.sub(r'^Ölçüler\s*', '', detail).strip()
        name, detail = fix_text(name), fix_text(detail)
        base = slugify(name) or 'urun'
        if base.isdigit():
            base = 'urun-' + base
        n = used.get(base, 0) + 1
        used[base] = n
        slug = base if n == 1 else f'{base}-{n}'
        rows.append({
            'id': pid, 'slug': slug, 'ad': name, 'kategori': cat, 'kod': code, 'detay': detail,
            'gorseller': ' '.join(x['i']), 'eski_fiyat': x['p'].strip(), 'yayinda': 'evet', 'eski_yol': x['c'],
        })
    with OUT.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'ürün yazıldı →', OUT)


if __name__ == '__main__':
    main()
