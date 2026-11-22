"""Ürün 'detay' parçalarını (ölçü, malzeme, not) İngilizceye çevirir.
Kural + sözlük tabanlı; elle düzeltmeler data/en_tokens_override.json içinde.
Kullanım: python3 tools/en_tokens.py  →  data/en_tokens.json (çıktı, build.py okur)
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

W = {
    # ölçü / yapı
    'yükseklik': 'Height', 'yukseklik': 'Height', 'genişlik': 'Width', 'genislik': 'Width', 'uzunluk': 'Length',
    'yarıçap': 'radius', 'yariçap': 'radius', 'yarıçapı': 'radius', 'yariçapi': 'radius', 'yarıçapi': 'radius', 'yari': 'half', 'çap': 'diameter',
    'kalınlık': 'thickness', 'kalinlik': 'thickness', 'kalınlığı': 'thickness', 'kalinlikta': 'thick',
    'ağırlık': 'Weight', 'toplam': 'Total', 'toplamı': 'Total', 'tanesi': 'each', 'teki': 'each', 'adet': 'pcs', 'adedi': 'qty',
    'tane': 'pcs', 'parça': 'pieces', 'parçali': 'pieces', 'parca': 'pieces', 'ile': 'to', 'arası': 'between', 'arasi': 'between', 'arasinda': 'between', 'arasında': 'between',
    'üst': 'top', 'alt': 'bottom', 'ön': 'front', 'yan': 'side', 'kenar': 'side', 'kisa': 'short', 'kenari': 'side', 'uzun': 'long',
    'boy': 'length', 'serbest': 'free', 'büyük': 'Large', 'küçük': 'Small', 'orta': 'Medium', 'ortadaki': 'middle', 'soldaki': 'left', 'sağdaki': 'right', 'sagdaki': 'right',
    'bir': 'one', 'levha': 'slab', 've': 'and', 'veya': 'or', 'ile birlikte': 'with', 'birlikte': 'together with',
    'stokta': 'in stock', 'stok': 'stock', 'sayisi': 'count', 'sürekli': 'continuously', 'bulunmaktadir': 'available',
    'degisen': 'varying', 'ebatlarda': 'in sizes', 'ebat': 'size', 'büyüklük': 'size', 'arasında': 'between',
    'ağız': 'mouth', 'agiz': 'mouth', 'ağzı': 'mouth', 'yüksekliği': 'height', 'yuksekligi': 'height',
    'oturma': 'Seat', 'oturak': 'Seat', 'tepsi': 'Tray', 'tabak': 'Plate', 'fincanlar': 'Cups', 'vazo': 'Vase', 'sürahi': 'Pitcher', 'derin': 'Deep',
    # malzeme
    'taşı': 'stone', 'taşından': 'stone', 'taş': 'Stone', 'tasi': 'stone', 'taşları': 'stones', 'mermeri': 'Marble', 'mermer': 'Marble',
    'granit': 'Granite', 'bazalt': 'Basalt', 'traverten': 'Travertine', 'onyx': 'Onyx', 'onix': 'Onyx', 'kayrak': 'Slate', 'kum': 'Sand', 'kumtaşı': 'Sandstone',
    'bal': 'Honey', 'kırmızı': 'Red', 'sarı': 'Yellow', 'yeşil': 'Green', 'pembe': 'Pink', 'gri': 'Grey', 'açık': 'Light', 'kahverengi': 'Brown', 'beyaz': 'White', 'siyah': 'Black',
    'ahşap': 'Wood', 'ağaç': 'Wood', 'agaç': 'Wood', 'ağacı': 'Wood', 'agacindan': 'wood', 'ağaça': 'Wood', 'kütük': 'log', 'kütükten': 'log', 'kütügünden': 'log', 'masif': 'Solid',
    'bakır': 'Copper', 'bronz': 'Bronze', 'pirinç': 'Brass', 'demir': 'Iron', 'metal': 'Metal', 'çelik': 'Steel', 'paslanmaz': 'Stainless', 'döküm': 'Cast', 'cam': 'Glass', 'camli': 'glass', 'seramik': 'Ceramic',
    'deri': 'Leather', 'kil': 'Clay', 'alçı': 'Plaster', 'patine': 'patina', 'kadife': 'Velvet', 'kumasli': 'fabric', 'çuha': 'felt', 'emaye': 'Enamel', 'kaplama': 'coating', 'kaplamali': 'coated', 'kaplı': 'covered',
    'fosili': 'Fossil', 'fosilli': 'fossil', 'midye': 'Mussel', 'serpantin': 'Serpentine', 'meteor': 'Meteor', 'çakıl': 'Pebble', 'çakil': 'Pebble', 'çakıl': 'Pebble', 'çakiltasi': 'Pebble', 'afyon': 'Afyon', 'marmara': 'Marmara', 'angel': 'Angel', 'okaliptus': 'Eucalyptus',
    'tuğla': 'Brick', 'zemin': 'floor', 'iç': 'Interior', 'içi': 'Interior',
    # not
    'yapımı': 'made', 'yapimi': 'made', 'yapım': 'made', 'yili': 'year', 'yılı': 'year', 'civari': 'approx.', 'üretimi': 'production', 'günümüz': 'Contemporary', 'almanya': 'Germany', 'alman': 'German',
    'el': 'Hand', 'oyması': 'carved', 'oyma': 'carved', 'oymalı': 'carved', 'desen': 'pattern', 'desenli': 'patterned', 'işlemeli': 'inlaid', 'işlenmiş': 'carved', 'çiçek': 'Flower', 'çiçeklik': 'Planter',
    'kaidesi': 'Pedestal', 'kaidesiyle': 'with pedestal', 'kaide': 'pedestal', 'ayaklar': 'Legs', 'ayakları': 'Legs', 'ayak': 'Leg', 'ayaklari': 'Legs', 'kısmı': 'part', 'kisim': 'part', 'kismi': 'part',
    'beslemeli': 'feed', 'yandan': 'side', 'alttan': 'bottom', 'önden': 'front', 'üstten': 'top', 'dişi': 'female', 'erkek': 'male', 'çekmeceli': 'drawers', 'çekmece': 'drawer', 'sandalye': 'chairs', 'raf': 'shelf', 'iki': 'Two', 'gözlü': 'compartment', 'göz': 'compartment',
    'kapı': 'door', 'kapıları': 'doors', 'açılıyor': 'open', 'açılır': 'opening', 'kapak': 'lid', 'kapağı': 'lid', 'kapandiginda': 'when closed', 'tek': 'Single', 'doğal': 'Natural', 'dogaltas': 'Natural stone', 'doğal taş': 'Natural stone', 'gövdesi': 'trunk', 'kökü': 'root', 'köke': 'root', 'girer': 'enters',
    'birebir': 'Life-size', 'ölçeklidir': 'scale', 'orijinal': 'Original', 'eski': 'Old', 'kağnı': 'ox-cart', 'arabası': 'cart', 'tekerinden': 'wheel', 'tekerlekli': 'wheeled', 'tekerlerin': 'Wheel', 'at': 'Horse',
    'kuş': 'Bird', 'kus': 'Bird', 'kaplan': 'Tiger', 'yavrulari': 'cubs', 'motifli': 'motif', 'arkası': 'Back', 'diger': 'Other', 'yüzünde': 'side', 'yüzü': 'side', 'semazen': 'Whirling dervish', 'heykeli': 'sculpture', 'heykel': 'Sculpture', 'rölyefi': 'Relief', 'rölyefli': 'Relief',
    'bahçe': 'Garden', 'lavabosu': 'Sink', 'çeşmesi': 'Fountain', 'lavabo': 'Sink', 'kafes': 'cage', 'marka': 'brand', 'seri': 'Serial', 'no': 'No.', 'patent': 'Patent', 'merhum': 'late', 'ressam': 'painter', 'tablo': 'painting', 'tablosunu': 'painting', 'yağlı': 'Oil', 'boya': 'paint',
    'çelik fermuar': 'Steel zip', 'fermuar': 'zip', 'aksam': 'fittings', 'aksamı': 'fittings', 'çerçeve': 'Frame', 'çerçeveli': 'framed', 'stor': 'roller', 'perde': 'blind', 'pervaneleri': 'blades', 'pervaneler': 'Blades', 'pervanaleri': 'Blades', 'rüzgarda': 'in the wind', 'döner': 'turn',
    'vidali': 'screw', 'dönerek': 'turning', 'yükselip': 'rises', 'alçalir': 'lowers', 'ucuna': '', 'tırnaklar': 'Claws', 'tirnaklari': 'claws', 'topları': 'balls', 'toplari': 'Balls', 'toplar': 'Balls', 'çeker': 'Capacity', 'çekeri': 'Capacity', 'libre': 'lb', 'sivama': 'plaster', 'kapali': 'closed',
    'şekerlik': 'Sugar bowl', 'çini': 'Tile-work', 'kesme': 'Cut', 'mumluk': 'Candle holder', 'bagcik': 'strap', 'ince': 'thin', 'kalin': 'thick', 'delikli': 'Perforated', 'çıpa': 'Anchor', 'balık': 'Fish', 'hasır': 'wicker', 'örme': 'woven', 'nü': 'Nude', 'kadın': 'Woman', 'kız': 'Girl', 'çocuğu': 'child', 'cilalı': 'Polished',
    'dogaçlama': 'Improvised', 'damperi': 'Dump bed', 'kalkıyor': 'tilts', 'freni': 'Brake', 'var': 'included', 'bağlama': 'Tie', 'kemeri': 'belt', 'ayı': 'Bear', 'köpek': 'Dog', 'başı': 'Head', 'başi': 'head', 'tarafi': 'side', 'ön tarafi': 'Front', 'sırt': 'Back', 'sırtı': 'Back', 'yaslama': 'rest', 'ünitesi': 'unit',
    'doğal ağaç': 'Natural wood', 'toprak': 'Clay', 'küp': 'jar', 'duvar': 'Wall', 'gabyon': 'gabion', 'örnegi': 'example', 'ürün': 'product', 'fiyat': 'price', 'yeldeğirmeni': 'Windmill', 'yel': 'wind', 'değirmeni': 'mill', 'kulübe': 'Cabin', 'sobası': 'stove', 'soba': 'stove', 'kömür': 'Coal',
    'parçalı': 'pieces', 'demonte': 'knock-down', 'yassı': 'Flat', 'emperador': 'Emperador', 'light': 'Light', 'elazig': 'Elazığ', 'elazığ': 'Elazığ', 'visne': 'Cherry', 'vişne': 'Cherry', 'vize': 'Vize', 'bakırköy': 'Bakırköy', 'kalesi': 'Castle', 'sehpa': 'Coffee table', 'sehpası': 'Coffee table',
    'ayaklarara si': '', 'cam altinda': 'Under glass', 'altin': 'Gold', 'altın': 'Gold', 'varak': 'leaf', 'tablasi': 'Top', 'üzerine': 'on', 'işlemeli': 'embroidered', 'kayaç': 'Rock', 'kaya': 'Rock', 'yeşil çuha': 'green felt', 'kapıları açılıyor': 'doors open',
    'bir levha': 'one slab', 'kilo': 'kg', 'yok': 'none', 'üretim': 'production',
}
# Cümle düzeyinde elle çeviriler (sözlükle bozulacak özel metinler)
FIX = {
    'Meteor Taşları 20cm-2kg ile 160cm-5000kg arasinda degisen ebatlarda stokta sürekli bulunmaktadir.': 'Meteor stones are always in stock in sizes ranging from 20 cm / 2 kg up to 160 cm / 5,000 kg.',
    "Katar`ly merhum Ressam Yusuf ?efir`in \"Meydan Okuma\" tablosunu 1.400.000 Do?al Ta? kullanarak Tekrar sanat ile bulu?turduk.": 'We recreated the painting "Challenge" by the late Qatari painter Yusuf Shefir using 1,400,000 natural stones.',
    'Birebir Ölçeklidir': 'Life-size',
    'Ayaklari Kapandiginda Yatak Kahvalti Sehpası olur': 'Becomes a breakfast-in-bed tray when the legs are folded',
    'Kaidesi Doğal Ağaç Köküdür ve Köke Giren Taşlar Doğal Formdur': 'The base is a natural tree root; the stones set into the root are in their natural form',
    'Pervaneler Demir Çerçeveli Stor Perde Kaplamali': 'Iron-framed blades covered with roller-blind fabric',
    'Pervanaleri Rüzgarda Döner': 'Blades turn in the wind',
    'pervaneleri rüzgarda döner': 'Blades turn in the wind',
    'Pervaneleri Rüzgarda Döner': 'Blades turn in the wind',
    'vidali dönerek yükselip alçalir': 'Rises and lowers by turning the screw',
    'Oturma ve Sırt Yaslama Ünitesi Ahşap': 'Wooden seat and backrest unit',
    'Orijinal Eski At Arabası Tekerlerinden El Yapımı': 'Hand-made from original old horse-cart wheels',
    'Eski Kağnı Arabası Tekerinden El Yapımı Dekoratif Bisiklet': 'Decorative bicycle hand-made from an old ox-cart wheel',
    'Ayak ve Kase Masif Ağaç Kütükten El Oyması': 'Foot and bowl hand-carved from a solid log',
    'Masif Ağaç Kütükten El Oyması': 'Hand-carved from a solid log',
    'Tek Parça Masif Ağaç Kütügünden El Yapımı': 'Hand-made from a single solid log',
    'Okaliptus Agacindan El Oyması': 'Hand-carved from eucalyptus wood',
    'Tabak Granit Taşından El Oyması': 'Plate hand-carved from granite',
    'Tablasi Kahverengi Deri Üzerine Altin Varak İşlemeli': 'Top: brown leather with gold-leaf inlay',
    'Kaidesi Midye Fosilli Taş': 'Pedestal: mussel-fossil stone',
    'Rölyefli Çiçeklik veya Bahçe Çeşmesi Lavabosu': 'Relief planter or garden fountain basin',
    'veya Bahçe Lavabosu': 'or garden basin',
    'veya Bahçe Çeşmesi Lavabosu': 'or garden fountain basin',
    'Duvar-Gabyon Örnegi..': 'Wall / gabion example',
    'Cam Altinda Kus Desenli Kumasli': 'Fabric with bird pattern under glass',
    'Alçı Patine ve Kil': 'Plaster patina and clay',
    'Alttan Beslemeli': 'Bottom-fed',
    'Yandan Beslemeli': 'Side-fed',
    'ST.DENIS Yandan Beslemeli': 'ST.DENIS, side-fed',
    'dişi döküm Önden ve üstten beslemeli 138x43cm ön': 'Female cast, front- and top-fed, front 138x43cm',
    'Dişi Emaye Kaplama': 'Female enamel coating',
    'Dişi Sarı Metal': 'Female, yellow metal',
    'Sarı Metal': 'Yellow metal',
    'Sarı Metal+Ahşap': 'Yellow metal and wood',
    'Bakır ve Sarı Metal': 'Copper and yellow metal',
    'Bakır İşlemeli': 'Copper inlay',
    'Marmara Mermeri ve Paslanmaz Çelik': 'Marmara marble and stainless steel',
    'Marmara Mermeri+Trakas Ahşap': 'Marmara marble and Thrace wood',
    'Traverten+Mermer+Onyx Taşı': 'Travertine, marble and onyx',
    'Granit Çakıl Taşı ve Metal': 'Granite pebbles and metal',
    'Çiçek Toplari ve Kaidesi Mermer': 'Flower balls and pedestal in marble',
    'Çiçek Dallari Metal': 'Flower branches in metal',
    'Ön Tarafi Ayı ve Köpek Başı': 'Front shows a bear and a dog head',
    'Arkası Kaplan Yavrulari Motifli': 'Back with tiger cub motifs',
    'Diger Yüzünde Semazen Heykeli': 'Whirling dervish sculpture on the other side',
    'Içi Döküm': 'Cast interior',
    'Iç Zemin Tuğla': 'Brick interior floor',
    'Iç Zeminler Yeşil Çuha Kaplı': 'Interior floors covered with green felt',
    'GAT SURSEIN yapımı Içi Sivama Tuğla': 'Made by GAT SURSEIN, plastered brick interior',
    'Çelik Aksam': 'Steel fittings',
    'Çelik Fermuar': 'Steel zip',
    'Deri ve Demir Aksam': 'Leather and iron fittings',
    'Demir ve Hasır Örme': 'Iron and wicker',
    'Çerçeve Demir': 'Iron frame',
    'Sırt Kısmı Kadife Kaplı': 'Velvet-covered back',
    'Açılır Camli Kapak': 'Opening glass lid',
    'Ortasi Cam': 'Glass center',
    'Ortasi Camli': 'Glass center',
    'Kapıları Açılıyor': 'Doors open',
    'Damperi Kalkıyor': 'Tipping bed',
    'Freni Var': 'With brake',
    'Bağlama Kemeri var': 'Includes tie-down strap',
    'Metal Bagcik': 'Metal strap',
    'Alt Kisim 2 gözlü Raf': 'Lower part: shelf with 2 compartments',
    'Altta İki Raf': 'Two shelves below',
    'Dört Köşesi Çekmeceli': 'Drawers at the four corners',
    'Çift Göz Tek Kapaklı': 'Double compartment, single lid',
    'Doğal Ağaç Gövdesi': 'Natural tree trunk',
    'Doğal Taş Kaidesiyle Birlikte 150x72x63cm': 'With natural stone pedestal 150x72x63cm',
    'Dogaltas Kaidesiyle Birlikte 131x74x41cm': 'With natural stone pedestal 131x74x41cm',
    'Dogaltas Kaidesiyle Birlikte 90x52x165cm': 'With natural stone pedestal 90x52x165cm',
    'Kaidesiyle Tek Parça': 'Single piece with pedestal',
    'Kaidesiyle İki Parça': 'Two pieces with pedestal',
    'Ayak Kısmı Taş': 'Stone base',
    'Ayakları Taş': 'Stone legs',
    'Ayaklar Granit Taşı': 'Granite legs',
    '4 parça Küfeki Taşı': '4 pieces, Küfeki stone',
    '(4 parça) Küfeki Taşı': '(4 pieces) Küfeki stone',
    'Küfeki Taşı': 'Küfeki stone',
    'Eski Dibek Taşı': 'Old stone mortar',
    'Okaliptus Ağacı': 'Eucalyptus wood',
    'Midye Fosilli Taş': 'Mussel-fossil stone',
    'Granit Taşından': 'Made of granite',
    'Çakiltasi Granit': 'Pebble granite',
    'Çakıl Granit Taşı': 'Pebble granite',
    'Granit Çakıl Taşı': 'Granite pebble stone',
    'Taş Traverten': 'Travertine stone',
    'Delikli Traverten Taşı': 'Perforated travertine',
    'Tek Parça Yeşil Onyx Taşı': 'Single-piece green onyx',
    'Açık Pembe Onyx Taşı': 'Light pink onyx',
    'Pembe Granit-İthal': 'Pink granite (imported)',
    'Tekerlekli Kantar': 'Steelyard scale on wheels',
    'Çini Şekerlik': 'Tile-work sugar bowl',
    'Kesme Cam Tepsi': 'Cut glass tray',
    'Mumluk': 'Candle holder',
    'Kömür Sobası': 'Coal stove',
    'Burgu Heykeli': 'Spiral sculpture',
    'Ahşap Yeldeğirmeni': 'Wooden windmill',
    'Kartal Başı Rölyefi': 'Eagle head relief',
    'Kartal Başı Rölyefi(boyanmamış)': 'Eagle head relief (unpainted)',
    'Kartal Başı Rölyefi(boyanmış)': 'Eagle head relief (painted)',
    'Köpek Başı Rölyefi(boyanmamış)': 'Dog head relief (unpainted)',
    'Köpek Başı Rölyefi(boyanmış)': 'Dog head relief (painted)',
    'Rölyefi (boyanmamış)': 'Relief (unpainted)',
    '(boyanmış)': '(painted)',
    'Soyut Heykel(yandan görünüm)': 'Abstract sculpture (side view)',
    'Balık Tutan Çocuk': 'Boy fishing',
    'Nü Kadın Heykeli': 'Nude woman sculpture',
    'Mermer Heykel 140x90x20cm': 'Marble sculpture 140x90x20cm',
    'Kuyu Ağzı ve Yalak Çiçeklik-Saksı Toplu Görünüm': 'Well heads and trough planters, group view',
    'Marmara Mermeri': 'Marmara marble',
    'Afyon Beyaz Mermeri': 'Afyon white marble',
    'Afyon Mermeri': 'Afyon marble',
    'Angel Mermeri': 'Angel marble',
    'Elazig Visne Mermeri': 'Elazığ cherry marble',
    'Vize Pembesi Mermer': 'Vize pink marble',
    'Emperador Light Mermeri': 'Emperador Light marble',
    'Yeşil Mermer': 'Green marble',
    'Kırmızı Onyx Taşı': 'Red onyx',
    'Kırmızı Onyx': 'Red onyx',
    'Kırmızı Onix Taş': 'Red onyx',
    'Kırmızı Onyx Kayaç': 'Red onyx rock',
    'Soldaki Kırmızı Onyx Kayaç': 'Left: red onyx rock',
    'sağdaki Bal Onyx Kayaç': 'Right: honey onyx rock',
    'Bal Onyx Taşı': 'Honey onyx',
    'Bal Onyx': 'Honey onyx',
    'Bal Onyx Kayaç': 'Honey onyx rock',
    'Bal Onyx Mermer': 'Honey onyx marble',
    'Onyx Taşı': 'Onyx',
    'Traverten Taşı': 'Travertine',
    'Traverten Taş̧i': 'Travertine',
    'Bazalt Taşı': 'Basalt',
    'Granit Taşı': 'Granite',
    'Kayrak Taşı': 'Slate',
    'Kum Taşı': 'Sandstone',
    'Kumtaşı': 'Sandstone',
    'Serpantin Taşı': 'Serpentine',
    'Paspala Taşı': 'Colorful marble (paspala)',
    'Dere Çakılı': 'Creek pebbles',
    'Ağaç Fosili Taşı': 'Petrified wood',
    'Agça Fosili Taşı': 'Petrified wood',
    'Ağça Fosili Taşı': 'Petrified wood',
    'Ağaça Fosili Taşı': 'Petrified wood',
    'AğaçHeykeli': 'Tree sculpture',
    'Yassı Gri': 'Flat grey',
    'Bombeli Ahşap': 'Curved wood',
    'Ahşap Desen': 'Wood pattern',
    'Ahşap ve Deri': 'Wood and leather',
    'Doğaçlama': 'Improvised',
    'Dogaçlama': 'Improvised',
    'Çıpa Tirnaklari Arasi Genislik 144cm': 'Width between anchor flukes 144 cm',
    'Tırnaklar Arası Genişlik 140cm': 'Width between flukes 140 cm',
    'Tekinin Kalınlığı 38cm': 'Thickness of each: 38 cm',
    'Yağlı Boya Tablo': 'Oil painting',
    'Çok Sanatçı': '',
}
UNIT = [(r'\bcm\b', 'cm'), (r'\bkg\b', 'kg')]
FOLD = str.maketrans('ıİşŞğĞüÜöÖçÇ', 'iIsSgGuUoOcC')


def tr_phrase(t):
    t = t.strip()
    if t in FIX:
        return FIX[t]
    # "Marmara Mermeri" gibi kalıplar sözlük + yedek
    m = re.match(r'^(.*\S)\s+yapımı\.?$', t)
    if m and not re.search(r'\d{3,}x', t):
        return 'Made in ' + m.group(1) if re.match(r'^(England|ALMANYA|Alman|Stradella)', m.group(1)) else 'Made by ' + m.group(1)
    if t.startswith('Kaidesi '):
        rest = FIX.get(t[len('Kaidesi '):]) or tr_words(t[len('Kaidesi '):])
        return 'Pedestal: ' + rest.lower() if rest else t
    return tr_words(t)


def tr_words(t):
    out = []
    parts = re.split(r'(\s+|[,()+]|(?<=\d)(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=[a-zçğıöşü])(?=\d))', t)
    for p in parts:
        if not p or p.isspace():
            out.append(p)
            continue
        k = p.lower()
        k2 = k.translate(FOLD)
        if re.match(r'^[\d.,xX×\-/]+$', p) or p in '(),+':
            out.append(p)
        elif k in W:
            out.append(W[k])
        elif k2 in W:
            out.append(W[k2])
        else:
            m = re.match(r'^(\d[\d.,xX×]*)(cm|kg|m|mm)$', p)
            out.append(p if m else p)
    s = ''.join(out)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def main():
    rows = [r for r in csv.DictReader((ROOT / 'data' / 'urunler.csv').open(encoding='utf-8-sig'))]
    toks = set()
    for r in rows:
        for t in r['detay'].split(','):
            t = t.strip()
            if t:
                toks.add(t)
    pure = re.compile(r'^[\d\s.,xX×\-+/*()~=çmkgcMKG]*$')
    out = {}
    for t in sorted(toks):
        if pure.match(t):
            continue
        out[t] = tr_phrase(t)
    ov = ROOT / 'data' / 'en_tokens_override.json'
    if ov.exists():
        out.update(json.loads(ov.read_text(encoding='utf-8')))
    (ROOT / 'data' / 'en_tokens.json').write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
    print(len(out), 'parça çevrildi')


if __name__ == '__main__':
    main()
