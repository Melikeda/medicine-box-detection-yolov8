# 🖥️ Development Environment Report

## 📌 Purpose

The purpose of this phase is to prepare a clean and reproducible development environment for the AI-Powered Medicine Box Detection System.

A properly configured environment ensures that all required dependencies are isolated and the project can be developed consistently across different machines.

---

# 🎯 Objectives

- Install Python
- Configure Visual Studio Code
- Create a virtual environment
- Install required Python libraries
- Prepare the project for future development

---

# 🛠️ Development Environment

## Operating System

- Windows 11

## Code Editor

- Visual Studio Code

## Version Control

- Git
- GitHub

## Programming Language

- Python 3.x

---

# 📦 Virtual Environment

A Python virtual environment was created to isolate project dependencies from the global Python installation.

Creating a virtual environment provides several advantages:

- Prevents dependency conflicts
- Makes the project portable
- Simplifies dependency management
- Improves reproducibility

Virtual environment creation command:

```bash
python -m venv venv
```

Activation (PowerShell):

```powershell
venv\Scripts\Activate.ps1
```

---

# 📚 Installed Libraries

The following libraries were installed during this phase:

- ultralytics
- torch
- torchvision
- opencv-python
- numpy
- matplotlib
- PyYAML
- Pillow

The installed packages are managed through the `requirements.txt` file.

---

# 📄 Configuration Files

The following files were prepared:

- requirements.txt
- docs/setup-guide.md

These files simplify project installation and environment setup for future users.

---

# ✅ Outcome

At the end of this phase:

- Python development environment is ready.
- Virtual environment is configured.
- Required dependencies are installed.
- Development setup documentation has been prepared.

The project is now ready to proceed to the dataset preparation stage.

---

# 📌 Next Phase

The next development stage is:

**Feature Branch**

```text
feature/roboflow-dataset
```

This phase will focus on collecting, organizing, and preparing the medicine box dataset before annotation in Roboflow.