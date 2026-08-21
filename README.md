# Gifted Brain Network Dashboard

An interactive dashboard based on Gabrielle Marion's analysis, designed to explore brain network metrics and cortical differences between gifted and control groups.

The dashboard is built with Python, Dash, and Plotly.

---

## Run the Dashboard Locally

### 1. Open the project directory

Open a terminal and navigate to the folder containing the project:

```
cd path/to/brain_network
```

### 2. Install the dependencies

If the required Python packages are not already installed, run:

```
pip install -r requirements.txt
```

### 3. Start the dashboard

Run:

```
python app.py
```

### 4. Open the dashboard

Once the application starts, the terminal will display a local address similar to:

```
http://127.0.0.1:8050/
```

Copy this address and paste it into your web browser to access the dashboard.

> **Note:** The local address is only available while `app.py` is running. Keep the terminal open while using the dashboard.

---

## Temporary Deployment

The dashboard can also be temporarily deployed online using [Render](https://render.com/).

For deployment on Render, the application can be started with:

```
gunicorn app:server
```

---

## Quick Start

```
cd path/to/brain_network
pip install -r requirements.txt
python app.py
```

Then open the local address displayed in the terminal in your web browser.