from pathlib import Path
from datetime import datetime, timezone
import io
import math
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="ATE Quality Control Suite | OPAx140 TIA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    FOLDER = Path(__file__).resolve().parent
except NameError:
    FOLDER = Path.cwd()

if "lot_mode" not in st.session_state:
    st.session_state.lot_mode = "precision"
if "overlay" not in st.session_state:
    st.session_state.overlay = False
if "lsl" not in st.session_state:
    st.session_state.lsl = 790.0
if "usl" not in st.session_state:
    st.session_state.usl = 820.0
if "batch" not in st.session_state:
    st.session_state.batch = 10000
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "trigger_print" not in st.session_state:
    st.session_state.trigger_print = False

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    header[data-testid="stHeader"], [data-testid="stSidebar"] {
        display: none !important;
    }
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 1600px !important;
    }

    div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.75rem !important;
        min-height: 34px !important;
        width: 100%;
    }
    div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover {
        background-color: #334155 !important;
        border-color: #475569 !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: rgba(16, 185, 129, 0.18) !important;
        color: #34d399 !important;
        border: 1px solid #10b981 !important;
    }
    div[data-testid="stDownloadButton"] > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
    }

    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #090d16 !important;
        border: 1px solid #334155 !important;
        border-radius: 5px !important;
    }
    input {
        color: #f8fafc !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        background-color: #090d16 !important;
    }
    div[data-testid="stNumberInput"] label, div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label {
        font-size: 11px !important;
        color: #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
    }

    .top-bar {
        background: #0f172a;
        border-bottom: 1px solid #1e293b;
        padding: 12px 18px;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .sub-bar {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 8px;
        margin-bottom: 16px;
    }
    .verdict-banner {
        border-radius: 8px;
        padding: 14px 20px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .verdict-pass {
        background: rgba(6, 78, 59, 0.35);
        border: 1px solid rgba(16, 185, 129, 0.45);
        color: #d1fae5;
    }
    .verdict-fail {
        background: rgba(136, 19, 55, 0.35);
        border: 1px solid rgba(244, 63, 94, 0.45);
        color: #ffe4e6;
    }
    .dot-pass {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 12px #34d399;
        display: inline-block;
        margin-right: 10px;
    }
    .dot-fail {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #f43f5e;
        box-shadow: 0 0 12px #f43f5e;
        display: inline-block;
        margin-right: 10px;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 12px;
        margin-bottom: 18px;
    }
    .kpi-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 14px 16px;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-title {
        font-size: 11px;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
        white-space: nowrap;
    }
    .kpi-val {
        font-size: 24px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
    }
    .kpi-sub {
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        color: #94a3b8;
        white-space: nowrap;
    }

    .panel {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        margin-bottom: 18px;
        overflow: hidden;
    }
    .panel-header {
        background: #161f33;
        border-bottom: 1px solid #1f2937;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .panel-title {
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        text-transform: uppercase;
    }
    .panel-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }
    .panel-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        background: #1e293b;
        color: #cbd5e1;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .ate-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }
    .ate-table th {
        text-align: left;
        padding: 8px 12px;
        color: #94a3b8;
        border-bottom: 1px solid #1f2937;
        text-transform: uppercase;
        font-size: 11px;
    }
    .ate-table td {
        padding: 7px 12px;
        border-bottom: 1px solid rgba(31, 41, 55, 0.7);
        color: #e2e8f0;
    }
    .pass-pill {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .fail-pill {
        background: rgba(244, 63, 94, 0.2);
        color: #fda4af;
        border: 1px solid rgba(244, 63, 94, 0.35);
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def load_clean_data(source) -> pd.DataFrame:
    df = pd.read_csv(source, sep=r"\s+", engine="python").dropna()
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce").dropna().drop_duplicates("run")
    df["run"] = df["run"].round().astype(int)
    return df.sort_values("run").reset_index(drop=True)


def compute_stats(df: pd.DataFrame, lsl_khz: float, usl_khz: float) -> dict:
    bw = df["bandwidth"].to_numpy()
    n = len(bw)
    low_hz, high_hz = lsl_khz * 1e3, usl_khz * 1e3
    mean_hz = float(np.mean(bw))
    std_hz = float(np.std(bw, ddof=1))
    var_hz = float(np.var(bw, ddof=1))
    min_hz, max_hz = float(np.min(bw)), float(np.max(bw))
    spread_pct = 100.0 * (max_hz - min_hz) / mean_hz

    cp = (high_hz - low_hz) / (6.0 * std_hz)
    cpu = (high_hz - mean_hz) / (3.0 * std_hz)
    cpl = (mean_hz - low_hz) / (3.0 * std_hz)
    cpk = min(cpu, cpl)
    sigma_lvl = 3.0 * cpk

    p_fail = normal_cdf((low_hz - mean_hz) / std_hz) + (1.0 - normal_cdf((high_hz - mean_hz) / std_hz))
    ppm = max(0, int(round(p_fail * 1e6)))

    passed = (bw >= low_hz) & (bw <= high_hz)
    pass_cnt = int(np.count_nonzero(passed))
    fail_cnt = int(n - pass_cnt)
    yield_pct = 100.0 * pass_cnt / n

    res = df.copy()
    res["serial"] = [f"SN-2026-{r:03d} (#{r})" for r in res["run"]]
    res["bw_hz"] = bw.round(1)
    res["bw_khz"] = (bw / 1e3).round(3)
    res["dev_pct"] = (100.0 * (bw - mean_hz) / mean_hz).round(3)
    res["z_score"] = ((bw - mean_hz) / std_hz).round(2)
    res["margin_khz"] = (np.minimum(bw - low_hz, high_hz - bw) / 1e3).round(2)
    res["result"] = np.where(passed, "PASS", "FAIL")

    return {
        "n": n, "bw": bw, "bw_khz": bw / 1e3,
        "mean_hz": mean_hz, "std_hz": std_hz, "var_hz": var_hz,
        "mean_khz": mean_hz / 1e3, "std_khz": std_hz / 1e3,
        "min_hz": min_hz, "max_hz": max_hz,
        "min_khz": min_hz / 1e3, "max_khz": max_hz / 1e3,
        "spread_pct": spread_pct, "cp": cp, "cpk": cpk,
        "sigma": sigma_lvl, "ppm": ppm,
        "pass_cnt": pass_cnt, "fail_cnt": fail_cnt, "yield_pct": yield_pct,
        "rows": res
    }


df_std = load_clean_data(FOLDER / "circuit.log.txt")
df_prec = load_clean_data(FOLDER / "circuitsim2.log.txt")

if st.session_state.lot_mode == "standard":
    active_df = df_std
    lot_id = "LOT-A: Standard Parts (5% R1, 10% Cf)"
    r_tol_svg, c_tol_svg = "{mc(100K, 0.05)} ±5%", "Cf=2pF {mc(2p, 0.1)} ±10%"
    bom_r1, bom_cf = "R1: 100 kΩ ±5% Thick-Film Carbon", "Cf: 2 pF ±10% Class-II Ceramic"
    schem_badge = "Baseline Schematic (circuit.asc)"
elif st.session_state.lot_mode == "custom" and "custom_df" in st.session_state:
    active_df = st.session_state.custom_df
    lot_id = f"Uploaded: {st.session_state.custom_name}"
    r_tol_svg, c_tol_svg = "Custom R1 Tolerance", "Custom Cf Tolerance"
    bom_r1, bom_cf = "R1: Custom Uploaded Lot", "Cf: Custom Uploaded Lot"
    schem_badge = "Custom Simulation Log"
else:
    active_df = df_prec
    lot_id = "LOT-B: Precision Parts (1% R1, 2% Cf)"
    r_tol_svg, c_tol_svg = "{mc(100K, 0.01)} ±1%", "Cf=2pF {mc(2p, 0.02)} ±2%"
    bom_r1, bom_cf = "R1: 100 kΩ ±1% Metal Thin-Film", "Cf: 2 pF ±2% C0G / NP0 Dielectric"
    schem_badge = "Upgraded Schematic (circuit (1).asc)"

s = compute_stats(active_df, st.session_state.lsl, st.session_state.usl)
other_bw_khz = (df_prec["bandwidth"].to_numpy() if st.session_state.lot_mode == "standard" else df_std["bandwidth"].to_numpy()) / 1e3

fig1, ax1 = plt.subplots(figsize=(6.8, 3.6), facecolor="#111827")
ax1.set_facecolor("#0b0f19")
for sp in ax1.spines.values():
    sp.set_color("#1e293b")

min_x = min(776.0, st.session_state.lsl - 4.0, float(np.min(s["bw_khz"])) - 2.0)
max_x = max(826.0, st.session_state.usl + 4.0, float(np.max(s["bw_khz"])) + 2.0)
bins = np.linspace(min_x, max_x, 15)

ax1.axvspan(st.session_state.lsl, st.session_state.usl, color="#10b981", alpha=0.12)
if st.session_state.overlay:
    ax1.hist(other_bw_khz, bins=bins, color="#a855f7", edgecolor="#a855f7", alpha=0.35, label="Comparison Lot")

counts, edges, patches = ax1.hist(s["bw_khz"], bins=bins, color="#38bdf8", edgecolor="#0f172a", alpha=0.78)
for b_l, b_r, p in zip(edges[:-1], edges[1:], patches):
    if 0.5 * (b_l + b_r) < st.session_state.lsl or 0.5 * (b_l + b_r) > st.session_state.usl:
        p.set_facecolor("#f43f5e")

x_curve = np.linspace(min_x, max_x, 250)
pdf = (1.0 / (s["std_khz"] * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x_curve - s["mean_khz"]) / s["std_khz"]) ** 2)
ax1.plot(x_curve, pdf * s["n"] * (edges[1] - edges[0]), color="#facc15", lw=2.2)
ax1.axvline(s["mean_khz"], color="#10b981", lw=2.0)
ax1.axvline(st.session_state.lsl, color="#f43f5e", ls="--", lw=1.8)
ax1.axvline(st.session_state.usl, color="#f43f5e", ls="--", lw=1.8)
ax1.set_xlim(min_x, max_x)
ax1.set_xlabel("Bandwidth Cutoff Frequency (-3 dB) [kHz]", color="#94a3b8", fontsize=9, fontfamily="monospace")
ax1.tick_params(colors="#94a3b8", labelsize=8.5)
ax1.grid(axis="y", color="#1e293b", lw=1)
plt.tight_layout()

png_buf = io.BytesIO()
fig1.savefig(png_buf, format="png", dpi=300, bbox_inches="tight")
csv_bytes = s["rows"].to_csv(index=False).encode("utf-8")

h_left, h_right = st.columns([6.2, 5.8])
with h_left:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding-top:4px;">
        <div style="width:12px; height:34px; background:#10b981; border-radius:2px;"></div>
        <div>
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:18px; font-weight:700; color:#ffffff; letter-spacing:-0.3px;">INDUSTRIAL ATE QUALITY CHECKER</span>
                <span style="font-size:11px; padding:2px 8px; border-radius:4px; background:rgba(59,130,246,0.2); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); font-family:'JetBrains Mono',monospace;">IPC-A-610 / ISO-9001 SPC</span>
            </div>
            <div style="font-size:11.5px; color:#94a3b8; font-family:'JetBrains Mono',monospace; margin-top:2px;">
                DUT: Texas Instruments OPAx140 Transimpedance Amplifier (GBW: 11 MHz | R1: 100 kΩ | Cf: 2 pF | Cj: 20 pF)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_right:
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("Upload LTSpice .log.txt"):
            st.session_state.show_uploader = not st.session_state.show_uploader
    with b2:
        st.download_button("Export Audit CSV", data=csv_bytes, file_name=f"ATE_QC_Audit_{st.session_state.lot_mode}.csv", mime="text/csv")
    with b3:
        st.download_button("Save 300-DPI Report PNG", data=png_buf.getvalue(), file_name=f"TIA_Yield_Histogram_{st.session_state.lot_mode}.png", mime="image/png", type="primary")
    with b4:
        if st.button("Print QC Certificate", type="primary"):
            st.session_state.trigger_print = True

if st.session_state.trigger_print:
    components.html("<script>window.parent.print();</script>", height=0)
    st.session_state.trigger_print = False

if st.session_state.show_uploader:
    up_file = st.file_uploader("Select LTSpice .log.txt file", type=["txt", "log", "csv"])
    if up_file is not None:
        st.session_state.custom_df = load_clean_data(up_file)
        st.session_state.custom_name = up_file.name
        st.session_state.lot_mode = "custom"
        st.session_state.show_uploader = False
        st.rerun()

st.markdown('<div class="sub-bar">', unsafe_allow_html=True)
c_lot, c_spec, c_batch = st.columns([4.8, 4.4, 2.8])

with c_lot:
    st.markdown('<div style="font-size:11px; font-weight:600; color:#94a3b8; text-transform:uppercase; margin-bottom:6px;">PRODUCTION LOT:</div>', unsafe_allow_html=True)
    lb1, lb2, lb3 = st.columns([1.3, 1.3, 1.1])
    with lb1:
        if st.button("Lot A: Standard (5% R, 10% C)", type="primary" if st.session_state.lot_mode == "standard" else "secondary"):
            st.session_state.lot_mode = "standard"
            st.rerun()
    with lb2:
        if st.button("Lot B: Precision (1% R, 2% C)", type="primary" if st.session_state.lot_mode == "precision" else "secondary"):
            st.session_state.lot_mode = "precision"
            st.rerun()
    with lb3:
        if st.button("Compare Lots Overlay", type="primary" if st.session_state.overlay else "secondary"):
            st.session_state.overlay = not st.session_state.overlay
            st.rerun()

with c_spec:
    sp1, sp2, sp3, sp4 = st.columns([1.2, 1.2, 0.9, 0.9])
    with sp1:
        new_lsl = st.number_input("SPEC LSL (KHZ)", value=float(st.session_state.lsl), step=0.5)
        if new_lsl != st.session_state.lsl:
            st.session_state.lsl = new_lsl
            st.rerun()
    with sp2:
        new_usl = st.number_input("SPEC USL (KHZ)", value=float(st.session_state.usl), step=0.5)
        if new_usl != st.session_state.usl:
            st.session_state.usl = new_usl
            st.rerun()
    with sp3:
        st.markdown("<div style='height:23px;'></div>", unsafe_allow_html=True)
        if st.button("790–820k"):
            st.session_state.lsl, st.session_state.usl = 790.0, 820.0
            st.rerun()
    with sp4:
        st.markdown("<div style='height:23px;'></div>", unsafe_allow_html=True)
        if st.button("790–810k"):
            st.session_state.lsl, st.session_state.usl = 790.0, 810.0
            st.rerun()

with c_batch:
    bt1, bt2 = st.columns([1.3, 1.2])
    with bt1:
        new_batch = st.number_input("BATCH SIZE", value=int(st.session_state.batch), step=1000)
        if new_batch != st.session_state.batch:
            st.session_state.batch = new_batch
            st.rerun()
    with bt2:
        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        st.markdown(f"<div style='font-family:JetBrains Mono,monospace; font-size:11px; color:#64748b; padding-top:26px;'>{utc_now}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

is_pass = s["yield_pct"] >= 95.0 and s["cpk"] >= 1.33
scrapped = int(round(st.session_state.batch * (1.0 - s["yield_pct"] / 100.0)))
scrap_cost = int(round(scrapped * 14.50))

if is_pass:
    v_class, d_class = "verdict-pass", "dot-pass"
    v_title = "QC VERDICT: PRODUCTION RELEASE APPROVED (SIX SIGMA CAPABLE)"
    v_sub = f"Cpk = {s['cpk']:.2f} (≥ 1.33 benchmark) and Yield = {s['yield_pct']:.1f}%. Component tolerances meet industrial IPC-A-610 class requirements."
else:
    v_class, d_class = "verdict-fail", "dot-fail"
    v_title = "QC VERDICT: LOT REJECTED — HIGH VARIANCE / NON-CONFORMING YIELD"
    v_sub = f"Cpk = {s['cpk']:.2f} (< 1.33 minimum) with {s['fail_cnt']}% scrap rate. Upgrade R1 to ±1% Thin-Film and Cf to ±2% C0G/NP0."

st.markdown(f"""
<div class="verdict-banner {v_class}">
    <div style="display:flex; align-items:center;">
        <span class="{d_class}"></span>
        <div>
            <div style="font-size:14px; font-weight:700; text-transform:uppercase;">{v_title}</div>
            <div style="font-size:12px; opacity:0.9; margin-top:2px;">{v_sub}</div>
        </div>
    </div>
    <div style="display:flex; gap:22px; font-family:'JetBrains Mono',monospace; font-size:12px;">
        <div><span style="opacity:0.7;">LOT ID:</span> <strong>{lot_id}</strong></div>
        <div><span style="opacity:0.7;">SAMPLE SIZE:</span> <strong>{s['n']} Runs</strong></div>
        <div><span style="opacity:0.7;">EST. SCRAP / BATCH:</span> <strong>{scrapped:,} units (${scrap_cost:,})</strong></div>
    </div>
</div>
""", unsafe_allow_html=True)

y_color = "#34d399" if is_pass else "#f43f5e"
c_color = "#34d399" if s["cpk"] >= 1.33 else ("#fbbf24" if s["cpk"] >= 1.0 else "#f43f5e")
offset = s["mean_khz"] - 0.5 * (st.session_state.lsl + st.session_state.usl)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-title">First-Pass Yield (FPY)</div>
        <div class="kpi-val" style="color:{y_color};">{s['yield_pct']:.1f}%</div>
        <div class="kpi-sub">Pass: {s['pass_cnt']} | Fail: {s['fail_cnt']}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Process Capability (Cpk)</div>
        <div class="kpi-val" style="color:{c_color};">{s['cpk']:.2f}</div>
        <div class="kpi-sub">Potential Cp: {s['cp']:.2f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Six Sigma & Defect PPM</div>
        <div class="kpi-val" style="color:#f8fafc;">{s['sigma']:.2f}σ</div>
        <div class="kpi-sub">Est. Defects: {s['ppm']:,} PPM</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Mean Bandwidth (μ)</div>
        <div class="kpi-val" style="color:#34d399;">{s['mean_khz']:.2f} kHz</div>
        <div class="kpi-sub">Spec Center Offset: {offset:+.2f} kHz</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Sample Std Dev (s)</div>
        <div class="kpi-val" style="color:#60a5fa;">{s['std_khz']:.2f} kHz</div>
        <div class="kpi-sub">Var: {(s['var_hz']/1e6):.2f} kHz²</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Worst-Case Spread</div>
        <div class="kpi-val" style="color:#fbbf24;">{s['spread_pct']:.2f}%</div>
        <div class="kpi-sub">{s['min_khz']:.2f} – {s['max_khz']:.2f} kHz</div>
    </div>
</div>
""", unsafe_allow_html=True)

ch1, ch2 = st.columns(2)
with ch1:
    st.markdown("""
    <div class="panel">
        <div class="panel-header">
            <div>
                <div class="panel-title">CHART 1: BANDWIDTH YIELD HISTOGRAM & GAUSSIAN FIT</div>
                <div class="panel-sub">Frequency distribution (-3 dB cutoff) vs. Lower & Upper Specification Limits</div>
            </div>
            <span class="panel-badge">Bins: 12 | Normal PDF</span>
        </div>
    """, unsafe_allow_html=True)
    st.pyplot(fig1)
    st.markdown("</div>", unsafe_allow_html=True)

with ch2:
    st.markdown("""
    <div class="panel">
        <div class="panel-header">
            <div>
                <div class="panel-title">CHART 2: SPC INDIVIDUAL RUN CONTROL CHART (I-CHART)</div>
                <div class="panel-sub">Run-by-run stability tracking across N=100 boards with ±3σ control limits</div>
            </div>
            <span class="panel-badge">UCL / LCL = μ ± 3s</span>
        </div>
    """, unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(6.8, 3.6), facecolor="#111827")
    ax2.set_facecolor("#0b0f19")
    for sp in ax2.spines.values():
        sp.set_color("#1e293b")

    runs = np.arange(1, s["n"] + 1)
    ucl = s["mean_khz"] + 3.0 * s["std_khz"]
    lcl = s["mean_khz"] - 3.0 * s["std_khz"]
    min_y = min(775.0, st.session_state.lsl - 4.0, lcl - 2.0, float(np.min(s["bw_khz"])) - 2.0)
    max_y = max(826.0, st.session_state.usl + 4.0, ucl + 2.0, float(np.max(s["bw_khz"])) + 2.0)

    ax2.axhspan(st.session_state.lsl, st.session_state.usl, color="#10b981", alpha=0.08)
    ax2.plot(runs, s["bw_khz"], color="#38bdf8", lw=1.4)
    fail_mask = (s["bw_khz"] < st.session_state.lsl) | (s["bw_khz"] > st.session_state.usl)
    ax2.scatter(runs[~fail_mask], s["bw_khz"][~fail_mask], color="#38bdf8", s=14, zorder=4)
    ax2.scatter(runs[fail_mask], s["bw_khz"][fail_mask], color="#f43f5e", s=28, zorder=5)

    ax2.axhline(s["mean_khz"], color="#10b981", lw=1.5)
    ax2.axhline(ucl, color="#f59e0b", ls=":", lw=1.4)
    ax2.axhline(lcl, color="#f59e0b", ls=":", lw=1.4)
    ax2.axhline(st.session_state.lsl, color="#f43f5e", ls="--", lw=1.8)
    ax2.axhline(st.session_state.usl, color="#f43f5e", ls="--", lw=1.8)
    ax2.set_ylim(min_y, max_y)
    ax2.set_xlabel("Serial Production Run Index (Run #1 to #100)", color="#94a3b8", fontsize=9, fontfamily="monospace")
    ax2.tick_params(colors="#94a3b8", labelsize=8.5)
    ax2.grid(axis="y", color="#1e293b", lw=1)
    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

mid1, mid2 = st.columns([5, 7])
with mid1:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">TABLE 1: EXECUTIVE STATISTICAL SUMMARY</div>
            <span class="panel-badge">Pandas / NumPy Engine (ddof=1)</span>
        </div>
        <div style="padding:12px;">
            <table class="ate-table">
                <thead>
                    <tr><th>Parameter</th><th style="text-align:right;">Measured Value</th><th style="text-align:right;">Standard / Benchmark</th></tr>
                </thead>
                <tbody>
                    <tr><td>Runs Analysed (N)</td><td style="text-align:right;font-weight:600;">{s['n']}</td><td style="text-align:right;color:#94a3b8;">100 Monte Carlo Runs</td></tr>
                    <tr><td>Mean Bandwidth (μ)</td><td style="text-align:right;font-weight:600;">{s['mean_hz']:,.1f} Hz ({s['mean_khz']:.2f} kHz)</td><td style="text-align:right;color:#94a3b8;">802.3 kHz Nominal</td></tr>
                    <tr><td>Sample Std Deviation (s)</td><td style="text-align:right;font-weight:600;">{s['std_hz']:,.1f} Hz ({s['std_khz']:.2f} kHz)</td><td style="text-align:right;color:#94a3b8;">≤ 3.5 kHz Target</td></tr>
                    <tr><td>Sample Variance (s²)</td><td style="text-align:right;font-weight:600;">{s['var_hz']:,.1f} Hz²</td><td style="text-align:right;color:#94a3b8;">ddof = 1 (Unbiased)</td></tr>
                    <tr><td>Worst-Case Minimum</td><td style="text-align:right;font-weight:600;">{s['min_hz']:,.1f} Hz ({s['min_khz']:.2f} kHz)</td><td style="text-align:right;color:#94a3b8;">≥ {st.session_state.lsl:.1f} kHz (LSL)</td></tr>
                    <tr><td>Worst-Case Maximum</td><td style="text-align:right;font-weight:600;">{s['max_hz']:,.1f} Hz ({s['max_khz']:.2f} kHz)</td><td style="text-align:right;color:#94a3b8;">≤ {st.session_state.usl:.1f} kHz (USL)</td></tr>
                    <tr><td>Total Drift Spread</td><td style="text-align:right;font-weight:600;">{s['spread_pct']:.2f} % of mean</td><td style="text-align:right;color:#94a3b8;">≤ 3.00 % of mean</td></tr>
                    <tr><td>Process Potential (Cp)</td><td style="text-align:right;font-weight:600;">{s['cp']:.2f}</td><td style="text-align:right;color:#94a3b8;">≥ 1.33 (4σ Industry Std)</td></tr>
                    <tr><td>Process Capability (Cpk)</td><td style="text-align:right;font-weight:600;color:{c_color};">{s['cpk']:.2f}</td><td style="text-align:right;color:#94a3b8;">≥ 1.33 (Six Sigma Ready)</td></tr>
                    <tr><td>Units Passed / Failed</td><td style="text-align:right;font-weight:600;">{s['pass_cnt']} PASS / {s['fail_cnt']} FAIL</td><td style="text-align:right;color:#94a3b8;">Zero Defect Target</td></tr>
                    <tr><td>Predicted Factory Yield</td><td style="text-align:right;font-weight:600;color:{y_color};">{s['yield_pct']:.1f} % ({s['ppm']:,} PPM)</td><td style="text-align:right;color:#94a3b8;">≥ 99.0 % Mass Prod.</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

with mid2:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-header">
            <div>
                <div class="panel-title">HARDWARE TOPOLOGY & BOM TOLERANCE AUDIT</div>
                <div class="panel-sub">LTSpice AC Sweep: .ac dec 100 10 10Meg | Cutoff: mag(V(Vo)) = LF_Gain / √2</div>
            </div>
            <span class="panel-badge" style="color:#6ee7b7;">{schem_badge}</span>
        </div>
        <div style="padding:16px; display:grid; grid-template-columns:1.35fr 1fr; gap:16px; align-items:center;">
            <div style="background:#090d16; border:1px solid #1e293b; border-radius:6px; padding:12px;">
                <svg viewBox="0 0 460 250" style="width:100%; height:auto;">
                    <line x1="60" y1="150" x2="150" y2="150" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="110" y1="150" x2="110" y2="90" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="110" y1="40" x2="110" y2="90" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="110" y1="90" x2="195" y2="90" stroke="#94a3b8" stroke-width="2"/>
                    <rect x="195" y="78" width="70" height="24" fill="#0f172a" stroke="#38bdf8" stroke-width="2"/>
                    <text x="230" y="94" fill="#38bdf8" font-size="11" font-family="monospace" text-anchor="middle">R1=100kΩ</text>
                    <text x="230" y="70" fill="#fbbf24" font-size="11" font-family="monospace" text-anchor="middle">{r_tol_svg}</text>
                    <line x1="265" y1="90" x2="340" y2="90" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="110" y1="40" x2="218" y2="40" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="218" y1="26" x2="218" y2="54" stroke="#a855f7" stroke-width="2.5"/>
                    <line x1="232" y1="26" x2="232" y2="54" stroke="#a855f7" stroke-width="2.5"/>
                    <line x1="232" y1="40" x2="340" y2="40" stroke="#94a3b8" stroke-width="2"/>
                    <text x="225" y="20" fill="#c084fc" font-size="11" font-family="monospace" text-anchor="middle">{c_tol_svg}</text>
                    <line x1="340" y1="40" x2="340" y2="165" stroke="#94a3b8" stroke-width="2"/>
                    <polygon points="150,125 150,205 290,165" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
                    <text x="162" y="155" fill="#94a3b8" font-size="14" font-family="monospace">-</text>
                    <text x="162" y="185" fill="#94a3b8" font-size="14" font-family="monospace">+</text>
                    <text x="205" y="170" fill="#10b981" font-size="12" font-weight="bold" font-family="monospace">OPAx140</text>
                    <line x1="130" y1="180" x2="150" y2="180" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="130" y1="180" x2="130" y2="215" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="118" y1="215" x2="142" y2="215" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="290" y1="165" x2="395" y2="165" stroke="#94a3b8" stroke-width="2"/>
                    <circle cx="395" cy="165" r="4" fill="#10b981"/>
                    <text x="405" y="169" fill="#10b981" font-size="12" font-family="monospace">Vo</text>
                    <circle cx="60" cy="185" r="14" fill="#0f172a" stroke="#f43f5e" stroke-width="2"/>
                    <line x1="60" y1="150" x2="60" y2="171" stroke="#94a3b8" stroke-width="2"/>
                    <line x1="60" y1="199" x2="60" y2="215" stroke="#94a3b8" stroke-width="2"/>
                    <text x="60" y="189" fill="#f43f5e" font-size="10" font-family="monospace" text-anchor="middle">I1</text>
                    <text x="16" y="189" fill="#94a3b8" font-size="10" font-family="monospace">Cj=20pF</text>
                </svg>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px; font-size:12px;">
                <div style="background:#090d16; border:1px solid #1e293b; border-radius:6px; padding:12px; font-family:'JetBrains Mono',monospace;">
                    <div style="color:#94a3b8; font-weight:600; text-transform:uppercase; margin-bottom:6px;">Active Component Spec</div>
                    <div style="color:#e2e8f0;">{bom_r1}</div>
                    <div style="color:#e2e8f0; margin-top:4px;">{bom_cf}</div>
                    <div style="color:#94a3b8; margin-top:4px;">Op-Amp: TI OPAx140 (±15V)</div>
                </div>
                <div style="background:#090d16; border:1px solid #1e293b; border-radius:6px; padding:12px; font-family:'JetBrains Mono',monospace;">
                    <div style="color:#94a3b8; font-weight:600; text-transform:uppercase; margin-bottom:6px;">Production Cost & Scrap Impact</div>
                    <div>Batch Size: <strong>{st.session_state.batch:,} boards</strong></div>
                    <div style="margin-top:3px;">Defective Boards: <strong style="color:{y_color};">{scrapped:,} units</strong></div>
                    <div style="margin-top:3px;">Est. Scrap Loss ($14.50/PCB): <strong>${scrap_cost:,}</strong></div>
                    <div style="margin-top:3px;">Precision BOM Delta (+$0.08/PCB): <strong>${int(st.session_state.batch * 0.08):,}</strong></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="panel">
    <div class="panel-header">
        <div>
            <div class="panel-title">TABLE 2: AUTOMATED PER-UNIT SERIALIZED QC LOG (N=100)</div>
            <div class="panel-sub">Complete unit-level traceability with deviation %, Z-score, and spec margin</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tf1, tf2 = st.columns([3, 3])
with tf1:
    search_q = st.text_input("Search Run # (e.g. 22)...", value="")
with tf2:
    status_q = st.selectbox("Filter Verdict Status", ["Show All Units (100)", "PASS Units Only", "FAIL Units Only (Out-of-Spec)"])

filtered_df = s["rows"]
if status_q == "PASS Units Only":
    filtered_df = filtered_df[filtered_df["result"] == "PASS"]
elif status_q == "FAIL Units Only (Out-of-Spec)":
    filtered_df = filtered_df[filtered_df["result"] == "FAIL"]
if search_q.strip():
    filtered_df = filtered_df[filtered_df["run"].astype(str).str.contains(search_q.strip())]

rows_html = []
for _, r in filtered_df.iterrows():
    badge = '<span class="pass-pill">PASS</span>' if r["result"] == "PASS" else '<span class="fail-pill">FAIL</span>'
    row_bg = 'style="background:rgba(136,19,55,0.18);"' if r["result"] == "FAIL" else ""
    m_col = "#f43f5e" if r["margin_khz"] < 0 else "#34d399"
    rows_html.append(
        f"<tr {row_bg}>"
        f"<td>{r['serial']}</td>"
        f"<td style='text-align:right;'>{r['bw_hz']:.1f}</td>"
        f"<td style='text-align:right;font-weight:600;color:#fff;'>{r['bw_khz']:.3f}</td>"
        f"<td style='text-align:right;'>{r['dev_pct']:+.3f}%</td>"
        f"<td style='text-align:right;'>{r['z_score']:+.2f}σ</td>"
        f"<td style='text-align:right;color:{m_col};font-weight:600;'>{r['margin_khz']:.2f}</td>"
        f"<td style='text-align:center;'>{badge}</td>"
        f"</tr>"
    )

st.markdown(f"""
<div class="panel" style="max-height:380px; overflow-y:auto; margin-top:-10px;">
    <table class="ate-table">
        <thead style="position:sticky; top:0; background:#0f172a;">
            <tr>
                <th>Serial / Run #</th>
                <th style="text-align:right;">Bandwidth (Hz)</th>
                <th style="text-align:right;">Cutoff (-3 dB) [kHz]</th>
                <th style="text-align:right;">Dev from Mean (%)</th>
                <th style="text-align:right;">Z-Score (σ)</th>
                <th style="text-align:right;">Spec Margin (kHz)</th>
                <th style="text-align:center;">QC Verdict</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows_html)}
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)