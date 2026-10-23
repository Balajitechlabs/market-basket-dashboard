import time
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules

def run_one(tx, algorithm, min_support, min_confidence, min_lift):
    te = TransactionEncoder()
    matrix = te.fit(tx).transform(tx)
    basket = pd.DataFrame(matrix, columns=te.columns_)
    start = time.perf_counter()
    if algorithm == "Apriori":
        freq = apriori(basket, min_support=min_support, use_colnames=True)
    else:
        freq = fpgrowth(basket, min_support=min_support, use_colnames=True)
    seconds = time.perf_counter() - start
    if freq.empty:
        itemsets = pd.DataFrame(columns=["itemsets","support","count","size"])
        rules = pd.DataFrame(columns=["antecedent","consequent","support","confidence","lift","rule"])
        return {"itemsets":itemsets,"rules":rules,"seconds":seconds}
    freq["count"] = (freq["support"] * len(tx)).round().astype(int)
    freq["size"] = freq["itemsets"].apply(len)
    freq["itemsets"] = freq["itemsets"].apply(lambda x: ", ".join(sorted(x)))
    itemsets = freq[["itemsets","support","count","size"]].sort_values(["size","support"], ascending=[True,False]).reset_index(drop=True)
    # mlxtend expects the frozenset-valued itemsets column; preserve a separate internal table.
    internal = apriori(basket, min_support=min_support, use_colnames=True) if algorithm == "Apriori" else fpgrowth(basket, min_support=min_support, use_colnames=True)
    try:
        rules_df = association_rules(internal, metric="confidence", min_threshold=min_confidence)
        rules_df = rules_df[rules_df["lift"] >= min_lift].copy()
        if rules_df.empty:
            rules = pd.DataFrame(columns=["antecedent","consequent","support","confidence","lift","rule"])
        else:
            rules_df["antecedent"] = rules_df["antecedents"].apply(lambda x: ", ".join(sorted(x)))
            rules_df["consequent"] = rules_df["consequents"].apply(lambda x: ", ".join(sorted(x)))
            rules_df["rule"] = rules_df["antecedent"] + " → " + rules_df["consequent"]
            rules = rules_df[["antecedent","consequent","support","confidence","lift","rule"]].sort_values("lift",ascending=False).reset_index(drop=True)
    except ValueError:
        rules = pd.DataFrame(columns=["antecedent","consequent","support","confidence","lift","rule"])
    return {"itemsets":itemsets,"rules":rules,"seconds":seconds}

def run_analysis(tx, min_support, min_confidence, min_lift, algorithm):
    if not tx or not any(tx):
        raise ValueError("Dataset contains no usable transactions.")

    result = {}
    if algorithm in ("Apriori", "Compare Both"):
        result["Apriori"] = run_one(tx, "Apriori", min_support, min_confidence, min_lift)
    if algorithm in ("FP-Growth", "Compare Both"):
        result["FP-Growth"] = run_one(tx, "FP-Growth", min_support, min_confidence, min_lift)
    if algorithm == "Compare Both":
        return result
    if algorithm in {"Apriori", "FP-Growth"}:
        return result
    raise ValueError(f"Unsupported algorithm: {algorithm}")
