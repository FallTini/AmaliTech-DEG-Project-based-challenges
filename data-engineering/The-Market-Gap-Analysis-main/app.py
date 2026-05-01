import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from collections import Counter

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Sugar Trap Analysis | Helix CPG Partners",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { font-family: "Helvetica Neue", sans-serif; color: #111; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("openfoodfacts_clean.csv")

    df["product_name"] = df["product_name"].fillna("Unknown")
    df["primary_category"] = df["primary_category"].fillna("Other")

    return df

df = load_data()

# ---------------------------
# BLUE OCEAN THRESHOLDS
# ---------------------------
PROTEIN_THRESHOLD = 10
SUGAR_THRESHOLD = 5

df["BlueOcean"] = df.apply(
    lambda r: "Opportunity"
    if r["proteins_100g"] >= PROTEIN_THRESHOLD and r["sugars_100g"] <= SUGAR_THRESHOLD
    else "Existing Market",
    axis=1
)

# ---------------------------
# Snack-relevant categories only for recommendation
# Meat & Fish excluded — client is a snack manufacturer
# ---------------------------
SNACK_RELEVANT = [
    "Snacks", "Beverages", "Dairy", "Cereals",
    "Bakery", "Sweets", "Condiments", "Produce"
]

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("Filters")

named_categories = sorted([c for c in df["primary_category"].unique() if c != "Other"])
all_options = named_categories + ["Other"]

selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=all_options,
    default=named_categories
)

filtered = df[df["primary_category"].isin(selected_categories)]

# ---------------------------
# HEADER
# ---------------------------
st.markdown("# Sugar Trap Market Analysis")
st.markdown("### Identifying High-Protein, Low-Sugar Market Opportunities")
st.markdown("---")

# ---------------------------
# KPI SECTION
# ---------------------------
total = len(filtered)
opp = (filtered["BlueOcean"] == "Opportunity").sum()
rate = (opp / total * 100) if total else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Products", f"{total:,}")
col2.metric("Opportunity Products", f"{opp:,}")
col3.metric("Opportunity Rate", f"{rate:.1f}%")

st.markdown("---")

# ---------------------------
# STORY 4 — KEY INSIGHT BOX
# ---------------------------
cat_summary = (
    filtered[filtered["primary_category"].isin(SNACK_RELEVANT)]
    .groupby("primary_category")["BlueOcean"]
    .apply(lambda x: (x == "Opportunity").mean() * 100)
    .reset_index(name="Opportunity %")
    .sort_values("Opportunity %", ascending=False)
)

best_category = cat_summary.iloc[0]["primary_category"] if len(cat_summary) > 0 else "Dairy"

st.markdown(f"""
<div style="
    background-color:#fff5f7;
    padding:24px;
    border-radius:12px;
    border-left:6px solid #c2185b;
    font-size:16px;
    line-height:1.8;
">
<b>🧠 Key Insight</b><br><br>
Based on the data, the biggest market opportunity is in <strong>{best_category}</strong>,
specifically targeting products with <strong>≥{PROTEIN_THRESHOLD}g of protein</strong>
and less than <strong>{SUGAR_THRESHOLD}g of sugar</strong> per 100g.<br><br>
This segment is structurally underserved — high consumer health demand,
low current product supply.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# STORY 3 — SCATTER PLOT
# ---------------------------
st.markdown("### Nutrient Landscape: Protein vs Sugar")
st.caption(
    f"Each dot = one product. "
    f"Top-left quadrant (protein ≥{PROTEIN_THRESHOLD}g, sugar ≤{SUGAR_THRESHOLD}g) = Blue Ocean opportunity."
)

fig = px.scatter(
    filtered,
    x="sugars_100g",
    y="proteins_100g",
    color="BlueOcean",
    color_discrete_map={
        "Opportunity": "#c2185b",
        "Existing Market": "#90caf9"
    },
    hover_data=["product_name", "primary_category"],
    labels={
        "sugars_100g": "Sugar per 100g (g)",
        "proteins_100g": "Protein per 100g (g)",
        "BlueOcean": "Market Segment"
    },
    opacity=0.6
)

fig.add_vline(
    x=SUGAR_THRESHOLD,
    line_dash="dash",
    line_color="#555",
    annotation_text=f"Sugar limit ({SUGAR_THRESHOLD}g)",
    annotation_position="top right"
)
fig.add_hline(
    y=PROTEIN_THRESHOLD,
    line_dash="dash",
    line_color="#555",
    annotation_text=f"Protein floor ({PROTEIN_THRESHOLD}g)",
    annotation_position="top right"
)

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("---")

# ---------------------------
# STORY 3 — CATEGORY BAR CHART
# ---------------------------
st.markdown("### Category-Level Opportunity Assessment")
st.caption("% of products in each category that fall in the high-protein, low-sugar zone.")

cat_chart = (
    filtered[filtered["primary_category"] != "Other"]
    .groupby("primary_category")["BlueOcean"]
    .apply(lambda x: (x == "Opportunity").mean() * 100)
    .reset_index(name="Opportunity %")
    .sort_values("Opportunity %", ascending=False)
)

fig2 = go.Figure(go.Bar(
    x=cat_chart["primary_category"],
    y=cat_chart["Opportunity %"],
    text=[f"{v:.1f}%" for v in cat_chart["Opportunity %"]],
    textposition="outside",
    textfont=dict(size=13, color="#111"),
    marker_color="#c2185b",
    marker_line_color="#8c0032",
    marker_line_width=1.2,
))

fig2.update_layout(
    yaxis=dict(
        title="Opportunity %",
        range=[0, cat_chart["Opportunity %"].max() * 1.25]
    ),
    xaxis_title="Category",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=40, b=40)
)

st.plotly_chart(fig2, use_container_width=True)
st.markdown("---")

# ---------------------------
# BONUS — HIDDEN GEM: Protein Sources
# Uses allowlist approach — only surfaces known protein ingredients
# ---------------------------
st.markdown("### 🥚 Hidden Gem: Top Protein Sources")
st.caption("Most frequent protein-source ingredients found in high-protein opportunity products.")

hp = filtered[
    (filtered["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (filtered["ingredients_text"] != "unknown") &
    (filtered["ingredients_text"].notna())
]

# Known protein source keywords allowlist approach
# Only ingredients matching these will be counted
PROTEIN_KEYWORDS = {
    # Animal proteins
    "whey", "casein", "collagen", "albumin",
    "chicken", "turkey", "tuna", "salmon", "beef", "pork", "cod", "tilapia",
    "egg", "eggs", "egg white", "egg whites",
    "milk protein", "milk proteins", "skimmed milk", "skim milk",
    "cottage", "ricotta", "greek", "skyr", "curd",
    # Plant proteins
    "pea protein", "soy protein", "hemp protein", "rice protein",
    "peanut", "peanuts", "almond", "almonds", "cashew", "cashews",
    "walnut", "walnuts", "pecan", "pecans", "pistachio", "pistachios",
    "hazelnut", "hazelnuts", "sunflower seed", "pumpkin seed",
    "chia", "flaxseed", "sesame",
    "lentil", "lentils", "chickpea", "chickpeas", "black bean", "kidney bean",
    "edamame", "tempeh", "tofu", "miso",
    "quinoa", "amaranth", "buckwheat",
    # Common protein labels in ingredient lists
    "whey protein", "plant protein", "isolate",
}

def clean_ing(text):
    return re.split(r",|\(|\)|\[|\]", str(text).lower())

raw_ingredients = []
for i in hp["ingredients_text"]:
    raw_ingredients.extend(clean_ing(i))

# Strip whitespace
raw_ingredients = [i.strip() for i in raw_ingredients if len(i.strip()) > 2]

# Keep only tokens that match or contain a protein keyword
matched = []
for token in raw_ingredients:
    for keyword in PROTEIN_KEYWORDS:
        if keyword in token:
            matched.append(keyword)  # normalize to the keyword itself
            break

top = Counter(matched).most_common(8)

if top:
    ing_df = pd.DataFrame(top, columns=["Ingredient", "Count"])

    fig3 = go.Figure(go.Bar(
        x=ing_df["Ingredient"],
        y=ing_df["Count"],
        text=[f"{v:,}" for v in ing_df["Count"]],
        textposition="outside",
        textfont=dict(size=13, color="#111"),
        marker_color="#1565c0",
        marker_line_color="#0d3c7a",
        marker_line_width=1.2,
    ))

    fig3.update_layout(
        yaxis=dict(
            title="Frequency",
            range=[0, ing_df["Count"].max() * 1.25]
        ),
        xaxis_title="Protein Source",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=40, b=40)
    )

    st.plotly_chart(fig3, use_container_width=True)

    top3 = ing_df["Ingredient"].head(3).tolist()
    st.markdown(f"**Top 3 protein sources:** `{top3[0]}` · `{top3[1]}` · `{top3[2]}`")

else:
    st.info("No recognizable protein sources found in the selected categories.")

st.markdown("---")

# ---------------------------
# CANDIDATE'S CHOICE — Bubble Chart
# ---------------------------
st.markdown("### 💡 Candidate's Choice: Market Size vs Opportunity Rate")
st.caption(
    "Bubble size = number of products. "
    "Top-right = large category with high opportunity = strongest R&D investment signal."
)

bubble_data = (
    filtered[filtered["primary_category"].isin(SNACK_RELEVANT)]
    .groupby("primary_category")
    .agg(
        total=("BlueOcean", "count"),
        opportunity_rate=("BlueOcean", lambda x: (x == "Opportunity").mean() * 100)
    )
    .reset_index()
)

fig4 = px.scatter(
    bubble_data,
    x="total",
    y="opportunity_rate",
    size="total",
    color="primary_category",
    text="primary_category",
    labels={
        "total": "Number of Products in Category",
        "opportunity_rate": "Opportunity Rate (%)",
        "primary_category": "Category"
    },
    size_max=60
)

fig4.update_traces(textposition="top center")
fig4.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
**Why this chart?**
Opportunity rate alone is misleading — a tiny niche with 80% opportunity rate
is less actionable than a large category with 40% rate.
This view combines **market size + opportunity rate** so the R&D team
can prioritize investment by both scale and whitespace simultaneously.
""")

st.markdown("---")

# ---------------------------
# STORY 4 — FINAL RECOMMENDATION
# ---------------------------
st.markdown("## 🚀 Final Recommendation")

cat_chart_snack = (
    filtered[filtered["primary_category"].isin(SNACK_RELEVANT)]
    .groupby("primary_category")["BlueOcean"]
    .apply(lambda x: (x == "Opportunity").mean() * 100)
    .reset_index(name="Opportunity %")
    .sort_values("Opportunity %", ascending=False)
)

if len(cat_chart_snack) >= 3:
    st.markdown(f"""
Based on the data, the biggest market opportunity is in **{best_category}**,
specifically targeting products with **≥{PROTEIN_THRESHOLD}g of protein**
and less than **{SUGAR_THRESHOLD}g of sugar** per 100g.

**Top 3 priority categories by opportunity rate:**

| Category | Opportunity Rate |
|---|---|
| {cat_chart_snack.iloc[0]['primary_category']} | {cat_chart_snack.iloc[0]['Opportunity %']:.1f}% |
| {cat_chart_snack.iloc[1]['primary_category']} | {cat_chart_snack.iloc[1]['Opportunity %']:.1f}% |
| {cat_chart_snack.iloc[2]['primary_category']} | {cat_chart_snack.iloc[2]['Opportunity %']:.1f}% |

These segments show the highest imbalance between **consumer health demand**
and **current product supply** the clearest Blue Ocean in the market.
""")

st.markdown("---")
st.caption("Sugar Trap Analysis • Built for Helix CPG Partners")
