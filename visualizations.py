from collections import Counter
import plotly.graph_objects as go

def make_fp_tree(transactions, min_support):
    counts=Counter(item for basket in transactions for item in set(basket))
    threshold=max(1, int(min_support*len(transactions) + 0.999999))
    frequent={item:count for item,count in counts.items() if count>=threshold}
    if not frequent:
        fig=go.Figure()
        fig.update_layout(title="FP-tree (no items meet minimum support)")
        return fig
    ordered=sorted(frequent, key=lambda x:(-frequent[x],x))
    nodes={"ROOT": {"parent":None,"count":len(transactions),"depth":0}}
    edges=[]
    for basket in transactions:
        filtered=sorted([x for x in set(basket) if x in frequent], key=lambda x:(-frequent[x],x))
        parent="ROOT"
        for item in filtered:
            key=parent+"|||"+item
            if key not in nodes:
                nodes[key]={"parent":parent,"label":item,"count":0,"depth":nodes[parent]["depth"]+1}
                edges.append((parent,key))
            nodes[key]["count"]+=1
            parent=key
    levels={}
    for key,node in nodes.items():
        levels.setdefault(node["depth"],[]).append(key)
    pos={}
    for depth, keys in levels.items():
        keys.sort(key=lambda k:(nodes[k].get("label",""),k))
        n=len(keys)
        for i,key in enumerate(keys):
            pos[key]=(i-(n-1)/2, -depth)
    ex,ey=[],[]
    for a,b in edges:
        ex += [pos[a][0],pos[b][0],None]
        ey += [pos[a][1],pos[b][1],None]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=ex,y=ey,mode="lines",line=dict(width=1),hoverinfo="none",showlegend=False))
    labels=[]
    for key,node in nodes.items():
        label="ROOT" if key=="ROOT" else f'{node["label"]} ({node["count"]})'
        labels.append(label)
    fig.add_trace(go.Scatter(x=[pos[k][0] for k in nodes],y=[pos[k][1] for k in nodes],
        mode="markers+text",text=labels,textposition="bottom center",
        marker=dict(size=24),hovertext=[f'{labels[i]}<br>Prefix depth: {nodes[k]["depth"]}' for i,k in enumerate(nodes)],
        hoverinfo="text",showlegend=False))
    fig.update_layout(title="Simplified FP-tree (node labels show item and prefix count)",
        xaxis=dict(visible=False),yaxis=dict(visible=False),height=440,margin=dict(l=20,r=20,t=60,b=70))
    return fig
