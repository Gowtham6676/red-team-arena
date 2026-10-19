import csv, glob
import matplotlib.pyplot as plt

for path in glob.glob("logs/*_results.csv"):
    rows = list(csv.DictReader(open(path)))
    name = path.split("\\")[-1].split("/")[-1].replace("_results.csv", "")
    plt.plot([int(r["round"]) for r in rows],
             [float(r["success_rate"]) * 100 for r in rows], marker="o", label=name)

plt.xlabel("Round"); plt.ylabel("Attack success rate (%)")
plt.title("Attack success over defender rounds"); plt.legend(); plt.grid(alpha=0.3)
plt.savefig("results.png", dpi=150, bbox_inches="tight")
print("Saved results.png")