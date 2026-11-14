(() => {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-navigation');
  if (!header || !toggle || !nav) return;

  header.dataset.menuReady = '';
  toggle.hidden = false;
  const closeMenu = () => {
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  };
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  header.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) {
      closeMenu();
      toggle.focus();
    }
  });
  const links = [...nav.querySelectorAll('[data-section-link]')];
  const setActive = id => {
    for (const link of links) {
      if (link.dataset.sectionLink === id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  };
  nav.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link) {
      setActive(link.dataset.sectionLink);
      closeMenu();
    }
  });
  const sections = [...document.querySelectorAll('[data-section]')];
  let pending = false;
  const updateActive = () => {
    pending = false;
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= 135) current = section;
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
      current = sections[sections.length - 1];
    }
    if (current) setActive(current.id);
  };
  if (sections.length) {
    window.addEventListener('scroll', () => {
      if (!pending) {
        pending = true;
        requestAnimationFrame(updateActive);
      }
    }, { passive: true });
    window.addEventListener('hashchange', updateActive);
    updateActive();
  }
})();
