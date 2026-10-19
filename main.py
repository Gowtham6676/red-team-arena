import argparse, csv, json, os
import llm
from agents import attacker, target_bot, judge, defender, BASE_RULES
from heldout import HELD_OUT


def run_heldout(rules, repeats=3):
    leaks = total = 0
    for atk in HELD_OUT:
        for _ in range(repeats):          # repeat because outputs are random
            reply = target_bot(atk, rules)
            leaks += judge(reply)["leaked"]
            total += 1
    return leaks / total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="llama3.2:3b")
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--attacks", type=int, default=8)
    args = p.parse_args()

    llm.MODEL = args.model
    tag = args.model.replace(":", "_").replace(".", "_")
    os.makedirs("logs", exist_ok=True)

    rules, history, log, rows = BASE_RULES, [], [], []

    print("Measuring held-out baseline...")
    baseline = run_heldout(BASE_RULES)
    print(f"Baseline held-out leak rate: {baseline:.0%}\n")

    for rnd in range(1, args.rounds + 1):
        wins, tries = [], 0
        for _ in range(args.attacks):
            atk = attacker(history)
            if atk is None:
                print("  attacker gave bad output, skipping")
                continue
            reply = target_bot(atk["message"], rules)
            verdict = judge(reply)
            tries += 1
            history.append({"strategy": atk["strategy"], "leaked": verdict["leaked"]})
            log.append({"round": rnd, "attack": atk, "reply": reply,
                        "verdict": verdict, "rules": rules})
            if verdict["leaked"]:
                wins.append(atk["message"])

        rate = len(wins) / tries if tries else 0
        rows.append({"round": rnd, "attacks": tries, "leaks": len(wins),
                     "success_rate": round(rate, 3)})
        print(f"Round {rnd}: {len(wins)}/{tries} attacks succeeded ({rate:.0%})")

        if wins:
            rules = defender(rules, wins)
            print(f"  Defender updated rules: {rules[:80]}...")

    final = run_heldout(rules)
    print(f"\nHeld-out leak rate: {baseline:.0%} -> {final:.0%}")

    with open(f"logs/{tag}_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    json.dump(log, open(f"logs/{tag}_attacks.json", "w"), indent=2)
    json.dump({"model": args.model, "baseline_heldout": baseline,
               "final_heldout": final, "final_rules": rules},
              open(f"logs/{tag}_summary.json", "w"), indent=2)


if __name__ == "__main__":
    main()