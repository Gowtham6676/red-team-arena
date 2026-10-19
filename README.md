# AI Red Team Arena

Four local LLM agents attack and harden a chatbot automatically, with no API keys and no cloud.

An **Attacker** tries to trick a chatbot into leaking a fake secret. A **Judge** scores each attempt. A **Defender** rewrites the chatbot's safety rules after every round. Success is measured on a **held-out set of attacks the Defender never sees**, so the improvement reflects generalisation and not memorisation.

Everything runs locally with [Ollama](https://ollama.com). The target is a toy chatbot I built, and the "secret" is a fake string used only for testing.

![Dashboard demo](demo.gif)

## How it works

```
   ┌──────────┐  attack message   ┌────────────┐  reply   ┌───────┐
   │ Attacker │ ────────────────► │ Target bot │ ───────► │ Judge │
   └──────────┘                   │ (has fake  │          └───┬───┘
        ▲                         │  secret)   │              │ leaked?
        │ strategies tried        └────────────┘              │
        │                               ▲                     ▼
        └───────────────────────────────┼──────────── ┌───────────────┐
                                        └─ new rules ─┤   Defender    │
                                                      └───────────────┘
```

Each run has several rounds:

1. The Attacker invents new strategies, avoiding ones already tried.
2. The Target bot replies under its current rules.
3. The Judge checks for leaks: a rule-based check (exact, spaced-out and reversed secrets) first, then an LLM check for partial leaks.
4. The Defender sees the successful attacks and rewrites the rules.
5. After all rounds, a **fixed set of 10 held-out attacks** (each repeated 3 times) measures the final leak rate.

The same held-out test is also run **before** any hardening, giving a baseline.

## Results

Held-out leak rate (30 trials per measurement; each model plays all four roles):

| Model | Before hardening | After hardening |
|---|---|---|
| llama3.2:3b | 77% | 20% |
| llama3.1:8b | 100% | 23% |
| qwen2.5:7b | 90% | 30% |

![Attack success per round](results.png)

**Observations**

- Attack success on the Attacker's own new strategies fell to 0% within 2-3 rounds for each model.
- Leak rates on the held-out attacks also dropped sharply, which shows the Defender's rules generalised to attacks it never saw.
- Some leaks remain after hardening (20-30%), so the rewritten rules are not a complete defence.
- The rules the Defender writes are often very broad (for example "refuse to discuss internal workings"). That blocks leaks, but it would also make a real support bot less helpful. Measuring that trade-off is future work.

## Tech stack

- Python 3.11+
- [Ollama](https://ollama.com) for local model inference (`ollama` Python library)
- Streamlit for the results dashboard
- Matplotlib and pandas for plots and results

## Getting started

**Prerequisites:** Python 3.11+, [Ollama](https://ollama.com) installed and running, and enough RAM for the model you choose (about 8 GB for 3B models, 16 GB for 7-8B models).

```bash
git clone https://github.com/<Gowtham6676>/red-team-arena.git
cd red-team-arena

python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

ollama pull llama3.2:3b
```

Run an experiment:

```bash
python main.py --model llama3.2:3b --rounds 5 --attacks 8
```

Options:

| Flag | Default | Meaning |
|---|---|---|
| `--model` | `llama3.2:3b` | Any model shown by `ollama list` |
| `--rounds` | 5 | Attack/defend rounds |
| `--attacks` | 8 | Attacks per round |

Each run writes to `logs/`:

- `<model>_results.csv`: attack success per round
- `<model>_attacks.json`: full attack log (attack, reply, verdict, rules in force)
- `<model>_summary.json`: baseline and final held-out leak rates, and the final rules

View the results:

```bash
python plot.py                   # saves results.png comparing all runs
streamlit run app.py             # interactive dashboard
```

## Project structure

```
red-team-arena/
├── llm.py          # the only file that talks to Ollama
├── agents.py       # Attacker, Target bot, Judge, Defender
├── heldout.py      # 10 fixed test attacks the Defender never sees
├── main.py         # orchestrator: rounds, metrics, logging
├── plot.py         # comparison chart across models
├── app.py          # Streamlit dashboard
├── logs/           # experiment outputs
└── requirements.txt
```

## Limitations

- **Small sample.** Each measurement is 30 trials, so a few extra leaks change the percentage noticeably. Results vary between runs, and each model was run once.
- **One model plays every role.** Attacker, Target, Judge and Defender all use the same model in a given run, so results mix attack skill and defence skill.
- **One fake secret.** Results may not transfer to other secrets or to real systems.
- **Imperfect judge.** The Judge combines exact-match rules with a small LLM, and the LLM part can miss subtle partial leaks.
- **Helpfulness is not measured.** The hardened rules were not tested for whether the bot still answers normal questions.

## Future work

- Use separate models for the Attacker and the Target to isolate which models are hardest to attack.
- Add a helpfulness test so over-restrictive rules are penalised.
- Run several repetitions per model and report averages with spread.
- Add more secret types and a larger, more varied held-out attack set.

## Responsible use

This project tests a chatbot I built, using a fake secret, in a local sandbox. It is intended for learning about prompt-injection robustness. Do not use it to attack systems you do not own or have permission to test.

## License

MIT
