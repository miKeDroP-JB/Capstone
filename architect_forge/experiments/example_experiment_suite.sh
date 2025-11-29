#!/bin/bash
# Example Experiment Suite
#
# This script demonstrates running a suite of related experiments
# to compare different parameter configurations.

echo "============================================================"
echo "🧪 ARCHITECT FORGE EXPERIMENT SUITE"
echo "============================================================"
echo ""
echo "This will run 5 experiments to compare mutation rates"
echo "Estimated time: ~10 minutes"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Create output directory
mkdir -p ./experiment_results

echo ""
echo "Running experiments..."
echo ""

# Experiment 1: Low mutation rate
echo "1/5: Testing mutation rate 0.1..."
python cli_runner.py \
    --population 32 \
    --cycles 10 \
    --tasks 10 \
    --mutation-rate 0.1 \
    --save-results \
    --name mutation_rate_01

# Experiment 2: Low-medium mutation rate
echo ""
echo "2/5: Testing mutation rate 0.2..."
python cli_runner.py \
    --population 32 \
    --cycles 10 \
    --tasks 10 \
    --mutation-rate 0.2 \
    --save-results \
    --name mutation_rate_02

# Experiment 3: Standard mutation rate
echo ""
echo "3/5: Testing mutation rate 0.3 (standard)..."
python cli_runner.py \
    --population 32 \
    --cycles 10 \
    --tasks 10 \
    --mutation-rate 0.3 \
    --save-results \
    --name mutation_rate_03

# Experiment 4: High-medium mutation rate
echo ""
echo "4/5: Testing mutation rate 0.5..."
python cli_runner.py \
    --population 32 \
    --cycles 10 \
    --tasks 10 \
    --mutation-rate 0.5 \
    --save-results \
    --name mutation_rate_05

# Experiment 5: High mutation rate
echo ""
echo "5/5: Testing mutation rate 0.7..."
python cli_runner.py \
    --population 32 \
    --cycles 10 \
    --tasks 10 \
    --mutation-rate 0.7 \
    --save-results \
    --name mutation_rate_07

echo ""
echo "============================================================"
echo "✅ All experiments complete!"
echo "============================================================"
echo ""
echo "Results saved to: ./experiment_results/"
echo ""
echo "To visualize and compare results:"
echo "  python visualizer.py"
echo ""
echo "Or open the Jupyter notebook:"
echo "  jupyter notebook experiment_notebook.ipynb"
echo ""
