import * as THREE from "three";

const colors = {
    body: 0x273449,
    trim: 0x64748b,
    screen: 0x0f766e,
    accent: 0x38bdf8,
    key: 0xcbd5e1
};

function material(color, metalness = 0.45, roughness = 0.35) {
    return new THREE.MeshStandardMaterial({ color, metalness, roughness });
}

function addBox(parent, dimensions, position, color, options = {}) {
    const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(...dimensions),
        material(color, options.metalness, options.roughness)
    );
    mesh.position.set(...position);
    if (options.rotation) mesh.rotation.set(...options.rotation);
    parent.add(mesh);
    return mesh;
}

function addCylinder(parent, radius, height, position, color, rotation = [0, 0, 0]) {
    const mesh = new THREE.Mesh(
        new THREE.CylinderGeometry(radius, radius, height, 32),
        material(color)
    );
    mesh.position.set(...position);
    mesh.rotation.set(...rotation);
    parent.add(mesh);
    return mesh;
}

function createLaptop(group) {
    addBox(group, [2.05, 1.3, 0.1], [0, 0.42, -0.16], colors.body);
    addBox(group, [1.87, 1.12, 0.025], [0, 0.43, -0.098], colors.screen);
    addBox(group, [2.34, 0.09, 1.42], [0, -0.31, 0.28], colors.trim);
    addBox(group, [0.85, 0.018, 0.42], [0, -0.255, 0.15], colors.body);
    for (let row = 0; row < 3; row += 1) {
        for (let column = 0; column < 10; column += 1) {
            addBox(
                group,
                [0.13, 0.018, 0.09],
                [-0.88 + column * 0.195, -0.252, 0.05 + row * 0.14],
                colors.key,
                { metalness: 0.1, roughness: 0.7 }
            );
        }
    }
}

function createPhone(group, tablet = false) {
    const width = tablet ? 1.65 : 1.05;
    const height = tablet ? 2.15 : 2;
    addBox(group, [width, height, 0.14], [0, 0, 0], colors.body);
    addBox(group, [width - 0.14, height - 0.2, 0.025], [0, 0, 0.083], colors.screen);
    addCylinder(group, 0.035, 0.015, [0, -height / 2 + 0.09, 0.104], colors.trim, [Math.PI / 2, 0, 0]);
}

function createMonitor(group) {
    addBox(group, [2.35, 1.48, 0.13], [0, 0.42, -0.12], colors.body);
    addBox(group, [2.16, 1.29, 0.025], [0, 0.43, -0.045], colors.screen);
    addBox(group, [0.16, 0.68, 0.18], [0, -0.67, -0.08], colors.trim);
    addBox(group, [0.9, 0.1, 0.55], [0, -1.02, 0.02], colors.body);
}

function createDesktop(group) {
    addBox(group, [1.45, 1.7, 0.92], [0, 0, 0], colors.body);
    addBox(group, [0.1, 1.45, 0.05], [0.43, 0, 0.49], colors.accent);
    addCylinder(group, 0.38, 0.05, [-0.23, 0.42, 0.49], colors.trim, [Math.PI / 2, 0, 0]);
    addCylinder(group, 0.38, 0.05, [-0.23, -0.42, 0.49], colors.trim, [Math.PI / 2, 0, 0]);
}

function createKeyboard(group) {
    addBox(group, [2.55, 0.16, 0.92], [0, 0, 0], colors.body);
    for (let row = 0; row < 4; row += 1) {
        for (let column = 0; column < 13; column += 1) {
            addBox(
                group,
                [0.14, 0.055, 0.13],
                [-1.12 + column * 0.185, 0.105, -0.3 + row * 0.19],
                row === 0 && column === 12 ? colors.accent : colors.key,
                { metalness: 0.05, roughness: 0.75 }
            );
        }
    }
}

function createMouse(group) {
    const body = new THREE.Mesh(
        new THREE.SphereGeometry(0.7, 32, 24),
        material(colors.body)
    );
    body.scale.set(0.72, 0.52, 1.1);
    group.add(body);
    addBox(group, [0.035, 0.035, 0.48], [0, 0.35, -0.08], colors.accent);
}

function createHeadphones(group) {
    const band = new THREE.Mesh(
        new THREE.TorusGeometry(0.72, 0.11, 16, 48, Math.PI),
        material(colors.body)
    );
    band.rotation.z = Math.PI;
    band.position.y = 0.15;
    group.add(band);
    addBox(group, [0.42, 0.72, 0.35], [-0.72, -0.45, 0], colors.trim);
    addBox(group, [0.42, 0.72, 0.35], [0.72, -0.45, 0], colors.trim);
    addBox(group, [0.32, 0.58, 0.38], [-0.72, -0.45, 0.12], colors.body);
    addBox(group, [0.32, 0.58, 0.38], [0.72, -0.45, 0.12], colors.body);
}

function createWatch(group) {
    addBox(group, [0.62, 0.78, 0.18], [0, 0, 0], colors.body);
    addBox(group, [0.48, 0.61, 0.03], [0, 0, 0.107], colors.screen);
    addBox(group, [0.35, 0.72, 0.12], [0, 0.72, 0], colors.trim);
    addBox(group, [0.35, 0.72, 0.12], [0, -0.72, 0], colors.trim);
}

function createStorage(group) {
    addBox(group, [2.25, 0.16, 0.72], [0, 0, 0], 0x166534);
    for (let index = 0; index < 5; index += 1) {
        addBox(group, [0.28, 0.12, 0.37], [-0.75 + index * 0.38, 0.12, 0], colors.body);
    }
    addBox(group, [0.3, 0.2, 0.5], [0.98, 0.02, 0], colors.accent);
}

function createGenericDevice(group) {
    addBox(group, [1.5, 1.3, 0.55], [0, 0, 0], colors.body);
    addBox(group, [1.2, 0.88, 0.04], [0, 0.02, 0.3], colors.screen);
    addCylinder(group, 0.12, 0.06, [0.5, -0.48, 0.31], colors.accent, [Math.PI / 2, 0, 0]);
}

function modelType(category) {
    const value = category.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    if (/laptop|notebook|portatil|computer|computador/.test(value)) return "laptop";
    if (/smartphone|iphone|phone|telefono|celular/.test(value)) return "phone";
    if (/tablet|e-ink/.test(value)) return "tablet";
    if (/monitor|display|pantalla/.test(value)) return "monitor";
    if (/desktop|mini pc|tower|pc de escritorio/.test(value)) return "desktop";
    if (/keyboard|teclado/.test(value)) return "keyboard";
    if (/mouse|mice|raton/.test(value)) return "mouse";
    if (/headphone|earbud|audio|auricular/.test(value)) return "headphones";
    if (/watch|reloj/.test(value)) return "watch";
    if (/ssd|storage|almacenamiento|network|red/.test(value)) return "storage";
    return "device";
}

function buildModel(category) {
    const group = new THREE.Group();
    switch (modelType(category)) {
        case "laptop":
            createLaptop(group);
            break;
        case "phone":
            createPhone(group);
            break;
        case "tablet":
            createPhone(group, true);
            break;
        case "monitor":
            createMonitor(group);
            break;
        case "desktop":
            createDesktop(group);
            break;
        case "keyboard":
            createKeyboard(group);
            break;
        case "mouse":
            createMouse(group);
            break;
        case "headphones":
            createHeadphones(group);
            break;
        case "watch":
            createWatch(group);
            break;
        case "storage":
            createStorage(group);
            break;
        default:
            createGenericDevice(group);
    }
    return group;
}

function disposeGroup(group) {
    const geometries = new Set();
    const materials = new Set();
    group.traverse((object) => {
        if (!object.isMesh) return;
        geometries.add(object.geometry);
        if (Array.isArray(object.material)) {
            object.material.forEach((item) => materials.add(item));
        } else {
            materials.add(object.material);
        }
    });
    geometries.forEach((geometry) => geometry.dispose());
    materials.forEach((item) => item.dispose());
}

function initViewer(viewer) {
    const container = viewer.querySelector("[data-3d-canvas]");
    const status = viewer.querySelector("[data-3d-status]");
    if (!container) return;

    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch (error) {
        if (status) status.textContent = "Tu navegador no pudo iniciar el visor 3D.";
        console.error("No se pudo iniciar el visor 3D:", error);
        return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setSize(container.clientWidth || 640, container.clientHeight || 360);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.replaceChildren(renderer.domElement);
    renderer.domElement.setAttribute("aria-label", viewer.dataset["3dTitle"] || "Modelo esquemático 3D");
    renderer.domElement.tabIndex = 0;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(3.2, 2.4, 4.8);
    camera.lookAt(0, 0, 0);
    scene.add(new THREE.HemisphereLight(0xe0f2fe, 0x334155, 2.1));
    const keyLight = new THREE.DirectionalLight(0xffffff, 3);
    keyLight.position.set(3, 5, 4);
    scene.add(keyLight);

    let model = buildModel(viewer.dataset.category || "");
    scene.add(model);

    function render() {
        renderer.render(scene, camera);
    }

    function resize() {
        const width = container.clientWidth;
        const height = container.clientHeight;
        if (!width || !height) return;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
        render();
    }

    function replaceModel(category) {
        scene.remove(model);
        disposeGroup(model);
        model = buildModel(category);
        scene.add(model);
        render();
    }

    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    const canvas = renderer.domElement;
    canvas.addEventListener("pointerdown", (event) => {
        dragging = true;
        lastX = event.clientX;
        lastY = event.clientY;
        canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener("pointermove", (event) => {
        if (!dragging) return;
        model.rotation.y += (event.clientX - lastX) * 0.012;
        model.rotation.x += (event.clientY - lastY) * 0.012;
        lastX = event.clientX;
        lastY = event.clientY;
        render();
    });
    canvas.addEventListener("pointerup", () => { dragging = false; });
    canvas.addEventListener("pointercancel", () => { dragging = false; });
    canvas.addEventListener("keydown", (event) => {
        const rotations = { ArrowLeft: [0, -0.15], ArrowRight: [0, 0.15], ArrowUp: [-0.15, 0], ArrowDown: [0.15, 0] };
        const rotation = rotations[event.key];
        if (!rotation) return;
        event.preventDefault();
        model.rotation.x += rotation[0];
        model.rotation.y += rotation[1];
        render();
    });
    canvas.style.touchAction = "none";

    const resetButton = viewer.querySelector("[data-3d-reset]");
    if (resetButton) {
        resetButton.addEventListener("click", () => {
            model.rotation.set(0, 0, 0);
            render();
            canvas.focus();
        });
    }

    if ("ResizeObserver" in window) {
        new ResizeObserver(resize).observe(container);
    } else {
        window.addEventListener("resize", resize);
    }
    resize();
    render();

    viewer.update3DCategory = (category) => {
        viewer.dataset.category = category;
        replaceModel(category);
    };
}

document.querySelectorAll("[data-3d-viewer]").forEach(initViewer);

const categorySelect = document.querySelector("[data-3d-category-select]");
const homeViewer = document.querySelector("[data-3d-home] [data-3d-viewer]");
if (categorySelect && homeViewer) {
    const categoryLink = document.querySelector("[data-3d-category-link]");
    categorySelect.addEventListener("change", () => {
        const selected = categorySelect.selectedOptions[0];
        homeViewer.update3DCategory?.(selected.dataset.categoryName || selected.textContent.trim());
        if (categoryLink && selected.dataset.categoryUrl) {
            categoryLink.href = selected.dataset.categoryUrl;
        }
    });
}
