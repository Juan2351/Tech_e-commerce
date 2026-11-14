import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";

const specLabels = {
  memory: "Memoria RAM",
  storage: "Almacenamiento",
  processor: "Procesador",
  graphics: "Gráficos",
  display: "Pantalla",
  ports: "Puertos",
  connectivity: "Conectividad",
  battery: "Batería",
  operatingSystem: "Sistema operativo",
};

const specKeysByPart = {
  battery: ["battery"],
  board: ["processor", "memory", "storage"],
  connection: ["ports", "connectivity"],
  controls: ["ports", "connectivity"],
  cpu: ["processor"],
  cushion: [],
  display: ["display"],
  gpu: ["graphics"],
  keys: [],
  case: [],
  band: [],
  cooling: [],
  stand: [],
  sensors: [],
  memory: ["memory"],
  ports: ["ports", "connectivity"],
  storage: ["storage"],
};

function getPartSpecs(component, specs) {
  const keys = specKeysByPart[component.id] || [];
  if (keys.length === 0) {
    return [{
      key: "catalog",
      label: "Dato técnico",
      value: "No hay una especificación publicada para esta parte.",
    }];
  }
  return keys.map((key) => ({ key, label: specLabels[key], value: specs[key] }));
}

function ProductComponents({ components, viewer, product }) {
  const [selectedId, setSelectedId] = useState(components[0]?.id ?? "");
  const [isExploded, setIsExploded] = useState(false);
  const selected = components.find((component) => component.id === selectedId);
  const selectedSpecs = selected ? getPartSpecs(selected, product.specs) : [];

  useEffect(() => {
    viewer.setOnPartSelected((component) => setSelectedId(component.id));
    return () => viewer.setOnPartSelected(() => {});
  }, [viewer]);

  function selectComponent(componentId) {
    setSelectedId(componentId);
    viewer.selectPart(componentId);
  }

  return (
    <div className="product-3d-explorer bootstrap-scope">
      <header className="product-3d-explorer-heading">
        <span className="product-3d-eyebrow">EXPLORACIÓN INTERACTIVA</span>
        <h2>Conoce cada componente</h2>
        <p>{product.name}</p>
      </header>

      <label className="product-3d-select-label" htmlFor="product-3d-component-select">
        Elige un componente
      </label>
      <select
        className="form-select product-3d-component-select"
        id="product-3d-component-select"
        value={selectedId}
        onChange={(event) => selectComponent(event.target.value)}
      >
        {components.map((component) => (
          <option key={component.id} value={component.id}>
            {component.label}
          </option>
        ))}
      </select>

      {selected && (
        <section className="product-3d-spec-card" aria-live="polite">
          <div className="product-3d-selected-heading">
            <div>
              <span className="product-3d-eyebrow">COMPONENTE SELECCIONADO</span>
              <h3>{selected.label}</h3>
            </div>
            <span className="product-3d-selected-mark" aria-hidden="true">✓</span>
          </div>
          <p className="product-3d-component-description">{selected.description}</p>
          <dl className="product-3d-spec-grid">
            {selectedSpecs.map((spec) => (
              <div className="product-3d-spec-item" key={spec.key}>
                <dt>{spec.label}</dt>
                <dd>{spec.value || "No especificado en el catálogo"}</dd>
              </div>
            ))}
          </dl>
          <p className="product-3d-source-note">
            Las especificaciones se extraen de la información publicada del producto. Si un dato no aparece, se indica como no especificado.
          </p>
        </section>
      )}

      <div className="product-3d-toolbar">
        <button
          className="btn btn-outline-secondary product-3d-action"
          type="button"
          onClick={() => setIsExploded(viewer.toggleExploded())}
          aria-pressed={isExploded}
        >
          {isExploded ? "Reunir componentes" : "Separar componentes"}
        </button>
        <button
          className="btn btn-outline-secondary product-3d-action"
          type="button"
          onClick={() => {
            viewer.resetView();
            setIsExploded(false);
          }}
        >
          Restablecer vista
        </button>
        <span className="product-3d-interaction-hint">Arrastra para girar · toca una pieza para ver sus datos</span>
      </div>
    </div>
  );
}

export function mountProductComponents(container, components, viewer, product) {
  const root = createRoot(container);
  root.render(
    <ProductComponents
      components={components}
      viewer={viewer}
      product={product}
    />,
  );
  return () => root.unmount();
}
