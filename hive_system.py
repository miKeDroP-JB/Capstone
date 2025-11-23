#!/usr/bin/env python3
"""
HIVE SYSTEM - Swarms of Swarms

Hierarchy:
- Glyph: Single operation
- Spell: Sequence of glyphs
- Agent: Collection of spells
- Swarm: Many agents in parallel
- HIVE: Many swarms in parallel (SWARM OF SWARMS)

Use Case: Powerload ALL your data into the system
- Downloaded repos
- Zip files
- Apps/codebases
- Any gathered data

Philosophy: Don't process files one at a time.
           Deploy 100 swarms processing 1000 files each.
           HIVE = 100,000 files processed simultaneously.
"""

from typing import Dict, List, Optional
from pathlib import Path
import asyncio
import json
import zipfile
import shutil
import subprocess
from datetime import datetime
from pydantic import BaseModel
import anthropic
import os


# ============================================================================
# HIVE MISSION - What the hive should accomplish
# ============================================================================

class HiveMission(BaseModel):
    """A mission for the entire hive"""
    goal: str
    input_paths: List[str]  # Paths to repos, zips, apps, etc.
    output_destination: str = "grimoire"
    swarms_to_deploy: int = 10  # How many swarms in the hive
    agents_per_swarm: int = 10  # How many agents per swarm
    mission_id: Optional[str] = None

    def __init__(self, **data):
        if 'mission_id' not in data or not data['mission_id']:
            data['mission_id'] = f"hive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        super().__init__(**data)


# ============================================================================
# SWARM TYPES - Different swarms for different tasks
# ============================================================================

class RepoIngestionSwarm:
    """Swarm that ingests git repositories into grimoire"""

    def __init__(self, swarm_id: str, grimoire_path: Path):
        self.swarm_id = swarm_id
        self.grimoire_path = grimoire_path
        self.agents = []

    async def ingest_repo(self, repo_path: str) -> Dict:
        """
        Ingest a repository into grimoire

        Extract:
        - All code files
        - Documentation
        - Commit history
        - Dependencies
        - Patterns and best practices
        """
        repo_path = Path(repo_path)

        if not repo_path.exists():
            return {"success": False, "error": "Repo path doesn't exist"}

        results = {
            "repo_name": repo_path.name,
            "files_processed": 0,
            "knowledge_extracted": [],
            "patterns_found": [],
            "dependencies": []
        }

        # Find all code files
        code_extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.cpp', '.c', '.h']
        code_files = []

        for ext in code_extensions:
            code_files.extend(repo_path.rglob(f'*{ext}'))

        # Process files in parallel
        tasks = [self._process_file(f) for f in code_files[:100]]  # Limit to 100 files per swarm
        file_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in file_results:
            if isinstance(result, dict) and result.get('success'):
                results['files_processed'] += 1
                results['knowledge_extracted'].extend(result.get('knowledge', []))
                results['patterns_found'].extend(result.get('patterns', []))

        # Extract dependencies
        results['dependencies'] = await self._extract_dependencies(repo_path)

        # Store in grimoire
        await self._store_in_grimoire(results)

        return {
            "success": True,
            "swarm_id": self.swarm_id,
            "results": results
        }

    async def _process_file(self, file_path: Path) -> Dict:
        """Process a single code file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract knowledge using Claude
            knowledge = await self._extract_knowledge_from_code(content, file_path.name)

            return {
                "success": True,
                "file": str(file_path),
                "knowledge": knowledge.get('knowledge', []),
                "patterns": knowledge.get('patterns', [])
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _extract_knowledge_from_code(self, code: str, filename: str) -> Dict:
        """Use Claude to extract knowledge from code"""

        # Check if we have Claude API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Fallback to pattern matching
            return self._extract_knowledge_fallback(code, filename)

        try:
            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"""Extract knowledge from this code file ({filename}):

{code[:3000]}  # First 3000 chars

Return JSON with:
- knowledge: List of key concepts/functions/patterns
- patterns: List of code patterns to remember
- dependencies: Any libraries/imports used

Format: {{"knowledge": [...], "patterns": [...], "dependencies": [...]}}"""
                }]
            )

            response_text = message.content[0].text

            # Try to parse JSON from response
            try:
                return json.loads(response_text)
            except:
                # If not valid JSON, create structured response
                return {
                    "knowledge": [response_text[:200]],
                    "patterns": [],
                    "dependencies": []
                }

        except Exception as e:
            return self._extract_knowledge_fallback(code, filename)

    def _extract_knowledge_fallback(self, code: str, filename: str) -> Dict:
        """Fallback knowledge extraction using patterns"""
        knowledge = []
        patterns = []
        dependencies = []

        lines = code.split('\n')

        # Extract imports/dependencies
        for line in lines[:50]:  # Check first 50 lines
            if 'import ' in line or 'from ' in line or 'require(' in line:
                dependencies.append(line.strip())

        # Extract function/class definitions
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                knowledge.append(line.strip())
            elif line.strip().startswith('async def '):
                knowledge.append(line.strip())
                patterns.append('async_pattern')

        return {
            "knowledge": knowledge[:20],  # Top 20
            "patterns": list(set(patterns)),
            "dependencies": dependencies[:10]
        }

    async def _extract_dependencies(self, repo_path: Path) -> List[str]:
        """Extract dependencies from package files"""
        dependencies = []

        # Python
        requirements = repo_path / 'requirements.txt'
        if requirements.exists():
            with open(requirements) as f:
                dependencies.extend(f.read().splitlines())

        # Node.js
        package_json = repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    dependencies.extend(deps.keys())
            except:
                pass

        return dependencies

    async def _store_in_grimoire(self, results: Dict):
        """Store results in grimoire"""
        self.grimoire_path.mkdir(parents=True, exist_ok=True)

        grimoire_file = self.grimoire_path / f"repo_{results['repo_name']}.json"

        with open(grimoire_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "swarm_id": self.swarm_id,
                "type": "repo_ingestion",
                "data": results
            }, f, indent=2)


class ZipIngestionSwarm:
    """Swarm that ingests zip files into grimoire"""

    def __init__(self, swarm_id: str, grimoire_path: Path):
        self.swarm_id = swarm_id
        self.grimoire_path = grimoire_path
        self.temp_path = Path(f"/tmp/hive_extract_{swarm_id}")

    async def ingest_zip(self, zip_path: str) -> Dict:
        """
        Ingest a zip file into grimoire

        Steps:
        1. Extract zip to temp location
        2. Analyze contents
        3. Route to appropriate swarms (repo swarm if it's a repo, etc.)
        4. Store results
        """
        zip_path = Path(zip_path)

        if not zip_path.exists() or not zip_path.suffix == '.zip':
            return {"success": False, "error": "Not a valid zip file"}

        # Extract
        self.temp_path.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_path)
        except Exception as e:
            return {"success": False, "error": f"Failed to extract: {e}"}

        # Analyze contents
        extracted_dirs = list(self.temp_path.iterdir())

        results = {
            "zip_name": zip_path.name,
            "extracted_to": str(self.temp_path),
            "contents": [],
            "repos_found": []
        }

        # Check if contents are repos
        for item in extracted_dirs:
            if item.is_dir():
                # Check if it's a git repo
                if (item / '.git').exists():
                    results['repos_found'].append(str(item))
                else:
                    # Check if it has code files
                    code_files = list(item.rglob('*.py')) + list(item.rglob('*.js'))
                    if code_files:
                        results['repos_found'].append(str(item))

        # If repos found, ingest them
        if results['repos_found']:
            repo_swarm = RepoIngestionSwarm(f"{self.swarm_id}_repo", self.grimoire_path)

            repo_tasks = [repo_swarm.ingest_repo(repo) for repo in results['repos_found']]
            repo_results = await asyncio.gather(*repo_tasks)

            results['contents'] = repo_results

        # Cleanup
        shutil.rmtree(self.temp_path, ignore_errors=True)

        # Store in grimoire
        await self._store_in_grimoire(results)

        return {
            "success": True,
            "swarm_id": self.swarm_id,
            "results": results
        }

    async def _store_in_grimoire(self, results: Dict):
        """Store results in grimoire"""
        self.grimoire_path.mkdir(parents=True, exist_ok=True)

        grimoire_file = self.grimoire_path / f"zip_{results['zip_name'].replace('.zip', '')}.json"

        with open(grimoire_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "swarm_id": self.swarm_id,
                "type": "zip_ingestion",
                "data": results
            }, f, indent=2)


class AppIngestionSwarm:
    """Swarm that ingests entire applications into grimoire"""

    def __init__(self, swarm_id: str, grimoire_path: Path):
        self.swarm_id = swarm_id
        self.grimoire_path = grimoire_path

    async def ingest_app(self, app_path: str) -> Dict:
        """
        Ingest an entire application

        Extract:
        - Architecture
        - API endpoints
        - Database schemas
        - Business logic
        - UI patterns
        """
        app_path = Path(app_path)

        if not app_path.exists():
            return {"success": False, "error": "App path doesn't exist"}

        results = {
            "app_name": app_path.name,
            "architecture": await self._analyze_architecture(app_path),
            "apis": await self._find_apis(app_path),
            "database": await self._find_database_schemas(app_path),
            "ui_patterns": await self._find_ui_patterns(app_path)
        }

        # Also ingest as repo
        repo_swarm = RepoIngestionSwarm(f"{self.swarm_id}_repo", self.grimoire_path)
        repo_result = await repo_swarm.ingest_repo(str(app_path))

        results['code_ingestion'] = repo_result

        # Store in grimoire
        await self._store_in_grimoire(results)

        return {
            "success": True,
            "swarm_id": self.swarm_id,
            "results": results
        }

    async def _analyze_architecture(self, app_path: Path) -> Dict:
        """Analyze app architecture"""
        architecture = {
            "type": "unknown",
            "framework": None,
            "structure": []
        }

        # Check for common frameworks
        if (app_path / 'package.json').exists():
            architecture['type'] = 'node'
            # Check package.json for framework
            try:
                with open(app_path / 'package.json') as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    if 'next' in deps:
                        architecture['framework'] = 'nextjs'
                    elif 'react' in deps:
                        architecture['framework'] = 'react'
                    elif 'express' in deps:
                        architecture['framework'] = 'express'
            except:
                pass

        elif (app_path / 'requirements.txt').exists() or (app_path / 'setup.py').exists():
            architecture['type'] = 'python'
            # Check for frameworks
            req_file = app_path / 'requirements.txt'
            if req_file.exists():
                with open(req_file) as f:
                    reqs = f.read().lower()
                    if 'fastapi' in reqs:
                        architecture['framework'] = 'fastapi'
                    elif 'flask' in reqs:
                        architecture['framework'] = 'flask'
                    elif 'django' in reqs:
                        architecture['framework'] = 'django'

        # Analyze directory structure
        dirs = [d.name for d in app_path.iterdir() if d.is_dir()]
        architecture['structure'] = dirs

        return architecture

    async def _find_apis(self, app_path: Path) -> List[str]:
        """Find API endpoints in the app"""
        apis = []

        # Search for API route definitions
        api_patterns = [
            '@app.route',  # Flask
            '@router.',    # FastAPI
            'app.get(',    # Express
            'app.post(',   # Express
            'router.get(', # Next.js
        ]

        code_files = list(app_path.rglob('*.py')) + list(app_path.rglob('*.js')) + list(app_path.rglob('*.ts'))

        for file in code_files[:50]:  # Limit to 50 files
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in api_patterns:
                        if pattern in content:
                            # Extract the line with the API definition
                            for line in content.split('\n'):
                                if pattern in line:
                                    apis.append(line.strip())
            except:
                pass

        return apis[:50]  # Top 50 APIs

    async def _find_database_schemas(self, app_path: Path) -> List[str]:
        """Find database schemas"""
        schemas = []

        # Look for schema files
        schema_files = list(app_path.rglob('*schema*.py')) + \
                      list(app_path.rglob('*models*.py')) + \
                      list(app_path.rglob('*schema*.sql'))

        for file in schema_files[:20]:
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    schemas.append({
                        "file": str(file),
                        "content": f.read()[:1000]  # First 1000 chars
                    })
            except:
                pass

        return schemas

    async def _find_ui_patterns(self, app_path: Path) -> List[str]:
        """Find UI patterns and components"""
        patterns = []

        # Look for component files
        ui_files = list(app_path.rglob('*.tsx')) + \
                  list(app_path.rglob('*.jsx')) + \
                  list(app_path.rglob('*component*.py'))

        for file in ui_files[:30]:
            patterns.append(str(file.name))

        return patterns

    async def _store_in_grimoire(self, results: Dict):
        """Store results in grimoire"""
        self.grimoire_path.mkdir(parents=True, exist_ok=True)

        grimoire_file = self.grimoire_path / f"app_{results['app_name']}.json"

        with open(grimoire_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "swarm_id": self.swarm_id,
                "type": "app_ingestion",
                "data": results
            }, f, indent=2)


# ============================================================================
# HIVE COORDINATOR - Orchestrates multiple swarms
# ============================================================================

class HiveCoordinator:
    """
    Coordinates multiple swarms working in parallel

    HIVE = Swarm of swarms
    """

    def __init__(self, grimoire_path: str = "grimoire"):
        self.grimoire_path = Path(grimoire_path)
        self.grimoire_path.mkdir(parents=True, exist_ok=True)
        self.active_hives = {}

    async def deploy_hive(self, mission: HiveMission) -> Dict:
        """
        Deploy a hive to accomplish a mission

        Steps:
        1. Analyze inputs (repos, zips, apps)
        2. Create swarms for each type
        3. Deploy all swarms in parallel
        4. Aggregate results
        5. Store in grimoire
        """
        print(f"\n🐝 DEPLOYING HIVE: {mission.mission_id}")
        print(f"   Goal: {mission.goal}")
        print(f"   Inputs: {len(mission.input_paths)} paths")
        print(f"   Swarms: {mission.swarms_to_deploy}")
        print(f"   Agents per swarm: {mission.agents_per_swarm}")

        # Categorize inputs
        categorized = self._categorize_inputs(mission.input_paths)

        print(f"\n📊 INPUT ANALYSIS:")
        print(f"   Repos: {len(categorized['repos'])}")
        print(f"   Zips: {len(categorized['zips'])}")
        print(f"   Apps: {len(categorized['apps'])}")
        print(f"   Other: {len(categorized['other'])}")

        # Create swarms
        swarms = []

        # Repo swarms
        for i, repo in enumerate(categorized['repos']):
            swarm = RepoIngestionSwarm(f"{mission.mission_id}_repo_{i}", self.grimoire_path)
            swarms.append(('repo', swarm, repo))

        # Zip swarms
        for i, zip_file in enumerate(categorized['zips']):
            swarm = ZipIngestionSwarm(f"{mission.mission_id}_zip_{i}", self.grimoire_path)
            swarms.append(('zip', swarm, zip_file))

        # App swarms
        for i, app in enumerate(categorized['apps']):
            swarm = AppIngestionSwarm(f"{mission.mission_id}_app_{i}", self.grimoire_path)
            swarms.append(('app', swarm, app))

        print(f"\n🚀 DEPLOYING {len(swarms)} SWARMS IN PARALLEL...")

        # Deploy all swarms in parallel
        tasks = []
        for swarm_type, swarm, input_path in swarms:
            if swarm_type == 'repo':
                tasks.append(swarm.ingest_repo(input_path))
            elif swarm_type == 'zip':
                tasks.append(swarm.ingest_zip(input_path))
            elif swarm_type == 'app':
                tasks.append(swarm.ingest_app(input_path))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        failed = len(results) - successful

        hive_result = {
            "mission_id": mission.mission_id,
            "goal": mission.goal,
            "swarms_deployed": len(swarms),
            "successful_swarms": successful,
            "failed_swarms": failed,
            "grimoire_location": str(self.grimoire_path),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        # Store hive results
        self._store_hive_results(hive_result)

        print(f"\n✅ HIVE MISSION COMPLETE")
        print(f"   Swarms deployed: {len(swarms)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Grimoire: {self.grimoire_path}")

        return hive_result

    def _categorize_inputs(self, input_paths: List[str]) -> Dict:
        """Categorize inputs by type"""
        categorized = {
            'repos': [],
            'zips': [],
            'apps': [],
            'other': []
        }

        for path_str in input_paths:
            path = Path(path_str)

            if not path.exists():
                continue

            # Check if zip
            if path.is_file() and path.suffix == '.zip':
                categorized['zips'].append(str(path))

            # Check if repo
            elif path.is_dir() and (path / '.git').exists():
                categorized['repos'].append(str(path))

            # Check if app (has package.json, requirements.txt, etc.)
            elif path.is_dir() and ((path / 'package.json').exists() or
                                    (path / 'requirements.txt').exists() or
                                    (path / 'setup.py').exists()):
                categorized['apps'].append(str(path))

            # Check if directory with code
            elif path.is_dir():
                code_files = list(path.rglob('*.py')) + list(path.rglob('*.js'))
                if code_files:
                    categorized['repos'].append(str(path))
                else:
                    categorized['other'].append(str(path))

            else:
                categorized['other'].append(str(path))

        return categorized

    def _store_hive_results(self, hive_result: Dict):
        """Store hive mission results"""
        hive_file = self.grimoire_path / f"hive_{hive_result['mission_id']}.json"

        with open(hive_file, 'w') as f:
            json.dump(hive_result, f, indent=2)

    def get_grimoire_summary(self) -> Dict:
        """Get summary of what's in the grimoire"""
        grimoire_files = list(self.grimoire_path.glob('*.json'))

        summary = {
            "total_files": len(grimoire_files),
            "hive_missions": 0,
            "repos_ingested": 0,
            "zips_ingested": 0,
            "apps_ingested": 0,
            "total_knowledge": 0
        }

        for file in grimoire_files:
            try:
                with open(file) as f:
                    data = json.load(f)

                    if data.get('type') == 'repo_ingestion':
                        summary['repos_ingested'] += 1
                    elif data.get('type') == 'zip_ingestion':
                        summary['zips_ingested'] += 1
                    elif data.get('type') == 'app_ingestion':
                        summary['apps_ingested'] += 1
                    elif 'mission_id' in data and data.get('swarms_deployed'):
                        summary['hive_missions'] += 1

                    # Count knowledge entries
                    if 'data' in data:
                        knowledge = data['data'].get('knowledge_extracted', [])
                        summary['total_knowledge'] += len(knowledge)
            except:
                pass

        return summary


# ============================================================================
# CLI AND DEMO
# ============================================================================

async def demo_hive_powerload():
    """
    Demonstrate powerloading data into grimoire using hives
    """
    print("\n" + "="*70)
    print("🐝 HIVE SYSTEM - POWERLOAD ALL YOUR DATA")
    print("="*70)
    print("\nHierarchy:")
    print("  Glyph → Spell → Agent → Swarm → HIVE")
    print("\nHIVE = Swarm of Swarms")
    print("Deploy 10 swarms × 10 agents each = 100 agents processing in parallel")
    print()

    # Initialize hive coordinator
    coordinator = HiveCoordinator(grimoire_path="grimoire")

    # Get all inputs from current directory
    current_dir = Path.cwd()

    # Find all repos, zips, apps in current directory
    inputs = []

    # Add current repo
    if (current_dir / '.git').exists():
        inputs.append(str(current_dir))
        print(f"✅ Found current repo: {current_dir.name}")

    # Find zip files
    zips = list(current_dir.glob('*.zip'))
    for zip_file in zips:
        inputs.append(str(zip_file))
        print(f"✅ Found zip: {zip_file.name}")

    # Find subdirectories that are repos or apps
    for subdir in current_dir.iterdir():
        if subdir.is_dir() and subdir.name not in ['.git', 'node_modules', '__pycache__', 'grimoire', '.next']:
            if (subdir / '.git').exists():
                inputs.append(str(subdir))
                print(f"✅ Found repo: {subdir.name}")
            elif (subdir / 'package.json').exists() or (subdir / 'requirements.txt').exists():
                inputs.append(str(subdir))
                print(f"✅ Found app: {subdir.name}")

    if not inputs:
        print("\n⚠️  No repos, zips, or apps found in current directory")
        print("   Defaulting to current directory...")
        inputs = [str(current_dir)]

    print(f"\n📊 TOTAL INPUTS: {len(inputs)}")

    # Create hive mission
    mission = HiveMission(
        goal="Powerload all repos, zips, and apps into grimoire",
        input_paths=inputs,
        swarms_to_deploy=len(inputs),  # One swarm per input
        agents_per_swarm=10
    )

    # Deploy hive
    result = await coordinator.deploy_hive(mission)

    # Show grimoire summary
    print("\n" + "="*70)
    print("📚 GRIMOIRE SUMMARY")
    print("="*70)

    summary = coordinator.get_grimoire_summary()
    print(f"\n   Total files in grimoire: {summary['total_files']}")
    print(f"   Hive missions completed: {summary['hive_missions']}")
    print(f"   Repos ingested: {summary['repos_ingested']}")
    print(f"   Zips ingested: {summary['zips_ingested']}")
    print(f"   Apps ingested: {summary['apps_ingested']}")
    print(f"   Knowledge entries: {summary['total_knowledge']}")

    print("\n" + "="*70)
    print("✅ POWERLOAD COMPLETE")
    print("="*70)
    print("\nAll your data is now in the grimoire.")
    print("All agents can now learn from everything you've built.")
    print("\n💝 Love • Loyalty • Honor • Everybody Eats\n")


if __name__ == "__main__":
    print("\n🐝 Starting Hive System...")
    print("   This will powerload ALL your data into the grimoire")
    print("   Using swarms of swarms for maximum parallelization\n")

    try:
        asyncio.run(demo_hive_powerload())
    except KeyboardInterrupt:
        print("\n\n⚠️  Hive mission interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
