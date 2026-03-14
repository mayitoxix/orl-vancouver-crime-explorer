# Vancouver Crime Explorer

## Overview
This project provides an interactive Streamlit dashboard for exploring crime patterns across Vancouver neighbourhoods. Users can filter incidents by neighbourhood, crime type, month, and time of day to examine how crime is distributed throughout the city. This dashboard uses Vancouver Police Department crime data for 2025.

## Run Application
Follow these steps to clone and run this application locally:

1. Clone the repository

Run the following commands in your terminal to clone the repository to your local machine:

```bash
git clone <git@github.com:mayitoxix/orl-vancouver-crime-explorer.git>
cd orl-vancouver-crime-explorer
```

2. Install the project environment

Navigate to the root of the project dirctory and run:

``` bash
conda env create -f environment.yml
conda activate orl-vancity-crime
```

3. Render the app

To render the app, navigate to the root of the project directory and run:

``` bash
streamlit run src/streamlit_app.py
```

This will open a new tab in your browser. If not, you can access using this URL: http://localhost:8501