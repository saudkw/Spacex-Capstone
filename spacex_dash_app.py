# spacex_dash_app.py

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# Load SpaceX dataset (official course dataset URL)

spacex_df = pd.read_csv("/Users/saud/Documents/New project/Spacex-Capstone/dataset_part_2.csv")

# Rename columns so they match the dashboard assignment code
spacex_df = spacex_df.rename(columns={
    "LaunchSite": "Launch Site",
    "PayloadMass": "Payload Mass (kg)",
    "Class": "class",
    "BoosterVersion": "Booster Version Category"
})

# Clean types
spacex_df["class"] = spacex_df["class"].astype(int)
spacex_df["Payload Mass (kg)"] = pd.to_numeric(spacex_df["Payload Mass (kg)"], errors="coerce")
spacex_df = spacex_df.dropna(subset=["Payload Mass (kg)"])
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        "SpaceX Launch Records Dashboard",
        style={"textAlign": "center", "color": "#503D36", "font-size": 40}
    ),

    dcc.Dropdown(
        id="site-dropdown",
        options=(
            [{"label": "All Sites", "value": "ALL"}] +
            [{"label": site, "value": site} for site in sorted(spacex_df["Launch Site"].unique())]
        ),
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    dcc.Graph(id="success-pie-chart"),

    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=max_payload,
        step=1000,
        marks={i: str(i) for i in range(0, int(max_payload) + 1000, 1000)},
        value=[0, max_payload]
    ),

    html.Br(),

    dcc.Graph(id="success-payload-scatter-chart")
])


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        success_by_site = spacex_df.groupby("Launch Site")["class"].sum().reset_index()
        fig = px.pie(
            success_by_site,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site"
        )
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        outcome_counts = filtered_df["class"].value_counts().reset_index()
        outcome_counts.columns = ["class", "count"]
        outcome_counts["Outcome"] = outcome_counts["class"].map({1: "Success", 0: "Failure"})
        fig = px.pie(
            outcome_counts,
            values="count",
            names="Outcome",
            title=f"Total Success vs Failure for {entered_site}"
        )
    return fig


@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"),
     Input("payload-slider", "value")]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        title = f"Payload vs. Outcome for {entered_site}"
    else:
        title = "Payload vs. Outcome for All Sites"

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
