# Multi-Agent System with Google ADK

This repository contains a demonstration of a multi-agent system built using Google's Agent Development Kit (ADK). The system consists of specialized agents for billing and technical support, coordinated by a main routing agent.

## Files

- `main.py`: Python script version of the multi-agent system
- `main.ipynb`: Jupyter notebook version with detailed explanations and interactive cells

## Prerequisites

Before running the notebook, ensure you have the following installed:

1. Python 3.8 or higher
2. Jupyter Notebook or JupyterLab
3. Google ADK packages:
   ```
   pip install google-adk google-generativeai
   ```

## Running the Jupyter Notebook

### Option 1: Using Jupyter Notebook

1. Navigate to the project directory in your terminal:
   ```
   cd /root/code/google/multiagent
   ```

2. Launch Jupyter Notebook:
   ```
   jupyter notebook
   ```

3. In the browser window that opens, click on `main.ipynb` to open the notebook.

4. Run the cells by clicking the "Run" button or pressing Shift+Enter for each cell.
   - You can run all cells at once by selecting "Cell" > "Run All" from the menu.

### Option 2: Using JupyterLab

1. Navigate to the project directory in your terminal:
   ```
   cd /root/code/google/multiagent
   ```

2. Launch JupyterLab:
   ```
   jupyter lab
   ```

3. In the browser window that opens, double-click on `main.ipynb` in the file browser.

4. Run the cells by clicking the "Run" button or pressing Shift+Enter for each cell.
   - You can run all cells at once by selecting "Run" > "Run All Cells" from the menu.

### Option 3: Using VS Code

1. Open VS Code and navigate to the project directory.

2. Install the "Jupyter" extension if you haven't already.

3. Open the `main.ipynb` file.

4. Run cells using the "Run Cell" button that appears above each cell or by pressing Shift+Enter.

## What the Notebook Does

The notebook demonstrates:

1. How to set up specialized agents for different tasks
2. How to create a coordinator agent that routes requests
3. How to process user queries through the multi-agent system
4. How to extract and display responses

The notebook is divided into sections with explanatory markdown cells and executable code cells. You can run each section independently to understand how the different components work together.

## Troubleshooting

- **ModuleNotFoundError**: If you encounter errors about missing modules, ensure you've installed all required packages:
  ```
  pip install google-adk google-generativeai
  ```

- **API Key Issues**: If you encounter authentication errors, check that the API key in the notebook is valid. You may need to replace it with your own API key.

- **Memory Issues**: If the notebook runs out of memory, try restarting the kernel and running only the cells you need.

## Additional Resources

- [Google ADK Documentation](https://developers.google.com/adk)
- [Gemini API Documentation](https://ai.google.dev/docs)
