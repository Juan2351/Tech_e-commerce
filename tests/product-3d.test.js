import assert from "node:assert/strict";
import test from "node:test";

import { getProductComponents, getProductSpecs } from "../static/js/product-3d.js";

test("headphone product titles use the headphone model and components", () => {
    const components = getProductComponents(
        "JBL Tune 720BT Wireless Over-Ear Headphones"
    );

    assert.deepEqual(
        components.map(({ label }) => label),
        ["Diadema", "Transductores", "Almohadillas", "Controles"]
    );
});

test("smartphone categories continue to use phone components", () => {
    const components = getProductComponents("Android Smartphones");

    assert.equal(components[0].label, "Pantalla");
    assert.equal(components.some(({ id }) => id === "camera"), true);
});

test("keyboard subcategory takes priority over its parent mouse-and-keyboard category", () => {
    const components = getProductComponents("Keyboards Mice & Keyboards");

    assert.deepEqual(
        components.map(({ label }) => label),
        ["Carcasa", "Teclas", "Circuitería", "Conexión"]
    );
});

test("laptop component specs include battery runtime and common listing formats", () => {
    const specs = getProductSpecs(
        "HP 14-inch laptop, 8GB DDR4 RAM, 192GB eMMC, Intel Celeron N4120",
        "14-inch HD display, 11-Hr Long Battery Life, Win11 Home, Wi-Fi 6"
    );

    assert.equal(specs.memory, "8GB DDR4");
    assert.match(specs.storage, /192GB eMMC/i);
    assert.match(specs.processor, /Celeron N4120/i);
    assert.match(specs.display, /14-inch/i);
    assert.match(specs.battery, /11-Hr Long Battery Life/i);
    assert.match(specs.operatingSystem, /Win11 Home/i);
    assert.match(specs.connectivity, /Wi-Fi 6/i);
});

test("laptop specs recognize SSD typos and Intel N-series processor models", () => {
    const specs = getProductSpecs(
        "15.6 inch Laptop, 16GB RAM, 512GB SDD, Intel 11th Gen N5095 Processor",
        "1920 x 1080 IPS screen, 144Hz, 512GB ROM"
    );

    assert.equal(specs.memory, "16GB RAM");
    assert.match(specs.storage, /512GB SDD/i);
    assert.match(specs.storage, /512GB ROM/i);
    assert.match(specs.processor, /Intel 11th Gen N5095 Processor/i);
    assert.match(specs.display, /144Hz/i);
    assert.match(specs.display, /IPS/i);
});
