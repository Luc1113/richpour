document.documentElement.classList.replace('no-js', 'js');

// Paint each section title's swash as it scrolls into view
const swashObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-painted');
            swashObserver.unobserve(entry.target);
        }
    });
}, { rootMargin: '0px 0px -15% 0px' });
document.querySelectorAll('.section-title').forEach(title => swashObserver.observe(title));

// Mobile navigation
const toggle = document.querySelector('.nav-toggle');
const nav = document.getElementById('site-nav');

function setNav(open) {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav.classList.toggle('is-open', open);
}

toggle.addEventListener('click', () => setNav(toggle.getAttribute('aria-expanded') !== 'true'));
nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setNav(false)));
document.addEventListener('keydown', e => { if (e.key === 'Escape') setNav(false); });

// Highlight the nav link for the section in the middle of the screen
const navLinks = [...document.querySelectorAll('#site-nav a[href*="#"], .menu-jump a')];
const spy = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const id = entry.target.id;
        navLinks.forEach(a => {
            const current = Boolean(id) && a.hash === `#${id}` && a.pathname === location.pathname;
            a.classList.toggle('is-current', current);
            // keep the active menu chip visible in its scrolling row
            if (current && a.closest('.menu-jump')) {
                const row = a.closest('ul');
                row.scrollTo({ left: a.offsetLeft - (row.clientWidth - a.offsetWidth) / 2, behavior: 'smooth' });
            }
        });
    });
}, { rootMargin: '-50% 0px -50% 0px' });
document.querySelectorAll('main > section[id], main > .hero, main > .menu-hero').forEach(section => spy.observe(section));

// Home: drop each dish photo onto the stack as the menu section scrolls by
const stack = document.querySelector('.stack');
if (stack) {
    const cards = [...stack.querySelectorAll('img')].slice(1);
    const feature = stack.closest('.feature');
    const track = stack.closest('.menu-body');
    const clamp = v => Math.min(1, Math.max(0, v));
    // each photo just lands on the pile at its own angle once you've scrolled to it
    const place = (card, shown) => { card.style.opacity = shown ? '1' : '0'; };
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
        cards.forEach(card => place(card, true));
    } else {
        let queued = false;
        const update = () => {
            queued = false;
            const vh = innerHeight;
            let progress;
            if (getComputedStyle(feature).position === 'sticky') {
                // pinned beside the list: build the pile while the list scrolls past
                const box = track.getBoundingClientRect();
                progress = (vh * 0.6 - box.top) / box.height;
            } else {
                // stacked layout: build it while the photo travels up the screen
                const box = feature.getBoundingClientRect();
                progress = (vh * 0.9 - box.top) / (vh * 0.65);
            }
            progress = clamp(progress) * cards.length;
            cards.forEach((card, i) => place(card, progress > i + 0.5));
        };
        const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
        addEventListener('scroll', queue, { passive: true });
        addEventListener('resize', queue);
        update();
    }
}

// Menu page: note when the section links have stuck under the nav
const jump = document.querySelector('.menu-jump');
if (jump) {
    const stickTop = parseFloat(getComputedStyle(jump).top) + 1;
    new IntersectionObserver(([entry]) => {
        jump.classList.toggle('is-stuck', entry.intersectionRatio < 1 && entry.boundingClientRect.top < stickTop + 1);
    }, { threshold: 1, rootMargin: `-${stickTop}px 0px 0px 0px` }).observe(jump);
}

// Stronger shadow once the page scrolls
const header = document.querySelector('.site-header');
const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Hero video: pausable, and held on its first frame for people who prefer less motion
const video = document.querySelector('.hero-video');
const videoToggle = document.querySelector('.video-toggle');
if (video && videoToggle) {
    const setPaused = paused => {
        paused ? video.pause() : video.play().catch(() => {});
        videoToggle.setAttribute('aria-pressed', String(paused));
        videoToggle.setAttribute('aria-label', paused ? 'Play video' : 'Pause video');
    };
    videoToggle.addEventListener('click', () => setPaused(!video.paused));
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) setPaused(true);
}

// Today's hours
const day = new Date().getDay();
const row = document.querySelector(`.hours tr[data-days="${day}"]`);
const todayHours = document.getElementById('today-hours');
if (row && todayHours) {
    row.classList.add('is-today');
    todayHours.textContent =
        `Open today ${row.querySelector('td').textContent}`;
}

// Turn the sheen as the page scrolls
if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
            document.documentElement.style.setProperty('--spin', `${window.scrollY * 0.06}deg`);
            ticking = false;
        });
    }, { passive: true });
}

document.getElementById('year').textContent = new Date().getFullYear();
