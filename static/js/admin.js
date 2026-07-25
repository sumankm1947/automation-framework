// Admin pages: order-status control and product management. Depends on helpers
// exposed by app.js via window.Shoplite. Non-admins are bounced to /login.
(function () {
  "use strict";

  var S = window.Shoplite;
  if (!S) return;
  var byId = S.byId, show = S.show, money = S.money;

  // Mirror of app/services.py ALLOWED_TRANSITIONS.
  var TRANSITIONS = {
    PLACED: ["PACKING", "CANCELLED"],
    PACKING: ["IN_TRANSIT", "CANCELLED"],
    IN_TRANSIT: ["DELIVERED"],
    DELIVERED: [],
    CANCELLED: [],
  };

  async function ensureAdmin() {
    if (!S.getToken()) { window.location.href = "/login"; return false; }
    var res = await S.authFetch("/api/auth/me");
    if (!res.ok) { window.location.href = "/login"; return false; }
    var me = await res.json();
    if (me.role !== "admin") { window.location.href = "/"; return false; }
    return true;
  }

  // --- Orders page -----------------------------------------------------
  async function initOrders() {
    if (!byId("admin-orders-title")) return;
    if (!(await ensureAdmin())) return;

    var res = await S.authFetch("/api/admin/orders");
    if (!res.ok) return;
    var orders = await res.json();
    show(byId("admin-orders-empty"), !orders.length);
    show(byId("admin-orders-table"), !!orders.length);
    var list = byId("admin-orders-list");
    list.innerHTML = "";

    orders.forEach(function (o) {
      var tr = document.createElement("tr");
      tr.setAttribute("data-testid", "admin-order-row");
      tr.setAttribute("data-order-id", o.id);

      var options = TRANSITIONS[o.status] || [];
      var selectHtml = options.length
        ? '<select data-testid="admin-status-select">' +
            options.map(function (s) { return '<option value="' + s + '">' + s + "</option>"; }).join("") +
          "</select>"
        : '<span class="muted" data-testid="admin-status-terminal">— terminal —</span>';
      var btnHtml = options.length
        ? '<button class="btn btn-primary" data-testid="admin-status-save">Save</button>'
        : "";

      tr.innerHTML =
        '<td><a href="/orders/' + o.id + '">#' + o.id + "</a></td>" +
        '<td data-testid="admin-order-customer">' + o.user_email + "</td>" +
        '<td class="price">' + money(o.total_cents) + "</td>" +
        '<td><span class="status-label status-' + o.status + '" data-testid="admin-order-status">' +
          o.status + "</span></td>" +
        "<td>" + selectHtml + "</td>" +
        "<td>" + btnHtml + "</td>";

      var saveBtn = tr.querySelector('[data-testid="admin-status-save"]');
      if (saveBtn) {
        saveBtn.addEventListener("click", async function () {
          var target = tr.querySelector('[data-testid="admin-status-select"]').value;
          var r = await S.jsonFetch("/api/admin/orders/" + o.id + "/status", "PATCH", { status: target });
          if (r.ok) { initOrders(); }
          else { var e = await r.json().catch(function(){return {};}); alert(e.detail || "Update failed"); }
        });
      }
      list.appendChild(tr);
    });
  }

  // --- Products page ---------------------------------------------------
  async function loadProducts() {
    var res = await S.authFetch("/api/products");
    if (!res.ok) return;
    var products = await res.json();
    var list = byId("admin-products-list");
    list.innerHTML = "";
    products.forEach(function (p) {
      var tr = document.createElement("tr");
      tr.setAttribute("data-testid", "admin-product-row");
      tr.setAttribute("data-product-id", p.id);
      tr.innerHTML =
        "<td>" + p.sku + "</td>" +
        "<td>" + p.name + "</td>" +
        '<td><input type="number" min="0" class="qty-input" data-testid="admin-product-price" value="' + p.price_cents + '"></td>' +
        '<td><input type="number" min="0" class="qty-input" data-testid="admin-product-stock" value="' + p.stock + '"></td>' +
        '<td><button class="btn btn-primary" data-testid="admin-product-save">Save</button></td>';
      tr.querySelector('[data-testid="admin-product-save"]').addEventListener("click", async function () {
        var body = {
          price_cents: parseInt(tr.querySelector('[data-testid="admin-product-price"]').value, 10),
          stock: parseInt(tr.querySelector('[data-testid="admin-product-stock"]').value, 10),
        };
        var r = await S.jsonFetch("/api/admin/products/" + p.id, "PATCH", body);
        if (r.ok) { loadProducts(); } else { alert("Update failed"); }
      });
      list.appendChild(tr);
    });
  }

  async function initProducts() {
    if (!byId("admin-products-title")) return;
    if (!(await ensureAdmin())) return;
    loadProducts();

    byId("product-create-form").addEventListener("submit", async function (e) {
      e.preventDefault();
      var err = byId("product-create-error"), ok = byId("product-create-ok");
      show(err, false); show(ok, false);
      var body = {
        sku: byId("product-sku").value,
        name: byId("product-name").value,
        price_cents: parseInt(byId("product-price").value, 10),
        stock: parseInt(byId("product-stock").value, 10),
        image_emoji: byId("product-emoji").value || "📦",
      };
      var r = await S.jsonFetch("/api/admin/products", "POST", body);
      if (r.status === 201) {
        ok.textContent = "Product created."; show(ok, true);
        e.target.reset(); byId("product-emoji").value = "📦";
        loadProducts();
      } else if (r.status === 409) {
        err.textContent = "SKU already exists"; show(err, true);
      } else {
        err.textContent = "Invalid product data"; show(err, true);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initOrders();
    initProducts();
  });
})();
