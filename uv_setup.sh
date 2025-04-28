#!/bin/bash
# Script to initialize Deepdevflow with uv

# Default settings
VENV_DIR=".venv"
REPO_DIR="."
REQUIREMENTS_FILE="requirements.txt"

# ANSI colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}    Deepdevflow Setup with UV Package Manager         ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Check if uv is installed
echo -e "${YELLOW}Checking if uv is installed...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}uv is not installed.${NC}"
    echo -e "${YELLOW}Installing uv...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # macOS or Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        # Windows or other
        echo -e "${RED}Please install uv manually:${NC}"
        echo -e "${YELLOW}Run: pip install uv${NC}"
        exit 1
    fi
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install uv. Please install it manually.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}uv is installed!${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
uv venv "$VENV_DIR"
echo -e "${GREEN}Virtual environment created at $VENV_DIR${NC}"

# Source the virtual environment
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # macOS or Linux
    source "$VENV_DIR/bin/activate"
else
    # Windows
    source "$VENV_DIR/Scripts/activate"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -e "$REPO_DIR"
echo -e "${GREEN}Dependencies installed!${NC}"

# Install development dependencies
echo -e "${YELLOW}Installing development dependencies...${NC}"
uv pip install -e "$REPO_DIR[dev]"
echo -e "${GREEN}Development dependencies installed!${NC}"

# Create example directories if they don't exist
echo -e "${YELLOW}Setting up project directories...${NC}"

# Ensure data directory exists for database
mkdir -p data
echo -e "${GREEN}Created data directory${NC}"

# Ensure logs directory exists
mkdir -p logs
echo -e "${GREEN}Created logs directory${NC}"

# Ensure configuration files exist
if [ ! -f "config/frontend_config.yaml.example" ] && [ -f "config/frontend_config.yaml" ]; then
    cp config/frontend_config.yaml config/frontend_config.yaml.example
    echo -e "${GREEN}Created frontend_config.yaml.example from existing file${NC}"
fi

echo -e "${BLUE}======================================================${NC}"
echo -e "${GREEN}Deepdevflow successfully set up!${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""
echo -e "${YELLOW}To activate the virtual environment:${NC}"
echo -e "  source $VENV_DIR/bin/activate  # On Linux/macOS"
echo -e "  $VENV_DIR\\Scripts\\activate     # On Windows"
echo ""
echo -e "${YELLOW}To run the backend:${NC}"
echo -e "  python -m backend.app"
echo ""
echo -e "${YELLOW}To run the frontend:${NC}"
echo -e "  streamlit run frontend/app.py"
echo ""
