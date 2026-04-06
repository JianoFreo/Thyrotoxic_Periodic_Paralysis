# Using Jupyter with this project

This project includes a small example notebook to explore the sample data and try quick ML/EDA workflows.

Quick steps:

1. Create a virtual environment (recommended) and activate it.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Start Jupyter:

```powershell
jupyter notebook
# or
jupyter lab
```

4. Open the notebook: `notebooks/TPP-ML-demo.ipynb` and run the cells. The notebook reads files from the `sample-data/` folder.

Notes:
- If your Python environment already has packages (pandas/matplotlib), you can skip reinstalling.
- The demo is minimal, feel free to extend it with sklearn or other ML libraries as needed.
