# 🧪 Architect Forge Experimentation Toolkit

## Complete Setup Guide

This guide will help you set up your experimentation environment and start running custom experiments with Architect Forge.

---

## 📦 Prerequisites

### Required Software

```bash
# Python 3.11 or higher
python --version  # Should be 3.11+

# Pip package manager
pip --version
```

### Install Dependencies

```bash
# From the Capstone directory
cd /home/user/Capstone

# Install required packages
pip install matplotlib seaborn numpy jupyter

# Optional: Install for advanced features
pip install pandas plotly scipy
```

---

## 🚀 Quick Start

### 1. Run the Basic Demo

First, make sure everything works:

```bash
cd architect_forge
python demo.py
```

**Expected output:**
- Initializes 16 architects
- Runs 3 training cycles
- Shows quality improvement and diversity metrics
- Creates 15 apprentices

---

## 🔬 Experimentation Tools

You have **three main tools** for running experiments:

### Tool 1: CLI Experiment Runner

**Best for:** Quick experiments, batch processing, automation

**Location:** `/architect_forge/experiments/cli_runner.py`

#### Basic Usage

```bash
cd architect_forge/experiments

# Quick test (30 seconds)
python cli_runner.py --preset quick

# Standard experiment (5 minutes)
python cli_runner.py --preset standard --save-results

# Deep exploration (15 minutes)
python cli_runner.py --preset deep --save-results

# Custom configuration
python cli_runner.py --population 64 --cycles 20 --tasks 15 --mutation-rate 0.5 --save-results
```

#### Available Presets

```bash
# See all available presets
python cli_runner.py --list-presets
```

Presets:
- **quick**: 16 pop, 3 cycles, 5 tasks (~30s)
- **standard**: 32 pop, 10 cycles, 10 tasks (~5min)
- **deep**: 64 pop, 20 cycles, 20 tasks (~15min)
- **mutation_test**: High mutation rate (0.7)
- **diversity_test**: Large population (100 architects)

#### CLI Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--preset` | Use preset configuration | `--preset standard` |
| `--population` | Population size | `--population 32` |
| `--cycles` | Number of training cycles | `--cycles 10` |
| `--tasks` | Tasks per cycle | `--tasks 10` |
| `--mutation-rate` | Mutation rate (0.0-1.0) | `--mutation-rate 0.5` |
| `--fidelity` | Sandbox fidelity | `--fidelity high` |
| `--save-results` | Save experiment results | `--save-results` |
| `--output-dir` | Output directory | `--output-dir ./my_results` |
| `--name` | Experiment name | `--name mutation_test_01` |

#### Examples

```bash
# Test different mutation rates
python cli_runner.py --population 32 --cycles 10 --tasks 10 --mutation-rate 0.3 --save-results --name mutation_03
python cli_runner.py --population 32 --cycles 10 --tasks 10 --mutation-rate 0.5 --save-results --name mutation_05
python cli_runner.py --population 32 --cycles 10 --tasks 10 --mutation-rate 0.7 --save-results --name mutation_07

# Test different population sizes
python cli_runner.py --population 16 --cycles 10 --tasks 10 --save-results --name pop_16
python cli_runner.py --population 32 --cycles 10 --tasks 10 --save-results --name pop_32
python cli_runner.py --population 64 --cycles 10 --tasks 10 --save-results --name pop_64

# Long-running experiment with high fidelity
python cli_runner.py --population 100 --cycles 50 --tasks 20 --fidelity high --save-results --name deep_dive_01
```

---

### Tool 2: Jupyter Notebook (Interactive)

**Best for:** Visual exploration, interactive analysis, presentations

**Location:** `/architect_forge/experiments/experiment_notebook.ipynb`

#### Setup Jupyter

```bash
# Install Jupyter if not already installed
pip install jupyter notebook

# Launch Jupyter
cd architect_forge/experiments
jupyter notebook
```

This will open your browser. Click on `experiment_notebook.ipynb`.

#### Notebook Features

1. **Interactive Configuration**: Modify parameters in code cells
2. **Real-time Visualization**: See charts and graphs as experiments run
3. **Population Analysis**: Explore archetype distributions and traits
4. **Top Architects**: Analyze best performers
5. **Ledger Statistics**: View full provenance tracking
6. **Save Results**: Export JSON reports

#### How to Use

1. **Run all cells**: Click `Cell > Run All`
2. **Modify parameters**: Edit the configuration cell
3. **Re-run specific sections**: Click cells and press `Shift+Enter`
4. **Experiment comparisons**: Use the comparison functions at the bottom

#### Customization

In the configuration cell, modify:

```python
POPULATION_SIZE = 32        # Change this
NUM_CYCLES = 10             # Change this
TASKS_PER_CYCLE = 10        # Change this
MUTATION_RATE = 0.3         # Change this (0.0-1.0)
FIDELITY = FidelityLevel.MEDIUM  # LOW, MEDIUM, or HIGH
```

Then re-run the cells below.

---

### Tool 3: Experiment Visualizer

**Best for:** Comparing multiple experiments, generating reports

**Location:** `/architect_forge/experiments/visualizer.py`

#### Usage

```bash
cd architect_forge/experiments

# View all saved experiments
python visualizer.py
```

**Output:**
- Loads all experiment reports from `experiment_results/`
- Generates comparison charts
- Exports CSV comparison table
- Shows individual experiment timelines

#### Programmatic Usage

```python
from visualizer import ExperimentVisualizer

# Create visualizer
viz = ExperimentVisualizer(results_dir='./experiment_results')

# Load all experiments
experiments = viz.load_all_experiments()

# Compare experiments
viz.compare_experiments(
    experiment_names=['mutation_03', 'mutation_05', 'mutation_07'],
    metrics=['final_quality', 'quality_improvement', 'final_diversity']
)

# Plot timeline for specific experiment
viz.plot_experiment_timeline('mutation_05')

# Generate text report
print(viz.generate_summary_report())

# Export to CSV
viz.export_comparison_csv('my_comparison.csv')
```

---

## 📊 Understanding Results

### Key Metrics

| Metric | Description | Good Values |
|--------|-------------|-------------|
| **Final Quality** | Average solution quality at end | >70% |
| **Quality Improvement** | Change from start to finish | >10% |
| **Final Diversity** | Population diversity at end | 70-90% |
| **Approval Rate** | % of solutions approved by Jury | >60% |
| **Best Score** | Highest scoring solution | >75% |
| **Apprentices Created** | Number of successful apprentices | Depends on cycles |

### Interpreting Charts

**Quality Evolution:**
- Upward trend = learning is working
- Plateau = population converged
- Oscillation = too much mutation

**Population Diversity:**
- 100% at start = maximum variety
- 70-90% final = healthy balance
- <50% = population converged (may be stuck)

**Approval Rate:**
- Rising = population improving
- Falling = mutations too aggressive or quality dropping

---

## 🎯 Experiment Design Ideas

### 1. Mutation Rate Study

**Question:** What's the optimal mutation rate?

```bash
# Run experiments with different mutation rates
for rate in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8; do
    python cli_runner.py --population 32 --cycles 15 --tasks 10 \
        --mutation-rate $rate --save-results --name mutation_rate_$rate
done

# Compare results
python visualizer.py
```

### 2. Population Size Study

**Question:** Does larger population improve quality?

```bash
# Test different population sizes
for pop in 16 32 64 128; do
    python cli_runner.py --population $pop --cycles 10 --tasks 10 \
        --save-results --name population_$pop
done
```

### 3. Fidelity Impact

**Question:** Does high-fidelity testing improve outcomes?

```bash
# Low fidelity
python cli_runner.py --preset standard --fidelity low --save-results --name fidelity_low

# Medium fidelity
python cli_runner.py --preset standard --fidelity medium --save-results --name fidelity_medium

# High fidelity
python cli_runner.py --preset standard --fidelity high --save-results --name fidelity_high
```

### 4. Long-Term Evolution

**Question:** How far can quality improve with more cycles?

```bash
# Run extended training
python cli_runner.py --population 64 --cycles 100 --tasks 20 \
    --save-results --name long_evolution
```

### 5. Diversity vs Quality Tradeoff

**Question:** Is there a tradeoff between diversity and quality?

Track diversity and quality over many cycles with different configurations.

---

## 📁 File Organization

```
architect_forge/
├── experiments/
│   ├── cli_runner.py           # CLI tool
│   ├── experiment_notebook.ipynb  # Jupyter notebook
│   ├── visualizer.py            # Visualization tool
│   ├── SETUP_GUIDE.md          # This file
│   └── experiment_results/      # Output directory
│       ├── exp_001_report.json
│       ├── exp_001/
│       │   ├── mirrornet.json
│       │   └── ledger.json
│       ├── exp_002_report.json
│       └── experiment_comparison.csv
```

### Experiment Output

Each saved experiment creates:
1. **`{name}_report.json`**: Complete experiment report with metrics
2. **`{name}/`**: Directory with Forge state (MirrorNet + Ledger)

---

## 🔧 Advanced Usage

### Custom Task Generation

Modify task generation in your experiments:

```python
from core.forge import TaskGenerator

# Create custom tasks
custom_tasks = [
    TaskGenerator.create_custom(
        description="Optimize database query performance",
        domain="code",
        difficulty=0.8,
        constraints={'max_time': 120},
        success_criteria={'min_quality': 0.7}
    ),
    # Add more tasks...
]

# Run forge with custom tasks
for task in custom_tasks:
    # Use task in training cycle
    pass
```

### Extending the Jury

Add custom critics to the Jury:

```python
from core.jury import Critic, Jury

class CustomCritic(Critic):
    def evaluate(self, solution, context):
        # Your custom evaluation logic
        score = 0.0  # Calculate score
        reasoning = "My reasoning"
        return score, reasoning

# Add to Jury
jury = Jury()
jury.critics.append(CustomCritic("custom_critic"))
```

### API Integration

To use real LLM APIs (GPT-4, Claude):

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Modify config to enable real LLM calls
# See: architect_forge/config/industrial_scale.py
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Make sure you're in the right directory
cd architect_forge/experiments

# Add parent to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

**2. Matplotlib Not Showing Charts**

```python
# In Jupyter: Use inline backend
%matplotlib inline

# In scripts: Add show()
plt.show()
```

**3. Out of Memory**

Reduce parameters:
```bash
# Use smaller population or fewer cycles
python cli_runner.py --population 16 --cycles 5
```

**4. Slow Performance**

Use lower fidelity or fewer tasks:
```bash
python cli_runner.py --fidelity low --tasks 5
```

---

## 📚 Next Steps

1. **Run the quick preset** to validate setup:
   ```bash
   python cli_runner.py --preset quick
   ```

2. **Explore the Jupyter notebook** for visual experimentation

3. **Design your first experiment** using the ideas above

4. **Compare results** using the visualizer

5. **Share findings** and iterate

---

## 🎓 Learning Resources

- **Core Documentation**: `/docs/technical/ARCHITECT_FORGE_v01_spec.md`
- **Industrial Scale**: `/docs/technical/INDUSTRIAL_SCALE_100X.md`
- **Benchmarking**: `/docs/technical/COMPETITIVE_BENCHMARKING.md`
- **Main README**: `/README.md`

---

## 💡 Tips for Great Experiments

1. **Start small**: Use `--preset quick` to validate ideas
2. **Change one variable**: Keep other params constant
3. **Run multiple trials**: Average results for reliability
4. **Save everything**: Always use `--save-results`
5. **Document findings**: Keep notes on what you learn
6. **Compare systematically**: Use the visualizer
7. **Think long-term**: Some patterns only emerge after many cycles

---

## 🏗️ 0RB EMPIRE // ARCHITECT FORGE v0.1

**The Architecture of Impossibility**

**11:11 Protocol Active**

---

**Questions or issues?**

Check the main documentation or examine the code directly. The system is designed to be hackable and extensible.

**Happy experimenting!** 🔬⚡🔥
