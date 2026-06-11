// Shared site header: inject the partial, set the active link, toggle the
// scroll border, and drive the mobile hamburger dropdown. No dependencies.
//
// Note: fetch('/header.html') requires the page to be served over HTTP
// (make website / python http.server / Vercel). Opening pages via file://
// is unsupported by design.
(function () {
  function init(hdr) {
    if (!hdr) return;

    // Active nav link by pathname (/docs and /docs/* -> "docs").
    var section = location.pathname.indexOf('/docs') === 0 ? 'docs' : '';
    if (section) {
      hdr.querySelectorAll('[data-nav="' + section + '"]').forEach(function (a) {
        a.classList.add('active');
      });
    }

    // Header border on scroll.
    var onScroll = function () { hdr.classList.toggle('scrolled', window.scrollY > 10); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });

    // Mobile hamburger dropdown.
    var toggle = hdr.querySelector('.nav-toggle');
    var menu = hdr.querySelector('.nav-menu');
    if (toggle && menu) {
      var setOpen = function (open) {
        hdr.classList.toggle('menu-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      };
      toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        setOpen(!hdr.classList.contains('menu-open'));
      });
      menu.addEventListener('click', function (e) {
        if (e.target.closest('a')) setOpen(false);
      });
      document.addEventListener('click', function (e) {
        if (hdr.classList.contains('menu-open') && !hdr.contains(e.target)) setOpen(false);
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && hdr.classList.contains('menu-open')) {
          setOpen(false);
          toggle.focus();
        }
      });
    }
  }

  function mount() {
    var slot = document.getElementById('site-header');
    if (!slot) return;
    fetch('/header.html')
      .then(function (r) { return r.text(); })
      .then(function (html) {
        slot.outerHTML = html;
        init(document.getElementById('hdr'));
      })
      .catch(function () { /* served over http only; file:// is unsupported by design */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
