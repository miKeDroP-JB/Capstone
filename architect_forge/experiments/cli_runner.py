#!/usr/bin/env python3
"""
CLI Experiment Runner for Architect Forge

Quick tool for running experiments with different configurations.

Usage:
    python cli_runner.py --population 32 --cycles 10 --tasks 10
    python cli_runner.py --preset quick
    python cli_runner.py --preset deep
    python cli_runner.py --mutation-rate 0.5 --save-results
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.forge import ArchitectForge, TaskGenerator
from core.sandbox import FidelityLevel


class ExperimentConfig:
    """Configuration for an experiment"""

    PRESETS = {
        'quick': {
            'population_size': 16,
            'num_cycles': 3,
            'tasks_per_cycle': 5,
            'mutation_rate': 0.3,
            'fidelity': 'medium',
            'description': 'Quick test run (30 seconds)'
        },
        'standard': {
            'population_size': 32,
            'num_cycles': 10,
            'tasks_per_cycle': 10,
            'mutation_rate': 0.3,
            'fidelity': 'medium',
            'description': 'Standard experiment (5 minutes)'
        },
        'deep': {
            'population_size': 64,
            'num_cycles': 20,
            'tasks_per_cycle': 20,
            'mutation_rate': 0.3,
            'fidelity': 'high',
            'description': 'Deep exploration (15 minutes)'
        },
        'mutation_test': {
            'population_size': 32,
            'num_cycles': 10,
            'tasks_per_cycle': 10,
            'mutation_rate': 0.7,
            'fidelity': 'medium',
            'description': 'High mutation rate test'
        },
        'diversity_test': {
            'population_size': 100,
            'num_cycles': 5,
            'tasks_per_cycle': 5,
            'mutation_rate': 0.3,
            'fidelity': 'medium',
            'description': 'Large population diversity test'
        },
    }

    def __init__(self, **kwargs):
        self.population_size = kwargs.get('population_size', 16)
        self.num_cycles = kwargs.get('num_cycles', 3)
        self.tasks_per_cycle = kwargs.get('tasks_per_cycle', 5)
        self.mutation_rate = kwargs.get('mutation_rate', 0.3)
        self.fidelity = kwargs.get('fidelity', 'medium')
        self.save_results = kwargs.get('save_results', False)
        self.output_dir = kwargs.get('output_dir', './experiment_results')
        self.experiment_name = kwargs.get('experiment_name', f'exp_{int(time.time())}')

    @classmethod
    def from_preset(cls, preset_name: str):
        """Create config from preset"""
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}")
        return cls(**cls.PRESETS[preset_name])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'population_size': self.population_size,
            'num_cycles': self.num_cycles,
            'tasks_per_cycle': self.tasks_per_cycle,
            'mutation_rate': self.mutation_rate,
            'fidelity': self.fidelity,
            'save_results': self.save_results,
            'output_dir': self.output_dir,
            'experiment_name': self.experiment_name,
        }


class ExperimentRunner:
    """Run and track experiments"""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.forge = None
        self.results = []
        self.metadata = {
            'start_time': None,
            'end_time': None,
            'duration': None,
        }

    def run(self) -> Dict[str, Any]:
        """Run the experiment"""
        print(f"\n{'='*70}")
        print(f"🔬 EXPERIMENT: {self.config.experiment_name}")
        print(f"{'='*70}\n")

        print("Configuration:")
        for key, value in self.config.to_dict().items():
            if key not in ['save_results', 'output_dir', 'experiment_name']:
                print(f"  • {key}: {value}")
        print()

        # Create Forge
        print(f"🔨 Creating Architect Forge (population={self.config.population_size})...")
        self.forge = ArchitectForge(population_size=self.config.population_size)

        # Initialize
        self.forge.initialize()

        # Get fidelity level
        fidelity_map = {
            'low': FidelityLevel.LOW,
            'medium': FidelityLevel.MEDIUM,
            'high': FidelityLevel.HIGH,
        }
        fidelity = fidelity_map.get(self.config.fidelity, FidelityLevel.MEDIUM)

        # Run training
        self.metadata['start_time'] = time.time()

        self.results = self.forge.run_training(
            num_cycles=self.config.num_cycles,
            tasks_per_cycle=self.config.tasks_per_cycle,
            mutation_rate=self.config.mutation_rate,
        )

        self.metadata['end_time'] = time.time()
        self.metadata['duration'] = self.metadata['end_time'] - self.metadata['start_time']

        # Generate report
        report = self._generate_report()

        # Save if requested
        if self.config.save_results:
            self._save_results(report)

        return report

    def _generate_report(self) -> Dict[str, Any]:
        """Generate experiment report"""
        if not self.results:
            return {'error': 'No results'}

        # Calculate statistics
        total_solutions = sum(r.solutions_generated for r in self.results)
        total_approved = sum(r.solutions_approved for r in self.results)
        total_apprentices = sum(r.apprentices_created for r in self.results)

        avg_quality = sum(r.average_quality for r in self.results) / len(self.results)
        final_quality = self.results[-1].average_quality
        quality_improvement = final_quality - self.results[0].average_quality

        avg_diversity = sum(r.population_diversity for r in self.results) / len(self.results)
        final_diversity = self.results[-1].population_diversity

        best_score = max(r.best_solution_score for r in self.results)

        # Get top architects
        top_architects = self.forge.ledger.get_top_architects(limit=5)

        report = {
            'experiment_name': self.config.experiment_name,
            'config': self.config.to_dict(),
            'metadata': self.metadata,
            'summary': {
                'total_cycles': len(self.results),
                'total_solutions': total_solutions,
                'total_approved': total_approved,
                'approval_rate': total_approved / total_solutions if total_solutions > 0 else 0,
                'total_apprentices': total_apprentices,
                'avg_quality': avg_quality,
                'final_quality': final_quality,
                'quality_improvement': quality_improvement,
                'quality_improvement_pct': quality_improvement / self.results[0].average_quality if self.results[0].average_quality > 0 else 0,
                'avg_diversity': avg_diversity,
                'final_diversity': final_diversity,
                'best_score': best_score,
            },
            'cycle_details': [
                {
                    'cycle': r.cycle_number,
                    'solutions': r.solutions_generated,
                    'approved': r.solutions_approved,
                    'apprentices': r.apprentices_created,
                    'quality': r.average_quality,
                    'diversity': r.population_diversity,
                    'best_score': r.best_solution_score,
                    'duration': r.duration,
                }
                for r in self.results
            ],
            'top_architects': [
                {
                    'id': arch_id,
                    'reputation': rep,
                }
                for arch_id, rep in top_architects
            ],
            'ledger_stats': self.forge.ledger.get_stats(),
        }

        return report

    def _save_results(self, report: Dict[str, Any]):
        """Save experiment results"""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        report_file = output_dir / f"{self.config.experiment_name}_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Save Forge state
        state_dir = output_dir / self.config.experiment_name
        self.forge.save_state(str(state_dir))

        print(f"\n✓ Results saved to {output_dir}/")
        print(f"  • Report: {report_file}")
        print(f"  • State: {state_dir}/")

    def print_summary(self):
        """Print experiment summary"""
        if not self.results:
            print("No results to display")
            return

        report = self._generate_report()
        summary = report['summary']

        print(f"\n{'='*70}")
        print(f"📊 EXPERIMENT SUMMARY: {self.config.experiment_name}")
        print(f"{'='*70}\n")

        print(f"⏱️  Duration: {self.metadata['duration']:.2f}s")
        print(f"\n📈 Results:")
        print(f"  • Total Cycles: {summary['total_cycles']}")
        print(f"  • Solutions Generated: {summary['total_solutions']:,}")
        print(f"  • Solutions Approved: {summary['total_approved']:,} ({summary['approval_rate']:.1%} approval rate)")
        print(f"  • Apprentices Created: {summary['total_apprentices']:,}")
        print(f"\n🎯 Quality:")
        print(f"  • Average Quality: {summary['avg_quality']:.2%}")
        print(f"  • Final Quality: {summary['final_quality']:.2%}")
        print(f"  • Improvement: {summary['quality_improvement']:+.2%} ({summary['quality_improvement_pct']:+.1%})")
        print(f"  • Best Score: {summary['best_score']:.2%}")
        print(f"\n🧬 Population:")
        print(f"  • Average Diversity: {summary['avg_diversity']:.2%}")
        print(f"  • Final Diversity: {summary['final_diversity']:.2%}")

        print(f"\n🏆 Top Architects:")
        for i, arch in enumerate(report['top_architects'][:5], 1):
            print(f"  {i}. {arch['id']} (reputation: {arch['reputation']:.2%})")

        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Architect Forge Experiment Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test run
  python cli_runner.py --preset quick

  # Standard experiment with results saved
  python cli_runner.py --preset standard --save-results

  # Custom configuration
  python cli_runner.py --population 64 --cycles 20 --tasks 15 --mutation-rate 0.5

  # High mutation rate experiment
  python cli_runner.py --preset mutation_test --save-results --name mutation_05

Available presets: """ + ', '.join(ExperimentConfig.PRESETS.keys())
    )

    # Preset or custom config
    parser.add_argument('--preset', type=str, help='Use preset configuration')
    parser.add_argument('--population', type=int, help='Population size')
    parser.add_argument('--cycles', type=int, help='Number of training cycles')
    parser.add_argument('--tasks', type=int, help='Tasks per cycle')
    parser.add_argument('--mutation-rate', type=float, help='Mutation rate (0.0-1.0)')
    parser.add_argument('--fidelity', choices=['low', 'medium', 'high'], help='Sandbox fidelity')

    # Output options
    parser.add_argument('--save-results', action='store_true', help='Save experiment results')
    parser.add_argument('--output-dir', type=str, default='./experiment_results', help='Output directory')
    parser.add_argument('--name', type=str, help='Experiment name')

    # List presets
    parser.add_argument('--list-presets', action='store_true', help='List available presets')

    args = parser.parse_args()

    # List presets if requested
    if args.list_presets:
        print("\n📋 Available Presets:\n")
        for name, config in ExperimentConfig.PRESETS.items():
            print(f"  {name}:")
            print(f"    Description: {config['description']}")
            print(f"    Population: {config['population_size']}")
            print(f"    Cycles: {config['num_cycles']}")
            print(f"    Tasks/cycle: {config['tasks_per_cycle']}")
            print(f"    Mutation rate: {config['mutation_rate']}")
            print(f"    Fidelity: {config['fidelity']}")
            print()
        return

    # Create configuration
    if args.preset:
        config = ExperimentConfig.from_preset(args.preset)
    else:
        config_dict = {}
        if args.population:
            config_dict['population_size'] = args.population
        if args.cycles:
            config_dict['num_cycles'] = args.cycles
        if args.tasks:
            config_dict['tasks_per_cycle'] = args.tasks
        if args.mutation_rate is not None:
            config_dict['mutation_rate'] = args.mutation_rate
        if args.fidelity:
            config_dict['fidelity'] = args.fidelity

        config = ExperimentConfig(**config_dict)

    # Apply overrides
    if args.save_results:
        config.save_results = True
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.name:
        config.experiment_name = args.name

    # Run experiment
    runner = ExperimentRunner(config)
    runner.run()
    runner.print_summary()


if __name__ == '__main__':
    main()
