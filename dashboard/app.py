
import os

import pandas as pd
import plotly.express as px
import psycopg
import streamlit as st

st.set_page_config(
    page_title="Engineering the Beautiful Game",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Engineering the Beautiful Game")
st.caption(
    "2015–2016 English Premier League | StatsBomb Open Data"
)

@st.cache_data(ttl=300)
def load_data():
    with psycopg.connect(
        dbname="engineering_the_beautiful_game",
        user="postgres",
        password=os.environ["PGPASSWORD"],
        host="localhost",
        port=5432
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.match_id,
                    t.team_id,
                    CASE
                        WHEN t.team_id = m.home_team_id
                        THEN m.home_team
                        ELSE m.away_team
                    END AS team_name,
                    t.result,
                    t.total_passes,
                    t.completed_passes,
                    t.pass_completion_rate,
                    t.progressive_passes,
                    t.progressive_carries,
                    t.final_third_entries,
                    t.total_shots,
                    t.total_xg,
                    t.shot_producing_possessions
                FROM team_match_stats t
                JOIN matches m
                    ON t.match_id = m.match_id
            """)

            rows = cursor.fetchall()
            columns = [
                col.name for col in cursor.description
            ]

    return pd.DataFrame(rows, columns=columns)


try:
    df = load_data()
except Exception as error:
    st.error(f"Database connection failed: {error}")
    st.stop()

st.sidebar.header("Filters")

teams = sorted(df["team_name"].unique())

selected_teams = st.sidebar.multiselect(
    "Select teams",
    options=teams,
    default=teams
)

selected_results = st.sidebar.multiselect(
    "Match results",
    options=["Win", "Draw", "Loss"],
    default=["Win", "Draw", "Loss"]
)

filtered = df[
    df["team_name"].isin(selected_teams)
    & df["result"].isin(selected_results)
].copy()

if filtered.empty:
    st.warning("No data matches your filters.")
    st.stop()

st.subheader("Performance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Team-Matches", f"{len(filtered):,}")
col2.metric(
    "Avg Pass Completion",
    f"{filtered['pass_completion_rate'].mean():.2f}%"
)
col3.metric(
    "Avg Shots",
    f"{filtered['total_shots'].mean():.2f}"
)
col4.metric(
    "Avg xG",
    f"{filtered['total_xg'].mean():.2f}"
)

st.divider()

st.subheader("Performance by Match Result")

metrics = {
    "Pass Completion (%)": "pass_completion_rate",
    "Progressive Passes": "progressive_passes",
    "Progressive Carries": "progressive_carries",
    "Final-Third Entries": "final_third_entries",
    "Shots": "total_shots",
    "Expected Goals (xG)": "total_xg",
    "Shot-Producing Possessions": "shot_producing_possessions"
}

selected_metric = st.selectbox(
    "Choose a performance metric",
    options=list(metrics.keys())
)

metric_column = metrics[selected_metric]

summary = (
    filtered.groupby("result", as_index=False)[metric_column]
    .mean()
)

fig = px.bar(
    summary,
    x="result",
    y=metric_column,
    color="result",
    category_orders={
        "result": ["Win", "Draw", "Loss"]
    },
    labels={
        "result": "Match Result",
        metric_column: selected_metric
    },
    title=f"Average {selected_metric} by Match Result"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Passing and Attacking Efficiency")

fig2 = px.scatter(
    filtered,
    x="pass_completion_rate",
    y="total_xg",
    color="result",
    hover_name="team_name",
    hover_data=["total_shots", "progressive_passes"],
    labels={
        "pass_completion_rate": "Pass Completion (%)",
        "total_xg": "Expected Goals (xG)"
    },
    title="Pass Completion vs. Expected Goals"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Team-Match Data")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)
