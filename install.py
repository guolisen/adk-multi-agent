#!/usr/bin/env python3
"""
Deepdevflow Installer Script

This script helps set up the Deepdevflow environment using uv,
a modern Python package installer. It creates a virtual environment
and installs all dependencies.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60 + "\n")


def run_command(command, description=None, exit_on_error=True):
    """Run a shell command and handle errors."""
    if description:
        print(f"→ {description}...")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        if exit_on_error:
            sys.exit(1)
        return False


def check_uv_installed():
    """Check if uv is installed, install if not."""
    try:
        subprocess.run(["uv", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        print("✅ uv is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed. Installing now...")
        
        # Install uv based on the platform
        if platform.system() == "Windows":
            run_command(
                "pip install uv",
                "Installing uv using pip"
            )
        else:  # macOS and Linux
            run_command(
                "curl -sL https://astral.sh/uv/install.sh | sh",
                "Installing uv using the official installer"
            )
        
        return check_uv_installed()


def setup_environment():
    """Set up the virtual environment and install dependencies."""
    venv_path = ".venv"
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_path):
        run_command("uv venv", "Creating virtual environment")
    else:
        print(f"✅ Virtual environment already exists at {venv_path}")
    
    # Activate virtual environment and install dependencies
    activate_cmd = f".\\{venv_path}\\Scripts\\activate" if platform.system() == "Windows" else f"source {venv_path}/bin/activate"
    
    # Install dependencies
    install_cmd = f"{activate_cmd} && uv pip install -e ."
    run_command(install_cmd, "Installing dependencies")
    
    # Install dev dependencies
    dev_install_cmd = f"{activate_cmd} && uv pip install -e \".[dev]\""
    run_command(dev_install_cmd, "Installing development dependencies", exit_on_error=False)


def create_example_configs():
    """Create example configuration files if they don't exist."""
    config_dir = Path("config")
    example_files = {
        "config.yaml": "config.yaml.example",
        "llm_config.yaml": "llm_config.yaml.example",
        "agent_config.yaml": "agent_config.yaml.example",
        "frontend_config.yaml": "frontend_config.yaml.example"
    }
    
    for config_file, example_file in example_files.items():
        config_path = config_dir / config_file
        example_path = config_dir / example_file
        
        # Copy existing config to example if example doesn't exist
        if not example_path.exists() and config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
            
            with open(example_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Created {example_file} from existing {config_file}")
        
        # Copy example to config if config doesn't exist
        if not config_path.exists() and example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Created {config_file} from {example_file}")


def main():
    """Main function to run the installation."""
    # Print welcome message
    print_header("Deepdevflow Installer")
    print("This script will set up the Deepdevflow environment using uv.")
    print("Make sure you have Python 3.9+ installed before proceeding.\n")
    
    # Check if uv is installed
    check_uv_installed()
    
    # Set up environment
    print_header("Setting Up Environment")
    setup_environment()
    
    # Create example configuration files
    print_header("Configuration Files")
    create_example_configs()
    
    # Print success message
    print_header("Installation Complete")
    print("Deepdevflow has been successfully installed!")
    print("\nTo activate the virtual environment:")
    
    if platform.system() == "Windows":
        print("  .venv\\Scripts\\activate")
    else:
        print("  source .venv/bin/activate")
    
    print("\nTo run the backend server:")
    print("  python -m backend.app")
    
    print("\nTo run the frontend:")
    print("  streamlit run frontend/app.py")
    
    print("\nEnjoy using Deepdevflow!")


if __name__ == "__main__":
    main()
