#!/usr/bin/env python3
"""
MULTI-SOURCE HARVESTER
Pull from: Local Git, Google Cloud, Base44, wherever your code lives
Consolidate ALL iterations into the machine's memory
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

class MultiSourceHarvester:
    def __init__(self):
        self.all_patterns = {
            "sources": [],
            "total_stats": {"files": 0, "lines": 0, "repos": 0},
            "tech_stack": set(),
            "verticals": set(),
            "apps_detected": [],
            "revenue_potential": []
        }
    
    def harvest_local(self, paths):
        """Harvest local directories"""
        print("\n📁 HARVESTING LOCAL REPOS...")
        for path in paths:
            if os.path.exists(path):
                stats = self._scan_directory(path)
                self.all_patterns["sources"].append({
                    "type": "local",
                    "path": path,
                    "stats": stats
                })
                print(f"   ✓ {path}: {stats['files']} files, {stats['lines']:,} lines")
    
    def harvest_google_cloud(self):
        """Pull repos/buckets from Google Cloud"""
        print("\n☁️ HARVESTING GOOGLE CLOUD...")
        print("   Checking for gcloud CLI...")
        
        try:
            # Check if gcloud is installed
            result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✓ gcloud CLI found")
                
                # List projects
                print("\n   Your GCP Projects:")
                projects = subprocess.run(
                    ['gcloud', 'projects', 'list', '--format=json'],
                    capture_output=True, text=True
                )
                if projects.returncode == 0:
                    proj_list = json.loads(projects.stdout)
                    for i, proj in enumerate(proj_list[:10], 1):
                        print(f"      {i}. {proj.get('projectId', 'unknown')}")
                    
                    # List Cloud Run services
                    print("\n   Cloud Run Services:")
                    services = subprocess.run(
                        ['gcloud', 'run', 'services', 'list', '--format=json'],
                        capture_output=True, text=True
                    )
                    if services.returncode == 0 and services.stdout.strip():
                        svc_list = json.loads(services.stdout)
                        for svc in svc_list:
                            svc_name = svc.get('metadata', {}).get('name', 'unknown')
                            print(f"      • {svc_name}")
                            self.all_patterns["apps_detected"].append({
                                "source": "gcp_cloud_run",
                                "name": svc_name,
                                "url": svc.get('status', {}).get('url', '')
                            })
                    
                    # List Cloud Storage buckets
                    print("\n   Cloud Storage Buckets:")
                    buckets = subprocess.run(
                        ['gsutil', 'ls'],
                        capture_output=True, text=True
                    )
                    if buckets.returncode == 0:
                        for bucket in buckets.stdout.strip().split('\n')[:10]:
                            if bucket:
                                print(f"      • {bucket}")
                                self.all_patterns["sources"].append({
                                    "type": "gcs_bucket",
                                    "path": bucket
                                })
                else:
                    print("   ⚠️ No projects found or not authenticated")
                    print("   Run: gcloud auth login")
            else:
                print("   ⚠️ gcloud CLI not found")
        except FileNotFoundError:
            print("   ⚠️ gcloud CLI not installed")
            print("   Install from: https://cloud.google.com/sdk/docs/install")
        
        self._manual_gcp_input()
    
    def _manual_gcp_input(self):
        """Manual input for GCP resources"""
        print("\n   📝 Manual GCP Entry:")
        print("   List your GCP resources (project IDs, bucket names, service URLs)")
        print("   One per line, empty to finish:")
        
        while True:
            resource = input("   GCP Resource: ").strip()
            if not resource:
                break
            self.all_patterns["sources"].append({
                "type": "gcp_manual",
                "resource": resource
            })
            print(f"      ✓ Added: {resource}")
    
    def harvest_base44(self):
        """Pull from Base44 projects"""
        print("\n🔧 HARVESTING BASE44...")
        print("   Base44 apps to consolidate:")
        print("   Enter project names/URLs (empty to finish):")
        
        while True:
            project = input("   Base44 Project: ").strip()
            if not project:
                break
            self.all_patterns["sources"].append({
                "type": "base44",
                "project": project
            })
            self.all_patterns["apps_detected"].append({
                "source": "base44",
                "name": project,
                "type": "no-code app"
            })
            print(f"      ✓ Added: {project}")
    
    def harvest_other_sources(self):
        """Catch-all for other platforms"""
        print("\n🌐 OTHER SOURCES...")
        platforms = [
            "Vercel deployments",
            "Netlify sites", 
            "Heroku apps",
            "Railway projects",
            "Replit projects",
            "GitHub repos (private)",
            "GitLab repos",
            "Firebase projects",
            "Supabase projects",
            "Other (specify)"
        ]
        
        print("   Other platforms with your code:")
        for i, p in enumerate(platforms, 1):
            print(f"      {i}. {p}")
        
        print("\n   Enter platform number and resource (e.g., '1 my-app.vercel.app')")
        print("   Empty to finish:")
        
        while True:
            entry = input("   Platform Resource: ").strip()
            if not entry:
                break
            parts = entry.split(' ', 1)
            if len(parts) >= 1:
                self.all_patterns["sources"].append({
                    "type": "other",
                    "entry": entry
                })
                print(f"      ✓ Added: {entry}")
    
    def _scan_directory(self, path):
        """Scan a local directory for code stats"""
        stats = {"files": 0, "lines": 0, "languages": {}}
        
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.next', 'dist', 'build']]
                
                for file in files:
                    ext = Path(file).suffix.lower()
                    code_exts = ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.sql', '.html', '.css']
                    
                    if ext in code_exts:
                        stats["files"] += 1
                        stats["languages"][ext] = stats["languages"].get(ext, 0) + 1
                        
                        try:
                            filepath = Path(root) / file
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                stats["lines"] += len(f.readlines())
                        except:
                            pass
        except Exception as e:
            print(f"      ⚠️ Error scanning {path}: {e}")
        
        self.all_patterns["total_stats"]["files"] += stats["files"]
        self.all_patterns["total_stats"]["lines"] += stats["lines"]
        self.all_patterns["total_stats"]["repos"] += 1
        
        return stats
    
    def estimate_portfolio_value(self):
        """Estimate total value of all code"""
        total_lines = self.all_patterns["total_stats"]["lines"]
        num_apps = len(self.all_patterns["apps_detected"])
        num_sources = len(self.all_patterns["sources"])
        
        # Conservative estimates
        code_value_low = total_lines * 50
        code_value_high = total_lines * 150
        
        # App value (each deployable app has value)
        app_value = num_apps * 10000  # $10K per deployable app
        
        # Platform diversity bonus
        platform_bonus = num_sources * 5000
        
        return {
            "code_value": {"low": code_value_low, "high": code_value_high},
            "app_portfolio_value": app_value,
            "platform_value": platform_bonus,
            "total_low": code_value_low + app_value + platform_bonus,
            "total_high": code_value_high + app_value + platform_bonus
        }
    
    def generate_machine_memory(self):
        """Convert harvested data into machine-readable patterns"""
        memory = {
            "harvested_at": datetime.now().isoformat(),
            "sources": self.all_patterns["sources"],
            "apps": self.all_patterns["apps_detected"],
            "stats": self.all_patterns["total_stats"],
            "portfolio_value": self.estimate_portfolio_value(),
            "ready_to_deploy": [],
            "needs_work": [],
            "high_value_patterns": []
        }
        
        # Identify deployment-ready apps
        for app in self.all_patterns["apps_detected"]:
            if app.get("url") or app["source"] in ["gcp_cloud_run", "base44"]:
                memory["ready_to_deploy"].append(app)
            else:
                memory["needs_work"].append(app)
        
        with open("machine_memory.json", "w") as f:
            json.dump(memory, f, indent=2, default=str)
        
        return memory

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              MULTI-SOURCE HARVESTER                           ║
║                                                               ║
║   Consolidate ALL your iterations:                            ║
║   • Local Git repos                                           ║
║   • Google Cloud (Cloud Run, GCS, etc)                        ║
║   • Base44 apps                                               ║
║   • Any other platforms                                       ║
║                                                               ║
║   Feed everything into the machine's memory                   ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    harvester = MultiSourceHarvester()
    
    # 1. Local repos
    print("="*60)
    print("STEP 1: LOCAL REPOSITORIES")
    print("="*60)
    print("Enter local paths to harvest (empty to skip):")
    print("Example: C:\\Users\\JB\\Projects\\my-app")
    
    local_paths = []
    while True:
        path = input("Local Path: ").strip()
        if not path:
            break
        local_paths.append(path)
    
    if local_paths:
        harvester.harvest_local(local_paths)
    
    # 2. Google Cloud
    print("\n" + "="*60)
    print("STEP 2: GOOGLE CLOUD")
    print("="*60)
    harvester.harvest_google_cloud()
    
    # 3. Base44
    print("\n" + "="*60)
    print("STEP 3: BASE44")
    print("="*60)
    harvester.harvest_base44()
    
    # 4. Other sources
    print("\n" + "="*60)
    print("STEP 4: OTHER PLATFORMS")
    print("="*60)
    harvester.harvest_other_sources()
    
    # Generate machine memory
    print("\n" + "="*60)
    print("GENERATING MACHINE MEMORY")
    print("="*60)
    memory = harvester.generate_machine_memory()
    
    # Final report
    value = memory["portfolio_value"]
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    HARVEST COMPLETE                           ║
╚═══════════════════════════════════════════════════════════════╝

  📊 TOTAL CONSOLIDATED:
     Sources: {len(memory['sources'])}
     Apps Detected: {len(memory['apps'])}
     Total Files: {memory['stats']['files']:,}
     Total Lines: {memory['stats']['lines']:,}
  
  🚀 DEPLOYMENT STATUS:
     Ready to Deploy: {len(memory['ready_to_deploy'])}
     Needs Work: {len(memory['needs_work'])}
  
  💰 PORTFOLIO VALUATION:
     Code Value: ${value['code_value']['low']:,.0f} - ${value['code_value']['high']:,.0f}
     App Portfolio: ${value['app_portfolio_value']:,.0f}
     Platform Value: ${value['platform_value']:,.0f}
     ─────────────────────────────
     TOTAL: ${value['total_low']:,.0f} - ${value['total_high']:,.0f}
  
  ✅ Machine memory saved to: machine_memory.json
  
  NEXT STEPS:
  1. Review machine_memory.json
  2. Pick highest-value apps to deploy first
  3. Feed patterns into ekosystem builder
  4. Let the machine compound your existing work
  
  DON'T DELETE ANYTHING - IT'S ALL TRAINING DATA NOW
""")

if __name__ == "__main__":
    main()
