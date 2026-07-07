# 🛠️ Setup Guide

This guide explains how to set up the development environment for the **AI-Powered Medicine Box Detection System**.

---

# Prerequisites

Before running the project, make sure the following software is installed:

- Python 3.12 or later
- Git
- Visual Studio Code

---

# Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/Melikeda/medicine-box-detection-yolov8.git
```

Navigate into the project directory:

```bash
cd medicine-box-detection-yolov8
```

---

# Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

---

# Activate the Virtual Environment

### Windows (PowerShell)

```powershell
venv\Scripts\Activate.ps1
```

### Windows (CMD)

```cmd
venv\Scripts\activate
```

---

# Install Required Libraries

Install all project dependencies:

```bash
pip install -r requirements.txt
```

---

# Verify Installation

Check that Python is installed correctly:

```bash
python --version
```

Check installed packages:

```bash
pip list
```

---

# Project Structure

```text
medicine-box-detection-yolov8/
│
├── docs/
├── src/
├── data/
├── models/
├── README.md
├── requirements.txt
└── LICENSE
```

---

# Ready to Start

The development environment is now ready.

You can proceed with dataset preparation and YOLOv8 model training.