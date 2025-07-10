import os
import shutil
import subprocess
import sys

def create_project(project_name, platform, dest_dir="."):
    """
    Creates a project directory structure.

    Args:
        project_name: The name of the project.
        platform: The platform (ios, flutter, or android).
        dest_dir: The destination directory for the project. Defaults to the current directory.
    """
    project_path = os.path.join(dest_dir, project_name)

    # 1. Create project directory
    try:
        os.makedirs(project_path, exist_ok=True)
        print(f"Created directory: {project_path}")
    except OSError as e:
        print(f"Error creating directory {project_path}: {e}")
        return

    # 2. Clone the repository and copy the platform-specific content
    repo_url = "https://github.com/BruceLan/prompt.git"
    temp_clone_dir = "prompt_temp"
    try:
        print(f"Cloning repository: {repo_url}")
        subprocess.run(["git", "clone", repo_url, temp_clone_dir], check=True, capture_output=True)
        
        source_dir = os.path.join(temp_clone_dir, "arch", platform)
        
        if os.path.exists(source_dir):
            # Copy contents of the platform directory to the new project directory
            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(project_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks=True, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            print(f"Copied contents of {source_dir} to {project_path}")
        else:
            print(f"Error: Source directory {source_dir} not found.")

    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr.decode()}")
    except Exception as e:
        print(f"An error occurred during clone and copy: {e}")
    finally:
        if os.path.exists(temp_clone_dir):
            shutil.rmtree(temp_clone_dir)
            print(f"Cleaned up temporary directory: {temp_clone_dir}")

    # Create .cursor/rules directory and process GEMINI.md
    try:
        rules_dir = os.path.join(project_path, ".cursor", "rules")
        os.makedirs(rules_dir, exist_ok=True)
        print(f"Created directory: {rules_dir}")

        gemini_md_path = os.path.join(project_path, "GEMINI.md")
        new_mdc_path = os.path.join(rules_dir, f"{platform.lower()}4dev.mdc")

        if os.path.exists(gemini_md_path):
            description = ""
            with open(gemini_md_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    description = first_line.lstrip('# ').strip()
                else:
                    description = first_line

            header = f"""---
description: {description}
globs:
alwaysApply: true
---
"""

            with open(gemini_md_path, 'r', encoding='utf-8') as f_read:
                original_content = f_read.read()

            with open(new_mdc_path, 'w', encoding='utf-8') as f_write:
                f_write.write(header + "\n" + original_content)

            print(f"Created rule file: {new_mdc_path}")

        else:
            print(f"Warning: GEMINI.md not found in {project_path}. Skipping rule creation.")

    except Exception as e:
        print(f"An error occurred while creating the rule file: {e}")


    # 3. Create docs directory
    try:
        docs_dir = os.path.join(project_path, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        print(f"Created directory: {docs_dir}")
    except OSError as e:
        print(f"Error creating directory {docs_dir}: {e}")

    # 4. Create audit directory
    try:
        audit_dir = os.path.join(project_path, "audit")
        os.makedirs(audit_dir, exist_ok=True)
        print(f"Created directory: {audit_dir}")
    except OSError as e:
        print(f"Error creating directory {audit_dir}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python create_project.py <project_name> <platform> [destination_directory]")
        print("Platform can be: ios, flutter, or android")
        sys.exit(1)

    project_name_arg = sys.argv[1]
    platform_arg = sys.argv[2]
    dest_dir_arg = sys.argv[3] if len(sys.argv) == 4 else "."


    if platform_arg not in ["ios", "flutter", "android"]:
        print(f"Invalid platform: {platform_arg}. Please choose from ios, flutter, or android.")
        sys.exit(1)

    create_project(project_name_arg, platform_arg, dest_dir_arg)