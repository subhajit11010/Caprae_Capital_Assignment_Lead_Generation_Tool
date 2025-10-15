import json
import pandas as pd
import re
import plotly.express as px


def parse_revenue(rev_str):
    if not rev_str or not isinstance(rev_str, str):
        return None
    match = re.search(r"\$([\d\.]+)\s*(million|billion)?", rev_str.lower())
    if match:
        num = float(match.group(1))
        scale = match.group(2)
        if scale == "billion":
            num *= 1e9
        elif scale == "million":
            num *= 1e6
        return num
    return None

def df_creator_from_json_and_process(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)["companies"]
        
    return pd.DataFrame(data)

def create_chart(filepath: str):
    df = df_creator_from_json_and_process(filepath)
    # print(df)
    industry_counts = df["key_industry"].value_counts().reset_index()
    industry_counts.columns = ["Industry", "Count"]
    country_counts = df["country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]
    btype_counts= df["business_type"].value_counts().reset_index()
    btype_counts.columns = ["Business Type", "Count"]

    df["approx_revenue_usd"] = df["approx_revenue"].apply(parse_revenue)

    fig_industry = px.pie(
        industry_counts,
        names="Industry",
        values="Count",
        title="Distribution of Companies by Industry",
        # hole=0.3  # Optional: Creates a donut chart
    )
    fig_country = px.pie(
        country_counts,
        names="Country",
        values="Count",
        title="Distribution of Companies by Country"
    )
    fig_btype = px.pie(
        btype_counts,
        names = "Business Type",
        values="Count",
        title="Distribution of Companies by Business types"
    )
    fig_rev = px.bar(
        df.sort_values(by="approx_revenue_usd", ascending=False),
        x="company_name",
        y="approx_revenue_usd",
        color="key_industry",
        title="Company Revenue Comparison",
        text="approx_revenue"
    )

    fig_industry.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        width = 400,
        height=480,
        margin=dict(l=0, r=0, b=0, t=20),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    fig_country.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        height=300,
        margin=dict(l=0, r=0, b=0, t=20),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )
    fig_btype.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        width = 400,
        height=300,
        margin=dict(l=0, r=0, b=0, t=20),
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    fig_rev.update_layout(
        xaxis_title="Company",
        yaxis_title="Revenue (USD)",
        yaxis_tickformat="$,.0f",
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        legend = dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
            y=-0.8
        )
    )

    return fig_industry, fig_country, fig_btype, fig_rev