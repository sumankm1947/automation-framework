// Small vanilla JS. The cart badge is fetch-driven so the UI has an async
// element to test. The cart API arrives in Milestone 4; until then the fetch
// simply leaves the badge at its server-rendered value.
(function () {
  "use strict";

  async function refreshCartBadge() {
    const badge = document.querySelector('[data-testid="cart-badge"]');
    if (!badge) return;
    try {
      const res = await fetch("/api/cart", { headers: { Accept: "application/json" } });
      if (!res.ok) return;
      const cart = await res.json();
      const count = (cart.items || []).reduce((n, item) => n + (item.quantity || 0), 0);
      badge.textContent = String(count);
    } catch (err) {
      // Cart endpoint not available yet — leave the badge as-is.
    }
  }

  document.addEventListener("DOMContentLoaded", refreshCartBadge);
})();
