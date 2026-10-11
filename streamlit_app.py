import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import torch

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Boom by Booms — Final Research Dashboard",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# MODELS
# ============================================================
class DefenceForecastNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(2, 8),
            torch.nn.ReLU(),
            torch.nn.Linear(8, 1),
        )

    def forward(self, x):
        return self.network(x)


@st.cache_resource
def load_defence_model():
    model = DefenceForecastNet()
    model.load_state_dict(
        torch.load(
            ROOT / "models" / "defence_exports_model.pth",
            map_location="cpu",
            weights_only=True,
        )
    )
    model.eval()
    return model


@st.cache_resource
def load_space_model():
    model = torch.nn.Linear(1, 1)
    model.load_state_dict(
        torch.load(
            ROOT / "models" / "space_nsil_revenue_model.pth",
            map_location="cpu",
            weights_only=True,
        )
    )
    model.eval()
    return model


def defence_forecast(model, a, b):
    with torch.no_grad():
        return model(torch.tensor([[float(a), float(b)]], dtype=torch.float32)).item()


def space_forecast(model):
    # Training time indices: 0..5 = FY2019-20..FY2024-25.
    # Therefore FY2025-26 is index 6.
    x_mean = 2.5
    x_std = (35.0 / 12.0) ** 0.5
    y_mean = 182195.6083333333
    y_std = 107603.27170338602

    x_next = torch.tensor([[(6.0 - x_mean) / x_std]], dtype=torch.float32)
    with torch.no_grad():
        y_std_pred = model(x_next).item()
    return y_std_pred * y_std + y_mean


def load_metadata():
    with open(ROOT / "metadata.json", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# DATA
# ============================================================
def load_data():
    defence = pd.read_csv(ROOT / "data" / "defence_exports.csv")
    nsil = pd.read_csv(ROOT / "data" / "nsil_total_revenue.csv")
    space_trade = pd.read_csv(ROOT / "data" / "space_trade.csv")
    gdp_fx = pd.read_csv(ROOT / "data" / "gdp_fx.csv")
    return defence, nsil, space_trade, gdp_fx


def prepare_macro_ratios(defence, space_trade, gdp_fx):
    df = gdp_fx.copy()
    df["gdp_current_crore"] = df["gdp_current_lakh_crore"] * 100000
    df["gdp_real_crore"] = df["gdp_constant_2011_12_lakh_crore"] * 100000
    df["gdp_deflator"] = df["gdp_current_crore"] / df["gdp_real_crore"]

    df["defence_export_crore"] = df["FY"].map(
        defence.set_index("FY")["defence_exports_crore"]
    )
    df["space_export_crore"] = df["FY"].map(
        space_trade.set_index("FY")["space_exports_crore"]
    )
    df["space_import_crore"] = df["FY"].map(
        space_trade.set_index("FY")["space_imports_crore"]
    )

    # Nominal export shares.
    df["defence_nominal_share_pct"] = (
        df["defence_export_crore"] / df["gdp_current_crore"] * 100
    )
    df["space_nominal_share_pct"] = (
        df["space_export_crore"] / df["gdp_current_crore"] * 100
    )

    # Analytical real-export proxy: deflate exports using GDP deflator.
    df["defence_real_proxy_crore"] = df["defence_export_crore"] / df["gdp_deflator"]
    df["space_real_proxy_crore"] = df["space_export_crore"] / df["gdp_deflator"]
    df["defence_real_share_pct"] = (
        df["defence_real_proxy_crore"] / df["gdp_real_crore"] * 100
    )
    df["space_real_share_pct"] = (
        df["space_real_proxy_crore"] / df["gdp_real_crore"] * 100
    )

    # USD presentation. Same FX basis for exports and GDP means the percentage is unchanged.
    df["defence_export_usd_million"] = (
        df["defence_export_crore"] * 10 / df["inr_per_usd_avg"]
    )
    df["space_export_usd_million"] = (
        df["space_export_crore"] * 10 / df["inr_per_usd_avg"]
    )
    df["gdp_usd_billion"] = (
        df["gdp_current_crore"] / df["inr_per_usd_avg"] / 100
    )
    df["defence_usd_share_pct"] = (
        df["defence_export_usd_million"] / (df["gdp_usd_billion"] * 1000) * 100
    )
    df["space_usd_share_pct"] = (
        df["space_export_usd_million"] / (df["gdp_usd_billion"] * 1000) * 100
    )
    return df


# ============================================================
# PLOTS
# ============================================================
def style_axes(ax):
    ax.grid(True, alpha=0.22, linewidth=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_series(df, x, y, title, ylabel, label=None):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(df[x], df[y], marker="o", linewidth=2, label=label)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel("Financial year")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)
    style_axes(ax)
    if label:
        ax.legend()
    fig.tight_layout()
    return fig


def plot_dual_share(df, nominal_col, real_col, title):
    d = df.dropna(subset=[nominal_col, real_col])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(d["FY"], d[nominal_col], marker="o", linewidth=2, label="Nominal basis")
    ax.plot(d["FY"], d[real_col], marker="o", linewidth=2, linestyle="--", label="Real basis / proxy")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel("Financial year")
    ax.set_ylabel("Exports as % of GDP")
    ax.tick_params(axis="x", rotation=45)
    style_axes(ax)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_usd_share(df, col, title):
    d = df.dropna(subset=[col])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(d["FY"], d[col], marker="o", linewidth=2)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel("Financial year")
    ax.set_ylabel("Exports as % of GDP")
    ax.tick_params(axis="x", rotation=45)
    style_axes(ax)
    fig.tight_layout()
    return fig


def plot_defence_forecast(defence, model, forecast):
    vals = defence["defence_exports_crore"].tolist()
    years = defence["FY"].tolist()
    predicted = [None, None]
    for i in range(2, len(vals)):
        predicted.append(defence_forecast(model, vals[i - 2], vals[i - 1]))

    x = years + ["2025-26"]
    actual = vals + [None]
    preds = predicted + [None]
    fcast = [None] * len(vals) + [forecast]

    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(x, actual, marker="o", linewidth=2, label="Verified historical")
    ax.plot(x, preds, marker="o", linestyle="--", linewidth=1.7, label="Model prediction")
    ax.plot(x, fcast, marker="o", markersize=8, linestyle="--", linewidth=2,
            label="FY2025-26 experimental forecast")
    ax.set_title("Defence Exports — Actual, Model Prediction and Forecast", loc="left", fontweight="bold")
    ax.set_xlabel("Financial year")
    ax.set_ylabel("₹ crore")
    ax.tick_params(axis="x", rotation=45)
    style_axes(ax)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_nsil_forecast(nsil, forecast_lakh):
    d = nsil.copy()
    d["Revenue (₹ crore)"] = d["total_revenue_lakh"] / 100
    x = d["FY"].tolist() + ["2025-26"]
    y = d["Revenue (₹ crore)"].tolist() + [None]
    f = [None] * len(d) + [forecast_lakh / 100]

    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(x, y, marker="o", linewidth=2, label="Verified historical")
    ax.plot(x, f, marker="o", markersize=8, linestyle="--", linewidth=2,
            label="FY2025-26 experimental forecast")
    ax.set_title("NSIL Total Revenue — Historical Trajectory and Forecast", loc="left", fontweight="bold")
    ax.set_xlabel("Financial year")
    ax.set_ylabel("₹ crore")
    ax.tick_params(axis="x", rotation=45)
    style_axes(ax)
    ax.legend()
    fig.tight_layout()
    return fig


# ============================================================
# APP
# ============================================================
metadata = load_metadata()
defence, nsil, space_trade, gdp_fx = load_data()
macro = prepare_macro_ratios(defence, space_trade, gdp_fx)

dmodel = load_defence_model()
space_model = load_space_model()
d_forecast = defence_forecast(
    dmodel,
    defence.iloc[-2]["defence_exports_crore"],
    defence.iloc[-1]["defence_exports_crore"],
)
s_forecast_lakh = space_forecast(space_model)
s_forecast_crore = s_forecast_lakh / 100

st.title("Boom by Booms — Strategic Defence & Space Research Dashboard")
st.caption(
    "Final reproducible dashboard: verified historical series, macroeconomic ratios, space trade, "
    "forecast outputs and the PyTorch implementation used for the forecasting extension."
)

c1, c2 = st.columns(2)
with c1:
    st.metric("Defence exports — FY2025-26 experimental forecast", f"₹{d_forecast:,.2f} crore")
with c2:
    st.metric("NSIL revenue — FY2025-26 experimental forecast", f"₹{s_forecast_crore:,.2f} crore")

st.divider()

# ============================================================
# I
# ============================================================
st.header("I. Export value over time")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Indian defence exports")
    st.pyplot(plot_series(defence, "FY", "defence_exports_crore", "Indian Defence Exports", "₹ crore"), clear_figure=True)
with col2:
    st.subheader("Indian space-technology-industry exports")
    st.pyplot(plot_series(space_trade, "FY", "space_exports_crore", "Space-Technology-Industry Exports", "₹ crore"), clear_figure=True)

st.info(
    "The space export series is specifically the Department of Space/ISRO parliamentary series for the "
    "space technology industry (FY2014-15 to FY2021-22). It is not substituted with NSIL revenue."
)

# ============================================================
# II
# ============================================================
st.header("II. Exports as a percentage of GDP — nominal and real")
st.caption(
    "Real export values are analytical proxies: nominal exports are deflated using the GDP deflator "
    "because a dedicated export-price deflator is not in the project dataset."
)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Defence exports / GDP")
    st.pyplot(plot_dual_share(macro, "defence_nominal_share_pct", "defence_real_share_pct", "Defence Exports as % of GDP"), clear_figure=True)
with col2:
    st.subheader("Space exports / GDP")
    st.pyplot(plot_dual_share(macro, "space_nominal_share_pct", "space_real_share_pct", "Space Exports as % of GDP"), clear_figure=True)

# ============================================================
# III
# ============================================================
st.header("III. Exports as a percentage of GDP — USD presentation")
st.caption(
    "Rupee values are converted using the annual-average ₹/US$ rate. Because exports and GDP use the same "
    "FX conversion, the resulting percentage is mathematically identical to the nominal rupee ratio."
)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Defence exports / GDP — USD basis")
    st.pyplot(plot_usd_share(macro, "defence_usd_share_pct", "Defence Exports as % of GDP — USD Basis"), clear_figure=True)
with col2:
    st.subheader("Space exports / GDP — USD basis")
    st.pyplot(plot_usd_share(macro, "space_usd_share_pct", "Space Exports as % of GDP — USD Basis"), clear_figure=True)

# ============================================================
# IV
# ============================================================
st.header("IV. Forecast trajectory and contextual events")
st.info(
    "Forecasts are exploratory model outputs, not official projections. Documented public–private events are "
    "shown as context and are not treated as causal interventions."
)
st.pyplot(plot_defence_forecast(defence, dmodel, d_forecast), clear_figure=True)
st.pyplot(plot_nsil_forecast(nsil, s_forecast_lakh), clear_figure=True)

events = pd.DataFrame([
    ["2020-12-03", "Agnikul Cosmos", "NDA / access to ISRO facilities and expertise"],
    ["2021-09-11", "Skyroot Aerospace", "Framework MoU / access to facilities and expertise"],
    ["2021-09-17", "Agnikul Cosmos", "Framework MoU / access to facilities and expertise"],
    ["2022-11", "Agnikul Cosmos", "Launchpad, mission-control, hot-test and FTS support"],
    ["2022-11-18", "Skyroot Aerospace", "Launch facilitation / technical support for Vikram-S"],
    ["2024-03-27", "Skyroot Aerospace", "KALAM-250 static-test infrastructure/support"],
    ["2024-05-30", "Agnikul Cosmos", "Launch facilitation / mission support for Agnibaan SOrTeD"],
    ["2024-12-16", "Agnikul Cosmos", "TDB financial assistance: ₹18 crore"],
], columns=["Date", "Company", "Documented mechanism"])
st.subheader("Documented public–private space collaboration events")
st.dataframe(events, use_container_width=True, hide_index=True)

# ============================================================
# V
# ============================================================
st.header("V. Value of space imports")
st.pyplot(plot_series(space_trade, "FY", "space_imports_crore", "Space-Technology-Industry Imports", "₹ crore"), clear_figure=True)
st.caption(
    "Official annual series currently available in the cited Department of Space / ISRO parliamentary answer: FY2014-15 to FY2021-22."
)

# ============================================================
# VI
# ============================================================
st.header("VI. Defence export value")
st.pyplot(plot_series(defence, "FY", "defence_exports_crore", "Value of Indian Defence Exports", "₹ crore"), clear_figure=True)

# ============================================================
# PYTORCH CODE SHOWCASE
# ============================================================
st.divider()
st.header("PyTorch forecast — implementation showcase")
st.caption(
    "This is a readable excerpt of the actual forecasting architecture and inference logic used in the project. "
    "The complete development notebook remains part of the reproducibility package."
)

with st.expander("1. Neural-network architecture — Defence exports", expanded=True):
    st.code('''class DefenceForecastNet(nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.network = nn.Sequential(\n            nn.Linear(2, 8),\n            nn.ReLU(),\n            nn.Linear(8, 1)\n        )\n\n    def forward(self, x):\n        return self.network(x)''', language="python")

with st.expander("2. Training setup"):
    st.code('''torch.manual_seed(42)\n\nmodel = DefenceForecastNet()\ncriterion = nn.MSELoss()\noptimizer = torch.optim.Adam(model.parameters(), lr=0.001)\n\nfor epoch in range(1000):\n    optimizer.zero_grad()\n    prediction = model(X_train_tensor)\n    loss = criterion(prediction, y_train_tensor)\n    loss.backward()\n    optimizer.step()''', language="python")

with st.expander("3. One-step forecast inference"):
    st.code('''with torch.no_grad():\n    next_input = torch.tensor([[21083.0, 23622.0]])\n    forecast = model(next_input).item()\n\n# FY2025-26 experimental forecast\n# ≈ ₹27,107.97 crore''', language="python")

with st.expander("4. Why the project keeps this forecast short-horizon"):
    st.markdown(
        "The annual defence-export series contains only nine observations. The model was evaluated on a "
        "chronological held-out test set of three observations. A longer recursive 2030/2035 trajectory can be "
        "generated mathematically, but it is not presented here as a reliable forecast because the available "
        "series is too short for that claim."
    )

# ============================================================
# DATA / MODEL INFORMATION
# ============================================================
st.divider()
st.header("Data, model and provenance")
info = pd.DataFrame([
    ["Defence forecast", "2016-17–2024-25 exports", "2→8→ReLU→1 feed-forward network", "FY2025-26", "Experimental"],
    ["Space forecast", "FY2019-20–FY2024-25 NSIL revenue", "1→1 linear trend", "FY2025-26", "Experimental"],
    ["Space trade", "FY2014-15–FY2021-22 imports/exports", "Official parliamentary series", "Historical", "Verified source"],
    ["GDP/FX layer", "FY2014-15–FY2024-25", "MoSPI/RBI-based macro layer", "Historical", "Source-vintage documented"],
], columns=["Component", "Data", "Method", "Period", "Status"])
st.dataframe(info, use_container_width=True, hide_index=True)

st.markdown("### Source register")
st.markdown(
    "- Department of Space / ISRO parliamentary answer: annual space-technology-industry imports and exports, FY2014-15–FY2021-22.\n"
    "- MoSPI / National Accounts: GDP at current and constant prices.\n"
    "- RBI / FBIL: annual-average ₹/US$ exchange rates.\n"
    "- DDP / Ministry of Defence: defence-export series.\n"
    "- NSIL / ISRO annual reports: NSIL financial and commercial-space context."
)

st.caption(
    "Research rule: annual, quarterly, event-specific and cumulative observations are not silently mixed. "
    "No missing years have been imputed in the official space-trade series."
)
