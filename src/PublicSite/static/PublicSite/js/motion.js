/* CSSA Motion — list reveals, count-ups, navbar state, and loop budgeting.
 *
 * Loaded with `defer`, so the DOM is parsed by the time this runs.
 *
 * There is deliberately no scroll listener and no scrollY arithmetic in this
 * file. Scroll position is read by IntersectionObserver (navbar state, loop
 * budgeting) and by the CSS scroll timeline in motion.css (progress bar), both
 * of which the browser batches off the main thread.
 *
 * Nothing here is required for the page to be readable: the reveal styles in
 * motion.css only apply once we add `cssa-motion` to <html>, which we skip when
 * the visitor has asked for reduced motion or the browser has no observer.
 */
(function () {
    'use strict';

    var root = document.documentElement;
    var prefersReducedMotion = window.matchMedia
        ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
        : false;
    var hasObserver = 'IntersectionObserver' in window;
    // Where CSS can scrub the reveal against the scroll itself, it does the job
    // better than we can and this file stays out of the way entirely.
    var hasViewTimeline = !!(window.CSS && CSS.supports &&
        CSS.supports('animation-timeline', 'view()'));
    var canAnimate = !prefersReducedMotion;
    var canReveal = canAnimate && hasObserver && !hasViewTimeline;

    var REVEAL_STEP = 80;   // ms between staggered siblings
    var REVEAL_MAX_STEPS = 5;    // cap the total stagger at ~400ms
    var TICKER_SPEED = 70;   // px per second, constant whatever the content

    function each(list, fn) {
        Array.prototype.forEach.call(list, fn);
    }

    function setClass(el, name, on) {
        if (on) {
            el.classList.add(name);
        } else {
            el.classList.remove(name);
        }
    }

    /* --------------------------------------------------------- 列表揭示 */

    function assignStagger() {
        each(document.querySelectorAll('[data-reveal-group]'), function (group) {
            var step = parseInt(group.getAttribute('data-reveal-step'), 10) || REVEAL_STEP;
            each(group.querySelectorAll('[data-reveal]'), function (item, index) {
                var delay = Math.min(index, REVEAL_MAX_STEPS) * step;
                item.style.setProperty('--cssa-reveal-delay', delay + 'ms');
            });
        });
    }

    function setUpReveals() {
        var targets = document.querySelectorAll('[data-reveal]');
        if (!targets.length || !canReveal) {
            return;
        }

        root.classList.add('cssa-motion');
        assignStagger();

        var observer = new IntersectionObserver(function (entries) {
            each(entries, function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                entry.target.classList.add('is-revealed');
                observer.unobserve(entry.target);
            });
        }, {
            threshold: 0,
            rootMargin: '0px 0px -10% 0px'
        });

        each(targets, function (el) {
            observer.observe(el);
        });
    }

    /* --------------------------------------------------------- 数字滚动 */

    function countUp(el) {
        var target = parseFloat(el.getAttribute('data-countup'));
        if (isNaN(target)) {
            return;
        }

        var from = parseFloat(el.getAttribute('data-countup-from'));
        if (isNaN(from)) {
            from = 0;
        }

        var suffix = el.getAttribute('data-countup-suffix') || '';
        var duration = parseInt(el.getAttribute('data-countup-duration'), 10) || 1200;
        var startedAt = null;

        function frame(now) {
            if (startedAt === null) {
                startedAt = now;
            }
            var progress = Math.min((now - startedAt) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(from + (target - from) * eased) + suffix;
            if (progress < 1) {
                window.requestAnimationFrame(frame);
            }
        }

        el.textContent = from + suffix;
        window.requestAnimationFrame(frame);
    }

    function setUpCountUps() {
        var targets = document.querySelectorAll('[data-countup]');
        if (!targets.length || !canAnimate || !hasObserver) {
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            each(entries, function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                observer.unobserve(entry.target);
                countUp(entry.target);
            });
        }, { threshold: 0.4 });

        each(targets, function (el) {
            observer.observe(el);
        });
    }

    /* ----------------------------------------------------------- 导航栏 */

    function setUpNavbar() {
        var navbar = document.querySelector('.cssa-navbar');
        var sentinel = document.querySelector('.cssa-scroll-sentinel');

        if (!navbar || !sentinel || !hasObserver) {
            return;
        }

        // The sentinel sits in the top 28px of the document. Once it is out of
        // view the page has left the top — no scroll handler needed.
        new IntersectionObserver(function (entries) {
            each(entries, function (entry) {
                setClass(navbar, 'is-scrolled', !entry.isIntersecting);
            });
        }, { threshold: 0 }).observe(sentinel);
    }

    /* ------------------------------------------------- 常驻动效预算控制 */

    function setUpLoopBudget() {
        var loops = document.querySelectorAll('[data-loop]');
        if (!loops.length) {
            return;
        }

        // A loop nobody can see is pure battery cost. Park it offscreen...
        if (hasObserver) {
            var observer = new IntersectionObserver(function (entries) {
                each(entries, function (entry) {
                    setClass(entry.target, 'is-paused', !entry.isIntersecting);
                });
            }, { rootMargin: '140px 0px' });

            each(loops, function (el) {
                observer.observe(el);
            });
        }

        // ...and park all of them while the tab is in the background.
        function syncVisibility() {
            setClass(root, 'is-tab-hidden', document.hidden);
        }

        document.addEventListener('visibilitychange', syncVisibility);
        syncVisibility();
    }

    /* --------------------------------------------------------- 跑马灯 */

    function setUpTicker() {
        var track = document.querySelector('[data-ticker-track]');
        if (!track || !canAnimate) {
            return;
        }

        var group = track.querySelector('.cssa-ticker__group');
        if (!group) {
            return;
        }

        // Repeat the list until it comfortably overflows the viewport, then
        // mirror the whole run so the -50% loop meets itself seamlessly.
        var guard = 0;
        while (track.scrollWidth < window.innerWidth * 1.5 && guard < 16) {
            track.appendChild(group.cloneNode(true));
            guard += 1;
        }

        var loopWidth = track.scrollWidth;
        if (loopWidth <= 0) {
            return;
        }

        var mirror = document.createDocumentFragment();
        each(track.children, function (node) {
            mirror.appendChild(node.cloneNode(true));
        });
        track.appendChild(mirror);

        track.style.setProperty(
            '--cssa-ticker-duration',
            Math.max(loopWidth / TICKER_SPEED, 18).toFixed(1) + 's'
        );
        track.classList.add('is-running');
    }

    setUpReveals();
    setUpCountUps();
    setUpNavbar();
    setUpLoopBudget();

    // Wait for webfonts and images so the ticker measures its real width.
    window.addEventListener('load', setUpTicker);
}());
