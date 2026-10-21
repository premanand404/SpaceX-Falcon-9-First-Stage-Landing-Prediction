"""Interactive Plotly Dash dashboard: filter launch site and payload mass."""
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from src.common import load_course_csv, ensure_class


def build_app():
    df = ensure_class(load_course_csv("dataset_part_2.csv"))
    for col in ["PayloadMass", "FlightNumber", "Class"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "LaunchSite" not in df:
        df["LaunchSite"] = "All sites"
    if "PayloadMass" not in df:
        df["PayloadMass"] = 0
    if "FlightNumber" not in df:
        df["FlightNumber"] = range(1, len(df)+1)
    sites = sorted(df["LaunchSite"].dropna().astype(str).unique().tolist())
    lo = int(max(0, df["PayloadMass"].min(skipna=True) or 0))
    hi = int(df["PayloadMass"].max(skipna=True) or 1)
    app = Dash(__name__)
    app.title = "SpaceX Falcon 9 Landing Analytics"
    app.layout = html.Div([
        html.H1("SpaceX Falcon 9 Landing Analytics"),
        html.Label("Launch site"),
        dcc.Dropdown(id="site", options=[{"label":"All sites","value":"__ALL__"}] + [{"label":s,"value":s} for s in sites], value="__ALL__", clearable=False),
        html.Label("Payload mass range (kg)"),
        dcc.RangeSlider(id="payload", min=lo, max=max(hi, lo+1), step=250, value=[lo, hi], tooltip={"placement":"bottom","always_visible":False}, marks=None, allowCross=False),
        html.Div([dcc.Graph(id="outcome-pie"), dcc.Graph(id="payload-flight")], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"16px"}),
        html.P("Class 1 denotes a successful first-stage landing; Class 0 denotes an unsuccessful landing.")
    ], style={"fontFamily":"Arial, sans-serif","maxWidth":"1300px","margin":"24px auto","padding":"0 18px"})

    @app.callback(Output("outcome-pie","figure"), Output("payload-flight","figure"), Input("site","value"), Input("payload","value"))
    def update(site, payload_range):
        filtered = df[(df["PayloadMass"] >= payload_range[0]) & (df["PayloadMass"] <= payload_range[1])].copy()
        if site != "__ALL__":
            filtered = filtered[filtered["LaunchSite"].astype(str) == site]
        outcomes = filtered["Class"].map({1:"Successful landing",0:"Unsuccessful landing"}).fillna("Unknown")
        pie_df = outcomes.value_counts().rename_axis("Outcome").reset_index(name="Launches")
        pie = px.pie(pie_df, names="Outcome", values="Launches", title="Landing outcome distribution", hole=.38)
        scatter = px.scatter(filtered, x="FlightNumber", y="PayloadMass", color=filtered["Class"].map({1:"Successful",0:"Unsuccessful"}), hover_data=[c for c in ["LaunchSite","Orbit","FlightNumber","PayloadMass"] if c in filtered.columns], title="Payload mass vs flight number", labels={"color":"Landing result","PayloadMass":"Payload mass (kg)"})
        return pie, scatter
    return app

if __name__ == "__main__":
    app = build_app()
    app.run(debug=False, host="127.0.0.1", port=8050)
