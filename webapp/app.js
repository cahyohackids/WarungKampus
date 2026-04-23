const tg = window.Telegram.WebApp;

// Variables
let products = [];
let categories = [];
let activeCategory = null;
let cart = {}; // { product_id: qty }
let userBalance = 0;

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    tg.expand();
    tg.ready();

    // Setup User Info
    setupUser();

    // Mock Data Fetching (Replace with actual API later)
    fetchData();

    // Setup Main Button
    tg.MainButton.text = "CHECKOUT";
    tg.MainButton.color = "#3b82f6";
    tg.MainButton.onClick(() => handleCheckout());

    // Topup Button
    document.getElementById("btn-topup-profile").addEventListener("click", () => {
        const userId = tg.initDataUnsafe?.user?.id || 0;
        fetch('/api/action', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, action: "topup" })
        });
        tg.close();
    });
});

function setupUser() {
    const user = tg.initDataUnsafe?.user;
    if (user) {
        document.getElementById("user-name-sm").innerText = user.first_name || "Guest";
        document.getElementById("user-initial-sm").innerText = (user.first_name || "G").charAt(0).toUpperCase();
        
        document.getElementById("profile-name").innerText = `${user.first_name || ""} ${user.last_name || ""}`.trim() || "Guest";
        document.getElementById("profile-id").innerText = `ID: ${user.id || "-"}`;
        document.getElementById("profile-avatar").innerText = (user.first_name || "G").charAt(0).toUpperCase();
    }
}

// Tab Navigation
window.switchTab = function(tabId) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(btn => {
        if (btn.dataset.tab === tabId) btn.classList.add('active');
        else btn.classList.remove('active');
    });

    // Update active screen
    document.querySelectorAll('.screen').forEach(screen => {
        if (screen.id === `screen-${tabId}`) screen.classList.add('active');
        else screen.classList.remove('active');
    });

    // Handle screen specific logic
    if (tabId === 'catalog') {
        updateMainButton();
    } else {
        tg.MainButton.hide();
        if (tabId === 'history') fetchHistory();
    }
}

async function fetchHistory() {
    try {
        const userId = tg.initDataUnsafe?.user?.id || 0;
        const res = await fetch('/api/history?user_id=' + userId);
        const data = await res.json();
        const container = document.getElementById('history-container');
        
        if (!data.orders || data.orders.length === 0) {
            container.innerHTML = `<p style="text-align:center; color:var(--text-secondary); margin-top:20px;">Belum ada riwayat transaksi.</p>`;
            return;
        }

        container.innerHTML = data.orders.map(o => {
            const date = new Date(o.created_at).toLocaleDateString('id-ID', {day: '2-digit', month: 'short', hour:'2-digit', minute:'2-digit'});
            return `
                <div class="history-card card-glass">
                    <div class="history-header">
                        <span>#${o.code}</span>
                        <span class="history-status status-${o.status}">${o.status}</span>
                    </div>
                    <div class="history-body">
                        <span class="history-title">${o.product_name} x${o.qty}</span>
                        <span class="history-price">Rp ${o.total_price.toLocaleString('id-ID')}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;">
                        ${date}
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        document.getElementById('history-container').innerHTML = `<p style="text-align:center; color:var(--danger-color);">Gagal memuat riwayat.</p>`;
    }
}

async function fetchData() {
    try {
        const userId = tg.initDataUnsafe?.user?.id || 0;
        const response = await fetch('/api/data?user_id=' + userId);
        if (!response.ok) throw new Error("Failed to load");
        
        const data = await response.json();
        
        userBalance = data.balance;
        categories = data.categories;
        products = data.products;

        const balanceText = `Rp ${userBalance.toLocaleString('id-ID')}`;
        document.getElementById("user-balance-sm").innerText = `Saldo: ${balanceText}`;
        document.getElementById("profile-balance").innerText = balanceText;
        
        renderCategories();
        renderProducts();
    } catch (err) {
        console.error("Failed to fetch data:", err);
        document.getElementById("product-list").innerHTML = `<p style="color: var(--danger-color); text-align: center; grid-column: 1/-1;">Gagal memuat produk. Coba lagi nanti.</p>`;
    }
}

function renderCategories() {
    const container = document.getElementById("category-list");
    container.innerHTML = `<button class="cat-btn ${!activeCategory ? 'active' : ''}" onclick="filterCategory(null)">Semua</button>`;
    
    categories.forEach(cat => {
        container.innerHTML += `<button class="cat-btn ${activeCategory === cat.id ? 'active' : ''}" onclick="filterCategory(${cat.id})">${cat.name}</button>`;
    });
}

function filterCategory(id) {
    activeCategory = id;
    renderCategories();
    renderProducts();
}

function renderProducts() {
    const container = document.getElementById("product-list");
    container.innerHTML = "";

    const filtered = activeCategory ? products.filter(p => p.category_id === activeCategory) : products;

    if (filtered.length === 0) {
        container.innerHTML = `<p style="color: var(--text-secondary); grid-column: 1/-1; text-align: center;">Tidak ada produk.</p>`;
        return;
    }

    filtered.forEach(p => {
        const qty = cart[p.id] || 0;
        
        const controlsHTML = qty > 0 
            ? `
                <div class="cart-controls">
                    <button class="cart-btn" onclick="updateCart(${p.id}, -1)">-</button>
                    <span class="qty-display">${qty}</span>
                    <button class="cart-btn" onclick="updateCart(${p.id}, 1)">+</button>
                </div>
            `
            : `<button class="add-btn" onclick="updateCart(${p.id}, 1)">+ Keranjang</button>`;

        container.innerHTML += `
            <div class="product-card card-glass">
                <div class="product-icon">${p.icon || '🛍️'}</div>
                <h4 class="product-name">${p.name}</h4>
                <p class="product-price">Rp ${p.price.toLocaleString('id-ID')}</p>
                <div class="product-actions" id="action-${p.id}">
                    ${controlsHTML}
                </div>
            </div>
        `;
    });
}

window.updateCart = (productId, change) => {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    let currentQty = cart[productId] || 0;
    let newQty = currentQty + change;

    // Clamp values
    if (newQty < 0) newQty = 0;
    if (newQty > product.stock) {
        tg.showAlert(`Maksimal stok tersisa ${product.stock} item`);
        newQty = product.stock;
    }

    if (newQty === 0) {
        delete cart[productId];
    } else {
        cart[productId] = newQty;
    }

    renderProducts();
    updateMainButton();
}

function updateMainButton() {
    const items = Object.entries(cart);
    if (items.length === 0) {
        tg.MainButton.hide();
        return;
    }

    let total = 0;
    let count = 0;
    
    items.forEach(([id, qty]) => {
        const p = products.find(prod => prod.id === parseInt(id));
        if (p) {
            total += p.price * qty;
            count += qty;
        }
    });

    tg.MainButton.text = `BAYAR (Rp ${total.toLocaleString('id-ID')})`;
    tg.MainButton.show();
}

function handleCheckout() {
    if (Object.keys(cart).length === 0) return;
    
    const orderItems = Object.entries(cart).map(([id, qty]) => ({
        product_id: parseInt(id),
        qty: qty
    }));

    tg.showPopup({
        title: "Pilih Pembayaran",
        message: "Silakan pilih metode pembayaran untuk order Anda:",
        buttons: [
            {id: "qris", type: "default", text: "QRIS / Transfer"},
            {id: "balance", type: "default", text: "Saldo Akun"},
            {type: "cancel"}
        ]
    }, function(buttonId) {
        if (buttonId === "qris" || buttonId === "balance") {
            const userId = tg.initDataUnsafe?.user?.id || 0;
            tg.MainButton.showProgress();
            
            fetch('/api/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: userId,
                    items: orderItems,
                    payment_method: buttonId
                })
            }).then(res => res.json())
              .then(data => {
                  if (data.detail) {
                      tg.showAlert(data.detail);
                  } else {
                      if (buttonId === 'qris') {
                          tg.showAlert("Order berhasil dibuat! Silakan cek chat bot untuk mengirimkan bukti transfer QRIS.");
                      } else {
                          tg.showAlert("Pembayaran berhasil! Silakan cek chat bot Anda.");
                      }
                      tg.close();
                  }
              })
              .catch(() => tg.showAlert("Terjadi kesalahan jaringan."))
              .finally(() => tg.MainButton.hideProgress());
        }
    });
}
