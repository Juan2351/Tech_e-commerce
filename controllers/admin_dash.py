from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go

from models import catalog


def init_admin_dash(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/admin/analytics/",
        title="Analítica | LePetit Admin",
        external_stylesheets=["/static/css/styles.css"],
    )
    dash_app.layout = html.Main(
        [
            html.Header(
                [
                    html.H1("Analítica de inventario"),
                    html.P(
                        "Indicadores del catálogo y stock de productos destacados.",
                        className="muted",
                    ),
                    html.A("Volver al panel", href="/admin/dashboard"),
                ],
                style={"marginBottom": "1.5rem"},
            ),
            dcc.Interval(
                id="admin-analytics-refresh",
                interval=300_000,
                n_intervals=0,
            ),
            html.Div(id="admin-analytics-metrics", className="stats-grid"),
            html.Section(
                dcc.Graph(
                    id="admin-analytics-stock",
                    config={"displayModeBar": False, "responsive": True},
                ),
                className="admin-panel",
                style={"marginTop": "1.5rem"},
            ),
        ],
        className="admin-dashboard-container",
        style={
            "maxWidth": "1280px",
            "margin": "2rem auto",
            "padding": "1.5rem",
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
                [html.P(label), html.H2(value)],
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

    return dash_app
