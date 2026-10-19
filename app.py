import glob, json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("AI Red Team Arena")
runs = sorted(glob.glob("logs/*_summary.json"))
if not runs:
    st.warning("No runs found. Run main.py first.")
    st.stop()

choice = st.selectbox("Run", runs)
tag = choice.replace("logs/", "").replace("logs\\", "").replace("_summary.json", "")
summary = json.load(open(choice))

c1, c2 = st.columns(2)
c1.metric("Held-out leak rate (before)", f"{summary['baseline_heldout']:.0%}")
c2.metric("Held-out leak rate (after)", f"{summary['final_heldout']:.0%}")

st.subheader("Attack success per round")
df = pd.read_csv(f"logs/{tag}_results.csv")
fig, ax = plt.subplots()
ax.plot(df["round"], df["success_rate"] * 100, marker="o")
ax.set_xlabel("Round")
ax.set_ylabel("Attack success (%)")
ax.set_ylim(0, 100)
ax.set_xticks(df["round"])
ax.grid(alpha=0.3)
st.pyplot(fig)

st.subheader("Final hardened rules")
st.write(summary["final_rules"])

st.subheader("Attack log")
for e in json.load(open(f"logs/{tag}_attacks.json")):
    icon = "🔴" if e["verdict"]["leaked"] else "🟢"
    with st.expander(f"{icon} Round {e['round']}: {e['attack']['strategy']}"):
        st.write("**Attack:**", e["attack"]["message"])
        st.write("**Reply:**", e["reply"])