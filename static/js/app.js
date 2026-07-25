// Shoplite front-end. Server-rendered pages call the JSON API from the browser
// using a JWT stored in localStorage. Kept small and vanilla so the UI has real
// async behaviour to practise test automation against.
(function () {
  "use strict";

  var TOKEN_KEY = "shoplite_token";
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var byId = function (id, root) { return $('[data-testid="' + id + '"]', root); };

  function getToken() { return localStorage.getItem(TOKEN_KEY); }
  function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
  function clearToken() { localStorage.removeItem(TOKEN_KEY); }

  function money(cents) { return "$" + (cents / 100).toFixed(2); }

  // fetch wrapper that attaches the bearer token.
  function authFetch(url, opts) {
    opts = opts || {};
    opts.headers = Object.assign(
      { Accept: "application/json" },
      opts.headers || {}
    );
    var token = getToken();
    if (token) opts.headers["Authorization"] = "Bearer " + token;
    return fetch(url, opts);
  }

  function jsonFetch(url, method, body) {
    return authFetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  function requireAuthOrRedirect() {
    if (!getToken()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  }

  function show(el, on) { if (el) el.hidden = !on; }

  // --- Nav -------------------------------------------------------------
  function updateNav() {
    var loggedIn = !!getToken();
    show(byId("nav-login"), !loggedIn);
    show(byId("nav-logout"), loggedIn);
    var logout = byId("nav-logout");
    if (logout && !logout._wired) {
      logout._wired = true;
      logout.addEventListener("click", function (e) {
        e.preventDefault();
        clearToken();
        window.location.href = "/login";
      });
    }
  }

  async function refreshCartBadge() {
    var badge = byId("cart-badge");
    if (!badge) return;
    if (!getToken()) { badge.textContent = "0"; return; }
    try {
      var res = await authFetch("/api/cart");
      if (!res.ok) return;
      var cart = await res.json();
      badge.textContent = String(cart.item_count || 0);
    } catch (e) { /* leave as-is */ }
  }

  // --- Add to cart (catalog + product detail) --------------------------
  function wireAddToCart() {
    document.querySelectorAll('[data-testid="add-to-cart"]').forEach(function (btn) {
      btn.addEventListener("click", async function () {
        if (!getToken()) { window.location.href = "/login"; return; }
        var pid = parseInt(btn.getAttribute("data-product-id"), 10);
        btn.disabled = true;
        try {
          var res = await jsonFetch("/api/cart/items", "POST", {
            product_id: pid,
            quantity: 1,
          });
          if (res.ok) {
            var cart = await res.json();
            var badge = byId("cart-badge");
            if (badge) badge.textContent = String(cart.item_count || 0);
            btn.textContent = "Added ✓";
            setTimeout(function () { btn.textContent = "Add to cart"; btn.disabled = false; }, 900);
          } else {
            var err = await res.json().catch(function () { return {}; });
            btn.textContent = err.detail || "Unavailable";
            setTimeout(function () { btn.textContent = "Add to cart"; btn.disabled = false; }, 1500);
          }
        } catch (e) { btn.disabled = false; }
      });
    });
  }

  // --- Login / Register page -------------------------------------------
  function wireLoginPage() {
    var loginForm = byId("login-form");
    if (!loginForm) return;

    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      var err = byId("login-error");
      show(err, false);
      var res = await jsonFetch("/api/auth/login", "POST", {
        email: byId("login-email").value,
        password: byId("login-password").value,
      });
      if (res.ok) {
        var data = await res.json();
        setToken(data.access_token);
        window.location.href = "/";
      } else {
        err.textContent = "Invalid email or password";
        show(err, true);
      }
    });

    var regForm = byId("register-form");
    regForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      var err = byId("register-error");
      var ok = byId("register-ok");
      show(err, false); show(ok, false);
      var res = await jsonFetch("/api/auth/register", "POST", {
        email: byId("register-email").value,
        password: byId("register-password").value,
      });
      if (res.status === 201) {
        ok.textContent = "Account created — you can sign in now.";
        show(ok, true);
        regForm.reset();
      } else if (res.status === 409) {
        err.textContent = "Email already registered";
        show(err, true);
      } else {
        err.textContent = "Password must be at least 8 characters";
        show(err, true);
      }
    });
  }

  // --- Cart page -------------------------------------------------------
  function renderCart(cart) {
    var empty = byId("cart-empty");
    var table = byId("cart-table");
    var box = byId("checkout-box");
    var body = byId("cart-items");
    var isEmpty = !cart.items.length;
    show(empty, isEmpty);
    show(table, !isEmpty);
    show(box, !isEmpty);
    byId("cart-total").textContent = money(cart.total_cents);

    body.innerHTML = "";
    cart.items.forEach(function (item) {
      var tr = document.createElement("tr");
      tr.setAttribute("data-testid", "cart-row");
      tr.setAttribute("data-item-id", item.id);
      tr.innerHTML =
        '<td data-testid="cart-row-name">' + item.image_emoji + " " + item.name + "</td>" +
        '<td class="price">' + money(item.unit_price_cents) + "</td>" +
        '<td><input type="number" min="1" max="100" class="qty-input" ' +
          'data-testid="cart-qty" value="' + item.quantity + '"></td>' +
        '<td class="price" data-testid="cart-line-total">' + money(item.line_total_cents) + "</td>" +
        '<td><button class="btn btn-danger" data-testid="cart-remove">Remove</button></td>';

      var qty = $('[data-testid="cart-qty"]', tr);
      qty.addEventListener("change", async function () {
        var res = await jsonFetch("/api/cart/items/" + item.id, "PATCH", {
          quantity: parseInt(qty.value, 10),
        });
        var cart2 = await res.json();
        if (res.ok) { renderCart(cart2); refreshCartBadge(); }
        else { alert(cart2.detail || "Update failed"); loadCart(); }
      });
      $('[data-testid="cart-remove"]', tr).addEventListener("click", async function () {
        var res = await authFetch("/api/cart/items/" + item.id, { method: "DELETE" });
        if (res.ok) { renderCart(await res.json()); refreshCartBadge(); }
      });
      body.appendChild(tr);
    });
  }

  async function loadCart() {
    var res = await authFetch("/api/cart");
    if (res.ok) renderCart(await res.json());
  }

  function wireCartPage() {
    if (!byId("cart-container")) return;
    if (!requireAuthOrRedirect()) return;
    loadCart();

    var form = byId("checkout-form");
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      var err = byId("checkout-error");
      show(err, false);
      var res = await jsonFetch("/api/checkout", "POST", {
        card_number: byId("checkout-card").value,
      });
      if (res.status === 201) {
        var order = await res.json();
        refreshCartBadge();
        window.location.href = "/orders/" + order.id;
      } else {
        var data = await res.json().catch(function () { return {}; });
        err.textContent = data.detail || "Checkout failed";
        show(err, true);
      }
    });
  }

  // --- Orders list -----------------------------------------------------
  async function wireOrdersPage() {
    if (!byId("orders-title")) return;
    if (!requireAuthOrRedirect()) return;
    var res = await authFetch("/api/orders");
    if (!res.ok) return;
    var orders = await res.json();
    show(byId("orders-empty"), !orders.length);
    show(byId("orders-table"), !!orders.length);
    var list = byId("orders-list");
    orders.forEach(function (o) {
      var tr = document.createElement("tr");
      tr.setAttribute("data-testid", "order-row");
      tr.innerHTML =
        '<td><a href="/orders/' + o.id + '" data-testid="order-link">#' + o.id + "</a></td>" +
        "<td>" + new Date(o.created_at).toLocaleString() + "</td>" +
        '<td><span class="status-label status-' + o.status + '" data-testid="order-row-status">' +
          o.status + "</span></td>" +
        '<td class="price">' + money(o.total_cents) + "</td>";
      list.appendChild(tr);
    });
  }

  // --- Order detail ----------------------------------------------------
  async function wireOrderDetailPage() {
    var root = byId("order-detail");
    if (!root) return;
    if (!requireAuthOrRedirect()) return;
    var id = root.getAttribute("data-order-id");
    var res = await authFetch("/api/orders/" + id);
    if (res.status === 404) { root.innerHTML = '<p data-testid="order-missing">Order not found.</p>'; return; }
    if (!res.ok) return;
    var order = await res.json();

    var badge = byId("order-status");
    badge.textContent = order.status;
    badge.className = "status-label status-" + order.status;
    byId("order-total").textContent = money(order.total_cents);

    var body = byId("order-items-body");
    order.items.forEach(function (it) {
      var tr = document.createElement("tr");
      tr.setAttribute("data-testid", "order-item-row");
      tr.innerHTML =
        "<td>" + it.product_name + "</td>" +
        '<td class="price">' + money(it.unit_price_cents) + "</td>" +
        "<td>" + it.quantity + "</td>" +
        '<td class="price">' + money(it.line_total_cents) + "</td>";
      body.appendChild(tr);
    });

    var timeline = byId("order-timeline");
    order.history.forEach(function (ev) {
      var li = document.createElement("li");
      li.setAttribute("data-testid", "timeline-event");
      li.innerHTML =
        '<span class="status-label status-' + ev.status + '">' + ev.status + "</span> " +
        '<time>' + new Date(ev.created_at).toLocaleString() + "</time>";
      timeline.appendChild(li);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateNav();
    refreshCartBadge();
    wireAddToCart();
    wireLoginPage();
    wireCartPage();
    wireOrdersPage();
    wireOrderDetailPage();
  });
})();
