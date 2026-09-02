# 🏥 Hospital Bed & Resource Availability Tracker
### Academic Project | Streamlit + Gemini 2.5 Flash AI

> ⚠️ **DISCLAIMER:** This is an academic prototype for educational and demonstration purposes only.
> All data is **fictional**. This application must **NOT** be used for real hospital decision-making
> or clinical management.

---

## 📋 What This Project Does

This application is an AI-powered dashboard that helps a hospital administrator track the
availability of hospital resources such as beds, ICU beds, ventilators, and more.

**Key Features:**
- 📊 Live dashboard with resource counts and availability percentages
- 🗂️ Add and update resources (admin panel)
- 🔍 Filter by hospital, department, resource type, and status
- 🚨 Configurable low-availability alerts
- 📈 30-day historical trend charts
- 🤖 AI-generated plain-language summary powered by Gemini 2.5 Flash
- 🧪 Built-in demo data — works immediately without any real data

---

## 📁 Project Files

```
hospital_tracker/
│
├── app.py                  ← Main Streamlit application (run this)
├── data.py                 ← All demo/sample data (fictional only)
├── requirements.txt        ← Python packages needed
├── README.md               ← This file
│
└── .streamlit/
    └── secrets.toml        ← Where you put your Gemini API key (private)
```

---

## 🚀 Step-by-Step Setup Guide (Beginner Friendly)

### Step 1 — Make sure Python is installed

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:
```
python --version
```
If you see a version number like `Python 3.10.x`, you are ready.
If not, download Python from https://www.python.org/downloads/ and install it.

---

### Step 2 — Open a terminal inside the project folder

Navigate into the `hospital_tracker` folder:
```
cd hospital_tracker
```

---

### Step 3 — Install required packages

Run this one command:
```
pip install -r requirements.txt
```
This installs Streamlit, Pandas, and the Gemini AI library.
Wait for it to finish (may take 1–2 minutes).

---

### Step 4 — Add your Gemini API Key (for AI features)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"** and copy it
4. Open the file `.streamlit/secrets.toml` (inside the `hospital_tracker` folder)
5. Replace `PASTE_YOUR_GEMINI_API_KEY_HERE` with your actual key:

```toml
GEMINI_API_KEY = "AIza...your_actual_key_here..."
```

6. Save the file.

> 💡 The `.streamlit` folder may be hidden on some systems.
> On Windows: enable "Show hidden items" in File Explorer.
> On Mac: press Cmd+Shift+. to show hidden files.

> ✅ The app still works **without** a key — the AI summary page will just show
> instructions for how to add the key instead of generating a summary.

---

### Step 5 — Run the application

Inside the `hospital_tracker` folder, run:
```
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**

---

## 🧪 How to Test Every Feature

### 1. Dashboard (📊)
- Click **"📊 Dashboard"** in the left sidebar
- **Expected:** You see 5 metric boxes at the top (Total, Available, Occupied, Under Maintenance, %)
- **Expected:** You see per-resource-type breakdown
- **Expected:** You see Low-Availability Alerts (or green "all OK" message)
- **Expected:** You see a bar chart of status distribution

### 2. Filters
- Use the **Filters** section in the sidebar
- Change Hospital from "All" to "City General Hospital"
- **Expected:** All data on screen updates to show only that hospital
- Try changing Department or Status — the table and metrics update live

### 3. Alert Threshold
- In the sidebar, find **"Alert Threshold"**
- Change the number (e.g. set it to 20)
- **Expected:** More alerts appear on the Dashboard because the threshold is higher
- Set it back to 3 — fewer alerts appear

### 4. Resource Management (🗂️)
**Add a resource:**
- Click **"🗂️ Resource Management"** in the sidebar
- Click the **"➕ Add Resource"** tab
- Fill in the form (pick a hospital, department, type, enter an ID like "BED-999", pick status)
- Click "➕ Add Resource"
- **Expected:** Green success message

**Update a resource:**
- Click the **"✏️ Update Status"** tab
- Pick any Resource ID from the dropdown
- Change the status to something different
- Click "✏️ Update Status"
- **Expected:** Green success message; if you go back to Dashboard, that resource shows the new status

**Search resources:**
- Click the **"🔎 View / Search"** tab
- Type "ICU" in the search box
- **Expected:** Table filters down to only ICU-related resources

### 5. Historical Analytics (📈)
- Click **"📈 Historical Analytics"** in the sidebar
- Choose a Hospital and Resource Type from the dropdowns
- **Expected:** A line chart showing 30 days of simulated data
- Change the "Show metric" dropdown between Available / Occupied / Under Maintenance
- **Expected:** Chart updates to show different metric
- Scroll down to see the "All Metrics Comparison" chart and summary statistics table

### 6. AI Summary (🤖)
- Click **"🤖 AI Summary"** in the sidebar
- Make sure you have added your Gemini API key (Step 4 above)
- Click **"🤖 Generate AI Summary"**
- **Expected:** A spinner appears, then a plain-English paragraph explaining the current resource situation
- **If no key:** You see a message explaining how to add the key

### 7. Reset Demo Data
- Go to **🗂️ Resource Management → 🔎 View / Search** tab
- Scroll down and click **"🔄 Reset to Demo Data"**
- **Expected:** All resources return to the original demo dataset

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `streamlit: command not found` | Run `pip install streamlit` first |
| App doesn't open in browser | Manually open http://localhost:8501 |
| AI Summary shows "API key not found" | Follow Step 4 above to add your key |
| AI error "quota exceeded" | Your free Gemini quota is used up; wait or use a new key |
| `ModuleNotFoundError` for any package | Run `pip install -r requirements.txt` again |
| Port already in use | Run `streamlit run app.py --server.port 8502` |

---

## 🔑 API Key Security Notes

- **Never share** your `secrets.toml` file with anyone
- **Never upload** your `secrets.toml` to GitHub or any public location
- The `.streamlit/secrets.toml` file is the standard Streamlit way to store secrets safely
- If you deploy to **Streamlit Cloud**, add your key in the app's "Secrets" settings panel instead

---

## 📚 Technology Stack

| Component | Technology |
|---|---|
| Web Framework | Streamlit (Python) |
| Data | Pandas + fictional demo data |
| Charts | Streamlit built-in charts |
| AI | Google Gemini 2.5 Flash via `google-generativeai` |
| Language | Python 3.9+ |

---

*Academic project — All data is fictional — Not for clinical use*
