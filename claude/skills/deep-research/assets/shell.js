/* shell.js — wires the A-bar: chapter index select, font menu, size menu.
   Persists font + size in localStorage; every storage access is try/catch
   wrapped since file:// and locked-down browsers can throw. */
(function () {
	var FONTS = [
		["Literata", "Literata:opsz,wght@7..72,400;7..72,600"],
		["Source Serif 4", "Source+Serif+4:opsz,wght@8..60,400;8..60,600"],
		["Newsreader", "Newsreader:opsz,wght@6..72,400;6..72,600"],
		["Crimson Pro", "Crimson+Pro:wght@400;600"],
		["EB Garamond", "EB+Garamond:wght@400;600"],
		["Merriweather", "Merriweather:wght@400;700"],
		["Lora", "Lora:wght@400;600"],
		["Libre Baskerville", "Libre+Baskerville:wght@400;700"],
		["Atkinson Hyperlegible", "Atkinson+Hyperlegible:wght@400;700"],
		["Inter", "Inter:wght@400;600"],
		["IBM Plex Sans", "IBM+Plex+Sans:wght@400;600"],
		["Charter", null]
	];
	var root = document.documentElement;
	var store = {
		get: function (k) {
			try { return localStorage.getItem(k); } catch (e) { return null; }
		},
		set: function (k, v) {
			try { localStorage.setItem(k, v); } catch (e) {}
		}
	};

	function loadFont(name) {
		var f = null;
		for (var i = 0; i < FONTS.length; i++) {
			if (FONTS[i][0] === name) { f = FONTS[i]; break; }
		}
		if (f && f[1] && !document.querySelector('link[data-font="' + name + '"]')) {
			var l = document.createElement("link");
			l.rel = "stylesheet";
			l.dataset.font = name;
			l.href = "https://fonts.googleapis.com/css2?family=" + f[1] + "&display=swap";
			document.head.appendChild(l);
		}
		root.style.setProperty("--font-body", '"' + name + '", Charter, Georgia, serif');
		store.set("font", name);
	}

	function setSize(s) {
		root.dataset.size = s;
		store.set("size", s);
	}

	document.querySelectorAll("[data-font-select]").forEach(function (s) {
		s.onchange = function (e) { loadFont(e.target.value); };
	});
	document.querySelectorAll("[data-size-select]").forEach(function (s) {
		s.onchange = function (e) { setSize(e.target.value); };
	});

	var savedFont = store.get("font");
	if (savedFont) {
		loadFont(savedFont);
		document.querySelectorAll("[data-font-select]").forEach(function (s) { s.value = savedFont; });
	}
	var savedSize = store.get("size");
	if (savedSize) {
		setSize(savedSize);
		document.querySelectorAll("[data-size-select]").forEach(function (s) { s.value = savedSize; });
	}

	document.querySelectorAll("[data-index]").forEach(function (sel) {
		var current = sel.dataset.current;
		var chapters = window.COURSE_INDEX || [];
		var frag = document.createDocumentFragment();
		chapters.forEach(function (c) {
			var o = document.createElement("option");
			o.value = c.href;
			o.textContent = c.label;
			if (c.id === current) o.selected = true;
			frag.appendChild(o);
		});
		sel.insertBefore(frag, sel.firstChild);
		sel.onchange = function (e) {
			if (e.target.value) location.href = e.target.value;
		};
	});
})();
