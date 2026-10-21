const productImageFallbacks = {
    "Android Smartphones": "photo-1511707171634-5f897ff02aa9",
    "iPhones (Apple)": "photo-1511707171634-5f897ff02aa9",
    "Business Laptops": "photo-1496181133206-80ce9b88a853",
    "General Laptops": "photo-1496181133206-80ce9b88a853",
    "Gaming Laptops": "photo-1486572788966-cfd3df1f5b42",
    "Desktop PCs & All-in-Ones": "photo-1496181133206-80ce9b88a853",
    "Mini PCs": "photo-1496181133206-80ce9b88a853",
    "Computer Mice": "photo-1527814050087-3793815479db",
    "Keyboards": "photo-1587829741301-dc798b83add3",
    "Earbuds & Headphones": "photo-1505740420928-5e560c06d30e",
    "Monitors": "photo-1527443224154-c4a3942d3acf",
    "Tablets & E-Ink": "photo-1544244015-0df4b3ffc6b0",
    "Smartwatches": "photo-1523275335684-37898b6baf30",
    "SSD & Networking": "photo-1496181133206-80ce9b88a853",
    "Power & Docks": "photo-1496181133206-80ce9b88a853"
};

function categoryFallbackUrl(category) {
    const photo = productImageFallbacks[category]
        || (/console|game/i.test(category || "")
            ? "photo-1486572788966-cfd3df1f5b42"
            : null);
    return photo
        ? `https://images.unsplash.com/${photo}?auto=format&fit=crop&w=640&q=80`
        : null;
}

async function sendCartRequest(url, method, body) {
    const options = {
        method,
        headers: { "Accept": "application/json" }
    };
    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    if (response.status === 204) {
        return { data: {} };
    }
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.error?.message || "No fue posible actualizar el carrito.");
    }
    return result;
}


function showFeedback(message, isError = false) {
    const feedback = document.querySelector("[data-feedback]");
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle("feedback-error", isError);
}

function updateCartCount(count) {
    document.querySelectorAll("[data-cart-count]").forEach((element) => {
        element.textContent = count;
    });
}

function applyImageFallback(image) {
    if (!image.dataset.categoryFallback) {
        image.dataset.categoryFallback = "true";
        const fallbackUrl = categoryFallbackUrl(image.dataset.productCategory);
        if (fallbackUrl) {
            image.src = fallbackUrl;
            return;
        }
    }
    if (!image.dataset.localFallback) {
        image.dataset.localFallback = "true";
        image.src = "/static/img/product-placeholder.svg";
    }
}

function initCarousels() {
    document.querySelectorAll("[data-carousel-prev]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const trackId = btn.dataset.carouselPrev;
            const track = document.getElementById(trackId);
            if (track) {
                const scrollAmount = Math.max(240, track.clientWidth * 0.75);
                track.scrollBy({ left: -scrollAmount, behavior: "smooth" });
            }
        });
    });

    document.querySelectorAll("[data-carousel-next]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const trackId = btn.dataset.carouselNext;
            const track = document.getElementById(trackId);
            if (track) {
                const scrollAmount = Math.max(240, track.clientWidth * 0.75);
                track.scrollBy({ left: scrollAmount, behavior: "smooth" });
            }
        });
    });
}

function initMobileMenu() {
    const toggleBtn = document.querySelector("[data-menu-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");
    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener("click", () => {
            navMenu.classList.toggle("nav-open");
        });

        // Cerrar menú al hacer clic en un enlace
        navMenu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("nav-open");
            });
        });
    }
}

function initAdminSidebar() {
    const toggleBtn = document.querySelector("[data-admin-sidebar-toggle]");
    const closeBtn = document.querySelector("[data-admin-close]");
    const overlay = document.querySelector("[data-admin-overlay]");
    const sidebar = document.getElementById("adminSidebar");
    const layout = document.getElementById("adminLayout");

    if (!sidebar) return;

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            if (window.innerWidth <= 900) {
                sidebar.classList.toggle("admin-sidebar-open");
                if (overlay) overlay.classList.toggle("active");
            } else {
                sidebar.classList.toggle("admin-sidebar-collapsed");
                if (layout) layout.classList.toggle("sidebar-collapsed");
            }
        });
    }

    function closeSidebar() {
        sidebar.classList.remove("admin-sidebar-open");
        if (overlay) overlay.classList.remove("active");
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeSidebar);
    }
    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }
}

function initModals() {
    document.querySelectorAll("[data-modal-open]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const modalId = btn.dataset.modalOpen;
            const modal = document.getElementById(modalId);
            if (!modal) return;

            if (btn.dataset.catId) {
                const idInput = modal.querySelector("#edit_cat_id");
                const nameInput = modal.querySelector("#edit_cat_nombre");
                const descInput = modal.querySelector("#edit_cat_desc");
                if (idInput) idInput.value = btn.dataset.catId;
                if (nameInput) nameInput.value = btn.dataset.catName || "";
                if (descInput) descInput.value = btn.dataset.catDesc || "";
            }

            modal.classList.add("modal-open");
            modal.setAttribute("aria-hidden", "false");
            const firstInput = modal.querySelector("input:not([type='hidden']), textarea");
            if (firstInput) setTimeout(() => firstInput.focus(), 60);
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".admin-modal");
            if (modal) {
                modal.classList.remove("modal-open");
                modal.setAttribute("aria-hidden", "true");
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            document.querySelectorAll(".admin-modal.modal-open").forEach((modal) => {
                modal.classList.remove("modal-open");
                modal.setAttribute("aria-hidden", "true");
            });
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initCarousels();
    initMobileMenu();
    initAdminSidebar();
    initModals();

    document.querySelectorAll("img").forEach((image) => {
        if (image.complete && image.naturalWidth === 0) {
            applyImageFallback(image);
        }
    });
});

document.addEventListener("click", async (event) => {
    const addButton = event.target.closest("[data-cart-add]");
    if (addButton) {
        const quantityInput = document.querySelector("[data-product-quantity]");
        const quantity = addButton.hasAttribute("data-quantity-input")
            ? Number.parseInt(quantityInput?.value || "1", 10)
            : Number.parseInt(addButton.dataset.quantity || "1", 10);
        addButton.disabled = true;
        try {
            const result = await sendCartRequest("/api/v1/carrito/productos", "POST", {
                product_id: addButton.dataset.productId,
                quantity
            });
            updateCartCount(result.data.cart_count);
            showFeedback(result.data.message);
        } catch (error) {
            showFeedback(error.message, true);
        } finally {
            addButton.disabled = false;
        }
        return;
    }

    const updateButton = event.target.closest("[data-cart-update]");
    if (updateButton) {
        const productId = updateButton.dataset.cartUpdate;
        const quantity = Number.parseInt(
            document.querySelector(`[data-cart-quantity="${CSS.escape(productId)}"]`)?.value || "",
            10
        );
        updateButton.disabled = true;
        try {
            await sendCartRequest(
                `/api/v1/carrito/productos/${encodeURIComponent(productId)}`,
                "PATCH",
                { quantity }
            );
            window.location.reload();
        } catch (error) {
            showFeedback(error.message, true);
            updateButton.disabled = false;
        }
        return;
    }

    const removeButton = event.target.closest("[data-cart-remove]");
    if (removeButton) {
        const productId = removeButton.dataset.cartRemove;
        removeButton.disabled = true;
        try {
            await sendCartRequest(
                `/api/v1/carrito/productos/${encodeURIComponent(productId)}`,
                "DELETE"
            );
            window.location.reload();
        } catch (error) {
            showFeedback(error.message, true);
            removeButton.disabled = false;
        }
    }
});

document.addEventListener("error", (event) => {
    if (!(event.target instanceof HTMLImageElement)) return;
    applyImageFallback(event.target);
}, true);