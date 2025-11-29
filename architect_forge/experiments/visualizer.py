"""
Experiment Visualization and Tracking Tools

Tools for visualizing and comparing multiple experiments.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime


class ExperimentVisualizer:
    """Visualize and compare experiment results"""

    def __init__(self, results_dir: str = './experiment_results'):
        self.results_dir = Path(results_dir)
        self.experiments = {}

    def load_experiment(self, experiment_name: str) -> Dict[str, Any]:
        """Load experiment from JSON report"""
        report_file = self.results_dir / f"{experiment_name}_report.json"

        if not report_file.exists():
            raise FileNotFoundError(f"Experiment not found: {experiment_name}")

        with open(report_file, 'r') as f:
            experiment = json.load(f)

        self.experiments[experiment_name] = experiment
        return experiment

    def load_all_experiments(self) -> List[str]:
        """Load all experiments from results directory"""
        if not self.results_dir.exists():
            print(f"Results directory not found: {self.results_dir}")
            return []

        report_files = list(self.results_dir.glob("*_report.json"))

        loaded = []
        for report_file in report_files:
            experiment_name = report_file.stem.replace('_report', '')
            try:
                self.load_experiment(experiment_name)
                loaded.append(experiment_name)
            except Exception as e:
                print(f"Failed to load {experiment_name}: {e}")

        return loaded

    def compare_experiments(
        self,
        experiment_names: List[str] = None,
        metrics: List[str] = None
    ):
        """Compare multiple experiments"""
        if experiment_names is None:
            experiment_names = list(self.experiments.keys())

        if not experiment_names:
            print("No experiments to compare")
            return

        if metrics is None:
            metrics = ['final_quality', 'quality_improvement', 'final_diversity']

        # Extract data
        data = {}
        for metric in metrics:
            data[metric] = []
            for exp_name in experiment_names:
                exp = self.experiments[exp_name]
                value = exp['summary'].get(metric, 0)
                data[metric].append(value)

        # Visualize
        fig, axes = plt.subplots(1, len(metrics), figsize=(6*len(metrics), 5))

        if len(metrics) == 1:
            axes = [axes]

        for ax, metric in zip(axes, metrics):
            values = data[metric]
            colors = plt.cm.viridis(np.linspace(0, 1, len(experiment_names)))

            bars = ax.bar(range(len(experiment_names)), values, color=colors)
            ax.set_xticks(range(len(experiment_names)))
            ax.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.set_title(f'{metric.replace("_", " ").title()} Comparison')
            ax.grid(axis='y', alpha=0.3)

            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.2%}' if metric.endswith('quality') or metric.endswith('diversity') else f'{value:.2f}',
                       ha='center', va='bottom')

        plt.tight_layout()
        plt.show()

    def plot_experiment_timeline(self, experiment_name: str):
        """Plot detailed timeline for single experiment"""
        if experiment_name not in self.experiments:
            self.load_experiment(experiment_name)

        exp = self.experiments[experiment_name]
        cycles = exp.get('cycle_details', [])

        if not cycles:
            print(f"No cycle details found for {experiment_name}")
            return

        # Extract data
        cycle_nums = [c['cycle'] for c in cycles]
        quality = [c['quality'] for c in cycles]
        diversity = [c['diversity'] for c in cycles]
        apprentices = [c['apprentices'] for c in cycles]
        approved = [c['approved'] for c in cycles]
        solutions = [c['solutions'] for c in cycles]

        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f'Experiment Timeline: {experiment_name}', fontsize=16, weight='bold')

        # Quality evolution
        ax1 = axes[0, 0]
        ax1.plot(cycle_nums, quality, 'o-', linewidth=2, markersize=8, color='#00ffff')
        ax1.fill_between(cycle_nums, quality, alpha=0.3, color='#00ffff')
        ax1.set_xlabel('Cycle')
        ax1.set_ylabel('Quality')
        ax1.set_title('Quality Evolution')
        ax1.grid(alpha=0.3)
        ax1.set_ylim(0, 1)

        # Diversity evolution
        ax2 = axes[0, 1]
        ax2.plot(cycle_nums, diversity, 'o-', linewidth=2, markersize=8, color='#ffaa00')
        ax2.fill_between(cycle_nums, diversity, alpha=0.3, color='#ffaa00')
        ax2.set_xlabel('Cycle')
        ax2.set_ylabel('Diversity')
        ax2.set_title('Population Diversity')
        ax2.grid(alpha=0.3)
        ax2.set_ylim(0, 1)

        # Apprentice creation
        ax3 = axes[1, 0]
        ax3.bar(cycle_nums, apprentices, color='#00ff00', alpha=0.7)
        ax3.set_xlabel('Cycle')
        ax3.set_ylabel('Apprentices')
        ax3.set_title('Apprentices Created')
        ax3.grid(axis='y', alpha=0.3)

        # Approval rate
        ax4 = axes[1, 1]
        approval_rate = [a/s if s > 0 else 0 for a, s in zip(approved, solutions)]
        ax4.plot(cycle_nums, approval_rate, 'o-', linewidth=2, markersize=8, color='#ff00ff')
        ax4.fill_between(cycle_nums, approval_rate, alpha=0.3, color='#ff00ff')
        ax4.set_xlabel('Cycle')
        ax4.set_ylabel('Approval Rate')
        ax4.set_title('Solution Approval Rate')
        ax4.grid(alpha=0.3)
        ax4.set_ylim(0, 1)

        plt.tight_layout()
        plt.show()

    def generate_summary_report(self) -> str:
        """Generate text summary of all experiments"""
        if not self.experiments:
            return "No experiments loaded"

        report = []
        report.append("=" * 70)
        report.append("EXPERIMENT SUMMARY REPORT")
        report.append("=" * 70)
        report.append("")

        for exp_name, exp_data in self.experiments.items():
            report.append(f"\n{exp_name}")
            report.append("-" * 70)

            config = exp_data.get('config', {})
            summary = exp_data.get('summary', {})

            report.append(f"  Configuration:")
            report.append(f"    • Population: {config.get('population_size', 'N/A')}")
            report.append(f"    • Cycles: {config.get('num_cycles', 'N/A')}")
            report.append(f"    • Tasks/cycle: {config.get('tasks_per_cycle', 'N/A')}")
            report.append(f"    • Mutation rate: {config.get('mutation_rate', 'N/A')}")

            report.append(f"  Results:")
            report.append(f"    • Final quality: {summary.get('final_quality', 0):.2%}")
            report.append(f"    • Quality improvement: {summary.get('quality_improvement', 0):+.2%}")
            report.append(f"    • Final diversity: {summary.get('final_diversity', 0):.2%}")
            report.append(f"    • Total apprentices: {summary.get('total_apprentices', 0)}")
            report.append(f"    • Best score: {summary.get('best_score', 0):.2%}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def export_comparison_csv(self, output_file: str = 'experiment_comparison.csv'):
        """Export experiment comparison to CSV"""
        if not self.experiments:
            print("No experiments to export")
            return

        import csv

        fieldnames = [
            'experiment_name',
            'population_size',
            'num_cycles',
            'tasks_per_cycle',
            'mutation_rate',
            'final_quality',
            'quality_improvement',
            'final_diversity',
            'total_solutions',
            'total_apprentices',
            'best_score',
        ]

        output_path = self.results_dir / output_file

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for exp_name, exp_data in self.experiments.items():
                config = exp_data.get('config', {})
                summary = exp_data.get('summary', {})

                row = {
                    'experiment_name': exp_name,
                    'population_size': config.get('population_size', ''),
                    'num_cycles': config.get('num_cycles', ''),
                    'tasks_per_cycle': config.get('tasks_per_cycle', ''),
                    'mutation_rate': config.get('mutation_rate', ''),
                    'final_quality': summary.get('final_quality', 0),
                    'quality_improvement': summary.get('quality_improvement', 0),
                    'final_diversity': summary.get('final_diversity', 0),
                    'total_solutions': summary.get('total_solutions', 0),
                    'total_apprentices': summary.get('total_apprentices', 0),
                    'best_score': summary.get('best_score', 0),
                }

                writer.writerow(row)

        print(f"✓ Comparison exported to: {output_path}")


def main():
    """Demonstration of visualizer"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         ARCHITECT FORGE EXPERIMENT VISUALIZER               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    viz = ExperimentVisualizer()

    # Load all experiments
    print("\nLoading experiments...")
    loaded = viz.load_all_experiments()

    if loaded:
        print(f"✓ Loaded {len(loaded)} experiments")
        print("\nExperiments:")
        for exp_name in loaded:
            print(f"  • {exp_name}")

        # Generate summary
        print("\n" + viz.generate_summary_report())

        # Export to CSV
        viz.export_comparison_csv()

        # Compare experiments
        if len(loaded) > 1:
            print("\nGenerating comparison charts...")
            viz.compare_experiments()

        # Plot first experiment timeline
        if loaded:
            print(f"\nGenerating timeline for: {loaded[0]}")
            viz.plot_experiment_timeline(loaded[0])
    else:
        print("No experiments found.")
        print(f"Run experiments using cli_runner.py with --save-results flag")


if __name__ == '__main__':
    main()
