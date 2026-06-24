from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import base64

from src.etl.data_loader import load_dataset
from src.utils.config import BASE_DIR
from src.utils.sample_data import load_or_create_sample_data
from src.utils.design_tokens import get_tokens
from src.utils.ui_components import inject_ui_styles, table_with_search_pagination


def configure_page(title: str) -> None:
    st.set_page_config(page_title=f"RetailPulse | {title}", page_icon="RP", layout="wide")

    # ensure theme key
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"

    # provide a theme selector in the sidebar (Light / Dark)
    with st.sidebar:
        st.markdown("## Appearance")
        _ = st.radio("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, key="theme")
        st.caption("Toggle theme for the app. This updates the design tokens.")

    # design tokens for both modes (kept minimal here)
    if st.session_state.theme == "Dark":
        tokens = {"bg": "#0F172A", "surface": "#0b1220", "primary": "#00d2ff", "primary-2": "#7cf9ff", "gold": "#d4af37", "muted": "#9ca3af", "text": "#e6eef2"}
    else:
        tokens = {"bg": "#F8FAFC", "surface": "#FFFFFF", "primary": "#2563EB", "primary-2": "#3B82F6", "gold": "#b8860b", "muted": "#475569", "text": "#0F172A"}

    # prepare logo src: prefer custom assets if present
    logo_custom_png = BASE_DIR / "assets" / "logo_custom.png"
    logo_custom_svg = BASE_DIR / "assets" / "logo_custom.svg"
    if logo_custom_png.exists():
        with open(logo_custom_png, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_src = f"data:image/png;base64,{img_b64}"
    elif logo_custom_svg.exists():
        with open(logo_custom_svg, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_src = f"data:image/svg+xml;base64,{img_b64}"
    else:
        logo_src = "assets/logo_icon.svg"

    # Inject a small set of global styles — keep CSS concise to avoid f-string brace issues
    header_html = f"""
    <style>
    :root {{ --rp-gold: {tokens['gold']}; --rp-accent1: {tokens['primary']}; --rp-bg: {tokens['bg']}; --rp-text: {tokens['text']}; --rp-muted: {tokens['muted']}; }}
    html, body, .stApp {{ background: var(--rp-bg) !important; color: var(--rp-text) !important; }}
    .section-title {{ font-weight:700; color: var(--rp-accent1); }}
    .rp-attribution {{ position: fixed; right: 12px; bottom: 8px; font-size: 0.85rem; color: var(--rp-muted); background: transparent; z-index: 2000; opacity: 0.95; padding: 6px 10px; border-radius: 6px; }}
    </style>
    <div class="rp-attribution">made by ATULYA RAJ SINGH</div>
    """

    st.markdown(header_html, unsafe_allow_html=True)

    # Inject global UI styles (animations, buttons, cards, tables)
    st.markdown(inject_ui_styles(get_tokens("dark" if st.session_state.get("theme", "Dark") == "Dark" else "light")), unsafe_allow_html=True)


def load_dashboard_data() -> dict[str, pd.DataFrame]:
    if "retailpulse_data" not in st.session_state:
        st.session_state.retailpulse_data = load_or_create_sample_data(BASE_DIR / "data" / "sample")
    return st.session_state.retailpulse_data


def upload_data_sidebar() -> dict[str, pd.DataFrame]:
    data = load_dashboard_data()
    with st.sidebar:
        # Collapsible, iconized sidebar menu
        collapsed = st.session_state.get("rp_sidebar_collapsed", False)
        if st.button("☰" if not collapsed else "→", key="rp_toggle_sidebar"):
            st.session_state["rp_sidebar_collapsed"] = not collapsed
            st.experimental_rerun()

        if st.session_state.get("rp_sidebar_collapsed"):
            try:
                st.image(str(BASE_DIR / "assets" / "logo_icon.svg"), width=38)
            except Exception:
                st.markdown("<div style='width:38px;height:38px;background:transparent;'></div>", unsafe_allow_html=True)
        else:
            try:
                st.image(str(BASE_DIR / "assets" / "logo_full.svg"), width=140)
            except Exception:
                st.markdown("<div style='height:48px;background:transparent;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<div style='font-weight:700;margin-bottom:6px'>Navigation</div>", unsafe_allow_html=True)
        # simple icon list (can be replaced with SVG icons later)
        nav_items = [
            ("🏠", "Home"),
            ("📊", "Analytics"),
            ("📈", "Forecasting"),
            ("📁", "Reports"),
            ("⚙️", "Settings"),
        ]
        for icon, label in nav_items:
            if st.button(f"{icon}  {label}", key=f"nav_{label}"):
                st.session_state["rp_active_page"] = label
                st.experimental_rerun()

        st.markdown("---")
        st.header("Data")
        st.caption("Upload CSV files or continue with realistic sample data.")
        for name in ["sales", "customers", "inventory", "transactions"]:
            uploaded = st.file_uploader(f"{name}.csv", type=["csv"], key=f"upload_{name}")
            if uploaded is not None:
                data[name] = load_dataset(name, uploaded)
                st.success(f"Loaded {name}: {len(data[name]):,} rows")
        if st.button("Reset sample data", use_container_width=True):
            st.session_state.retailpulse_data = load_or_create_sample_data(BASE_DIR / "data" / "sample")
            st.rerun()
    return data


def kpi_row(metrics: list[tuple[str, str | int | float, str | None]]) -> None:
    columns = st.columns(len(metrics))
    for column, (label, value, delta) in zip(columns, metrics, strict=True):
        column.metric(label, value, delta=delta)


def sales_filters(sales: pd.DataFrame) -> pd.DataFrame:
    frame = sales.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    with st.sidebar:
        products = sorted(frame["product_id"].unique())
        selected_products = st.multiselect("Products", products, default=products[: min(len(products), 5)])
        min_date, max_date = frame["date"].min().date(), frame["date"].max().date()
        selected_range = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
    if selected_products:
        frame = frame[frame["product_id"].isin(selected_products)]
    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start, end = pd.to_datetime(selected_range[0]), pd.to_datetime(selected_range[1])
        frame = frame[(frame["date"] >= start) & (frame["date"] <= end)]
    return frame


def download_frame(label: str, frame: pd.DataFrame, filename: str) -> None:
    st.download_button(label, frame.to_csv(index=False), file_name=filename, mime="text/csv", use_container_width=True)


def revenue_chart(sales: pd.DataFrame):
    daily = sales.groupby("date", as_index=False).agg(revenue=("revenue", "sum"), quantity_sold=("quantity_sold", "sum"))
    dark = st.session_state.get("theme", "Dark") == "Dark"
    tokens = get_tokens("dark" if dark else "light")
    fig = px.line(daily, x="date", y="revenue", title="Revenue Trend", template=("plotly_dark" if dark else "plotly_white"), color_discrete_sequence=[tokens.get("accent", "#00d2ff")])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=tokens.get("text", "#e6eef2"), height=300)
    return fig


def category_chart(sales: pd.DataFrame):
    if "category" not in sales.columns:
        dark = st.session_state.get("theme", "Dark") == "Dark"
        tokens = get_tokens("dark" if dark else "light")
        fig = px.bar(
            sales.groupby("product_id", as_index=False)["revenue"].sum(),
            x="product_id",
            y="revenue",
            title="Revenue by Product",
            template=("plotly_dark" if dark else "plotly_white"),
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=tokens.get("text", "#e6eef2"), height=300)
        return fig
    return px.bar(
        sales.groupby("category", as_index=False)["revenue"].sum(),
        x="category",
        y="revenue",
        color="category",
        title="Revenue by Category",
        template=("plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"),
        color_discrete_sequence=px.colors.qualitative.Plotly,
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=(get_tokens("dark").get("text") if st.session_state.get("theme", "Dark") == "Dark" else get_tokens("light").get("text")), height=300)
