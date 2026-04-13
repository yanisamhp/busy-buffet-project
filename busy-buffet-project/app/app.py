import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.graph_objects as go
import plotly.express as px

# ─── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Busy Buffet — Hotel Amber 85",
    layout="wide",
)

# ─── Colors ────────────────────────────────────────────────
TEMPLATE    = "plotly_white"

C_INHOUSE   = "#1B365D"
C_WALKIN    = "#5B9BD5"
C_CREAM     = "#E7E6E6"
C_GRAY      = "#A5A5A5"
C_GREEN     = "#92DE76"
C_RED       = "#CF766C"
COLOR_SCALE = [C_INHOUSE, C_WALKIN, "#8497B0", "#ADB9CA", C_CREAM]

# ─── Montserrat + Theme CSS ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Sarabun:wght@400;500;600&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"],
[data-testid="stSidebar"], button, input, textarea, select {
    font-family: 'Montserrat', 'Sarabun', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1B365D;
    padding-top: 2rem;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.88rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    padding: 6px 0;
    color: #ADB9CA !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr {
    border-color: #2d4a6e !important;
}

/* Main bg */
[data-testid="stAppViewContainer"] > .main {
    background-color: #f9f9fb;
}

/* Page title */
h1 {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: #1B365D !important;
    letter-spacing: -0.01em;
}
h2 {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #1B365D !important;
    margin-top: 1.5rem !important;
}
h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    color: #44546A !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* KPI card */
.kpi-card {
    background: #ffffff;
    border: 1px solid #E7E6E6;
    border-top: 4px solid #1B365D;
    border-radius: 8px;
    padding: 20px 20px 16px;
}
.kpi-card .label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #A5A5A5;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.kpi-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #1B365D;
    line-height: 1.1;
}
.kpi-card .sub {
    font-size: 0.75rem;
    color: #A5A5A5;
    margin-top: 4px;
}

/* Verdict box */
.verdict-box {
    border-radius: 6px;
    padding: 14px 18px;
    margin: 10px 0 20px;
    font-size: 0.88rem;
    line-height: 1.65;
    font-family: 'Montserrat', 'Sarabun', sans-serif;
}
.verdict-true  { background: #f2faf0; border-left: 4px solid #92DE76; color: #2d5a20; }
.verdict-false { background: #fdf3f2; border-left: 4px solid #CF766C; color: #7a2e28; }

/* Comment quote */
.comment-quote {
    background: #f0f4f9;
    border-left: 4px solid #5B9BD5;
    border-radius: 0 6px 6px 0;
    padding: 12px 18px;
    margin: 8px 0 20px;
    font-size: 0.9rem;
    color: #1B365D;
    font-style: italic;
}

/* Divider */
hr { border: none; border-top: 1px solid #E7E6E6; margin: 24px 0; }

/* Caption */
.stCaption { color: #A5A5A5 !important; font-size: 0.78rem !important; }

/* Comparison table */
.compare-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.compare-table th {
    background: #1B365D;
    color: #ffffff;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.compare-table td { padding: 9px 14px; border-bottom: 1px solid #E7E6E6; color: #333; }
.compare-table tr:nth-child(even) td { background: #f9f9fb; }
.tag-yes { color: #92DE76; font-weight: 700; }
.tag-no  { color: #CF766C; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─── Plotly font helper ─────────────────────────────────────
FONT = dict(family="Montserrat, Sarabun, sans-serif", size=12, color="#44546A")

def apply_font(fig, height=320):
    fig.update_layout(
        font=FONT,
        height=height,
        margin=dict(t=16, b=8, l=8, r=8),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
    )
    fig.update_xaxes(tickfont=FONT, title_font=FONT, showgrid=False, linecolor="#E7E6E6")
    fig.update_yaxes(tickfont=FONT, title_font=FONT, gridcolor="#f0f0f0", linecolor="#E7E6E6")
    return fig

# ─── Load & prep data ──────────────────────────────────────
from pathlib import Path
import pandas as pd
from datetime import timedelta
import streamlit as st

@st.cache_data
def load_data():

    # Path to data
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "busy_buffet_clean.pkl"

    df = pd.read_pickle(DATA_PATH)

    # Create 30-min slots from 06:00–13:30
    slots = [
        timedelta(hours=h, minutes=m)
        for h in range(6, 14)
        for m in (0, 30)
    ]

    seated = df[df["seating_status"] != "Walk-away"]

    occ_rows = []

    for _, row in seated.iterrows():

        if pd.isna(row["meal_start"]) or pd.isna(row["meal_end"]):
            continue

        pax_val = row["pax"] if row["pax"] > 0 else 1

        for slot in slots:

            if row["meal_start"] <= slot < row["meal_end"]:

                total_sec = int(slot.total_seconds())

                h = total_sec // 3600
                m = (total_sec % 3600) // 60

                occ_rows.append({
                    "date": row["date"],
                    "slot_str": f"{h:02d}:{m:02d}",
                    "pax": pax_val,
                })

    occ_df = pd.DataFrame(occ_rows)

    n_days = df["date"].nunique()

    occ_avg = (
        occ_df
        .groupby("slot_str")["pax"]
        .sum()
        .div(n_days)
        .round(1)
        .reset_index()
    )

    occ_avg.columns = ["slot", "avg_pax"]

    return df, occ_avg, n_days


df, occ_avg, n_days = load_data()

# ─── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0 8px 20px;'>
        <div style='font-size:1.1rem; font-weight:700; letter-spacing:0.01em;'>Busy Buffet</div>
        <div style='font-size:0.78rem; color:#8497B0; margin-top:2px;'>Hotel Amber Sukhumvit 85</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["Overview", "Task 1 — Staff Comments", "Task 2 — Actions", "Task 3 — Recommendation"],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.72rem; color:#8497B0; padding: 0 8px; line-height:1.7;'>
        ข้อมูล 5 วัน<br>13–18 Jan 2026
    </div>
    """, unsafe_allow_html=True)

# ─── KPI helper ────────────────────────────────────────────
def kpi(col, label, value, sub="", accent=C_INHOUSE):
    col.markdown(f"""
    <div class="kpi-card" style="border-top-color:{accent};">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "Overview":
    st.title("Busy Buffet")
    st.markdown("## Atmind Data Analytics Test 2026")
    st.markdown("""<div class="comment-quote">
        Presented by : Yanisa Mahuppon
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.title("Overview")

    total_groups = len(df)
    total_pax    = int(df["pax"].sum())
    walkaway     = int(df["is_walkaway"].sum())
    avg_wait     = df.loc[df["wait_time_min"] > 0, "wait_time_min"].mean()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Groups",  f"{total_groups:,}", "รวม 5 วัน")
    kpi(c2, "Total Pax",     f"{total_pax:,}",    "รวม 5 วัน",           C_WALKIN)
    kpi(c3, "Walk-away",     f"{walkaway}",        "groups ที่รอแล้วออก", C_RED)
    kpi(c4, "Avg Wait Time", f"{avg_wait:.0f} min","เฉพาะกลุ่มที่รอคิว",  C_GRAY)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Pax per Day")
        daily = (
            df[df["seating_status"] != "Walk-away"]
            .groupby("date")["pax"].sum().reset_index()
        )
        daily["date_str"] = daily["date"].dt.strftime("%d %b (%a)")
        fig = go.Figure(go.Bar(
            x=daily["date_str"], y=daily["pax"],
            marker_color=C_INHOUSE,
            text=daily["pax"].astype(int), textposition="outside",
            textfont=dict(size=11, color=C_INHOUSE),
            width=0.55,
        ))
        fig.update_layout(yaxis_title="Pax", yaxis_range=[0, 200], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    with col_r:
        st.markdown("#### Guest Mix")
        totals = df["Guest_type"].value_counts().reset_index()
        totals.columns = ["Guest_type", "count"]
        fig = px.pie(
            totals, names="Guest_type", values="count",
            color="Guest_type",
            color_discrete_map={"In house": C_INHOUSE, "Walk in": C_WALKIN},
            hole=0.55,
        )
        fig.update_traces(
            textinfo="label+percent", textposition="outside",
            textfont=dict(family="Montserrat, Sarabun, sans-serif", size=12),
        )
        fig.update_layout(showlegend=False, template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Avg Occupancy per 30-min Slot")
    fig = go.Figure(go.Bar(
        x=occ_avg["slot"], y=occ_avg["avg_pax"],
        marker_color=[
            C_INHOUSE if v >= 25 else C_WALKIN if v >= 10 else C_CREAM
            for v in occ_avg["avg_pax"]
        ],
        text=occ_avg["avg_pax"], textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        xaxis_title="Time slot", yaxis_title="Avg pax sitting",
        yaxis_range=[0, 42], template=TEMPLATE,
    )
    st.plotly_chart(apply_font(fig, height=300), use_container_width=True)
    st.caption("สีเข้ม = peak (≥25 pax)   สีฟ้า = ปานกลาง   สีอ่อน = เบาบาง")


# ══════════════════════════════════════════════════════════
# PAGE: TASK 1
# ══════════════════════════════════════════════════════════
elif page == "Task 1 — Staff Comments":
    st.title("Task 1 — Staff Comments")
    st.markdown("For each staff comment, create visuals and analysis to prove if their statement is true or not.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Comment 1 ──────────────────────────────────────────
    st.markdown("## Comment 1")
    st.markdown("""<div class="comment-quote">
        "In-house (hotel) customers are unhappy that they have to wait for a table. Walk-in customers are also unhappy, when they queue up for a long time
and leave the queue because they don’t want to wait any longer"
    </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Avg Wait Time by Guest Type")
        wait_avg = (
            df[df["wait_time_min"] > 0]
            .groupby("Guest_type")["wait_time_min"]
            .mean().round(1).reset_index()
        )
        wait_avg.columns = ["Guest_type", "avg_wait"]
        fig = go.Figure(go.Bar(
            x=wait_avg["Guest_type"], y=wait_avg["avg_wait"],
            marker_color=[C_INHOUSE, C_WALKIN],
            text=wait_avg["avg_wait"].apply(lambda v: f"{v:.0f} min"),
            textposition="outside",
            textfont=dict(size=12, color=C_INHOUSE),
            width=0.45,
        ))
        fig.update_layout(yaxis_title="Minutes", yaxis_range=[0, 55], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    with col_r:
        st.markdown("#### Walk-away Count by Guest Type")
        wa = (
            df[df["is_walkaway"]]
            .groupby("Guest_type").size()
            .reset_index(name="walk_away")
        )
        fig = go.Figure(go.Bar(
            x=wa["Guest_type"], y=wa["walk_away"],
            marker_color=[C_INHOUSE, C_WALKIN],
            text=wa["walk_away"], textposition="outside",
            textfont=dict(size=12, color=C_INHOUSE),
            width=0.45,
        ))
        fig.update_layout(yaxis_title="Groups", yaxis_range=[0, 11], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-true">
        <b>TRUE</b> — Walk-in รอเฉลี่ย 38 นาที, In-house 28 นาที
        มี walk-away ทั้งสองกลุ่ม กลุ่มละ 7 groups ความล่าช้าในการจัดสรรโต๊ะส่งผลกระทบต่อความพึงพอใจและสูญเสียโอกาสในการขาย
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Comment 2 ──────────────────────────────────────────
    st.markdown("## Comment 2")
    st.markdown("""<div class="comment-quote">
        "We are very busy every day of the week. If it’s going to be this busy every week I think it’s impossible to sustain this business. This buffet business is not
possible for this hotel"
    </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Pax per Day")
        daily = (
            df[df["seating_status"] != "Walk-away"]
            .groupby("date")["pax"].sum().reset_index()
        )
        daily["date_str"] = daily["date"].dt.strftime("%d %b (%a)")
        fig = go.Figure(go.Bar(
            x=daily["date_str"], y=daily["pax"],
            marker_color=C_INHOUSE,
            text=daily["pax"].astype(int), textposition="outside",
            textfont=dict(size=11, color=C_INHOUSE),
            width=0.55,
        ))
        fig.update_layout(yaxis_title="Pax", yaxis_range=[0, 200], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    with col_r:
        st.markdown("#### Avg Occupancy per 30-min Slot")
        fig = go.Figure(go.Bar(
            x=occ_avg["slot"], y=occ_avg["avg_pax"],
            marker_color=[
                C_INHOUSE if v >= 25 else C_WALKIN if v >= 10 else C_CREAM
                for v in occ_avg["avg_pax"]
            ],
            text=occ_avg["avg_pax"], textposition="outside",
            textfont=dict(size=10),
        ))
        fig.update_layout(
            xaxis_title="Time", yaxis_title="Avg pax sitting",
            yaxis_range=[0, 42], template=TEMPLATE,
        )
        st.plotly_chart(apply_font(fig), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-true">
        <b>TRUE (บางส่วน)</b> — ปริมาณลูกค้าหนาแน่นทุกวัน แต่ความแออัดไม่ได้เกิดตลอดเวลา โดยจะพีคสูงสุดในช่วง 08:30–10:30 น. 
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Comment 3 ──────────────────────────────────────────
    st.markdown("## Comment 3")
    st.markdown("""<div class="comment-quote">
        "Walk-in customers sit the whole day. It's very difficult to find seats for in-house customers. We don’t have enough tables so when one customer sits
for a long time it makes the queue very long"
    </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Avg Meal Duration by Guest Type")
        dur_avg = (
            df.groupby("Guest_type")["meal_duration_min"]
            .mean().round(1).reset_index()
        )
        dur_avg.columns = ["Guest_type", "avg_dur"]
        fig = go.Figure(go.Bar(
            x=dur_avg["Guest_type"], y=dur_avg["avg_dur"],
            marker_color=[C_INHOUSE, C_WALKIN],
            text=dur_avg["avg_dur"].apply(lambda v: f"{v:.0f} min"),
            textposition="outside",
            textfont=dict(size=12, color=C_INHOUSE),
            width=0.45,
        ))
        fig.update_layout(yaxis_title="Minutes", yaxis_range=[0, 95], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    with col_r:
        st.markdown("#### Meal Duration Distribution")
        bins   = [0, 60, 120, 180, 999]
        labels = ["< 1h", "1–2h", "2–3h", "3h+"]
        df["dur_group"] = pd.cut(df["meal_duration_min"], bins=bins, labels=labels)
        bucket = (
            df.groupby(["Guest_type", "dur_group"], observed=True)
            .size().reset_index(name="n")
        )
        total = bucket.groupby("Guest_type")["n"].transform("sum")
        bucket["pct"] = (bucket["n"] / total * 100).round(1)
        fig = px.bar(
            bucket, x="Guest_type", y="pct", color="dur_group",
            color_discrete_sequence=COLOR_SCALE,
            barmode="stack", text="pct",
            labels={"pct": "%", "Guest_type": "", "dur_group": "Duration"},
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%", textposition="inside",
            textfont=dict(family="Montserrat, sans-serif", size=11, color="white"),
        )
        fig.update_layout(yaxis_ticksuffix="%", yaxis_range=[0, 110], template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-true">
        <b>TRUE</b> — Walk-in นั่งเฉลี่ย 73 นาที vs In-house 46 นาที (นานกว่าเกือบ 2 เท่า)
        In-house 84% กินไม่ถึง 1h ขณะที่ Walk-in กระจายตัวนานกว่ามาก
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE: TASK 2
# ══════════════════════════════════════════════════════════
elif page == "Task 2 — Actions":
    st.title("Task 2 — Actions")
    st.markdown("For each of the recommended actions, create visual and analysis to disprove why each of them will not work.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Action 1 ───────────────────────────────────────────
    st.markdown("## Action 1 — Reduce seating time (5 hours to less)")

    seated_df = df[df["meal_duration_min"].notna()]
    rows = []
    for guest in ["In house", "Walk in"]:
        sub   = seated_df[seated_df["Guest_type"] == guest]["meal_duration_min"]
        over  = round((sub > 120).sum() / len(sub) * 100, 1)
        under = round(100 - over, 1)
        rows.append({"Guest_type": guest, "Under 2h": under, "Over 2h": over})
    a1_df   = pd.DataFrame(rows)
    a1_melt = a1_df.melt(id_vars="Guest_type", var_name="group", value_name="pct")

    fig = px.bar(
        a1_melt, x="Guest_type", y="pct", color="group",
        color_discrete_map={"Under 2h": C_INHOUSE, "Over 2h": C_RED},
        barmode="stack", text="pct",
        labels={"pct": "%", "Guest_type": "", "group": ""},
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%", textposition="inside",
        textfont=dict(family="Montserrat, sans-serif", size=12, color="white"),
    )
    fig.update_layout(yaxis_ticksuffix="%", yaxis_range=[0, 110], template=TEMPLATE)
    st.plotly_chart(apply_font(fig, height=300), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-false">
        <b>จะไม่ได้ผล</b> — In-house 97% นั่งไม่ถึง 2h อยู่แล้ว
        ลดเวลาไม่ช่วยอะไร แต่สร้างความไม่พอใจให้ลูกค้าที่ไม่ได้ทำอะไรผิด
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Action 2 ───────────────────────────────────────────
    st.markdown("## Action 2 — Increase price everyday to 259")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Guest Mix รวม 5 วัน")
        totals = df["Guest_type"].value_counts().reset_index()
        totals.columns = ["Guest_type", "count"]
        fig = px.pie(
            totals, names="Guest_type", values="count",
            color="Guest_type",
            color_discrete_map={"In house": C_INHOUSE, "Walk in": C_WALKIN},
            hole=0.55,
        )
        fig.update_traces(
            textinfo="label+percent", textposition="outside",
            textfont=dict(family="Montserrat, Sarabun, sans-serif", size=12),
        )
        fig.update_layout(showlegend=False, template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    with col_r:
        st.markdown("#### Guest Mix รายวัน")
        guest_daily = (
            df.groupby(["date", "Guest_type"]).size()
            .reset_index(name="count")
        )
        guest_daily["date_str"] = guest_daily["date"].dt.strftime("%d %b")
        fig = px.bar(
            guest_daily, x="date_str", y="count", color="Guest_type",
            color_discrete_map={"In house": C_INHOUSE, "Walk in": C_WALKIN},
            barmode="group", text="count",
            labels={"count": "Groups", "date_str": "Date", "Guest_type": ""},
        )
        fig.update_traces(
            textposition="outside",
            textfont=dict(family="Montserrat, sans-serif", size=11),
        )
        fig.update_layout(template=TEMPLATE)
        st.plotly_chart(apply_font(fig), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-false">
        <b>จะไม่ได้ผล</b> — Walk-in คือ 57% ของลูกค้าทั้งหมดและเป็นแหล่งรายได้หลัก
        In-house ส่วนใหญ่ได้ breakfast รวมในแพ็กเกจห้อง ราคา 259 บาท ไม่กระทบพวกเขาเลย
        การขึ้นราคาจะลด walk-in demand พร้อมกับรายได้
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Action 3 ───────────────────────────────────────────
    st.markdown("## Action 3 — Queue skipping for in-house guest")

    peak_start = timedelta(hours=8)
    peak_end   = timedelta(hours=10)

    wi_in_peak = df[
        (df["Guest_type"] == "Walk in") &
        (df["seating_status"] != "Walk-away") &
        df["meal_start"].notna() & df["meal_end"].notna() &
        (df["meal_start"] < peak_end) &
        (df["meal_end"]   > peak_start)
    ].copy()

    ih_queued = df[
        (df["Guest_type"] == "In house") &
        (df["seating_status"] == "Queued") &
        df["queue_start"].notna() & df["queue_end"].notna()
    ].copy()
    ih_queued["wait"] = (
        ih_queued["queue_end"] - ih_queued["queue_start"]
    ).dt.total_seconds() / 60

    avg_wi_dur  = wi_in_peak["meal_duration_min"].mean()
    avg_ih_wait = ih_queued["wait"].mean()

    a3_df = pd.DataFrame({
        "Group"  : ["Walk-in sitting (peak)", "In-house waiting"],
        "Minutes": [round(avg_wi_dur, 0), round(avg_ih_wait, 0)],
        "color"  : [C_WALKIN, C_INHOUSE],
    })
    fig = go.Figure(go.Bar(
        x=a3_df["Group"], y=a3_df["Minutes"],
        marker_color=a3_df["color"],
        text=a3_df["Minutes"].apply(lambda v: f"{v:.0f} min"),
        textposition="outside",
        textfont=dict(size=12, color=C_INHOUSE),
        width=0.4,
    ))
    fig.update_layout(yaxis_title="Minutes", yaxis_range=[0, 110], template=TEMPLATE)
    st.plotly_chart(apply_font(fig, height=300), use_container_width=True)

    st.markdown("""<div class="verdict-box verdict-false">
        <b>จะไม่ได้ผล</b> — In-house รอคิวเฉลี่ย 28 นาที
        แต่ walk-in ที่นั่งอยู่ช่วงเดียวกันใช้เวลาเฉลี่ย 81 นาที
        Queue skip ช่วยลำดับได้ แต่โต๊ะยังไม่ว่างตราบใดที่ walk-in นั่งนาน
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE: TASK 3
# ══════════════════════════════════════════════════════════
elif page == "Task 3 — Recommendation":
    st.title("Task 3 — Recommendation")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("## Reserved Seating สำหรับ In-house")
    st.markdown("""
    ปรับ Action 3 จาก Queue Skipping เป็น **Reserved Seating Zone**

    - จัดโต๊ะ dedicated zone แยกสำหรับ in-house ก่อน check-in
    - In-house แจ้ง preferred time ผ่าน front desk ตอน check-in
    - หลัง 09:00 release โต๊ะให้ walk-in ได้ทันที ไม่สูญเสียรายได้
    """)

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### In-house: เวลาที่นิยมมากิน")
    
        ih_seated = df[
            (df["Guest_type"] == "In house") &
            df["meal_start"].notna()
        ].copy()

        OPEN_HOUR = 6
        CLOSE_HOUR = 11

        # Convert to real hour
        ih_seated["meal_hour"] = (
            ih_seated["meal_start"]
            .dt.total_seconds()
            .div(3600)
            .astype(int)
            + OPEN_HOUR
        )

        # Keep only breakfast hours
        ih_seated = ih_seated[
            ih_seated["meal_hour"].between(OPEN_HOUR, CLOSE_HOUR)
        ]

        # Count per hour
        ih_hour = (
            ih_seated
            .groupby("meal_hour")
            .size()
            .reset_index(name="count")
        )

        # Find peak hours automatically
        peak_hours = (
            ih_hour
            .sort_values("count", ascending=False)
            .head(2)["meal_hour"]
            .tolist()
        )

        ih_hour["hour_str"] = ih_hour["meal_hour"].apply(
            lambda h: f"{h:02d}:00"
        )

        fig = go.Figure(go.Bar(
            x=ih_hour["hour_str"],
            y=ih_hour["count"],
            marker_color=[
                C_INHOUSE if h in peak_hours else C_WALKIN
                for h in ih_hour["meal_hour"]
            ],
            text=ih_hour["count"],
            textposition="outside",
        ))

        fig.update_layout(
            xaxis_title="Time", yaxis_title="Groups (5-day total)",
            yaxis_range=[0, 80], template=TEMPLATE,
        )
        st.plotly_chart(apply_font(fig), use_container_width=True)
        st.caption("Reserve zone ช่วง 07:00–09:00 ตรงกับ peak ของ in-house")

    with col_r:
        st.markdown("#### Tables to Reserve per Day")
        ih_daily = (
            df[df["Guest_type"] == "In house"]
            .groupby("date")["pax"].sum().reset_index()
        )
        ih_daily["date_str"]      = ih_daily["date"].dt.strftime("%d %b")
        ih_daily["tables_needed"] = (ih_daily["pax"] / 2).apply(np.ceil).astype(int)
        avg_t = ih_daily["tables_needed"].mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ih_daily["date_str"], y=ih_daily["tables_needed"],
            marker_color=C_INHOUSE,
            text=ih_daily["tables_needed"], textposition="outside",
            textfont=dict(size=11, color=C_INHOUSE),
            width=0.5,
        ))
        fig.add_hline(
            y=avg_t, line_dash="dash", line_color=C_WALKIN, line_width=1.5,
            annotation_text=f"Avg {avg_t:.0f} tables/day",
            annotation_font=dict(family="Montserrat, sans-serif", size=11, color=C_WALKIN),
            annotation_position="top right",
        )
        fig.update_layout(
            xaxis_title="Date", yaxis_title="Tables",
            yaxis_range=[0, 50], template=TEMPLATE,
        )
        st.plotly_chart(apply_font(fig), use_container_width=True)
        st.caption("ต้อง reserve เฉลี่ย ~28 โต๊ะต่อวัน ช่วง 07:00–09:00")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Queue Skipping vs Reserved Seating")

    st.markdown(f"""
    <table class="compare-table">
        <tr>
            <th>ประเด็น</th>
            <th>Queue Skipping</th>
            <th>Reserved Seating</th>
        </tr>
        <tr>
            <td>แก้ปัญหาโต๊ะเต็ม</td>
            <td><span class="tag-no">ไม่แก้</span></td>
            <td><span class="tag-yes">จัดโต๊ะไว้ล่วงหน้า</span></td>
        </tr>
        <tr>
            <td>In-house มีที่นั่งแน่นอน</td>
            <td><span class="tag-no">ยังรอถ้าโต๊ะเต็ม</span></td>
            <td><span class="tag-yes">มีโต๊ะรอแน่นอน</span></td>
        </tr>
        <tr>
            <td>Walk-in ยอมรับได้</td>
            <td><span class="tag-no">โกรธเพราะถูกแทรกคิว</span></td>
            <td><span class="tag-yes">รู้ล่วงหน้า ยอมรับได้</span></td>
        </tr>
        <tr>
            <td>กระทบรายได้</td>
            <td>ไม่มี</td>
            <td>ไม่มี</td>
        </tr>
        <tr>
            <td>ดำเนินการ</td>
            <td><span class="tag-yes">ง่าย</span></td>
            <td><span class="tag-yes">แจ้ง front desk ตอน check-in</span></td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
