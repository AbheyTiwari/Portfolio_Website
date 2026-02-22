/* ============================================================
   ABHEY TIWARI PORTFOLIO — script.js
   Handles: magnetic cursor, mobile nav, AI chat modal
   ============================================================ */

// ── MOBILE NAV ───────────────────────────────────────────────
const mobileToggle = document.getElementById('mobileToggle');
const navMobile    = document.getElementById('navMobile');

function closeMobile() {
    navMobile?.classList.remove('open');
    if (mobileToggle) mobileToggle.textContent = '☰';
}

mobileToggle?.addEventListener('click', () => {
    const isOpen = navMobile.classList.toggle('open');
    mobileToggle.textContent = isOpen ? '✕' : '☰';
});


// ── AI CHAT MODAL ────────────────────────────────────────────
const API_URL = 'http://localhost:8000/chat'; // ← change to your deployed URL

const fab      = document.getElementById('aiFab');
const modal    = document.getElementById('aiModal');
const overlay  = document.getElementById('aiOverlay');
const closeBtn = document.getElementById('aiClose');
const form     = document.getElementById('aiForm');
const input    = document.getElementById('aiInput');
const messages = document.getElementById('aiMessages');

function openModal() {
    modal?.classList.add('open');
    overlay?.classList.add('open');
    input?.focus();
}

function closeModal() {
    modal?.classList.remove('open');
    overlay?.classList.remove('open');
}

fab?.addEventListener('click', openModal);
closeBtn?.addEventListener('click', closeModal);
overlay?.addEventListener('click', closeModal);

// Close on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = `ai-msg ${role}`;
    div.innerHTML = `<div class="msg-bubble">${text}</div>`;
    messages?.appendChild(div);
    if (messages) messages.scrollTop = messages.scrollHeight;
}

function addTyping() {
    const div = document.createElement('div');
    div.className = 'ai-msg assistant typing-indicator';
    div.id = 'typingDot';
    div.innerHTML = '<div class="msg-bubble"><span></span><span></span><span></span></div>';
    messages?.appendChild(div);
    if (messages) messages.scrollTop = messages.scrollHeight;
}

function removeTyping() {
    document.getElementById('typingDot')?.remove();
}

form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input?.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    if (input) input.value = '';
    addTyping();

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        removeTyping();
        addMessage(data.reply, 'assistant');

    } catch (err) {
        removeTyping();
        addMessage(
            'Backend not connected. Start the server with:<br><code>uvicorn main:app --reload --port 8000</code>',
            'assistant'
        );
    }
});


// ── SMOOTH SCROLL FOR NAV LINKS ──────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href   = this.getAttribute('href');
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            const offset = parseInt(getComputedStyle(document.documentElement)
                .getPropertyValue('--nav-h')) || 60;
            const top = target.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    });
});

/* ============================================================
   HOLOGRAPHIC CHROMATIC ABERRATION CURSOR
   Inspired by: iridescent topographic contour forms with RGB split edges
   Technique: Canvas 2D with layered noise fields, RGB channel offset,
              drip physics, and contour line rendering
   ============================================================ */

(function () {
    'use strict';

    // ── SETUP CANVAS ─────────────────────────────────────────
    const canvas = document.createElement('canvas');
    canvas.id = 'cursor-canvas';
    canvas.style.cssText = `
        position:fixed;top:0;left:0;
        width:100vw;height:100vh;
        pointer-events:none;z-index:99999;
    `;
    document.body.appendChild(canvas);

    const label = document.createElement('div');
    label.id = 'cursor-label';
    document.body.appendChild(label);

    const ctx = canvas.getContext('2d');
    let W, H;

    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // ── STATE ─────────────────────────────────────────────────
    let mx = -300, my = -300;           // raw mouse
    let cx = -300, cy = -300;           // cursor center (lagged)
    let vx = 0,    vy = 0;             // velocity for drip
    let hoverType = 'default';          // 'default' | 'btn' | 'text' | 'img'
    let t = 0;                          // time

    // Drip particles
    const drips = [];
    const MAX_DRIPS = 4;

    // Trail history
    const trail = [];
    const TRAIL_LEN = 8;

    // ── MOUSE TRACKING ────────────────────────────────────────
    document.addEventListener('mousemove', e => {
        mx = e.clientX;
        my = e.clientY;
        classifyTarget(e.target);
    });

    document.addEventListener('mouseleave', () => { mx = -300; my = -300; });

    // ── CLASSIFY HOVER TARGET ─────────────────────────────────
    function classifyTarget(el) {
        let node = el;
        let type = 'default';
        while (node && node !== document.body) {
            const tag = node.tagName?.toLowerCase();
            if (['a','button'].includes(tag) ||
                node.classList?.contains('btn-raw') ||
                node.classList?.contains('project-cta') ||
                node.classList?.contains('ai-fab')) {
                type = 'btn'; break;
            }
            if (tag === 'img' ||
                node.classList?.contains('project-img-wrap') ||
                node.classList?.contains('img-placeholder')) {
                type = 'img'; break;
            }
            if (['h1','h2','h3','input','textarea'].includes(tag)) {
                type = 'text'; break;
            }
            node = node.parentElement;
        }
        hoverType = type;

        // Label
        if (type === 'btn' && el.textContent) {
            label.textContent = el.closest('a,button')?.textContent?.trim().slice(0, 20) || 'OPEN';
            label.classList.add('visible');
        } else {
            label.classList.remove('visible');
        }
    }

    // ── PERLIN-LIKE NOISE (simple smooth noise) ───────────────
    function fade(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
    function lerp(a, b, t) { return a + t * (b - a); }

    // Simple value noise
    const perm = new Uint8Array(512);
    for (let i = 0; i < 256; i++) perm[i] = i;
    for (let i = 255; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [perm[i], perm[j]] = [perm[j], perm[i]];
    }
    for (let i = 0; i < 256; i++) perm[256 + i] = perm[i];

    function grad(hash, x, y) {
        const h = hash & 3;
        const u = h < 2 ? x : y;
        const v = h < 2 ? y : x;
        return ((h & 1) ? -u : u) + ((h & 2) ? -v : v);
    }

    function noise(x, y) {
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;
        x -= Math.floor(x);
        y -= Math.floor(y);
        const u = fade(x), v = fade(y);
        const a = perm[X] + Y, b = perm[X + 1] + Y;
        return lerp(
            lerp(grad(perm[a],   x,   y), grad(perm[b],   x-1, y),   u),
            lerp(grad(perm[a+1], x,   y-1), grad(perm[b+1], x-1, y-1), u),
            v
        ) * 0.5 + 0.5;
    }

    // ── CURSOR SIZE BY STATE ──────────────────────────────────
    function targetSize() {
        if (hoverType === 'btn')  return 14;
        if (hoverType === 'img')  return 16;
        if (hoverType === 'text') return 6;
        return 9;
    }

    let cursorSize = 9;

    // ── DRIP SPAWNER ──────────────────────────────────────────
    function spawnDrip() {
        if (drips.length >= MAX_DRIPS) return;
        const angle = Math.random() * Math.PI * 2;
        const r = cursorSize * 0.4;
        drips.push({
            x: cx + Math.cos(angle) * r,
            y: cy + Math.sin(angle) * r,
            vx: (Math.random() - 0.5) * 1,
            vy: Math.random() * 1.5 + 0.5,
            life: 1,
            size: Math.random() * 3 + 1.5,
            hue: Math.random() * 360,
        });
    }

    // ── HOLOGRAPHIC COLOR ─────────────────────────────────────
    // Returns an iridescent rainbow color based on angle + noise + time
    function holoColor(angle, nx, alpha = 1) {
        const hue = ((angle / (Math.PI * 2)) * 360 + nx * 180 + t * 40) % 360;
        return `hsla(${hue}, 100%, 65%, ${alpha})`;
    }

    // ── DRAW THE HOLOGRAPHIC CURSOR ───────────────────────────
    function drawHoloCursor(x, y, size, time) {
        const RINGS     = 8;         // fewer rings for small size
        const RGB_SPLIT = 1.5;       // subtle aberration at small scale

        // For each RGB channel, draw slightly offset (chromatic aberration)
        const channels = [
            { dx:  RGB_SPLIT, dy: -RGB_SPLIT * 0.5, color: 'rgba(255,0,100,', blend: 'screen' },
            { dx:  0,         dy:  0,                color: 'rgba(0,255,180,', blend: 'screen' },
            { dx: -RGB_SPLIT, dy:  RGB_SPLIT * 0.5,  color: 'rgba(100,100,255,', blend: 'screen' },
        ];

        channels.forEach(({ dx, dy, color, blend }) => {
            ctx.save();
            ctx.globalCompositeOperation = blend;

            // Draw topographic contour rings
            for (let r = RINGS; r >= 1; r--) {
                const frac    = r / RINGS;
                const radius  = size * frac;
                const warp    = size * 0.35 * (1 - frac);  // warp amount
                const pts     = 64;
                const alpha   = 0.06 + frac * 0.08;

                ctx.beginPath();
                for (let i = 0; i <= pts; i++) {
                    const angle = (i / pts) * Math.PI * 2;
                    // Noise-based distortion — gives organic topographic shape
                    const nx  = noise(
                        Math.cos(angle) * 1.5 + x * 0.005 + time * 0.3,
                        Math.sin(angle) * 1.5 + y * 0.005 + time * 0.2
                    );
                    const warpR = radius + (nx - 0.5) * warp * 2;
                    const px    = x + dx + Math.cos(angle) * warpR;
                    const py    = y + dy + Math.sin(angle) * warpR;
                    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
                }
                ctx.closePath();

                // Iridescent fill — color shifts per ring
                const hue = ((frac * 360) + time * 60 + r * 20) % 360;
                ctx.fillStyle = `hsla(${hue}, 100%, 60%, ${alpha})`;
                ctx.fill();

                // Contour line stroke
                ctx.strokeStyle = color + (alpha * 2.5) + ')';
                ctx.lineWidth   = 0.6;
                ctx.stroke();
            }

            // Edge glow — bright outline with chromatic offset
            const edgePts = 80;
            ctx.beginPath();
            for (let i = 0; i <= edgePts; i++) {
                const angle = (i / edgePts) * Math.PI * 2;
                const nx    = noise(
                    Math.cos(angle) * 2 + x * 0.005 + time * 0.4,
                    Math.sin(angle) * 2 + y * 0.005 + time * 0.3
                );
                const warpR = size + (nx - 0.5) * size * 0.4;
                const px    = x + dx + Math.cos(angle) * warpR;
                const py    = y + dy + Math.sin(angle) * warpR;
                i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.strokeStyle = color + '0.9)';
            ctx.lineWidth   = 1.5;
            ctx.stroke();

            ctx.restore();
        });

        // Center bright core
        const core = ctx.createRadialGradient(x, y, 0, x, y, size * 0.25);
        core.addColorStop(0,   'rgba(255,255,255,0.7)');
        core.addColorStop(0.4, 'rgba(200,255,240,0.2)');
        core.addColorStop(1,   'rgba(255,255,255,0)');
        ctx.save();
        ctx.globalCompositeOperation = 'screen';
        ctx.beginPath();
        ctx.arc(x, y, size * 0.25, 0, Math.PI * 2);
        ctx.fillStyle = core;
        ctx.fill();
        ctx.restore();
    }

    // ── DRAW TRAIL ────────────────────────────────────────────
    function drawTrail() {
        for (let i = 0; i < trail.length; i++) {
            const pt    = trail[i];
            const alpha = (i / trail.length) * 0.35;
            const size  = cursorSize * (i / trail.length) * 0.5;
            if (size < 2) continue;

            ctx.save();
            ctx.globalCompositeOperation = 'screen';
            const hue = (pt.hue + t * 30) % 360;
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, size, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${hue}, 100%, 65%, ${alpha})`;
            ctx.fill();
            ctx.restore();
        }
    }

    // ── DRAW DRIPS ────────────────────────────────────────────
    function drawDrips() {
        for (let i = drips.length - 1; i >= 0; i--) {
            const d = drips[i];
            d.x  += d.vx;
            d.y  += d.vy;
            d.vy += 0.12;  // gravity
            d.vx *= 0.98;
            d.life -= 0.025;

            if (d.life <= 0) { drips.splice(i, 1); continue; }

            ctx.save();
            ctx.globalCompositeOperation = 'screen';
            const hue = (d.hue + t * 40) % 360;
            const r   = d.size * d.life;
            const grad = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, r);
            grad.addColorStop(0,   `hsla(${hue}, 100%, 75%, ${d.life * 0.8})`);
            grad.addColorStop(0.5, `hsla(${(hue + 60) % 360}, 100%, 60%, ${d.life * 0.4})`);
            grad.addColorStop(1,   `hsla(${(hue + 120) % 360}, 100%, 50%, 0)`);
            ctx.beginPath();
            ctx.arc(d.x, d.y, r, 0, Math.PI * 2);
            ctx.fillStyle = grad;
            ctx.fill();
            ctx.restore();
        }
    }

    // ── MAIN LOOP ─────────────────────────────────────────────
    let lastDrip = 0;

    function loop(timestamp) {
        t = timestamp * 0.001;

        ctx.clearRect(0, 0, W, H);

        // Lag cursor toward mouse
        cx += (mx - cx) * 0.12;
        cy += (my - cy) * 0.12;

        // Lerp size
        cursorSize += (targetSize() - cursorSize) * 0.1;

        // Trail
        if (mx > -200) {
            trail.push({ x: cx, y: cy, hue: (t * 60) % 360 });
            if (trail.length > TRAIL_LEN) trail.shift();
        }

        // Occasional drips when moving fast
        const speed = Math.hypot(mx - cx, my - cy);
        if (speed > 8 && timestamp - lastDrip > 120) {
            spawnDrip();
            lastDrip = timestamp;
        }

        // Draw
        drawTrail();
        drawDrips();
        if (mx > -200) drawHoloCursor(cx, cy, cursorSize, t);

        // Move label
        if (label.classList.contains('visible')) {
            label.style.transform = `translate(calc(${cx}px - 50%), calc(${cy}px + 28px))`;
        }

        requestAnimationFrame(loop);
    }

    requestAnimationFrame(loop);

    // ── CLICK BURST ───────────────────────────────────────────
    document.addEventListener('click', () => {
        for (let i = 0; i < 5; i++) spawnDrip();
    });

})();