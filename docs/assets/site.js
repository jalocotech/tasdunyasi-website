/* Taş Dünyası — statik site betiği: galeri, ebat seçimi, yükleme hesabı, teklif formu, arama */
(function () {
	'use strict';
	var cfg = window.TD || {};
	var root = document.documentElement.getAttribute('data-root') || '';

	function track(name, params) {
		if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
	}
	function digits(s) { return String(s || '').replace(/\D+/g, ''); }

	// --- Mobil menü ---
	(function () {
		var btn = document.querySelector('.menu-btn'), menu = document.getElementById('menu');
		if (!btn || !menu) return;
		function set(open) {
			menu.hidden = !open;
			btn.setAttribute('aria-expanded', open ? 'true' : 'false');
			btn.setAttribute('aria-label', open ? 'Menüyü kapat' : 'Menüyü aç');
		}
		btn.addEventListener('click', function () { set(menu.hidden); });
		menu.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
		document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); } });
		window.addEventListener('resize', function () { if (window.innerWidth > 900) set(false); });
	})();

	// --- İletişim bağlantıları (config.js'ten) ---
	var wa = digits(cfg.whatsapp);
	document.querySelectorAll('[data-wa]').forEach(function (a) {
		if (!wa) { a.hidden = true; return; }
		var text = a.getAttribute('data-wa') || 'Merhaba, ürünleriniz hakkında bilgi almak istiyorum.';
		a.href = 'https://wa.me/' + wa + '?text=' + encodeURIComponent(text);
		a.target = '_blank'; a.rel = 'noopener';
		a.addEventListener('click', function () { track('whatsapp_click', { urun: a.getAttribute('data-urun') || '' }); });
	});

	// --- Görsel yüklenemezse gizle ---
	document.querySelectorAll('img[data-fallback]').forEach(function (img) {
		img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
	});

	// --- Ürün galerisi ---
	var main = document.querySelector('[data-main-img]');
	var thumbs = [].slice.call(document.querySelectorAll('[data-thumb]'));
	var cur = 0;
	function show(i) {
		if (!thumbs.length || !main) return;
		cur = (i + thumbs.length) % thumbs.length;
		main.src = thumbs[cur].getAttribute('data-thumb');
		thumbs.forEach(function (x, k) { x.setAttribute('aria-pressed', k === cur ? 'true' : 'false'); });
		var n = document.querySelector('[data-gal-i]'); if (n) n.textContent = cur + 1;
		var cp = document.querySelector('[data-gal-cap]'); if (cp) cp.textContent = thumbs[cur].getAttribute('data-cap') || '';
		thumbs[cur].scrollIntoView({ block: 'nearest', inline: 'center' });
	}
	thumbs.forEach(function (b, k) { b.addEventListener('click', function () { show(k); }); });
	var pv = document.querySelector('[data-prev]'), nx = document.querySelector('[data-next]');
	if (pv) pv.addEventListener('click', function () { show(cur - 1); });
	if (nx) nx.addEventListener('click', function () { show(cur + 1); });
	if (main && thumbs.length > 1) {
		var sx = null;
		main.parentNode.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
		main.parentNode.addEventListener('touchend', function (e) { if (sx === null) return; var d = e.changedTouches[0].clientX - sx; if (Math.abs(d) > 40) show(cur + (d < 0 ? 1 : -1)); sx = null; }, { passive: true });
	}

	// --- Ebat ve yükleme seçimi → teklif formu ---
	var state = { size: '', load: '' };
	var productName = (document.querySelector('[data-product]') || {}).getAttribute ? document.querySelector('[data-product]').getAttribute('data-product') : '';
	var formProduct = document.querySelector('[data-form-product]');
	function syncForm() {
		if (!formProduct || !productName) return;
		formProduct.value = [productName, state.size, state.load].filter(Boolean).join(' – ');
		var lbl = document.querySelector('[data-size-label]');
		if (lbl) lbl.textContent = state.size || '—';
	}
	function group(sel, key, onPick) {
		var btns = document.querySelectorAll(sel);
		btns.forEach(function (b) {
			b.addEventListener('click', function () {
				btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
				state[key] = b.getAttribute('data-value');
				if (onPick) onPick(b);
				syncForm();
			});
			if (b.getAttribute('aria-pressed') === 'true') { state[key] = b.getAttribute('data-value'); if (onPick) onPick(b); }
		});
	}
	group('[data-size]', 'size');
	group('[data-load]', 'load', function (b) {
		var bags = b.getAttribute('data-bags'), min = parseFloat(b.getAttribute('data-min')), max = parseFloat(b.getAttribute('data-max'));
		var f = function (n) { return String(n).replace('.', ','); };
		var e1 = document.querySelector('[data-load-bags]'), e2 = document.querySelector('[data-load-tons]'), e3 = document.querySelector('[data-load-value]');
		if (e1) e1.textContent = bags;
		if (e2) e2.textContent = f(min) + '–' + f(max) + ' t';
		if (e3) {
			var p = parseFloat(e3.getAttribute('data-price'));
			e3.textContent = '$' + Math.round(min * p).toLocaleString('en-US') + ' – $' + Math.round(max * p).toLocaleString('en-US');
		}
	});
	syncForm();

	// --- Teklif formu: sunucu yok; mesajı WhatsApp ya da e-posta ile gönderir ---
	var form = document.querySelector('[data-quote-form]');
	if (form) {
		var params = new URLSearchParams(window.location.search);
		if (params.get('urun') && formProduct && !formProduct.value) formProduct.value = params.get('urun');
		var msg = form.querySelector('.form-msg');
		var mail = (cfg.email || '').trim();
		var bWa = form.querySelector('[data-send="wa"]'), bMail = form.querySelector('[data-send="mail"]');
		if (bWa && !wa) bWa.hidden = true;
		if (bMail && !mail) bMail.hidden = true;
		if (!wa && !mail && msg) msg.textContent = 'Taslak: WhatsApp numarası ve e-posta adresi config.js dosyasına eklenince form çalışır. Şimdilik bizi telefonla arayabilirsiniz.';
		function compose() {
			var v = function (n) { var el = form.elements[n]; return el ? String(el.value || '').trim() : ''; };
			var lines = ['Teklif talebi', 'Ürün: ' + v('urun'), 'Miktar: ' + v('miktar'), 'Teslim yeri: ' + v('teslimat'), 'Ad soyad: ' + v('ad'), 'Firma: ' + v('firma'), 'Telefon: ' + v('telefon'), 'E-posta: ' + v('eposta')];
			if (v('mesaj')) lines.push('Not: ' + v('mesaj'));
			return lines.join('\n');
		}
		function send(kind) {
			if (!form.reportValidity()) return;
			var text = compose();
			track('generate_lead', { kanal: kind, urun: form.elements.urun ? form.elements.urun.value : '' });
			if (kind === 'wa') window.open('https://wa.me/' + wa + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
			else window.location.href = 'mailto:' + mail + '?subject=' + encodeURIComponent('Teklif talebi: ' + (form.elements.urun ? form.elements.urun.value : '')) + '&body=' + encodeURIComponent(text);
		}
		form.addEventListener('submit', function (e) { e.preventDefault(); send(wa ? 'wa' : 'mail'); });
		if (bWa) bWa.addEventListener('click', function () { send('wa'); });
		if (bMail) bMail.addEventListener('click', function () { send('mail'); });
	}

	// --- Arama (urunler sayfası): search.json üzerinde ---
	var box = document.querySelector('[data-search-results]');
	if (box) {
		var q = (new URLSearchParams(window.location.search).get('q') || '').trim();
		var input = document.querySelector('[data-search-input]');
		if (input) input.value = q;
		var fold = function (s) {
			return String(s).toLocaleLowerCase('tr').replace(/ı/g, 'i').replace(/ğ/g, 'g').replace(/ü/g, 'u').replace(/ş/g, 's').replace(/ö/g, 'o').replace(/ç/g, 'c');
		};
		if (q) {
			fetch(root + 'search.json').then(function (r) { return r.json(); }).then(function (items) {
				var words = fold(q).split(/\s+/).filter(Boolean);
				var hits = items.filter(function (it) { var h = fold(it.t + ' ' + it.c); return words.every(function (w) { return h.indexOf(w) >= 0; }); });
				var head = document.querySelector('[data-search-head]');
				if (head) head.textContent = '"' + q + '" için ' + hits.length + ' ürün';
				document.querySelectorAll('[data-hide-on-search]').forEach(function (el) { el.hidden = true; });
				box.innerHTML = '';
				hits.slice(0, 120).forEach(function (it) {
					var a = document.createElement('a'); a.className = 'card'; a.href = root + 'urun/' + it.s + '/';
					var im = document.createElement('div'); im.className = 'card-img';
					if (it.i) { var img = document.createElement('img'); img.loading = 'lazy'; img.alt = it.t; img.src = (cfg.imgBase || '') + it.i; im.appendChild(img); }
					var body = document.createElement('div'); body.className = 'card-body';
					var t = document.createElement('span'); t.className = 'card-title'; t.textContent = it.t;
					var c = document.createElement('span'); c.className = 'card-sub'; c.textContent = it.c;
					body.appendChild(t); body.appendChild(c); a.appendChild(im); a.appendChild(body); box.appendChild(a);
				});
				if (!hits.length) box.innerHTML = '<p class="note">Sonuç bulunamadı. Aradığınız ürünü bize yazın, tedarik edelim.</p>';
				track('search', { search_term: q });
			});
		}
	}

	// --- Telefon ve teklif tıklamaları ---
	document.addEventListener('click', function (e) {
		var el = e.target.closest ? e.target.closest('[data-ev]') : null;
		if (el) track(el.getAttribute('data-ev'), { urun: el.getAttribute('data-urun') || '' });
	});
})();
