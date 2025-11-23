#!/usr/bin/env python3
"""
Quick app generator - Actually writes files to disk
"""

import asyncio
import os
import shutil
from code_generator import CodeGenerationEngine


async def generate_and_save(description: str, output_dir: str = None):
    """Generate app and save all files to disk"""

    if output_dir is None:
        # Create based on description
        app_name = description.lower().replace(" ", "_")[:20]
        output_dir = f"./generated_{app_name}"

    # Clean existing
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    print(f"\n📁 Output directory: {output_dir}\n")

    # Generate
    engine = CodeGenerationEngine()
    result = await engine.think(description)

    if result.success:
        # Get the generated code
        request_id = result.request_id
        code = None

        # Find the code in engine's requests
        for req_id, request in engine.requests.items():
            if req_id == request_id:
                # Regenerate code (since we don't store it)
                synthesis = engine._template_architecture(request)
                code = await engine._generate_complete_code(request, synthesis)
                break

        if code:
            # Write all files
            write_generated_files(output_dir, code)

            print(f"\n✅ Files written to: {output_dir}")
            print(f"\n📂 Structure:")
            print_tree(output_dir)

            print(f"\n🚀 To run:")
            print(f"\n   Backend:")
            print(f"     cd {output_dir}/backend")
            print(f"     pip install -r requirements.txt")
            print(f"     uvicorn main:app --reload")
            print(f"\n   Frontend:")
            print(f"     cd {output_dir}/frontend")
            print(f"     npm install")
            print(f"     npm start")

    return result


def write_generated_files(base_dir: str, code):
    """Write all generated files"""

    # Frontend files
    for filename, content in code.frontend.items():
        filepath = os.path.join(base_dir, "frontend", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)

    # Backend files
    for filename, content in code.backend.items():
        filepath = os.path.join(base_dir, "backend", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)

    # API files
    for filename, content in code.api.items():
        filepath = os.path.join(base_dir, "api", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)

    # Test files
    for filename, content in code.tests.items():
        filepath = os.path.join(base_dir, "tests", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)

    # Config files (at root)
    for filename, content in code.config.items():
        filepath = os.path.join(base_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

    # README
    with open(os.path.join(base_dir, "README.md"), 'w') as f:
        f.write(code.readme)


def print_tree(directory, prefix="", max_depth=3, current_depth=0):
    """Print directory tree"""

    if current_depth >= max_depth:
        return

    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return

    for i, entry in enumerate(entries):
        if entry.startswith('.'):
            continue

        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1

        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{entry}")

        if os.path.isdir(path):
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(path, next_prefix, max_depth, current_depth + 1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = "Build me a todo app"

    print(f"\n🎯 Generating: {description}\n")

    asyncio.run(generate_and_save(description))
