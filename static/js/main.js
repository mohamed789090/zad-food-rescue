/**
 * منصة زَادْ (ZAD) — محرك الأنيميشن والتفاعل المتقدم (GSAP + Lenis Smooth Scroll)
 * إعداد: فريق مشروع التخرج لنظم المعلومات الإدارية 2026
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. تفعيل التمرير السلس الفائق (Lenis Smooth Scrolling)
    initLenisSmoothScroll();

    // 2. تشغيل حزمة أنيميشن GSAP (Hero, Numbers CountUp, Cards Reveal)
    initGsapAnimations();

    // 3. تأثير الضوء الموجه التفاعلي للكروت (Spotlight Card Hover Effect)
    initSpotlightCards();

    // 4. نظام الإشعارات العائم الحديث (Modern Floating Toasts)
    initZadToasts();

    // 5. تفعيل أدوات التلميح (Bootstrap Tooltips)
    initBootstrapTooltips();

    // 6. نسخ كود الحجز بنقرة واحدة مع تفاعل حركي فوري
    initCodeCopy();

    // 7. حاسبة الخصم الفورية في نماذج إضافة وتعديل الوجبات
    initLiveDiscountCalculators();

    // 8. تأكيد سريع للعمليات الحساسة (مثل الإلغاء والحذف)
    initConfirmHandlers();

    // 9. زر إظهار وإخفاء كلمة المرور (Show/Hide Password)
    initPasswordToggle();

    // 10. مؤقت العد التنازلي لإغلاق عروض الفوائض (Surplus Expiry Countdown)
    initSurplusCountdownTimers();
});

/* --------------------------------------------------------------------------
   1. Lenis Smooth Scroll (التمرير السلس العصري)
   -------------------------------------------------------------------------- */
let lenis = null;

function initLenisSmoothScroll() {
    if (typeof Lenis !== "undefined") {
        lenis = new Lenis({
            duration: 1.1,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            orientation: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
            wheelMultiplier: 1.0,
            touchMultiplier: 1.5,
        });

        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);

        if (typeof ScrollTrigger !== "undefined") {
            lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.add((time) => {
                lenis.raf(time * 1000);
            });
            gsap.ticker.lagSmoothing(0);
        }
    }
}

/* --------------------------------------------------------------------------
   2. GSAP Animations Suite (الأنيميشن الشامل)
   -------------------------------------------------------------------------- */
function initGsapAnimations() {
    if (typeof gsap === "undefined") return;

    if (typeof ScrollTrigger !== "undefined") {
        gsap.registerPlugin(ScrollTrigger);
    }

    const heroTl = gsap.timeline({ defaults: { ease: "power3.out" } });

    if (document.querySelector(".hero-glass-section")) {
        heroTl.from(".hero-glass-section .badge", { opacity: 0, y: -20, duration: 0.6 })
              .from(".hero-glass-section h1", { opacity: 0, y: 30, duration: 0.8 }, "-=0.3")
              .from(".hero-glass-section p.lead", { opacity: 0, y: 20, duration: 0.7 }, "-=0.4")
              .from(".hero-stats-glass", { opacity: 0, scale: 0.95, duration: 0.8 }, "-=0.3");
    }

    animateNumbersCountUp();

    const cards = document.querySelectorAll(".zad-card");
    if (cards.length > 0) {
        gsap.from(cards, {
            opacity: 0,
            y: 45,
            duration: 0.65,
            stagger: 0.1,
            ease: "power2.out",
            scrollTrigger: {
                trigger: ".row.g-4",
                start: "top 85%",
                toggleActions: "play none none none"
            }
        });
    }

    const navbar = document.querySelector(".zad-navbar");
    if (navbar) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 40) {
                navbar.classList.add("nav-scrolled");
            } else {
                navbar.classList.remove("nav-scrolled");
            }
        });
    }
}

function animateNumbersCountUp() {
    const numberElements = document.querySelectorAll(".stat-num");
    numberElements.forEach(function (el) {
        const rawText = el.innerText.trim();
        const targetValue = parseFloat(rawText.replace(/[^0-9.]/g, ''));
        if (isNaN(targetValue) || targetValue === 0) return;

        const isDecimal = rawText.includes('.');
        const obj = { val: 0 };

        gsap.to(obj, {
            val: targetValue,
            duration: 1.8,
            ease: "power2.out",
            onUpdate: function () {
                let currentStr = isDecimal ? obj.val.toFixed(1) : Math.floor(obj.val).toString();
                const smallTag = el.querySelector("small");
                if (smallTag) {
                    el.childNodes[0].nodeValue = currentStr + " ";
                } else {
                    el.innerText = currentStr;
                }
            }
        });
    });
}

/* --------------------------------------------------------------------------
   3. تأثير الإضاءة الفأرية التفاعلي للكروت (Spotlight Card Hover Effect)
   -------------------------------------------------------------------------- */
function initSpotlightCards() {
    const cards = document.querySelectorAll(".zad-card, .spotlight-card, .metric-card");
    cards.forEach(function (card) {
        card.classList.add("spotlight-card");
        card.addEventListener("mousemove", function (e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty("--mouse-x", `${x}px`);
            card.style.setProperty("--mouse-y", `${y}px`);
        });
    });
}

/* --------------------------------------------------------------------------
   4. نظام الإشعارات العائم الحديث (Modern Floating Toasts)
   -------------------------------------------------------------------------- */
function showZadToast(message, category = "info") {
    let container = document.getElementById("zadToastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "zadToastContainer";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    let iconClass = "fa-circle-info text-primary";
    let catClass = "toast-info";

    if (category === "success") {
        iconClass = "fa-circle-check text-success";
        catClass = "toast-success";
    } else if (category === "danger" || category === "error") {
        iconClass = "fa-circle-exclamation text-danger";
        catClass = "toast-danger";
    } else if (category === "warning") {
        iconClass = "fa-triangle-exclamation text-warning";
        catClass = "toast-warning";
    }

    toast.className = `zad-toast ${catClass}`;
    toast.innerHTML = `
        <div class="fs-4"><i class="fa-solid ${iconClass}"></i></div>
        <div class="flex-grow-1">
            <div class="small fw-bold text-dark">${message}</div>
        </div>
        <button type="button" class="btn-close small ms-2" aria-label="Close"></button>
    `;

    toast.querySelector(".btn-close").addEventListener("click", function () {
        dismissToast(toast);
    });

    container.appendChild(toast);

    setTimeout(function () {
        dismissToast(toast);
    }, 4500);
}

function dismissToast(toast) {
    toast.classList.add("zad-toast-out");
    setTimeout(function () {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function initZadToasts() {
    const flashHolders = document.querySelectorAll('.zad-raw-flash');
    flashHolders.forEach(function (el) {
        const msg = el.getAttribute("data-msg");
        const cat = el.getAttribute("data-cat") || "info";
        if (msg) {
            showZadToast(msg, cat);
        }
    });
}

/* --------------------------------------------------------------------------
   5. أدوات إضافية وميكرو-إنتركشنز
   -------------------------------------------------------------------------- */
function initBootstrapTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/* --------------------------------------------------------------------------
   6. نسخ كود الحجز بنقرة واحدة
   -------------------------------------------------------------------------- */
function initCodeCopy() {
    const codeBoxes = document.querySelectorAll('.zad-code-box, .pickup-code');
    codeBoxes.forEach(function (box) {
        box.title = "اضغط لنسخ كود الاستلام مباشرة";
        box.addEventListener("click", function () {
            const codeEl = box.querySelector('.zad-code-text') || box;
            const textToCopy = codeEl.innerText.trim();
            if (navigator.clipboard) {
                navigator.clipboard.writeText(textToCopy).then(function () {
                    showZadToast(`تم نسخ الكود (${textToCopy}) إلى الحافظة بنجاح! 📋`, "success");
                });
            }
        });
    });
}

/* --------------------------------------------------------------------------
   7. حاسبة الخصم الفورية في نماذج الوجبات
   -------------------------------------------------------------------------- */
function initLiveDiscountCalculators() {
    document.querySelectorAll('.zad-meal-form').forEach(function (form) {
        const origInput = form.querySelector('input[name="original_price"]');
        const discInput = form.querySelector('input[name="discounted_price"]');
        const badge = form.querySelector('.live-discount-badge');

        if (origInput && discInput && badge) {
            function updateBadge() {
                const orig = parseFloat(origInput.value) || 0;
                const disc = parseFloat(discInput.value) || 0;
                if (orig > 0 && disc >= 0 && orig > disc) {
                    const pct = Math.round(((orig - disc) / orig) * 100);
                    const savedAmt = (orig - disc).toFixed(1);
                    badge.innerHTML = `🔥 نسبة الخصم: ${pct}% (توفير: ${savedAmt} ج.م)`;
                    badge.style.display = "block";
                } else {
                    badge.style.display = "none";
                }
            }
            origInput.addEventListener("input", updateBadge);
            discInput.addEventListener("input", updateBadge);
        }
    });
}

/* --------------------------------------------------------------------------
   8. تأكيد العمليات الحساسة
   -------------------------------------------------------------------------- */
function initConfirmHandlers() {
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener("click", function (e) {
            const promptMsg = el.getAttribute("data-confirm") || "هل أنت متأكد من المتابعة؟";
            if (!confirm(promptMsg)) {
                e.preventDefault();
            }
        });
    });
}

/* --------------------------------------------------------------------------
   9. زر إظهار وإخفاء كلمة المرور
   -------------------------------------------------------------------------- */
function initPasswordToggle() {
    const toggleBtns = document.querySelectorAll('.btn-toggle-password');
    toggleBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const icon = btn.querySelector('i');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            }
        });
    });
}

/* --------------------------------------------------------------------------
   10. مؤقت العد التنازلي لإغلاق عروض الفوائض (Surplus Expiry Countdown)
   -------------------------------------------------------------------------- */
function initSurplusCountdownTimers() {
    const timerEls = document.querySelectorAll('.meal-countdown');
    if (timerEls.length === 0) return;

    timerEls.forEach(function (el) {
        const mealId = parseInt(el.getAttribute('data-meal-id')) || 1;
        const now = new Date();
        const expiryKey = 'zad_meal_expiry_' + mealId;
        let expiryTimestamp = localStorage.getItem(expiryKey);

        if (!expiryTimestamp || parseInt(expiryTimestamp) < now.getTime()) {
            const remainingMinutes = 60 + ((mealId * 29) % 95);
            expiryTimestamp = now.getTime() + (remainingMinutes * 60 * 1000);
            localStorage.setItem(expiryKey, expiryTimestamp);
        } else {
            expiryTimestamp = parseInt(expiryTimestamp);
        }

        function updateClock() {
            const current = new Date().getTime();
            const diff = expiryTimestamp - current;

            if (diff <= 0) {
                el.innerHTML = '<span class="badge bg-secondary px-2 py-1 small">انتهى موعد العرض</span>';
                const parentBox = el.closest('.surplus-countdown-box');
                if (parentBox) {
                    parentBox.classList.remove('bg-danger-subtle', 'border-danger-subtle');
                    parentBox.classList.add('bg-light', 'border-secondary-subtle');
                }
                return;
            }

            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            const hStr = hours < 10 ? '0' + hours : hours;
            const mStr = minutes < 10 ? '0' + minutes : minutes;
            const sStr = seconds < 10 ? '0' + seconds : seconds;

            el.textContent = `${hStr}:${mStr}:${sStr}`;

            if (diff < 30 * 60 * 1000) {
                el.classList.add('animate-pulse', 'text-danger');
            }
        }

        updateClock();
        setInterval(updateClock, 1000);
    });
}
