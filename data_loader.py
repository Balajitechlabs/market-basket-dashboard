import pandas as pd

def sample_dataset(name):
    if name == "Mini Grocery Example":
        return [
            ["Milk","Bread","Butter"], ["Bread","Butter"], ["Milk","Bread"],
            ["Milk","Butter"], ["Milk","Bread","Butter"]
        ]
    if name == "Supermarket Basket":
        return [
            ["Milk","Bread","Eggs"],["Bread","Butter"],["Milk","Bread","Butter"],
            ["Eggs","Bread"],["Milk","Eggs"],["Bread","Butter","Jam"],
            ["Milk","Bread","Eggs","Butter"],["Coffee","Sugar","Milk"],
            ["Coffee","Sugar"],["Bread","Milk"],["Eggs","Butter"],
            ["Milk","Bread","Butter"],["Coffee","Milk","Sugar"],
            ["Bread","Jam"],["Milk","Bread","Eggs"]
        ]
    if name == "Bakery":
        return [
            ["Bread","Croissant","Coffee"],["Bread","Butter"],["Cake","Coffee"],
            ["Croissant","Coffee"],["Bread","Butter","Jam"],["Cake","Tea"],
            ["Bread","Coffee"],["Muffin","Coffee"],["Cake","Muffin"],
            ["Bread","Butter"],["Croissant","Tea"],["Coffee","Muffin"]
        ]
    return [
        ["Laptop","Mouse","Laptop Bag"],["Phone","Case","Screen Protector"],
        ["Laptop","Mouse"],["Phone","Earbuds"],["Tablet","Case","Stylus"],
        ["Laptop","Laptop Bag"],["Phone","Case"],["Tablet","Stylus"],
        ["Laptop","Mouse","USB Hub"],["Phone","Earbuds","Case"],
        ["Tablet","Case"],["Laptop","USB Hub"]
    ]

def load_transactions(df, mode="wide"):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")
    if df.empty:
        return []
    if mode == "long":
        lower = {c.lower(): c for c in df.columns}
        tid = next((lower[k] for k in ["transactionid","transaction_id","transaction id","orderid","order_id","order id","invoice","invoiceno"] if k in lower), None)
        item = next((lower[k] for k in ["item","product","productname","product_name","description"] if k in lower), None)
        if not tid or not item:
            raise ValueError("Long format needs columns like TransactionID and Item (or Product).")
        baskets = []
        for _, group in df.groupby(tid, sort=False):
            vals = [str(x).strip() for x in group[item].dropna() if str(x).strip()]
            if vals: baskets.append(list(dict.fromkeys(vals)))
        return baskets
    baskets=[]
    for _, row in df.iterrows():
        vals=[]
        for value in row.tolist():
            if pd.isna(value): continue
            # Avoid treating zero/false placeholders as products.
            s=str(value).strip()
            if not s or s.lower() in {"nan","none","null","0","false"}: continue
            vals.append(s)
        if vals: baskets.append(list(dict.fromkeys(vals)))
    return baskets
