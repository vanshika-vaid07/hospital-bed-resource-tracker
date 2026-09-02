"""
app.py — Hospital Bed & Resource Availability Tracker
======================================================
Academic prototype — NOT for real clinical or medical use.

Run with:
    streamlit run app.py
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os

# ── Third-party ───────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd

# ── Local modules ─────────────────────────────────────────────────────────────
from data import (
    generate_resource_data,
    generate_historical_data,
    HOSPITALS,
    DEPARTMENTS,
    RESOURCE_TYPES,
    STATUSES,
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the FIRST Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Hospital Resource Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION-STATE INITIALISATION
# ══════════════════════════════════════════════════════════════════════════════
if "resources" not in st.session_state:
    st.session_state["resources"] = generate_resource_data()

if "history" not in st.session_state:
    st.session_state["history"] = generate_historical_data(days=30)

if "threshold" not in st.session_state:
    st.session_state["threshold"] = 3          # default low-availability threshold

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_gemini_summary(resource_summary: str) -> str:
    """
    Calls the Gemini 2.5 Flash API and returns an AI-generated summary.
    Returns an error message string if the API key is missing or the call fails.
    """
    # --- Try to read the key from Streamlit secrets, then environment variable ---
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.environ.get("GEMINI_API_KEY", "")

    # Treat the placeholder value (user hasn't replaced it yet) the same as missing
    if not api_key or api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        return (
            "⚠️ **Gemini API key not found.**\n\n"
            "To enable the AI summary:\n"
            "1. Open the file `.streamlit/secrets.toml` inside the `hospital_tracker` folder.\n"
            "2. Add your key: `GEMINI_API_KEY = \"YOUR_KEY_HERE\"`\n"
            "3. Save the file and refresh this page.\n\n"
            "You can get a free key at https://aistudio.google.com/app/apikey"
        )

    try:
        import google.generativeai as genai          # imported here to avoid crash if not installed

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are an AI assistant helping a hospital administrator understand their current
resource availability situation. Based on the data summary below, please provide:

1. A brief overview of the current hospital resource situation (2-3 sentences).
2. Which resource types have the lowest availability and may need attention.
3. Which hospitals or departments appear most under pressure.
4. A simple, plain-language recommendation for the administrator.

Keep the response concise (under 200 words), friendly, and easy to understand.

IMPORTANT: Do NOT make any medical diagnoses, clinical decisions, or patient-specific recommendations.
This is for resource management only.

--- RESOURCE DATA SUMMARY ---
{resource_summary}
"""

        response = model.generate_content(prompt)
        return response.text

    except ImportError:
        return (
            "⚠️ The `google-generativeai` package is not installed.\n"
            "Run `pip install google-generativeai` and restart the app."
        )
    except Exception as exc:
        return f"⚠️ Gemini API error: {exc}"


def build_resource_summary(df: pd.DataFrame) -> str:
    """Creates a plain-text summary of the resource DataFrame for the AI prompt."""
    lines = []
    total = len(df)
    lines.append(f"Total resources tracked: {total}")

    for status in STATUSES:
        count = len(df[df["Status"] == status])
        pct = round(count / total * 100, 1) if total else 0
        lines.append(f"  - {status}: {count} ({pct}%)")

    lines.append("")
    lines.append("Breakdown by Resource Type:")
    for rtype in df["Resource Type"].unique():
        sub = df[df["Resource Type"] == rtype]
        avail = len(sub[sub["Status"] == "Available"])
        lines.append(f"  {rtype}: {avail} available out of {len(sub)}")

    lines.append("")
    lines.append("Breakdown by Hospital:")
    for hosp in df["Hospital"].unique():
        sub = df[df["Hospital"] == hosp]
        avail = len(sub[sub["Status"] == "Available"])
        lines.append(f"  {hosp}: {avail} available out of {len(sub)}")

    return "\n".join(lines)


def apply_filters(df: pd.DataFrame, hospital, department, rtype, status) -> pd.DataFrame:
    """Returns a filtered copy of the DataFrame based on the selected sidebar filters."""
    filtered = df.copy()
    if hospital != "All":
        filtered = filtered[filtered["Hospital"] == hospital]
    if department != "All":
        filtered = filtered[filtered["Department"] == department]
    if rtype != "All":
        filtered = filtered[filtered["Resource Type"] == rtype]
    if status != "All":
        filtered = filtered[filtered["Status"] == status]
    return filtered


def status_colour(status: str) -> str:
    """Returns a simple emoji badge for a status value."""
    return {"Available": "🟢", "Occupied": "🔴", "Under Maintenance": "🟡"}.get(status, "⚪")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hospital.png", width=72)
    st.title("🏥 Hospital Tracker")
    st.caption("Academic Demo — Not for clinical use")
    st.divider()

    # Navigation
    page = st.radio(
        "Navigate to",
        [
            "📊 Dashboard",
            "🗂️ Resource Management",
            "📈 Historical Analytics",
            "🤖 AI Summary",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # ── Global Filters ──
    st.subheader("🔍 Filters")
    f_hospital = st.selectbox("Hospital", ["All"] + HOSPITALS)
    f_department = st.selectbox("Department", ["All"] + DEPARTMENTS)
    f_rtype = st.selectbox("Resource Type", ["All"] + RESOURCE_TYPES)
    f_status = st.selectbox("Status", ["All"] + STATUSES)

    st.divider()

    # ── Alert Threshold ──
    st.subheader("🚨 Alert Threshold")
    threshold = st.number_input(
        "Warn when available count ≤",
        min_value=1,
        max_value=20,
        value=st.session_state["threshold"],
        step=1,
        help="An alert appears on the Dashboard when any resource type in a hospital "
             "has this many (or fewer) units left Available.",
    )
    st.session_state["threshold"] = threshold

    st.divider()
    st.caption("⚠️ DISCLAIMER: This application is an academic prototype for demonstration and educational purposes only. It must NOT be used for real hospital decision-making or clinical management.")

# ══════════════════════════════════════════════════════════════════════════════
# FILTERED DATA  (used by all pages)
# ══════════════════════════════════════════════════════════════════════════════
df_all = st.session_state["resources"]
df_filtered = apply_filters(df_all, f_hospital, f_department, f_rtype, f_status)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Hospital Resource Dashboard")
    st.caption("Live snapshot of all tracked hospital resources (demo data).")
    st.divider()

    # ── Top Metrics ──────────────────────────────────────────────────────────
    total_res   = len(df_filtered)
    avail_res   = len(df_filtered[df_filtered["Status"] == "Available"])
    occup_res   = len(df_filtered[df_filtered["Status"] == "Occupied"])
    maint_res   = len(df_filtered[df_filtered["Status"] == "Under Maintenance"])
    avail_pct   = round(avail_res / total_res * 100, 1) if total_res else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Resources",     total_res)
    c2.metric("🟢 Available",        avail_res)
    c3.metric("🔴 Occupied",         occup_res)
    c4.metric("🟡 Under Maintenance", maint_res)
    c5.metric("✅ Availability %",   f"{avail_pct}%")

    st.divider()

    # ── Per-Resource-Type Metrics ─────────────────────────────────────────────
    st.subheader("Resource Type Breakdown")
    col_pairs = st.columns(3)
    for idx, rtype in enumerate(RESOURCE_TYPES):
        sub = df_filtered[df_filtered["Resource Type"] == rtype]
        a = len(sub[sub["Status"] == "Available"])
        t = len(sub)
        col_pairs[idx % 3].metric(rtype, f"{a} / {t} available")

    st.divider()

    # ── Low-Availability Alerts ───────────────────────────────────────────────
    st.subheader("🚨 Low-Availability Alerts")
    alert_found = False

    # Alerts always run against the FULL (unfiltered) dataset so that status/dept
    # filters don't produce false "0 available" warnings.
    for hosp in (HOSPITALS if f_hospital == "All" else [f_hospital]):
        for rtype in (RESOURCE_TYPES if f_rtype == "All" else [f_rtype]):
            sub = df_all[
                (df_all["Hospital"] == hosp) &
                (df_all["Resource Type"] == rtype) &
                (df_all["Status"] == "Available")
            ]
            if len(sub) <= threshold:
                st.warning(
                    f"⚠️ **{hosp}** — **{rtype}**: only **{len(sub)}** unit(s) available "
                    f"(threshold = {threshold})"
                )
                alert_found = True

    if not alert_found:
        st.success(f"✅ All resource types are above the alert threshold ({threshold} units).")

    st.divider()

    # ── Resource Table ────────────────────────────────────────────────────────
    st.subheader("📋 Resource Details")

    if df_filtered.empty:
        st.info("No resources match the selected filters. Try changing the filter options in the sidebar.")
    else:
        display_df = df_filtered.copy()
        display_df["Status"] = display_df["Status"].apply(
            lambda s: f"{status_colour(s)} {s}"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Status Pie-style Bar Chart ────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Status Distribution")

    if not df_filtered.empty:
        status_counts = df_filtered["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.bar_chart(status_counts.set_index("Status"))
    else:
        st.info("No data to chart. Adjust your filters.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — RESOURCE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗂️ Resource Management":
    st.title("🗂️ Resource Management")
    st.caption("Add new resources or update the status of existing ones.")
    st.divider()

    tab_add, tab_update, tab_view = st.tabs(["➕ Add Resource", "✏️ Update Status", "🔎 View / Search"])

    # ── Tab: Add Resource ─────────────────────────────────────────────────────
    with tab_add:
        st.subheader("Add a New Resource")
        with st.form("add_resource_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_hospital  = st.selectbox("Hospital",      HOSPITALS,       key="add_hosp")
                new_dept      = st.selectbox("Department",    DEPARTMENTS,     key="add_dept")
                new_rtype     = st.selectbox("Resource Type", RESOURCE_TYPES,  key="add_rtype")
            with col2:
                new_id        = st.text_input("Resource ID / Name", placeholder="e.g. BED-301")
                new_status    = st.selectbox("Current Status", STATUSES,       key="add_status")
                new_note      = st.text_area("Notes (optional)", height=80)

            submitted = st.form_submit_button("➕ Add Resource", use_container_width=True)

        if submitted:
            if not new_id.strip():
                st.error("❌ Please enter a Resource ID or Name before submitting.")
            elif new_id.strip() in st.session_state["resources"]["Resource ID"].values:
                st.error(f"❌ Resource ID **{new_id.strip()}** already exists. Please use a unique ID.")
            else:
                from datetime import datetime
                new_row = {
                    "Hospital":      new_hospital,
                    "Department":    new_dept,
                    "Resource Type": new_rtype,
                    "Resource ID":   new_id.strip(),
                    "Status":        new_status,
                    "Last Updated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.session_state["resources"] = pd.concat(
                    [st.session_state["resources"], pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                st.success(f"✅ Resource **{new_id.strip()}** added successfully as **{new_status}**.")

    # ── Tab: Update Status ────────────────────────────────────────────────────
    with tab_update:
        st.subheader("Update Resource Status")
        st.info("Use the filters in the sidebar to narrow down the list, then pick a Resource ID to update.")

        resource_ids = df_filtered["Resource ID"].tolist()

        if not resource_ids:
            st.warning("No resources match the current filters. Adjust the sidebar filters to find resources.")
        else:
            with st.form("update_form"):
                selected_id  = st.selectbox("Select Resource ID", resource_ids)
                new_status_u = st.selectbox("New Status", STATUSES, key="upd_status")
                upd_note     = st.text_input("Reason / Note (optional)")
                update_btn   = st.form_submit_button("✏️ Update Status", use_container_width=True)

            if update_btn:
                from datetime import datetime
                mask = st.session_state["resources"]["Resource ID"] == selected_id
                st.session_state["resources"].loc[mask, "Status"]       = new_status_u
                st.session_state["resources"].loc[mask, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success(f"✅ **{selected_id}** status updated to **{new_status_u}**.")
                st.rerun()

    # ── Tab: View / Search ────────────────────────────────────────────────────
    with tab_view:
        st.subheader("View & Search Resources")
        search_term = st.text_input("🔍 Search by Resource ID or keyword", placeholder="e.g. BED or ICU")

        view_df = df_filtered.copy()
        if search_term.strip():
            view_df = view_df[
                view_df["Resource ID"].str.contains(search_term.strip(), case=False, na=False) |
                view_df["Resource Type"].str.contains(search_term.strip(), case=False, na=False) |
                view_df["Department"].str.contains(search_term.strip(), case=False, na=False)
            ]

        st.write(f"Showing **{len(view_df)}** resource(s).")
        if view_df.empty:
            st.info("No matching resources found.")
        else:
            st.dataframe(view_df, use_container_width=True, hide_index=True)

        if st.button("🔄 Reset to Demo Data"):
            st.session_state["resources"] = generate_resource_data()
            st.success("✅ Resource data has been reset to the original demo dataset.")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — HISTORICAL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Historical Analytics":
    st.title("📈 Historical Occupancy & Availability Trends")
    st.caption("30-day simulated trend data (demo only — not real historical records).")
    st.divider()

    hist_df = st.session_state["history"]

    # Selector controls
    col1, col2, col3 = st.columns(3)
    with col1:
        h_hosp  = st.selectbox("Hospital",      HOSPITALS,      key="hist_hosp")
    with col2:
        h_rtype = st.selectbox("Resource Type", RESOURCE_TYPES, key="hist_rtype")
    with col3:
        h_metric = st.selectbox("Show metric",  ["Available", "Occupied", "Under Maintenance"], key="hist_metric")

    # Filter history
    hist_filtered = hist_df[
        (hist_df["Hospital"]       == h_hosp) &
        (hist_df["Resource Type"]  == h_rtype)
    ].copy()

    hist_filtered = hist_filtered.sort_values("Date")

    if hist_filtered.empty:
        st.warning("No historical data available for this selection.")
    else:
        st.subheader(f"{h_metric} trend — {h_rtype} at {h_hosp}")
        chart_data = hist_filtered.set_index("Date")[[h_metric]]
        st.line_chart(chart_data)

        st.divider()

        # All-three-metrics comparison
        st.subheader("All Metrics Comparison")
        all_metrics = hist_filtered.set_index("Date")[["Available", "Occupied", "Under Maintenance"]]
        st.line_chart(all_metrics)

        st.divider()

        # Summary statistics
        st.subheader("Summary Statistics (last 30 days)")
        summary = hist_filtered[["Available", "Occupied", "Under Maintenance", "Total"]].describe().round(1)
        st.dataframe(summary, use_container_width=True)

        st.divider()

        # Bar chart: average availability per resource type (across all hospitals)
        st.subheader("Average Daily Availability — All Resource Types")
        avg_avail = (
            hist_df[hist_df["Hospital"] == h_hosp]
            .groupby("Resource Type")["Available"]
            .mean()
            .round(1)
            .reset_index()
        )
        avg_avail.columns = ["Resource Type", "Avg Available"]
        st.bar_chart(avg_avail.set_index("Resource Type"))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — AI SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Summary":
    st.title("🤖 AI-Powered Resource Summary")
    st.caption(
        "Uses Google Gemini 2.5 Flash to generate a plain-language summary of the current resource situation. "
        "AI does NOT make clinical decisions or medical diagnoses."
    )
    st.divider()

    st.info(
        "The AI reads the **currently filtered resource data** and generates a short, "
        "easy-to-understand summary. Use the sidebar filters to focus on a specific hospital or resource type, "
        "then click the button below."
    )

    # Show what data will be used
    st.subheader("Data being analysed")
    total = len(df_filtered)
    avail = len(df_filtered[df_filtered["Status"] == "Available"])
    occup = len(df_filtered[df_filtered["Status"] == "Occupied"])
    maint = len(df_filtered[df_filtered["Status"] == "Under Maintenance"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Resources", total)
    m2.metric("Available",       avail)
    m3.metric("Occupied",        occup)
    m4.metric("Under Maintenance", maint)

    if df_filtered.empty:
        st.warning("No data to analyse. Please adjust the filters in the sidebar.")
    else:
        st.divider()
        if st.button("🤖 Generate AI Summary", use_container_width=True):
            with st.spinner("Asking Gemini 2.5 Flash to analyse the resource data…"):
                summary_text = build_resource_summary(df_filtered)
                ai_response  = get_gemini_summary(summary_text)

            st.divider()
            st.subheader("📝 AI-Generated Summary")
            st.markdown(ai_response)

            st.divider()
            st.caption(
                "⚠️ DISCLAIMER: The above AI-generated summary is for educational/demonstration purposes only. "
                "It is NOT a clinical recommendation and must NOT be used for real medical or hospital decisions."
            )

        # Show the raw data summary that will be sent
        with st.expander("🔍 See the raw data summary sent to the AI"):
            st.text(build_resource_summary(df_filtered))

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER  (shown on every page)
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.caption(
    "🎓 **Hospital Bed & Resource Availability Tracker** | Academic Prototype | "
    "All data is fictional and for demonstration purposes only. | "
    "Not for real clinical or hospital use."
)
