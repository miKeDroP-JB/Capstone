# 🧪 Architect Forge Experimentation Toolkit

**Tools for running, tracking, and analyzing Architect Forge experiments**

---

## 🎯 What's Included

This directory contains everything you need to run custom experiments with Architect Forge:

| Tool | Purpose | Best For |
|------|---------|----------|
| **`cli_runner.py`** | Command-line experiment runner | Quick tests, automation, batch processing |
| **`experiment_notebook.ipynb`** | Interactive Jupyter notebook | Visual exploration, presentations, learning |
| **`visualizer.py`** | Experiment comparison & visualization | Analyzing multiple experiments, reporting |
| **`SETUP_GUIDE.md`** | Complete setup and usage guide | Getting started, tutorials, troubleshooting |

---

## ⚡ Quick Start

### 1. Run Your First Experiment

```bash
# Quick test (30 seconds)
python cli_runner.py --preset quick

# Standard experiment with saved results (5 minutes)
python cli_runner.py --preset standard --save-results
```

### 2. Visual Experimentation

```bash
# Launch Jupyter notebook
jupyter notebook experiment_notebook.ipynb
```

### 3. Compare Results

```bash
# After running experiments with --save-results
python visualizer.py
```

---

## 📋 Available Presets

| Preset | Population | Cycles | Tasks | Time | Use Case |
|--------|-----------|--------|-------|------|----------|
| **quick** | 16 | 3 | 5 | ~30s | Quick validation |
| **standard** | 32 | 10 | 10 | ~5min | Normal experimentation |
| **deep** | 64 | 20 | 20 | ~15min | Thorough exploration |
| **mutation_test** | 32 | 10 | 10 | ~5min | High mutation rate (0.7) |
| **diversity_test** | 100 | 5 | 5 | ~3min | Large population study |

```bash
# List all presets
python cli_runner.py --list-presets
```

---

## 🔬 Example Experiments

### Test Mutation Rates

```bash
python cli_runner.py --population 32 --cycles 10 --mutation-rate 0.3 --save-results --name mutation_03
python cli_runner.py --population 32 --cycles 10 --mutation-rate 0.5 --save-results --name mutation_05
python cli_runner.py --population 32 --cycles 10 --mutation-rate 0.7 --save-results --name mutation_07

# Compare results
python visualizer.py
```

### Test Population Sizes

```bash
python cli_runner.py --population 16 --cycles 10 --save-results --name pop_16
python cli_runner.py --population 32 --cycles 10 --save-results --name pop_32
python cli_runner.py --population 64 --cycles 10 --save-results --name pop_64
```

### Long-Term Evolution

```bash
python cli_runner.py --population 64 --cycles 100 --tasks 20 --save-results --name evolution_100
```

---

## 📊 CLI Parameters

```bash
python cli_runner.py [OPTIONS]

Options:
  --preset PRESET           Use preset configuration (quick/standard/deep/etc.)
  --population N            Population size (default: 16)
  --cycles N                Number of training cycles (default: 3)
  --tasks N                 Tasks per cycle (default: 5)
  --mutation-rate RATE      Mutation rate 0.0-1.0 (default: 0.3)
  --fidelity LEVEL          Sandbox fidelity: low/medium/high (default: medium)
  --save-results            Save experiment results to JSON
  --output-dir DIR          Output directory (default: ./experiment_results)
  --name NAME               Experiment name (default: exp_TIMESTAMP)
  --list-presets            List available presets
```

---

## 📁 Output Structure

```
experiment_results/
├── my_experiment_report.json      # Experiment metrics and summary
├── my_experiment/                 # Forge state
│   ├── mirrornet.json             # Population state
│   └── ledger.json                # Provenance ledger
└── experiment_comparison.csv      # CSV export of all experiments
```

---

## 📈 Key Metrics

**Quality Metrics:**
- **Final Quality**: Average solution quality at end (target: >70%)
- **Quality Improvement**: Change from start to finish (target: >10%)
- **Best Score**: Highest scoring solution (target: >75%)

**Population Metrics:**
- **Final Diversity**: Population variety (healthy: 70-90%)
- **Approval Rate**: % of solutions approved by Jury (target: >60%)
- **Apprentices Created**: Number of successful apprentices

---

## 🎓 Full Documentation

**Read the complete setup guide for:**
- Detailed installation instructions
- Jupyter notebook walkthrough
- Advanced customization
- Experiment design ideas
- Troubleshooting

👉 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)**

---

## 🔧 Requirements

```bash
# Install dependencies
pip install matplotlib seaborn numpy jupyter

# Optional
pip install pandas plotly scipy
```

---

## 💡 Tips

1. **Start with presets**: Use `--preset quick` to validate ideas
2. **Save your results**: Always use `--save-results` for important experiments
3. **Change one variable**: Keep other parameters constant for clear comparisons
4. **Use the visualizer**: Compare multiple experiments systematically
5. **Document findings**: Keep notes on what you learn

---

## 🏗️ 0RB EMPIRE // ARCHITECT FORGE v0.1

**The Architecture of Impossibility**

**11:11 Protocol Active**

---

**Ready to experiment?**

```bash
python cli_runner.py --preset quick
```

🔬⚡🔥
