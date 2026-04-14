const PRODUCTS = [
    {"id": 1, "name": "Apple iPhone 15 Pro Max", "price": 159900, "trust": 92, "auth": 90, "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&fit=crop"},
    {"id": 2, "name": "Sony WH-1000XM5 Headphones", "price": 34990, "trust": 88, "auth": 85, "img": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&fit=crop"},
    {"id": 3, "name": "Samsung Galaxy S24 Ultra", "price": 129999, "trust": 65, "auth": 58, "img": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&fit=crop"},
    {"id": 4, "name": "Bose Smart Soundbar 900", "price": 89900, "trust": 91, "auth": 89, "img": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&fit=crop"},
    {"id": 5, "name": "ASUS ROG Zephyrus G14 Laptop", "price": 169990, "trust": 52, "auth": 45, "img": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400&fit=crop"},
    {"id": 6, "name": "GoPro HERO12 Black", "price": 39990, "trust": 95, "auth": 94, "img": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&fit=crop"},
    {"id": 7, "name": "Apple MacBook Air M2", "price": 114990, "trust": 78, "auth": 75, "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&fit=crop"},
    {"id": 8, "name": "Apple Watch Ultra 2", "price": 89900, "trust": 93, "auth": 91, "img": "https://images.unsplash.com/photo-1434493789847-2f02bffa6ae6?w=400&fit=crop"},
    {"id": 9, "name": "Dyson V15 Detect Vacuum", "price": 62900, "trust": 48, "auth": 40, "img": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&fit=crop"},
    {"id": 10, "name": "Apple AirPods Pro 2nd Gen", "price": 24900, "trust": 89, "auth": 87, "img": "https://images.unsplash.com/photo-1606220588913-b3aecb31c195?w=400&fit=crop"}
];

// Extend array to 50 simulated high-fidelity electronics
const ALL_PRODUCTS = [];
for (let i = 0; i < 5; i++) {
    PRODUCTS.forEach(p => {
        ALL_PRODUCTS.push({
            id: ALL_PRODUCTS.length + 1,
            name: `${p.name} ${i === 0 ? '' : (i === 1 ? ' (Refurbished)' : i === 2 ? ' (Bundle)' : i === 3 ? ' (Imported)' : ' (Lite)')}`,
            price: Math.max(1000, p.price + (i * 1200 - 2400)), // jitter price a bit
            trust: Math.max(0, Math.min(100, p.trust + (i * 3 - 6))), // jitter trust
            auth: Math.max(0, Math.min(100, p.auth + (i * 3 - 6))),
            img: p.img
        });
    });
}

let compareSet = new Set();

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('product-count').textContent = ALL_PRODUCTS.length;
    renderGrid(ALL_PRODUCTS);
    setupEvents();
});

function getTrustClass(trust) {
    if (trust >= 80) return 'trust-safe';
    if (trust >= 60) return 'trust-warn';
    return 'trust-fail';
}

function renderGrid(productsList) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';
    
    if (productsList.length === 0) {
        grid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 3rem;">No products found.</p>`;
        return;
    }
    
    productsList.forEach(p => {
        const starCount = Math.min(5, Math.ceil(p.trust / 20));
        const ratingHTML = '★'.repeat(starCount) + '<span style="color:var(--border)">' + '★'.repeat(5 - starCount) + '</span>';
        
        const cClass = getTrustClass(p.trust);
        
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <input type="checkbox" class="compare-checkbox" data-id="${p.id}" ${compareSet.has(p.id) ? 'checked' : ''}>
            <div class="p-img-wrap">
                <img src="${p.img}" loading="lazy" alt="${p.name}">
            </div>
            <div class="p-name">${p.name}</div>
            <div class="p-rating">${ratingHTML} <span style="color:var(--text-muted); margin-left:8px;">(${Math.floor(p.trust * 14.3)})</span></div>
            <div class="trust-badge-wrap ${cClass}">
                <svg viewBox="0 0 36 36" class="circular-chart">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <path class="circle" stroke-dasharray="0, 100" data-target="${p.trust}" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <text x="18" y="22.5" class="percentage">${p.trust}</text>
                </svg>
                <span class="trust-label">Trust Score</span>
            </div>
            <div class="p-price">₹ ${p.price.toLocaleString()}</div>
            <div class="p-actions">
                <button class="btn btn-outline btn-insight" data-id="${p.id}">View Insights</button>
            </div>
        `;
        grid.appendChild(card);
    });

    // Trigger ring animation
    setTimeout(() => {
        document.querySelectorAll('.circle').forEach(c => {
            c.style.strokeDasharray = `${c.dataset.target}, 100`;
        });
    }, 100);
}

function setupEvents() {
    // Search
    document.querySelector('.search-bar input').addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = ALL_PRODUCTS.filter(p => p.name.toLowerCase().includes(term));
        document.getElementById('product-count').textContent = filtered.length;
        renderGrid(filtered);
    });

    // Insights Panel Trigger
    document.addEventListener('click', e => {
        if (e.target.classList.contains('btn-insight')) {
            const id = parseInt(e.target.dataset.id);
            openInsights(id);
        }
    });

    // Close Modals / Panels
    document.getElementById('close-panel').addEventListener('click', closeInsights);
    document.getElementById('panel-overlay').addEventListener('click', () => {
        closeInsights();
        closeModal();
    });

    // Compare Selection Logic
    document.addEventListener('change', e => {
        if (e.target.classList.contains('compare-checkbox')) {
            const id = parseInt(e.target.dataset.id);
            if (e.target.checked) {
                if (compareSet.size >= 3) {
                    e.target.checked = false;
                    alert("You can compare up to 3 products at once.");
                    return;
                }
                compareSet.add(id);
            } else {
                compareSet.delete(id);
            }
            updateCompareBtn();
        }
    });

    // Open Compare Modal
    document.getElementById('compare-btn').addEventListener('click', openCompareModal);
    document.getElementById('close-modal').addEventListener('click', closeModal);
}

function updateCompareBtn() {
    const btn = document.getElementById('compare-btn');
    const span = document.getElementById('compare-count');
    span.textContent = `(${compareSet.size})`;
    btn.disabled = compareSet.size < 2;
}

function openInsights(id) {
    const p = ALL_PRODUCTS.find(x => x.id === id);
    const panel = document.getElementById('panel-content');
    
    // Derived Metrics
    const overpayRatio = (100 - p.trust) / 100 * 0.35; // up to 35% manipulation markup
    const overpay = Math.floor(p.price * overpayRatio);
    const fairPrice = p.price - overpay;
    const susp = 100 - p.auth;

    // AI Recommendation
    let rec = "Buy Recommended";
    let recColor = "var(--success)";
    if (p.trust < 60) { rec = "High Risk - Avoid"; recColor = "var(--danger)"; }
    else if (p.trust < 80) { rec = "Caution - Verify Seller"; recColor = "var(--warning)"; }

    panel.innerHTML = `
        <div class="p-img-wrap" style="height:160px; background:white; padding:15px; border-radius:8px; margin-bottom:1.5rem; border:1px solid var(--border);">
            <img src="${p.img}" alt="${p.name}">
        </div>
        <h2 style="font-size:1.25rem; font-weight:600; margin-bottom:0.5rem; color:#111827;">${p.name}</h2>
        <div style="font-size:1.5rem; font-weight:700; margin-bottom:1.5rem;">₹ ${p.price.toLocaleString()}</div>
        
        <div class="sp-block">
            <h3>Transaction Assessment</h3>
            <p style="font-size:0.875rem; color:var(--text-muted); margin-bottom:0.75rem;">Analysis indicates a product reliability score based on footprint analysis across cross-platform data.</p>
            <div style="font-weight:700; color:${recColor}; font-size:1rem; display:flex; align-items:center; gap:8px;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${recColor}"></span>
                ${rec}
            </div>
        </div>

        <div class="sp-block">
            <h3>Price Integrity Check</h3>
            <div class="sp-price-wrap">
                <span class="sp-price-orig">₹ ${p.price.toLocaleString()} (Listing)</span>
                ${overpay > 0 ? `<span class="sp-price-diff">Risk Premium: +₹ ${overpay.toLocaleString()}</span>` : `<span style="color:var(--success); font-size:0.875rem; font-weight:600;">Fair Pricing</span>`}
            </div>
            <div style="font-size:0.875rem; color:var(--text-muted); margin-top:0.5rem;">Estimated Fair Market Value</div>
            <div class="sp-price-fair">₹ ${fairPrice.toLocaleString()}</div>
            <canvas id="trendCanvas" class="trend-canvas"></canvas>
            <div style="text-align:right; font-size:0.75rem; color:var(--text-muted); margin-top:4px;">14-Day Price Trend</div>
        </div>

        <div class="sp-block">
            <h3>Review Authenticity</h3>
            <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.875rem;">
                <span style="color:var(--success)">${p.auth}% Verified</span>
                <span style="color:var(--danger)">${susp}% Suspicious</span>
            </div>
            <div class="auth-bar-wrap">
                <div class="auth-genuine" style="width: 0%"></div>
                <div class="auth-suspicious" style="width: 0%"></div>
            </div>
            <div class="auth-labels">
                <span>Organic Profiles</span>
                <span>Anomalous Patterns</span>
            </div>
        </div>
    `;

    document.getElementById('side-panel').classList.add('open');
    document.getElementById('panel-overlay').classList.add('show');

    // Trigger animations
    requestAnimationFrame(() => {
        setTimeout(() => {
            document.querySelector('.auth-genuine').style.width = `${p.auth}%`;
            document.querySelector('.auth-suspicious').style.width = `${susp}%`;
            drawTrendCanvas();
        }, 50);
    });
}

function closeInsights() {
    document.getElementById('side-panel').classList.remove('open');
    document.getElementById('panel-overlay').classList.remove('show');
}

function openCompareModal() {
    const arr = Array.from(compareSet).map(id => ALL_PRODUCTS.find(p => p.id === id));
    
    // Calculate best value
    const bestId = arr.reduce((max, p) => p.trust > max.trust ? p : max, arr[0]).id;

    const body = document.getElementById('compare-body');
    body.innerHTML = '';
    
    arr.forEach(p => {
        const isBest = p.id === bestId;
        const dom = document.createElement('div');
        dom.className = `compare-item ${isBest ? 'compare-best' : ''}`;
        
        dom.innerHTML = `
            ${isBest ? '<div class="best-badge">BEST VALUE</div>' : ''}
            <div style="height:120px; display:flex; align-items:center; justify-content:center; margin-bottom:1rem; background:white; border-radius:8px; padding:10px;">
                <img src="${p.img}" style="max-height:100%; object-fit:contain;">
            </div>
            <h4 style="font-size:0.9rem; margin-bottom:0.75rem; color:#111827; height:2.5rem; overflow:hidden;">${p.name}</h4>
            <div style="font-size:1.5rem; font-weight:700; margin-bottom:1.5rem; color:#111827;">₹ ${p.price.toLocaleString()}</div>
            
            <div style="padding-top:1rem; border-top:1px solid var(--border)">
                <p style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted); margin-bottom:0.25rem;">Trust Score</p>
                <div style="font-size:1.75rem; font-weight:700; color: ${getTrustColor(p.trust)}">${p.trust}%</div>
            </div>
            
            <div style="padding-top:1rem; margin-top:1rem; border-top:1px solid var(--border)">
                <p style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-muted); margin-bottom:0.25rem;">Authentic Reviews</p>
                <div style="font-weight:600; font-size:1.1rem; color: #111827;">${p.auth}%</div>
            </div>
        `;
        body.appendChild(dom);
    });

    document.getElementById('compare-modal').classList.add('open');
}

function closeModal() {
    document.getElementById('compare-modal').classList.remove('open');
}

function getTrustColor(trust) {
    if (trust >= 80) return 'var(--success)';
    if (trust >= 60) return 'var(--warning)';
    return 'var(--danger)';
}

function drawTrendCanvas() {
    const canvas = document.getElementById('trendCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Handle High DPI displays
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    
    ctx.beginPath();
    ctx.moveTo(0, rect.height);
    
    const points = 12;
    const step = rect.width / (points - 1);
    
    for(let i=0; i<points; i++) {
        // Generate a jagged trendline
        const y = rect.height - (Math.random() * (rect.height * 0.7) + (rect.height * 0.15));
        const x = i * step;
        ctx.lineTo(x, y);
    }
    
    ctx.strokeStyle = "var(--primary)";
    ctx.lineWidth = 2.5;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.stroke();
    
    // Area fill gradient below the line
    ctx.lineTo(rect.width, rect.height);
    ctx.lineTo(0, rect.height);
    const grad = ctx.createLinearGradient(0,0,0,rect.height);
    grad.addColorStop(0, "rgba(37,99,235,0.15)");
    grad.addColorStop(1, "rgba(37,99,235,0)");
    ctx.fillStyle = grad;
    ctx.fill();
}
