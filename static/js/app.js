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
            throw new Error(result.error?.message || "MySQL no está disponible.");
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

document.addEventListener("DOMContentLoaded", checkDatabaseConnection);

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
    if (event.target instanceof HTMLImageElement && !event.target.dataset.fallback) {
        event.target.dataset.fallback = "true";
        event.target.src = "/static/img/product-placeholder.svg";
    }
}, true);