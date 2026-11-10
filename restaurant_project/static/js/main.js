document.addEventListener("DOMContentLoaded", () => {
    // Polished, accessible Django message toasts.
    document.querySelectorAll("[data-app-toast]").forEach((toast) => {
        const close = () => {
            toast.classList.add("toast-hiding");
            window.setTimeout(() => toast.remove(), 220);
        };
        toast.querySelector("[data-toast-close]")?.addEventListener("click", close);
        const duration = Number(toast.dataset.duration || 1800);
        const progress = toast.querySelector(".toast-progress-bar");
        if (progress) progress.style.animationDuration = `${duration}ms`;
        window.setTimeout(close, duration);
    });

    // Add items to the session cart in the background: no page refresh, so users
    // can add the same food repeatedly without losing their current search/results.
    document.addEventListener("click", async (event) => {
        const addLink = event.target.closest("a[data-add-to-cart]");
        if (!addLink) return;
        event.preventDefault();
        if (addLink.dataset.busy === "true") return;
        addLink.dataset.busy = "true";
        addLink.classList.add("is-adding");
        const originalHtml = addLink.innerHTML;
        addLink.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Adding';
        try {
            const response = await fetch(addLink.href, {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest", "Accept": "application/json" },
                credentials: "same-origin"
            });
            const data = await response.json();
            if (!response.ok || !data.ok) throw new Error(data.message || "Could not add this item.");

            const cartLink = document.querySelector(".cart-link");
            if (cartLink) {
                let badge = cartLink.querySelector(".cart-badge");
                if (!badge) {
                    badge = document.createElement("span");
                    badge.className = "cart-badge";
                    cartLink.appendChild(badge);
                }
                badge.textContent = data.cart_count;
                badge.setAttribute("aria-label", `${data.cart_count} items in cart`);
            }
            showAppToast(data.message || `${data.food_name} added to cart.`, "success");
        } catch (error) {
            console.error("FoodieHub add to cart:", error);
            showAppToast(error.message || "Unable to add item. Please try again.", "error");
        } finally {
            addLink.innerHTML = originalHtml;
            addLink.classList.remove("is-adding");
            delete addLink.dataset.busy;
        }
    });

    function showAppToast(message, type = "info") {
        let stack = document.querySelector(".app-toast-stack");
        if (!stack) {
            stack = document.createElement("div");
            stack.className = "app-toast-stack";
            stack.setAttribute("aria-label", "Notifications");
            stack.setAttribute("aria-live", "polite");
            document.body.appendChild(stack);
        }
        const toast = document.createElement("div");
        toast.className = `app-toast app-toast-${type}`;
        toast.dataset.appToast = "";
        toast.dataset.duration = "1800";
        toast.setAttribute("role", "status");
        const iconClass = type === "success" ? "bi-check-lg" : type === "error" ? "bi-x-lg" : "bi-info-lg";
        const title = type === "success" ? "Added to cart" : type === "error" ? "Could not add item" : "Notification";
        const icon = document.createElement("div");
        icon.className = "app-toast-icon";
        icon.setAttribute("aria-hidden", "true");
        icon.innerHTML = `<i class="bi ${iconClass}"></i>`;
        const content = document.createElement("div");
        content.className = "app-toast-content";
        const heading = document.createElement("strong");
        heading.className = "app-toast-title";
        heading.textContent = title;
        const body = document.createElement("div");
        body.className = "app-toast-message";
        body.textContent = message;
        content.append(heading, body);
        const close = document.createElement("button");
        close.type = "button";
        close.className = "app-toast-close";
        close.dataset.toastClose = "";
        close.setAttribute("aria-label", "Dismiss notification");
        close.innerHTML = '<i class="bi bi-x"></i>';
        toast.append(icon, content, close);
        stack.appendChild(toast);
        const dismiss = () => {
            if (!toast.isConnected) return;
            toast.classList.add("toast-hiding");
            window.setTimeout(() => toast.remove(), 220);
        };
        close.addEventListener("click", dismiss);
        window.setTimeout(dismiss, 1800);
    }

    // AJAX menu search: update results in place, never submit/reload on each keystroke.
    const form = document.getElementById("menu-search-form");
    const searchInput = document.getElementById("food-search");
    const categorySelect = document.getElementById("food-category");
    const status = document.getElementById("search-status");
    if (!form || !searchInput || !categorySelect) return;

    let debounceTimer = null;
    let activeController = null;
    let requestNumber = 0;
    const submitButton = form.querySelector('button[type="submit"]');

    const getUrl = () => {
        const url = new URL(form.action, window.location.href);
        const q = searchInput.value.trim();
        const category = categorySelect.value;
        if (q) url.searchParams.set("q", q); else url.searchParams.delete("q");
        if (category) url.searchParams.set("category", category); else url.searchParams.delete("category");
        return url;
    };

    const updateResults = async () => {
        const url = getUrl();
        const thisRequest = ++requestNumber;
        if (activeController) activeController.abort();
        activeController = new AbortController();
        if (status) status.textContent = "Searching…";
        if (submitButton) submitButton.disabled = true;
        try {
            const response = await fetch(url.toString(), {
                method: "GET",
                headers: { "X-Requested-With": "XMLHttpRequest" },
                signal: activeController.signal,
                credentials: "same-origin"
            });
            if (!response.ok) throw new Error(`Search failed (${response.status})`);
            const html = await response.text();
            if (thisRequest !== requestNumber) return;
            const nextDoc = new DOMParser().parseFromString(html, "text/html");
            const nextResults = nextDoc.getElementById("food-results");
            const nextToolbar = nextDoc.getElementById("menu-toolbar");
            const nextEmpty = nextDoc.getElementById("menu-empty-state");
            const currentResults = document.getElementById("food-results");
            const currentToolbar = document.getElementById("menu-toolbar");
            const currentEmpty = document.getElementById("menu-empty-state");
            if (!nextResults || !currentResults || !nextToolbar || !currentToolbar) {
                throw new Error("The menu results could not be updated.");
            }
            currentResults.innerHTML = nextResults.innerHTML;
            currentToolbar.innerHTML = nextToolbar.innerHTML;
            if (currentEmpty && nextEmpty) {
                currentEmpty.outerHTML = nextEmpty.outerHTML;
            } else if (currentEmpty && !nextEmpty) {
                currentEmpty.remove();
            } else if (!currentEmpty && nextEmpty) {
                currentToolbar.insertAdjacentElement("afterend", nextEmpty);
            }
            // Keep the input focused and preserve the current page while making the URL shareable.
            window.history.replaceState({}, "", url.pathname + url.search);
            if (status) status.textContent = `${nextDoc.querySelectorAll('#food-results .food-card').length} menu results updated.`;
        } catch (error) {
            if (error.name !== "AbortError") {
                if (status) status.textContent = "Could not update results. You can press Search to retry.";
                console.error("FoodieHub menu search:", error);
            }
        } finally {
            if (thisRequest === requestNumber && submitButton) submitButton.disabled = false;
        }
    };

    const scheduleSearch = () => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(updateResults, 250);
    };
    searchInput.addEventListener("input", scheduleSearch);
    categorySelect.addEventListener("change", () => {
        window.clearTimeout(debounceTimer);
        updateResults();
    });
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        window.clearTimeout(debounceTimer);
        updateResults();
    });

    // Clear-search links are replaced dynamically, so delegate the click handler.
    form.addEventListener("click", (event) => {
        const clearLink = event.target.closest('a[aria-label="Clear search"]');
        if (!clearLink) return;
        event.preventDefault();
        searchInput.value = "";
        searchInput.focus();
        updateResults();
    });
    document.addEventListener("click", (event) => {
        const resetLink = event.target.closest('#menu-toolbar a');
        if (!resetLink) return;
        event.preventDefault();
        searchInput.value = "";
        categorySelect.value = "";
        searchInput.focus();
        updateResults();
    });
});
