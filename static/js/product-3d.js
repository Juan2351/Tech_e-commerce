import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";

const componentCatalog = {
    laptop: [
        { id: "case", label: "Chasis", description: "Estructura exterior y soporte del equipo." },
        { id: "display", label: "Pantalla y bisagras", description: "Panel frontal y bisagras del portátil; el brillo del modelo es ilustrativo." },
        { id: "keyboard", label: "Teclado y touchpad", description: "Teclas y área táctil de entrada, dibujadas a escala visual." },
        { id: "board", label: "Placa base y puertos", description: "Zona ilustrativa de circuitos y conectores; no especifica compatibilidad." },
        { id: "cpu", label: "Procesador", description: "Procesador representativo situado sobre la placa base." },
        { id: "memory", label: "Memoria RAM", description: "Módulos representativos; la capacidad y generación se muestran solo si aparecen en la ficha del producto." },
        { id: "storage", label: "Almacenamiento", description: "Unidad representativa; capacidad e interfaz tomadas de la información publicada." },
        { id: "cooling", label: "Refrigeración", description: "Ventilador y disipación térmica representados de forma esquemática." },
        { id: "battery", label: "Batería y altavoces", description: "Módulos representativos de energía y audio interno, sin capacidad especificada." }
    ],
    phone: [
        { id: "display", label: "Pantalla", description: "Panel frontal de visualización." },
        { id: "board", label: "Placa base", description: "Zona ilustrativa para circuitos y conexiones." },
        { id: "battery", label: "Batería", description: "Módulo interno de energía, sin capacidad especificada." },
        { id: "camera", label: "Cámaras", description: "Conjunto de cámaras representado de forma general." }
    ],
    monitor: [
        { id: "case", label: "Carcasa", description: "Estructura exterior del monitor." },
        { id: "display", label: "Panel y cámara", description: "Superficie de visualización y cámara frontal ilustrativa." },
        { id: "board", label: "Controladora", description: "Zona esquemática de control y procesamiento de imagen." },
        { id: "stand", label: "Base y soporte", description: "Estructura ilustrativa de soporte." },
        { id: "ports", label: "Conexiones y controles", description: "Área visual de conectores y controles; no indica puertos específicos." }
    ],
    desktop: [
        { id: "case", label: "Chasis", description: "Estructura exterior del equipo." },
        { id: "board", label: "Placa base", description: "Zona ilustrativa para circuitos y conexiones principales." },
        { id: "cpu", label: "Procesador", description: "Procesador central representativo, sin modelo o rendimiento especificado." },
        { id: "cooling", label: "Refrigeración", description: "Ventiladores y flujo de aire ilustrativos." },
        { id: "gpu", label: "Tarjeta gráfica", description: "Tarjeta de expansión representativa; puede variar o no estar incluida." },
        { id: "memory", label: "Memoria RAM", description: "Módulos representativos, sin capacidad o generación especificada." },
        { id: "storage", label: "Almacenamiento", description: "Unidad representativa, sin capacidad o interfaz especificada." },
        { id: "power", label: "Fuente de poder", description: "Fuente representativa, sin potencia especificada." }
    ],
    audio: [
        { id: "band", label: "Diadema", description: "Estructura exterior de soporte." },
        { id: "driver", label: "Transductores", description: "Elementos de audio ilustrativos; no indican características acústicas." },
        { id: "cushion", label: "Almohadillas", description: "Superficies de contacto representadas de forma general." },
        { id: "controls", label: "Controles", description: "Zona genérica de controles y conexiones." }
    ],
    wearable: [
        { id: "case", label: "Carcasa", description: "Estructura exterior del dispositivo." },
        { id: "display", label: "Pantalla", description: "Panel frontal del dispositivo." },
        { id: "battery", label: "Batería", description: "Módulo interno de energía, sin capacidad especificada." },
        { id: "sensors", label: "Sensores", description: "Área esquemática para sensores; no representa mediciones específicas." },
        { id: "band", label: "Correa", description: "Estructura exterior de sujeción." }
    ],
    peripheral: [
        { id: "case", label: "Carcasa", description: "Estructura exterior del periférico." },
        { id: "keys", label: "Teclas", description: "Superficie de entrada representada de forma general." },
        { id: "board", label: "Circuitería", description: "Zona ilustrativa de circuitos y conexiones." },
        { id: "connection", label: "Conexión", description: "Conector representativo; el tipo depende del producto." }
    ],
    generic: [
        { id: "case", label: "Carcasa", description: "Estructura exterior del producto." },
        { id: "board", label: "Circuitería", description: "Zona ilustrativa de circuitos y conexiones." },
        { id: "power", label: "Alimentación", description: "Módulo de alimentación representado de forma general." }
    ],
    mouse: [
        { id: "case", label: "Carcasa", description: "Estructura exterior del periférico." },
        { id: "keys", label: "Controles", description: "Botones y rueda representados de forma general." },
        { id: "board", label: "Sensor", description: "Zona ilustrativa del sensor y la circuitería." },
        { id: "connection", label: "Conexión", description: "Conector representativo; el tipo depende del producto." }
    ],
    storage: [
        { id: "case", label: "Carcasa", description: "Estructura exterior de la unidad o accesorio." },
        { id: "storage", label: "Almacenamiento", description: "Unidad representativa, sin capacidad especificada." },
        { id: "board", label: "Controladora", description: "Zona ilustrativa de control y circuitos." },
        { id: "ports", label: "Conexiones", description: "Área visual de conectores; no indica puertos específicos." }
    ],
    hub: [
        { id: "case", label: "Carcasa", description: "Cuerpo exterior compacto del hub." },
        { id: "board", label: "Circuitería", description: "Circuito de distribución representativo." },
        { id: "ports", label: "Puertos", description: "Conectores ilustrativos; confirma los puertos del producto en sus especificaciones." },
        { id: "connection", label: "Cable y conector", description: "Conexión representativa; el tipo puede variar según el producto." }
    ]
};

function getModelType(category = "") {
    const name = category.toLocaleLowerCase();
    if (/laptop|notebook|port[aá]til/.test(name)) return "laptop";
    if (/smartphone|iphone|(?:^|[^a-z])phones?(?:$|[^a-z])|tel[eé]fono|tablet|e-ink/.test(name)) return "phone";
    if (/monitor|display|pantalla/.test(name)) return "monitor";
    if (/desktop|mini pc|all-in-one|computador de escritorio|pc de escritorio/.test(name)) return "desktop";
    if (/headphones?|headsets?|earbuds?|auriculares?|audio|aud[ií]fonos?/.test(name)) return "audio";
    if (/watch|wearable|reloj/.test(name)) return "wearable";
    if (/keyboard|teclado/.test(name)) return "peripheral";
    if (/mice|mouse|rat[oó]n/.test(name)) return "mouse";
    if (/hub|dock/.test(name)) return "hub";
    if (/ssd|storage|network|power/.test(name)) return "storage";
    return "generic";
}

export function getProductComponents(category) {
    const type = getModelType(category);
    if (/tablet|e-ink/i.test(category || "")) {
        return [
            { id: "display", label: "Pantalla", description: "Panel frontal de visualización." },
            { id: "board", label: "Placa base", description: "Zona ilustrativa para circuitos y conexiones." },
            { id: "battery", label: "Batería", description: "Módulo de energía, sin capacidad especificada." },
            { id: "camera", label: "Cámaras", description: "Conjunto representado de forma general." }
        ];
    }
    return componentCatalog[type];
}

export function getProductSpecs(productName = "", description = "") {
    const source = `${productName} ${description}`.replace(/\s+/g, " ").trim();
    const first = (pattern) => source.match(pattern)?.[0]?.trim() || "";
    const uniqueMatches = (pattern) => [...new Set(
        [...source.matchAll(pattern)].map(([value]) => value.trim())
    )];
    const displayDetails = uniqueMatches(/\b\d{1,2}(?:\.\d)?[\s-]*(?:"|inches?|inch)(?=\s|[|,;]|$)|\b\d{3,4}\s?[x×]\s?\d{3,4}\b|\b\d{2,3}\s?Hz\b|\b(?:Full\s?HD|FHD|QHD|WQHD|UHD|4K|2K|HD|OLED|IPS|AMOLED|Retina|Mini-LED|Touchscreen)\b/gi);
    const memory = first(/\b\d{1,3}\s?GB\s*(?:LP?DDR[345X]?|DDR[345X]?|RAM|memory)\b/i)
        || first(/\b\d{1,3}\s?GB\s*(?:unified\s+memory|unified\s+RAM)\b/i)
        || first(/\bRAM\s*(?:of|:)?\s*\d{1,3}\s?GB\b/i);
    const storage = uniqueMatches(/\b\d+(?:\.\d+)?\s?(?:TB|GB)\s*(?:(?:NVMe|PCIe|SATA|M\.2)\s*)?(?:SSD|SDD|HDD|eMMC|ROM|Storage)\b/gi);
    const expandableStorage = first(/\b(?:expandable|upgradable)\s+(?:to\s+)?\d+(?:\.\d+)?\s?(?:TB|GB)\b/i);
    if (expandableStorage && storage.length) storage[0] += ` (${expandableStorage})`;
    const ports = uniqueMatches(/\b(?:USB(?:[- ]?[A-Z0-9]+)?|Type-C|Thunderbolt(?:\s?\d)?|HDMI(?:\s?\d(?:\.\d)?)?|DisplayPort|RJ-45|Ethernet)\b/gi);
    const connectivity = uniqueMatches(/\b(?:Wi-?Fi\s?\d?|Bluetooth\s?[\d.]+|BT\s?[\d.]+|Wi-?Fi\s?6E)\b/gi);
    const batteryCapacity = first(/\b\d+(?:\.\d+)?\s?(?:mAh|Wh|watt-?hours?)\b/i);
    const batteryRuntime = first(/\b(?:up to\s*)?\d+(?:\.\d+)?\s*[- ]?\s*(?:hours?|hrs?|h)\s*(?:long\s*)?battery life\b/i)
        || first(/\bbattery life\s*(?:of|up to)?\s*\d+(?:\.\d+)?\s*[- ]?\s*(?:hours?|hrs?|h)\b/i);
    const graphics = first(/\b(?:NVIDIA\s+)?(?:GeForce\s+)?(?:RTX|GTX)\s?\d{3,4}(?:\s?Ti)?\b/i)
        || first(/\bAMD\s+Radeon\s+[A-Za-z0-9 ]+(?=\s*(?:\||,|;|$))/i)
        || first(/\bIntel\s+(?:UHD|HD|Iris|Arc)\s+Graphics\b/i);
    const processor = first(/\bAMD\s+Ryzen\s+[3579]\s+\d{4,5}[A-Z]{0,2}\b/i)
        || first(/\bAMD\s+Ryzen\s+[A-Za-z0-9-]+\b/i)
        || first(/\bIntel\s+(?:(?:Core\s+)?(?:i[3579]-?\d+[A-Z]*|Ultra\s+\d+\s+\d+[A-Z]*)|Pentium\s+[A-Za-z0-9-]+|Celeron\s+[A-Za-z0-9-]+)\b/i)
        || first(/\b(?:Celeron|Cerelon)\s+[A-Za-z0-9-]+\b/i)
        || first(/\b(?:Intel\s+(?:\d{1,2}(?:st|nd|rd|th)\s+Gen\s+)?)?N\d{2,4}\s*(?:\([^)]{0,30}\)\s*)?(?:Processor|CPU)\b/i)
        || first(/\bApple\s+M[1-9]\s*(?:Pro|Max|Ultra)?\b/i)
        || first(/\bSnapdragon\s+[A-Za-z0-9-]+\b/i)
        || first(/\b\d{4,5}[A-Z]{0,2}\s+Processor\b/i);
    const operatingSystem = first(/\b(?:Windows|Win)\s?\d+(?:\s(?:Home|Pro))?(?:\s+in S Mode)?\b/i)
        || first(/\b(?:macOS|ChromeOS|Linux|Android\s?\d*|iOS\s?\d*)\b/i);

    return {
        memory,
        storage: storage.join(" + "),
        processor,
        graphics,
        display: displayDetails.join(" · "),
        ports: ports.join(", "),
        connectivity: connectivity.join(", "),
        battery: [batteryCapacity, batteryRuntime].filter(Boolean).join(" · "),
        operatingSystem
    };
}

function makeMaterial(color, metalness = 0.08) {
    return new THREE.MeshStandardMaterial({
        color,
        roughness: 0.48,
        metalness,
        emissive: 0x000000
    });
}

function addBox(root, parts, partId, size, position, color, rotation = [0, 0, 0]) {
    const radius = Math.max(0.002, Math.min(...size) * 0.12);
    const mesh = new THREE.Mesh(
        new RoundedBoxGeometry(...size, 3, radius),
        makeMaterial(color)
    );
    mesh.position.set(...position);
    mesh.rotation.set(...rotation);
    mesh.userData.partId = partId;
    root.add(mesh);
    if (!parts.has(partId)) parts.set(partId, []);
    parts.get(partId).push(mesh);
    return mesh;
}

function addSphere(root, parts, partId, radius, position, color, segments = 12) {
    const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(radius, segments, 8),
        makeMaterial(color)
    );
    mesh.position.set(...position);
    mesh.userData.partId = partId;
    root.add(mesh);
    if (!parts.has(partId)) parts.set(partId, []);
    parts.get(partId).push(mesh);
    return mesh;
}

function addTorus(root, parts, partId, radius, tube, position, color, arc = Math.PI) {
    const mesh = new THREE.Mesh(
        new THREE.TorusGeometry(radius, tube, 8, 24, arc),
        makeMaterial(color)
    );
    mesh.position.set(...position);
    mesh.rotation.z = Math.PI;
    mesh.userData.partId = partId;
    root.add(mesh);
    if (!parts.has(partId)) parts.set(partId, []);
    parts.get(partId).push(mesh);
    return mesh;
}

function addCylinder(root, parts, partId, radiusTop, radiusBottom, height, position, color, radialSegments = 12) {
    const mesh = new THREE.Mesh(
        new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments),
        makeMaterial(color)
    );
    mesh.position.set(...position);
    mesh.userData.partId = partId;
    root.add(mesh);
    if (!parts.has(partId)) parts.set(partId, []);
    parts.get(partId).push(mesh);
    return mesh;
}

function buildLaptop(root, parts) {
    const chassis = addBox(root, parts, "case", [2.8, 0.14, 1.9], [0, 0, 0], 0x64748b);
    chassis.material.metalness = 0.68;
    chassis.material.roughness = 0.3;
    const bottomCover = addBox(root, parts, "case", [2.68, 0.035, 1.78], [0, -0.085, 0], 0x475569);
    bottomCover.material.metalness = 0.62;
    bottomCover.material.roughness = 0.34;
    const keyboardDeck = addBox(root, parts, "case", [2.62, 0.025, 1.72], [0, 0.078, 0.02], 0x94a3b8);
    keyboardDeck.material.metalness = 0.65;
    keyboardDeck.material.roughness = 0.32;

    addBox(root, parts, "display", [2.8, 1.8, 0.11], [0, 0.98, -0.91], 0x111827);
    const screen = addBox(root, parts, "display", [2.55, 1.54, 0.025], [0, 0.98, -0.84], 0xffffff);
    const screenCanvas = document.createElement("canvas");
    screenCanvas.width = 512;
    screenCanvas.height = 320;
    const screenContext = screenCanvas.getContext("2d");
    const screenGradient = screenContext.createLinearGradient(0, 0, 512, 320);
    screenGradient.addColorStop(0, "#10264a");
    screenGradient.addColorStop(0.52, "#2563a8");
    screenGradient.addColorStop(1, "#22a6a1");
    screenContext.fillStyle = screenGradient;
    screenContext.fillRect(0, 0, 512, 320);
    screenContext.fillStyle = "rgba(132, 204, 255, 0.32)";
    screenContext.beginPath();
    screenContext.ellipse(175, 105, 154, 104, -0.48, 0, Math.PI * 2);
    screenContext.fill();
    screenContext.fillStyle = "rgba(15, 23, 42, 0.72)";
    screenContext.fillRect(0, 294, 512, 26);
    screenContext.fillStyle = "rgba(255, 255, 255, 0.86)";
    screenContext.beginPath();
    screenContext.arc(24, 307, 6, 0, Math.PI * 2);
    screenContext.fill();
    for (let index = 0; index < 4; index += 1) {
        screenContext.fillStyle = `rgba(255, 255, 255, ${0.72 - index * 0.1})`;
        screenContext.fillRect(190, 92 + index * 31, 218 - index * 17, 15);
    }
    const screenTexture = new THREE.CanvasTexture(screenCanvas);
    screenTexture.colorSpace = THREE.SRGBColorSpace;
    screen.material = new THREE.MeshStandardMaterial({
        map: screenTexture,
        emissive: 0x17243a,
        emissiveMap: screenTexture,
        emissiveIntensity: 0.28,
        roughness: 0.3,
        metalness: 0.02
    });
    const hinge = addCylinder(root, parts, "display", 0.065, 0.065, 2.45, [0, 0.17, -0.78], 0x94a3b8, 16);
    hinge.rotation.z = Math.PI / 2;
    addSphere(root, parts, "display", 0.035, [0, 1.68, -0.84], 0x0f172a, 8);
    addSphere(root, parts, "display", 0.012, [0, 1.68, -0.858], 0x60a5fa, 8);
    addBox(root, parts, "keyboard", [2.47, 0.035, 0.94], [0, 0.116, 0.13], 0x334155);
    for (let row = 0; row < 4; row += 1) {
        for (let column = 0; column < 11; column += 1) {
            addBox(
                root,
                parts,
                "keyboard",
                [0.17, 0.035, 0.13],
                [-1.02 + column * 0.204, 0.15, -0.19 + row * 0.19],
                row === 0 ? 0xe2e8f0 : 0xf1f5f9
            );
        }
    }
    addBox(root, parts, "keyboard", [0.58, 0.035, 0.13], [0, 0.15, 0.58], 0xf1f5f9);
    addBox(root, parts, "keyboard", [0.72, 0.018, 0.38], [0, 0.14, 0.83], 0x1e293b);
    addBox(root, parts, "keyboard", [0.63, 0.012, 0.29], [0, 0.153, 0.83], 0x94a3b8);
    for (let side = -1; side <= 1; side += 2) {
        for (let index = 0; index < 5; index += 1) {
            addBox(root, parts, "keyboard", [0.035, 0.012, 0.035], [side * 1.12, 0.146, -0.19 + index * 0.075], 0x1e293b);
        }
    }
    for (let index = 0; index < 3; index += 1) {
        addBox(root, parts, "case", [0.16, 0.018, 0.035], [-0.48 + index * 0.48, -0.072, -0.82], 0x1e293b);
    }
    addBox(root, parts, "case", [0.24, 0.045, 0.055], [-1.36, 0.005, 0.42], 0x0f172a);
    addBox(root, parts, "case", [0.18, 0.045, 0.055], [-1.36, 0.005, 0.55], 0x0f172a);
    addBox(root, parts, "case", [0.2, 0.045, 0.055], [1.36, 0.005, 0.42], 0x0f172a);
    addBox(root, parts, "case", [0.16, 0.045, 0.055], [1.36, 0.005, 0.55], 0x0f172a);
    addBox(root, parts, "board", [0.95, 0.08, 0.56], [-0.62, -0.2, 0.45], 0x22c55e);
    addBox(root, parts, "cpu", [0.38, 0.1, 0.34], [-0.62, -0.08, 0.44], 0xe2e8f0);
    addBox(root, parts, "cooling", [0.5, 0.1, 0.48], [-1.12, -0.05, 0.45], 0x64748b);
    addCylinder(root, parts, "cooling", 0.2, 0.2, 0.08, [-1.12, 0.02, 0.45], 0x38bdf8, 16);
    addBox(root, parts, "memory", [0.12, 0.08, 0.4], [-0.04, -0.06, 0.43], 0x38bdf8);
    addBox(root, parts, "memory", [0.12, 0.08, 0.4], [0.12, -0.06, 0.43], 0x0ea5e9);
    addBox(root, parts, "storage", [0.42, 0.1, 0.25], [0.43, -0.05, 0.4], 0x8b5cf6);
    addBox(root, parts, "battery", [1.05, 0.12, 0.62], [0.72, -0.16, 0.48], 0x8b5cf6);
    addBox(root, parts, "battery", [0.22, 0.16, 0.3], [1.14, 0.05, -0.42], 0x0f172a);
    addBox(root, parts, "battery", [0.22, 0.16, 0.3], [-1.14, 0.05, -0.42], 0x0f172a);
    for (let index = 0; index < 3; index += 1) {
        addBox(root, parts, "board", [0.14, 0.12, 0.08], [-0.9 + index * 0.3, -0.03, 0.77], 0x94a3b8);
    }
    for (let index = 0; index < 3; index += 1) {
        addBox(root, parts, "board", [0.16, 0.045, 0.13], [-0.65 + index * 0.28, 0.015, 0.94], 0x0f172a);
    }
    addBox(root, parts, "board", [0.48, 0.05, 0.12], [1.32, 0.005, -0.2], 0x0f172a);
}

function buildPhone(root, parts) {
    const body = addBox(root, parts, "case", [1.22, 2.2, 0.16], [0, 0, 0], 0x64748b);
    body.material.metalness = 0.72;
    body.material.roughness = 0.28;
    addBox(root, parts, "display", [1.08, 2.02, 0.025], [0, 0, 0.095], 0x38bdf8);
    addBox(root, parts, "display", [0.38, 0.075, 0.025], [0, 0.96, 0.11], 0x0f172a);
    addSphere(root, parts, "camera", 0.035, [0.19, 0.96, 0.128], 0x111827, 10);
    addBox(root, parts, "display", [0.34, 0.035, 0.018], [0, -1.04, 0.105], 0xcbd5e1);

    addBox(root, parts, "battery", [0.72, 1.28, 0.025], [0, -0.02, -0.055], 0x8b5cf6);
    addBox(root, parts, "board", [0.55, 0.42, 0.025], [0, 0.78, -0.055], 0x22c55e);

    const cameraBump = addBox(root, parts, "camera", [0.42, 0.55, 0.07], [-0.34, 0.72, -0.105], 0x334155);
    cameraBump.material.metalness = 0.45;
    for (const [x, y] of [[-0.42, 0.88], [-0.25, 0.88], [-0.42, 0.62]]) {
        addSphere(root, parts, "camera", 0.065, [x, y, -0.15], 0x0f172a, 12);
        addSphere(root, parts, "camera", 0.032, [x, y, -0.186], 0x60a5fa, 10);
    }

    for (const [x, y] of [[-0.63, 0.55], [-0.63, 0.22], [0.63, 0.58], [0.63, 0.28]]) {
        addBox(root, parts, "case", [0.035, 0.16, 0.055], [x, y, 0], 0x334155);
    }
}

function buildMonitor(root, parts) {
    addBox(root, parts, "case", [2.8, 1.9, 0.14], [0, 0.5, 0], 0x334155);
    addBox(root, parts, "display", [2.58, 1.68, 0.025], [0, 0.5, 0.09], 0x38bdf8);
    addBox(root, parts, "case", [2.8, 0.09, 0.18], [0, 1.46, 0], 0x0f172a);
    addSphere(root, parts, "case", 0.035, [0, 1.46, 0.105], 0xe2e8f0, 8);
    addBox(root, parts, "stand", [0.35, 0.9, 0.35], [0, -0.82, 0], 0x64748b);
    addBox(root, parts, "stand", [1.5, 0.12, 0.75], [0, -1.32, 0], 0x475569);
    addBox(root, parts, "board", [0.72, 0.12, 0.4], [1.32, 0.48, -0.12], 0x22c55e);
    addBox(root, parts, "ports", [0.52, 0.16, 0.24], [1.3, -0.05, -0.12], 0x8b5cf6);
    for (let index = 0; index < 3; index += 1) {
        addBox(root, parts, "ports", [0.24, 0.045, 0.025], [1.12 + index * 0.19, -0.05, 0.02], 0x0f172a);
    }
}

function buildDesktop(root, parts) {
    addBox(root, parts, "case", [1.58, 2.34, 0.08], [0, 0, -0.42], 0x334155);
    addBox(root, parts, "case", [0.1, 2.32, 0.86], [-0.78, 0, 0], 0x475569);
    addBox(root, parts, "case", [0.1, 2.32, 0.86], [0.78, 0, 0], 0x475569);
    addBox(root, parts, "case", [1.5, 0.1, 0.86], [0, 1.12, 0], 0x475569);
    addBox(root, parts, "case", [1.5, 0.1, 0.86], [0, -1.12, 0], 0x475569);
    addBox(root, parts, "board", [1.08, 1.46, 0.11], [-0.03, 0.15, 0], 0x22c55e);
    addBox(root, parts, "cpu", [0.46, 0.42, 0.16], [-0.08, 0.52, 0.12], 0xcbd5e1);
    addBox(root, parts, "cpu", [0.34, 0.3, 0.035], [-0.08, 0.52, 0.22], 0x64748b);
    addBox(root, parts, "memory", [0.16, 0.86, 0.13], [0.33, 0.2, 0.15], 0x38bdf8);
    addBox(root, parts, "memory", [0.16, 0.86, 0.13], [0.56, 0.2, 0.15], 0x38bdf8);
    addBox(root, parts, "gpu", [1.18, 0.28, 0.48], [0.02, -0.42, 0.2], 0x64748b);
    addBox(root, parts, "gpu", [0.52, 0.06, 0.04], [0.02, -0.42, 0.45], 0x38bdf8);
    addBox(root, parts, "storage", [0.48, 0.16, 0.34], [0.48, 0.88, 0.17], 0x8b5cf6);
    addBox(root, parts, "power", [0.78, 0.38, 0.66], [0.32, -0.88, -0.02], 0x334155);
    for (const [x, y] of [[-0.44, 0.75], [0.45, 0.75], [-0.44, -0.65]]) {
        addTorus(root, parts, "cooling", 0.31, 0.055, [x, y, 0.28], 0x38bdf8, Math.PI * 2);
        addCylinder(root, parts, "cooling", 0.23, 0.23, 0.045, [x, y, 0.3], 0x1e293b, 20);
        addCylinder(root, parts, "cooling", 0.07, 0.07, 0.055, [x, y, 0.33], 0xe2e8f0, 12);
    }
    addBox(root, parts, "case", [0.56, 1.65, 0.025], [0.39, 0.06, 0.49], 0x1e293b);
}

function buildAudio(root, parts) {
    const headbandCurve = new THREE.CubicBezierCurve3(
        new THREE.Vector3(-0.74, -0.06, 0),
        new THREE.Vector3(-0.82, 1.35, 0),
        new THREE.Vector3(0.82, 1.35, 0),
        new THREE.Vector3(0.74, -0.06, 0)
    );
    const headband = new THREE.Mesh(
        new THREE.TubeGeometry(headbandCurve, 28, 0.105, 10, false),
        makeMaterial(0x334155, 0.42)
    );
    headband.userData.partId = "band";
    root.add(headband);
    parts.set("band", [headband]);

    const innerBandCurve = new THREE.CubicBezierCurve3(
        new THREE.Vector3(-0.69, -0.02, 0.035),
        new THREE.Vector3(-0.74, 1.2, 0.035),
        new THREE.Vector3(0.74, 1.2, 0.035),
        new THREE.Vector3(0.69, -0.02, 0.035)
    );
    const innerBand = new THREE.Mesh(
        new THREE.TubeGeometry(innerBandCurve, 24, 0.045, 8, false),
        makeMaterial(0x0f172a)
    );
    innerBand.userData.partId = "band";
    root.add(innerBand);
    parts.get("band").push(innerBand);

    for (const side of [-1, 1]) {
        const x = side * 0.75;
        const y = -0.34;
        addBox(root, parts, "band", [0.11, 0.35, 0.18], [side * 0.72, -0.08, 0], 0x64748b);

        const cup = addCylinder(root, parts, "cushion", 0.38, 0.38, 0.27, [x, y, 0], 0x1e293b, 32);
        cup.rotation.x = Math.PI / 2;
        const cushionRing = new THREE.Mesh(
            new THREE.TorusGeometry(0.29, 0.085, 10, 32),
            makeMaterial(0x0b1220)
        );
        cushionRing.position.set(x, y, 0.17);
        cushionRing.userData.partId = "cushion";
        root.add(cushionRing);
        parts.get("cushion").push(cushionRing);

        const driver = addCylinder(root, parts, "driver", 0.205, 0.205, 0.035, [x, y, 0.15], 0x475569, 32);
        driver.rotation.x = Math.PI / 2;
        const driverCap = new THREE.Mesh(
            new THREE.TorusGeometry(0.14, 0.018, 6, 24),
            makeMaterial(0x38bdf8, 0.22)
        );
        driverCap.position.set(x, y, 0.19);
        driverCap.userData.partId = "driver";
        root.add(driverCap);
        parts.get("driver").push(driverCap);
        addSphere(root, parts, "driver", 0.06, [x, y, 0.205], 0x0f172a, 12);

        for (let index = 0; index < 3; index += 1) {
            addSphere(root, parts, "controls", 0.035, [x + side * 0.37, y + 0.11 - index * 0.1, 0.02], 0x94a3b8, 8);
        }
    }
}

function buildWearable(root, parts) {
    addBox(root, parts, "band", [0.48, 1.3, 0.16], [0, 1.05, 0], 0x475569);
    addBox(root, parts, "band", [0.48, 1.3, 0.16], [0, -1.05, 0], 0x475569);
    addBox(root, parts, "case", [1.1, 1.18, 0.2], [0, 0, 0], 0x334155);
    addBox(root, parts, "display", [0.88, 0.92, 0.025], [0, 0, 0.12], 0x38bdf8);
    addBox(root, parts, "battery", [0.65, 0.42, 0.12], [1, 0.4, 0], 0x8b5cf6);
    addBox(root, parts, "sensors", [0.62, 0.42, 0.12], [-1, -0.4, 0], 0x22c55e);
}

function buildPeripheral(root, parts) {
    addBox(root, parts, "case", [2.8, 0.16, 1.25], [0, 0, 0], 0x334155);
    addBox(root, parts, "board", [2.45, 0.055, 1.05], [0, -0.075, 0], 0x22c55e);
    for (let row = 0; row < 5; row += 1) {
        const keyCount = [14, 14, 14, 13, 12][row];
        const keyWidth = row === 4 ? 0.16 : 0.145;
        const rowWidth = keyCount * 0.18;
        const startX = -rowWidth / 2 + 0.09;
        for (let column = 0; column < keyCount; column += 1) {
            const isSpacebar = row === 4 && column >= 3 && column <= 8;
            if (isSpacebar && column !== 5) continue;
            addBox(
                root,
                parts,
                "keys",
                [isSpacebar ? 0.78 : keyWidth, 0.07, 0.15],
                [isSpacebar ? 0 : startX + column * 0.18, 0.12, -0.49 + row * 0.23],
                row === 0 ? 0x38bdf8 : 0xe2e8f0
            );
        }
    }
    const cable = addCylinder(root, parts, "connection", 0.035, 0.035, 0.38, [0, 0, -0.78], 0x64748b, 10);
    cable.rotation.x = Math.PI / 2;
    addBox(root, parts, "connection", [0.18, 0.12, 0.1], [0, 0, -0.98], 0x8b5cf6);
}

function buildGeneric(root, parts) {
    addBox(root, parts, "case", [1.8, 1.55, 0.65], [0, 0, 0], 0x334155);
    addBox(root, parts, "board", [1.15, 0.12, 0.72], [1.35, 0.15, 0], 0x22c55e);
    addBox(root, parts, "power", [0.78, 0.24, 0.55], [-1.25, -0.58, 0], 0x8b5cf6);
}

function buildMouse(root, parts) {
    const shell = addSphere(root, parts, "case", 0.65, [0, 0, 0], 0x334155, 16);
    shell.scale.set(0.82, 0.48, 1.15);
    addBox(root, parts, "keys", [0.09, 0.08, 0.66], [0, 0.28, 0], 0x38bdf8);
    addBox(root, parts, "board", [0.5, 0.08, 0.58], [1.05, 0, 0], 0x22c55e);
    addBox(root, parts, "connection", [0.28, 0.12, 0.16], [-0.95, 0, 0], 0x8b5cf6);
}

function buildStorage(root, parts) {
    addBox(root, parts, "case", [1.8, 0.46, 1.15], [0, 0, 0], 0x334155);
    addBox(root, parts, "storage", [1.3, 0.12, 0.72], [1.25, 0.1, 0], 0x8b5cf6);
    addBox(root, parts, "board", [0.72, 0.12, 0.58], [-1.22, 0.1, 0], 0x22c55e);
    addBox(root, parts, "ports", [0.3, 0.16, 0.26], [-1.28, -0.22, 0], 0x38bdf8);
}

function buildHub(root, parts) {
    addBox(root, parts, "case", [1.8, 0.32, 0.82], [0.25, 0, 0], 0x334155);
    addBox(root, parts, "board", [1.35, 0.08, 0.56], [0.25, -0.04, 0], 0x22c55e);
    for (let index = 0; index < 4; index += 1) {
        addBox(root, parts, "ports", [0.22, 0.14, 0.3], [-0.35 + index * 0.4, 0.03, 0.31], 0x0f172a);
        addBox(root, parts, "ports", [0.22, 0.14, 0.3], [-0.35 + index * 0.4, 0.03, -0.31], 0x0f172a);
    }
    const cable = addCylinder(root, parts, "connection", 0.07, 0.07, 0.68, [-0.95, 0, 0], 0x64748b, 10);
    cable.rotation.z = Math.PI / 2;
    addBox(root, parts, "connection", [0.3, 0.14, 0.24], [-1.36, 0, 0], 0x38bdf8);
}

const builders = {
    laptop: buildLaptop,
    phone: buildPhone,
    monitor: buildMonitor,
    desktop: buildDesktop,
    audio: buildAudio,
    wearable: buildWearable,
    peripheral: buildPeripheral,
    mouse: buildMouse,
    storage: buildStorage,
    hub: buildHub,
    generic: buildGeneric
};

export function mountProductViewer(container, category, onPartSelected = () => {}) {
    let handlePartSelected = onPartSelected;
    const renderer = new THREE.WebGLRenderer({
        alpha: true,
        antialias: false,
        powerPreference: "low-power"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.25));
    renderer.setClearColor(0x000000, 0);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;

    scene.add(new THREE.HemisphereLight(0xe2e8f0, 0x334155, 2.2));
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.1);
    keyLight.position.set(3, 5, 4);
    scene.add(keyLight);
    const fillLight = new THREE.DirectionalLight(0x93c5fd, 1.1);
    fillLight.position.set(-4, 2, 3);
    scene.add(fillLight);
    const rimLight = new THREE.DirectionalLight(0xffffff, 1.25);
    rimLight.position.set(1, 3, -4);
    scene.add(rimLight);

    const root = new THREE.Group();
    const model = new THREE.Group();
    const initialRotation = new THREE.Euler(-0.06, -0.42, 0);
    root.rotation.copy(initialRotation);
    root.add(model);
    scene.add(root);
    const parts = new Map();
    builders[getModelType(category)](model, parts);
    const modelBounds = new THREE.Box3().setFromObject(model);
    const modelCenter = modelBounds.getCenter(new THREE.Vector3());
    const modelRadius = modelBounds.getBoundingSphere(new THREE.Sphere()).radius;
    model.position.sub(modelCenter);
    container.replaceChildren(renderer.domElement);
    let isExploded = false;
    const viewDirection = new THREE.Vector3(3.2, 2.6, 7.5).normalize();
    const worldUp = new THREE.Vector3(0, 1, 0);
    const cameraRight = new THREE.Vector3().crossVectors(worldUp, viewDirection).normalize();
    const cameraUp = new THREE.Vector3().crossVectors(viewDirection, cameraRight).normalize();

    const render = () => {
        const width = Math.max(1, container.clientWidth);
        const height = Math.max(1, container.clientHeight);
        camera.aspect = width / height;
        const verticalFov = THREE.MathUtils.degToRad(camera.fov);
        const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * camera.aspect);
        root.updateMatrixWorld(true);
        const corner = new THREE.Vector3();
        let fitDistance = 0;
        const verticalSlope = Math.tan(verticalFov / 2);
        const horizontalSlope = Math.tan(horizontalFov / 2);
        parts.forEach((meshes) => {
            meshes.forEach((mesh) => {
                if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
                const bounds = mesh.geometry.boundingBox;
                for (let xIndex = 0; xIndex < 2; xIndex += 1) {
                    for (let yIndex = 0; yIndex < 2; yIndex += 1) {
                        for (let zIndex = 0; zIndex < 2; zIndex += 1) {
                            corner.set(
                                xIndex ? bounds.max.x : bounds.min.x,
                                yIndex ? bounds.max.y : bounds.min.y,
                                zIndex ? bounds.max.z : bounds.min.z
                            );
                            corner.applyMatrix4(mesh.matrixWorld);
                            const depth = corner.dot(viewDirection);
                            const horizontal = Math.abs(corner.dot(cameraRight)) / horizontalSlope;
                            const vertical = Math.abs(corner.dot(cameraUp)) / verticalSlope;
                            fitDistance = Math.max(fitDistance, depth + horizontal, depth + vertical);
                        }
                    }
                }
            });
        });
        fitDistance = Math.max(fitDistance + (isExploded ? 0.75 : 0), modelRadius * 0.2) * 1.12;
        camera.position.copy(viewDirection).multiplyScalar(fitDistance);
        camera.near = Math.max(0.05, fitDistance / 100);
        camera.far = fitDistance + modelRadius * 8;
        camera.lookAt(0, 0, 0);
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
        renderer.render(scene, camera);
    };

    let resizeObserver;
    const handleResize = () => render();
    if (typeof ResizeObserver !== "undefined") {
        resizeObserver = new ResizeObserver(handleResize);
        resizeObserver.observe(container);
    } else {
        window.addEventListener("resize", handleResize);
    }

    const originalPositions = new Map();
    const directions = new Map();
    parts.forEach((meshes, id) => {
        const center = new THREE.Vector3();
        meshes.forEach((mesh) => center.add(mesh.position));
        center.divideScalar(meshes.length);
        if (center.lengthSq() < 0.05) {
            const fallbackDirections = {
                case: new THREE.Vector3(0, 0, -1),
                board: new THREE.Vector3(-1, 0, 0),
                display: new THREE.Vector3(0, 1, 0),
                battery: new THREE.Vector3(1, -0.2, 0),
                ports: new THREE.Vector3(0, -1, 1)
            };
            center.copy(fallbackDirections[id] || new THREE.Vector3(0, 0, 1));
        }
        directions.set(id, center.normalize());
        meshes.forEach((mesh) => originalPositions.set(mesh, mesh.position.clone()));
    });

    let pointerStart;
    let hasDragged = false;
    const handlePointerDown = (event) => {
        pointerStart = { x: event.clientX, y: event.clientY };
        hasDragged = false;
        renderer.domElement.setPointerCapture(event.pointerId);
    };
    const handlePointerMove = (event) => {
        if (!pointerStart || !renderer.domElement.hasPointerCapture(event.pointerId)) return;
        const deltaX = event.clientX - pointerStart.x;
        const deltaY = event.clientY - pointerStart.y;
        if (Math.abs(deltaX) + Math.abs(deltaY) > 3) hasDragged = true;
        root.rotation.y += deltaX * 0.008;
        root.rotation.x = THREE.MathUtils.clamp(root.rotation.x + deltaY * 0.006, -0.7, 0.7);
        pointerStart = { x: event.clientX, y: event.clientY };
        render();
    };
    const handlePointerUp = (event) => {
        if (renderer.domElement.hasPointerCapture(event.pointerId)) {
            renderer.domElement.releasePointerCapture(event.pointerId);
        }
        pointerStart = null;
        if (!hasDragged) {
            const bounds = renderer.domElement.getBoundingClientRect();
            const pointer = new THREE.Vector2(
                ((event.clientX - bounds.left) / bounds.width) * 2 - 1,
                -((event.clientY - bounds.top) / bounds.height) * 2 + 1
            );
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(pointer, camera);
            const hit = raycaster.intersectObjects(root.children, true)
                .find(({ object }) => object.userData.partId);
            if (hit) selectPart(hit.object.userData.partId);
        }
    };
    const handlePointerCancel = () => {
        pointerStart = null;
    };

    renderer.domElement.addEventListener("pointerdown", handlePointerDown);
    renderer.domElement.addEventListener("pointermove", handlePointerMove);
    renderer.domElement.addEventListener("pointerup", handlePointerUp);
    renderer.domElement.addEventListener("pointercancel", handlePointerCancel);

    render();

    function selectPart(partId) {
        const selected = getProductComponents(category).find((component) => component.id === partId);
        if (!selected) return;
        parts.forEach((meshes, id) => {
            meshes.forEach((mesh) => {
                mesh.material.emissive.setHex(id === partId ? 0x2563eb : 0x000000);
                mesh.material.emissiveIntensity = id === partId ? 0.9 : 0;
            });
        });
        render();
        handlePartSelected(selected);
    }

    function toggleExploded() {
        isExploded = !isExploded;
        parts.forEach((meshes, id) => {
            const direction = directions.get(id);
            meshes.forEach((mesh) => {
                const original = originalPositions.get(mesh);
                mesh.position.copy(original);
                if (isExploded) mesh.position.addScaledVector(direction, 0.72);
            });
        });
        render();
        return isExploded;
    }

    function resetView() {
        root.rotation.copy(initialRotation);
        if (isExploded) toggleExploded();
        render();
    }

    return {
        selectPart,
        toggleExploded,
        resetView,
        setOnPartSelected(callback) {
            handlePartSelected = callback;
        },
        dispose() {
            if (resizeObserver) resizeObserver.disconnect();
            else window.removeEventListener("resize", handleResize);
            renderer.domElement.removeEventListener("pointerdown", handlePointerDown);
            renderer.domElement.removeEventListener("pointermove", handlePointerMove);
            renderer.domElement.removeEventListener("pointerup", handlePointerUp);
            renderer.domElement.removeEventListener("pointercancel", handlePointerCancel);
            root.traverse((object) => {
                if (!object.isMesh) return;
                object.geometry.dispose();
                if (object.material.map) object.material.map.dispose();
                if (object.material.emissiveMap && object.material.emissiveMap !== object.material.map) {
                    object.material.emissiveMap.dispose();
                }
                object.material.dispose();
            });
            renderer.dispose();
            renderer.forceContextLoss();
            renderer.domElement.remove();
        }
    };
}
