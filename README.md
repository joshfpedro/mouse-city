# Mouse City Project

This project analyzes mouse activity and social behavior in a multi-cage environment. It includes data processing scripts, exploratory data analysis notebooks, and an interactive web application to visualize the results.

## Scientific Context

This project is based on a study of mouse behavior in a "rural-like city" environment. The experiment tracked a cohort of female C57BL/6J mice using RFID tags to monitor their movement and interaction within a complex, multi-cage setup. The environment included a central hub with natural soil and several interconnected cages providing nesting materials, food, and water.

A key component of the study was a reward competition paradigm using a FED3 (Feeding Experimentation Device 3) device. This allowed researchers to investigate learning and motivation by requiring mice to perform specific tasks (nose pokes) to receive a sugar pellet reward. The difficulty of the task was progressively increased (e.g., from a fixed ratio of 1 to 5 pokes per reward).

The primary goal of this research is to understand how environmental complexity and social dynamics influence learning, behavior, and social structures in mice. The data collected from this experiment, including activity levels, cage preferences, and social interactions, provides a rich dataset for exploring these scientific questions. The findings may have broader implications for neuroscience and behavioral biology, particularly in understanding the interplay between environment, social hierarchy, and cognitive processes.

## Project Structure

- `data/`: Contains raw, intermediate, and processed data.
  - `raw/`: The original data from the experiment.
  - `intermediate/`: Intermediate data files generated during processing.
  - `processed/`: Final processed data used for analysis and visualization.
- `notebooks/`: Jupyter notebooks for data cleaning, preprocessing, and exploratory data analysis.
- `app.py`: A Streamlit web application for visualizing the processed data.
- `requirements.txt`: A list of Python dependencies for this project.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mouse-city
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Data Processing

The Jupyter notebooks in the `notebooks/` directory are used to process the raw data. They should be run in the following order:

1.  `0-data-cleaning.ipynb`
2.  `1.1-rural-data-preprocessing.ipynb`
3.  `1.2-urban-data-preprocessing.ipynb`
4.  `2-intermediate-processing.ipynb`
5.  `3-visualization.ipynb`

To run the notebooks, start the Jupyter server:
```bash
jupyter notebook
```

## Running the Web Application

The Streamlit application provides an interactive dashboard to explore the mouse activity data. To run the app, use the following command:

```bash
streamlit run app.py
```

This will start a local web server, and you can view the dashboard in your browser. The dashboard displays a social network graph, an activity histogram, and a heatmap of cage activity, which can be filtered by different time periods.
