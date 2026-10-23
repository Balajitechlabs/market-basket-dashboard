import streamlit as st
import pandas as pd
import plotly.express as px
import time
from io import BytesIO
from data_loader import load_transactions, sample_dataset
from algorithms import run_analysis
from visualizations import make_fp_tree

st.set_page_config(page_title="Market Basket Analysis", page_icon="🛒", layout="wide")
st.title("🛒 Market Basket Analysis")
st.caption("Learn how Apriori and FP-Growth discover frequent itemsets and association rules.")

with st.sidebar:
    st.header("1. Choose data")
    dataset_name = st.selectbox("Sample dataset", ["Mini Grocery Example", "Supermarket Basket", "Bakery", "Electronics Store"])
    uploaded = st.file_uploader("Or upload CSV / Excel", type=["csv", "xlsx", "xls"])
    format_choice = st.radio("Uploaded data format", [
        "Products across columns (one transaction per row)",
        "TransactionID + Item rows"
    ], help="Choose the format that matches your file.")
    st.divider()
    st.header("2. Algorithm settings")
    algorithm = st.selectbox("Algorithm", ["Compare Both", "Apriori", "FP-Growth"])
    support = st.slider("Minimum support", 0.05, 1.0, 0.20, 0.05,
                        help="Fraction of all transactions containing an itemset.")
    confidence = st.slider("Minimum confidence", 0.05, 1.0, 0.50, 0.05,
                           help="How often the right-hand item appears when the left-hand items appear.")
    lift = st.slider("Minimum lift", 0.0, 5.0, 1.0, 0.1,
                     help="Lift above 1 indicates a positive association.")
    run = st.button("▶ Run analysis", type="primary", use_container_width=True)

try:
    if uploaded:
        if uploaded.name.lower().endswith(".csv"):
            raw = pd.read_csv(uploaded)
        else:
            raw = pd.read_excel(uploaded)
        tx = load_transactions(raw, "wide" if format_choice.startswith("Products") else "long")
        data_label = uploaded.name
    else:
        tx = sample_dataset(dataset_name)
        data_label = dataset_name
except Exception as e:
    st.error(f"Could not read this dataset: {e}")
    st.stop()

if not tx or not any(tx):
    st.warning("No transactions found. Check your file format and try again.")
    st.stop()

items = sorted(set(item for basket in tx for item in basket))
c1,c2,c3 = st.columns(3)
c1.metric("Transactions", len(tx))
c2.metric("Unique items", len(items))
c3.metric("Selected dataset", data_label)
st.subheader("Preview transactions")
st.dataframe(pd.DataFrame({"Transaction ID":[f"T{i+1}" for i in range(min(20,len(tx)))],
                           "Items":[", ".join(x) for x in tx[:20]]}), use_container_width=True, hide_index=True)
st.caption("For sales records, group products by transaction/order ID first. The algorithms require baskets, not individual sales lines.")

if "results" not in st.session_state or run:
    with st.spinner("Mining frequent itemsets and association rules..."):
        try:
            st.session_state["results"] = run_analysis(tx, support, confidence, lift, algorithm)
            st.session_state["result_signature"] = (data_label, algorithm, support, confidence, lift, len(tx))
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()
results = st.session_state["results"]
sig = (data_label, algorithm, support, confidence, lift, len(tx))
if st.session_state.get("result_signature") != sig:
    st.info("Settings or data changed. Click **Run analysis** to refresh the results.")

if run or st.session_state.get("result_signature") == sig:
    st.subheader("Analysis results")
    selected = results
    if algorithm == "Compare Both":
        left,right = st.columns(2)
        for col, name in [(left,"Apriori"),(right,"FP-Growth")]:
            r=results[name]
            col.metric(f"{name} frequent itemsets", len(r["itemsets"]))
            col.metric(f"{name} association rules", len(r["rules"]))
            col.metric("Execution time", f'{r["seconds"]:.4f} s')
        comp = pd.DataFrame([{"Algorithm":n,"Frequent itemsets":len(results[n]["itemsets"]),
                              "Association rules":len(results[n]["rules"]),"Seconds":results[n]["seconds"]}
                             for n in ["Apriori","FP-Growth"]])
        st.plotly_chart(px.bar(comp, x="Algorithm", y=["Frequent itemsets","Association rules"],
                               barmode="group", title="Algorithm output comparison"), use_container_width=True)
        st.plotly_chart(px.bar(comp, x="Algorithm", y="Seconds", title="Measured execution time (lower is faster)"), use_container_width=True)
        selected = results["Apriori"]
        tabs = st.tabs(["Apriori", "FP-Growth"])
        for tab, name in zip(tabs, ["Apriori","FP-Growth"]):
            with tab:
                r=results[name]
                st.markdown(f"**Frequent itemsets: {len(r['itemsets'])} · Rules: {len(r['rules'])}**")
                if not r["itemsets"].empty:
                    st.dataframe(r["itemsets"], use_container_width=True, hide_index=True)
                if not r["rules"].empty:
                    st.dataframe(r["rules"], use_container_width=True, hide_index=True)
                if name == "FP-Growth":
                    st.plotly_chart(make_fp_tree(tx, support), use_container_width=True)
    else:
        selected = results[algorithm]
        st.metric("Execution time", f'{selected["seconds"]:.4f} s')
        st.metric("Frequent itemsets", len(selected["itemsets"]))
        st.metric("Association rules", len(selected["rules"]))
        if not selected["itemsets"].empty:
            st.plotly_chart(px.bar(selected["itemsets"].head(20), x="itemsets", y="support",
                                   title="Frequent itemsets (top 20 by support)", hover_data=["count"]),
                            use_container_width=True)
            st.plotly_chart(px.histogram(selected["itemsets"], x="support", nbins=10,
                                         title="Support distribution"), use_container_width=True)
            st.subheader("Frequent itemsets")
            st.dataframe(selected["itemsets"], use_container_width=True, hide_index=True)
        else:
            st.info("No itemsets meet the minimum support. Lower the support threshold.")
        if not selected["rules"].empty:
            st.subheader("Association rules")
            st.plotly_chart(px.bar(selected["rules"].head(15), x="rule", y="lift",
                                   title="Association rules ranked by lift", hover_data=["confidence","support"]),
                            use_container_width=True)
            st.dataframe(selected["rules"], use_container_width=True, hide_index=True)
        else:
            st.info("No rules meet the selected confidence and lift thresholds.")
        if algorithm == "FP-Growth":
            st.subheader("Simplified FP-tree illustration")
            st.plotly_chart(make_fp_tree(tx, support), use_container_width=True)

st.subheader("How to read the results")
a,b,c=st.columns(3)
a.markdown("**Support**  \nShare of transactions containing the itemset.")
b.markdown("**Confidence**  \nShare of antecedent transactions that also contain the consequent.")
c.markdown("**Lift**  \nAbove 1 suggests the items occur together more often than expected under independence.")
st.caption("The FP-tree view is a simplified frequency-ordered prefix tree for learning; frequent itemsets and rules are computed by mlxtend's real algorithm implementations.")

for name in ["Apriori","FP-Growth"]:
    if name in results:
        r=results[name]
        st.download_button(f"Download {name} itemsets CSV", r["itemsets"].to_csv(index=False).encode("utf-8"),
                           file_name=f"{name.lower().replace('-','_')}_itemsets.csv", mime="text/csv", key=name+"items")
        st.download_button(f"Download {name} rules CSV", r["rules"].to_csv(index=False).encode("utf-8"),
                           file_name=f"{name.lower().replace('-','_')}_rules.csv", mime="text/csv", key=name+"rules")
