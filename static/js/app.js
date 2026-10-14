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

async function checkDatabaseConnection() {
    const badge = document.querySelector("[data-database-status]");
    if (!badge) return;
    try {
        const response = await fetch("/api/v1/salud", {
            headers: { "Accept": "application/json" },
            cache: "no-store"
        });
        const result = await response.json();
        if (!response.ok || result.data?.connection !== true) {
            throw new Error(result.error?.message || "La base de datos local no está disponible.");
        }
        badge.textContent = `Base de datos conectada · ${result.data.database}`;
        badge.classList.add("database-connected");
        badge.title = `Conexión verificada por Flask y SQL. Tasa: ${result.data.usd_to_cop_rate} COP/USD.`;
    } catch (error) {
        badge.textContent = "Base de datos sin conexión";
        badge.classList.add("database-disconnected");
        badge.title = error.message;
    }
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

document.addEventListener("DOMContentLoaded", () => {
    checkDatabaseConnection();
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