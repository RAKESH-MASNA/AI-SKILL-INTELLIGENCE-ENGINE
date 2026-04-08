import streamlit as st
import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter
import community as community_louvain
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

st.set_page_config(page_title="AI Skill Intelligence Engine", layout="wide")

st.title("🚀 AI Skill Evolution & Talent Intelligence Dashboard")

# ---------------------------
# Load Dataset
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/ai_job_dataset.csv")
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    df["skill_list"] = df["required_skills"].apply(
        lambda x: [s.strip().lower() for s in str(x).split(",")]
    )
    return df

df = load_data()

# ---------------------------
# Sidebar Navigation
# ---------------------------
menu = st.sidebar.radio(
    "Select Module",
    [
        "Skill Market Insights",
        "Skill Ecosystems",
        "Trend Detection",
        "Career Roadmap Generator"
    ]
)

# ============================================================
# MODULE 1: Skill Market Insights
# ============================================================
if menu == "Skill Market Insights":

    st.header("📊 Top Skill Demand")

    all_skills = [skill for skills in df["skill_list"] for skill in skills]
    skill_counts = Counter(all_skills)

    skill_freq_df = pd.DataFrame(skill_counts.items(),
                                 columns=["skill", "frequency"])
    skill_freq_df = skill_freq_df.sort_values(by="frequency", ascending=False)

    st.dataframe(skill_freq_df.head(20))

    st.bar_chart(skill_freq_df.set_index("skill").head(10))

# ============================================================
# MODULE 2: Skill Ecosystems
# ============================================================
elif menu == "Skill Ecosystems":

    st.header("🌐 Skill Community Detection")

    # Build graph
    G = nx.Graph()

    for skills in df["skill_list"]:
        for pair in combinations(skills, 2):
            G.add_edge(pair[0], pair[1])

    partition = community_louvain.best_partition(G)

    community_df = pd.DataFrame(
        partition.items(),
        columns=["skill", "community"]
    )

    st.write("Total Communities:", community_df["community"].nunique())
    st.dataframe(community_df)

# ============================================================
# MODULE 3: Trend Detection
# ============================================================
elif menu == "Trend Detection":

    st.header("📈 Skill Trend Analysis")

    df["year_month"] = df["posting_date"].dt.to_period("M")
    df_exploded = df.explode("skill_list")

    monthly_counts = (
        df_exploded
        .groupby(["year_month", "skill_list"])
        .size()
        .reset_index(name="count")
    )

    skill_selected = st.selectbox(
        "Select Skill",
        df_exploded["skill_list"].unique()
    )

    skill_trend = monthly_counts[
        monthly_counts["skill_list"] == skill_selected
    ]

    st.line_chart(
        skill_trend.set_index("year_month")["count"]
    )

# ============================================================
# MODULE 4: Career Roadmap Generator
# ============================================================
elif menu == "Career Roadmap Generator":

    st.header("🛣 Career Roadmap Generator")

    roles = df["job_title"].unique()
    target_role = st.selectbox("Select Target Role", roles)

    user_input = st.text_input(
        "Enter your current skills (comma separated)"
    )

    if st.button("Generate Roadmap"):

        user_skills = set(
            [s.strip().lower() for s in user_input.split(",")]
        )

        df_exploded = df.explode("skill_list")

        role_skills = (
            df_exploded[df_exploded["job_title"] == target_role]
            ["skill_list"]
            .value_counts()
            .head(10)
            .index
        )

        role_skills = set(role_skills)

        skill_gap = role_skills - user_skills

        st.subheader("🎯 Target Role Skills")
        st.write(role_skills)

        st.subheader("📉 Skill Gap")
        st.write(skill_gap)

        st.success("Recommended Learning Order:")
        for skill in skill_gap:
            st.write("•", skill)
