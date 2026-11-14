from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go

from models import catalog


def init_admin_dash(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/admin/analytics/",
        title="Analítica Integral | LePetit Admin",
        external_stylesheets=["/static/css/styles.css", "/static/css/admin.css"],
    )
    dash_app.layout = html.Main(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.Span(
                                "PORTAL ADMINISTRATIVO · INTELIGENCIA DE NEGOCIO",
                                style={
                                    "fontSize": "0.75rem",
                                    "fontWeight": "700",
                                    "letterSpacing": "0.08em",
                                    "color": "#2563eb",
                                    "display": "block",
                                    "marginBottom": "0.25rem",
                                },
                            ),
                            html.H1(
                                "Analítica Integral de Inventario, Categorías, Clientes y Pedidos",
                                style={"margin": "0 0 0.35rem 0", "fontSize": "1.75rem"},
                            ),
                            html.P(
                                "Explora el rendimiento por línea de producto, valorización de stock, segmentación VIP y alertas de reabastecimiento.",
                                className="muted",
                                style={"margin": "0"},
                            ),
                        ]
                    ),
                    html.Nav(
                        [
                            html.A(
                                "← Volver al Panel Admin",
                                href="/admin/dashboard",
                                className="button button-hero",
                                style={
                                    "background": "#2563eb",
                                    "color": "#ffffff",
                                    "padding": "0.6rem 1.15rem",
                                    "borderRadius": "6px",
                                    "fontWeight": "600",
                                    "textDecoration": "none",
                                },
                            ),
                            html.A(
                                "Productos",
                                href="/admin/productos",
                                className="button button-secondary button-sm",
                            ),
                            html.A(
                                "Categorías y Cupones",
                                href="/admin/categorias",
                                className="button button-secondary button-sm",
                            ),
                            html.A(
                                "Pedidos",
                                href="/admin/pedidos",
                                className="button button-secondary button-sm",
                            ),
                            html.A(
                                "Clientes",
                                href="/admin/clientes",
                                className="button button-secondary button-sm",
                            ),
                            html.A(
                                "Salir a la Tienda",
                                href="/tienda",
                                className="button button-secondary button-sm",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "gap": "0.55rem",
                            "alignItems": "center",
                        },
                    ),
                ],
                className="admin-panel",
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "1.25rem",
                    "marginBottom": "1.5rem",
                },
            ),
            dcc.Interval(
                id="admin-analytics-refresh",
                interval=300_000,
                n_intervals=0,
            ),
            html.Div(id="admin-analytics-metrics", className="stats-grid"),
            html.Section(
                [
                    html.Div(
                        [
                            html.Strong(
                                "Filtrar análisis detallado por Categoría Principal:",
                                style={"fontSize": "0.9rem"},
                            ),
                            dcc.Dropdown(
                                id="admin-analytics-category-filter",
                                options=[
                                    {"label": "Todas las categorías (Vista global)", "value": "all"}
                                ],
                                value="all",
                                clearable=False,
                                style={"minWidth": "300px"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "alignItems": "center",
                            "justifyContent": "space-between",
                            "gap": "1rem",
                        },
                    )
                ],
                className="admin-panel",
                style={"marginBottom": "1.5rem"},
            ),
            html.Div(
                [
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-categories-chart",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-value-chart",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                ],
                className="admin-two-cols",
            ),
            html.Div(
                [
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-stock",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-low-stock-chart",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                ],
                className="admin-two-cols",
            ),
            html.Div(
                [
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-clients-chart",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                    html.Section(
                        dcc.Graph(
                            id="admin-analytics-orders-chart",
                            config={"displayModeBar": False, "responsive": True},
                        ),
                        className="admin-panel",
                    ),
                ],
                className="admin-two-cols",
            ),
            html.Section(
                [
                    html.H2(
                        "Matriz Comparativa por Categoría Principal",
                        style={"fontSize": "1.15rem", "marginBottom": "1rem"},
                    ),
                    html.Div(
                        id="admin-analytics-categories-table",
                        className="admin-table-wrapper",
                    ),
                ],
                className="admin-panel",
                style={"marginTop": "1.5rem"},
            ),
        ],
        className="admin-dashboard-container",
        style={
            "maxWidth": "1340px",
            "margin": "1.5rem auto 3rem",
            "padding": "0 1.25rem",
            "fontFamily": "system-ui, sans-serif",
        },
    )

    @dash_app.callback(
        Output("admin-analytics-metrics", "children"),
        Output("admin-analytics-stock", "figure"),
        Input("admin-analytics-refresh", "n_intervals"),
    )
    def refresh_dashboard(_):
        stats = catalog.fetch_dashboard_stats()
        products = catalog.fetch_top_products(limit=8)
        metrics = [
            ("Productos", stats["total_products"]),
            ("Categorías", stats["total_categories"]),
            ("Clientes", stats["total_clients"]),
            ("Stock", f'{stats["total_stock"]:,}'),
            ("Bajo stock", stats["low_stock_count"]),
        ]
        cards = [
            html.Article(
                [html.P(label, className="stat-label"), html.H2(value, className="stat-number")],
                className="stat-card",
            )
            for label, value in metrics
        ]
        figure = go.Figure(
            go.Bar(
                x=[product.stock for product in products],
                y=[product.nombre[:36] for product in products],
                orientation="h",
                marker_color="#2563eb",
                hovertemplate="%{y}<br>Stock: %{x}<extra></extra>",
            )
        )
        figure.update_layout(
            title="Stock de productos destacados",
            xaxis_title="Unidades disponibles",
            yaxis_title="Producto",
            yaxis={"autorange": "reversed"},
            template="plotly_white",
            margin={"l": 12, "r": 16, "t": 48, "b": 44},
            autosize=True,
        )
        return cards, figure

    @dash_app.callback(
        Output("admin-analytics-category-filter", "options"),
        Output("admin-analytics-categories-chart", "figure"),
        Output("admin-analytics-value-chart", "figure"),
        Output("admin-analytics-low-stock-chart", "figure"),
        Output("admin-analytics-clients-chart", "figure"),
        Output("admin-analytics-orders-chart", "figure"),
        Output("admin-analytics-categories-table", "children"),
        Input("admin-analytics-refresh", "n_intervals"),
        Input("admin-analytics-category-filter", "value"),
    )
    def refresh_extended_analytics(_, selected_category):
        cat_filter = None
        if selected_category and str(selected_category) != "all":
            try:
                cat_filter = int(selected_category)
            except ValueError:
                cat_filter = None

        breakdown = catalog.fetch_analytics_breakdown(category_id=cat_filter)
        categories_summary = breakdown["categories_summary"]
        low_stock_products = breakdown["low_stock_products"]
        roles_summary = breakdown["roles_summary"]
        orders_summary = breakdown["orders_summary"]

        dropdown_options = [
            {"label": "Todas las categorías (Vista global)", "value": "all"}
        ] + [
            {
                "label": f"{c['categoria']} ({c['total_products']} prod. · {c['total_stock']:,} uds.)",
                "value": str(c["id_main_cat"]),
            }
            for c in categories_summary
        ]

        cat_names = [c["categoria"] for c in categories_summary]
        cat_prod_counts = [c["total_products"] for c in categories_summary]
        cat_low_counts = [c["low_stock_count"] for c in categories_summary]

        categories_fig = go.Figure(
            data=[
                go.Bar(
                    name="Total Productos",
                    x=cat_names,
                    y=cat_prod_counts,
                    marker_color="#2563eb",
                ),
                go.Bar(
                    name="En Bajo Stock (<15 uds.)",
                    x=cat_names,
                    y=cat_low_counts,
                    marker_color="#f59e0b",
                ),
            ]
        )
        categories_fig.update_layout(
            title="Análisis por Categoría: Cantidad de Productos vs. Alertas de Bajo Stock",
            xaxis_title="Categoría Principal",
            yaxis_title="Número de Productos",
            barmode="group",
            template="plotly_white",
            margin={"l": 16, "r": 16, "t": 48, "b": 64},
            legend={"orientation": "h", "y": 1.12},
            autosize=True,
        )

        value_fig = go.Figure(
            data=[
                go.Bar(
                    x=[c["total_value_usd"] for c in categories_summary],
                    y=cat_names,
                    orientation="h",
                    marker_color="#0f172a",
                    customdata=[c["total_stock"] for c in categories_summary],
                    hovertemplate=(
                        "<b>%{y}</b><br>Valor inventario: $%{x:,.2f} USD"
                        "<br>Unidades en stock: %{customdata:,}<extra></extra>"
                    ),
                )
            ]
        )
        value_fig.update_layout(
            title="Valorización de Inventario (USD) y Volumen por Categoría",
            xaxis_title="Valor Total en Inventario (USD)",
            yaxis_title="Categoría",
            yaxis={"autorange": "reversed"},
            template="plotly_white",
            margin={"l": 16, "r": 16, "t": 48, "b": 44},
            autosize=True,
        )

        low_stock_fig = go.Figure(
            go.Bar(
                x=[p.stock for p in low_stock_products],
                y=[f"{p.nombre[:32]} ({p.categoria[:14]})" for p in low_stock_products],
                orientation="h",
                marker_color="#dc2626",
                hovertemplate="%{y}<br>Stock crítico: %{x} uds.<extra></extra>",
            )
        )
        low_stock_fig.update_layout(
            title="Productos Críticos con Bajo Stock (< 15 unidades)",
            xaxis_title="Unidades restantes",
            yaxis_title="Producto",
            yaxis={"autorange": "reversed"},
            template="plotly_white",
            margin={"l": 12, "r": 16, "t": 48, "b": 44},
            autosize=True,
        )

        clients_fig = go.Figure(
            go.Pie(
                labels=["Clientes Estándar", "Clientes VIP (10% Dto.)", "Administradores"],
                values=[
                    roles_summary.get("cliente", 0),
                    roles_summary.get("vip", 0),
                    roles_summary.get("admin", 0),
                ],
                hole=0.45,
                marker={"colors": ["#3b82f6", "#f59e0b", "#0f172a"]},
            )
        )
        clients_fig.update_layout(
            title="Distribución de Usuarios y Membresías por Rol",
            template="plotly_white",
            margin={"l": 16, "r": 16, "t": 48, "b": 32},
            autosize=True,
        )

        orders_fig = go.Figure(
            go.Bar(
                x=["Pendientes", "Confirmados", "Cancelados"],
                y=[
                    orders_summary.get("pending_confirmation", 0),
                    orders_summary.get("confirmed", 0),
                    orders_summary.get("cancelled", 0),
                ],
                marker_color=["#f59e0b", "#16a34a", "#dc2626"],
                hovertemplate="Estado: %{x}<br>Pedidos: %{y}<extra></extra>",
            )
        )
        orders_fig.update_layout(
            title="Estado Operativo de Pedidos Registrados",
            xaxis_title="Estado de la Orden",
            yaxis_title="Cantidad de Pedidos",
            template="plotly_white",
            margin={"l": 16, "r": 16, "t": 48, "b": 44},
            autosize=True,
        )

        table = html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Categoría Principal"),
                            html.Th("Total Productos"),
                            html.Th("Unidades en Stock"),
                            html.Th("Productos en Bajo Stock"),
                            html.Th("Calificación Promedio"),
                            html.Th("Valorización (USD)"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(html.Strong(c["categoria"])),
                                html.Td(f"{c['total_products']:,}"),
                                html.Td(f"{c['total_stock']:,} uds."),
                                html.Td(
                                    html.Span(
                                        f"{c['low_stock_count']} alertas",
                                        className=(
                                            "badge badge-warning"
                                            if c["low_stock_count"] > 0
                                            else "badge badge-success"
                                        ),
                                    )
                                ),
                                html.Td(f"{c['avg_rating']:.2f} / 5.0"),
                                html.Td(f"${c['total_value_usd']:,.2f} USD"),
                            ]
                        )
                        for c in categories_summary
                    ]
                ),
            ],
            className="admin-table",
        )

        return (
            dropdown_options,
            categories_fig,
            value_fig,
            low_stock_fig,
            clients_fig,
            orders_fig,
            table,
        )

    return dash_app
