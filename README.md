# Python Project - Scrapy Template

This project is built using [Scrapy](https://scrapy.org/), a powerful framework for web scraping and data mining. 
Follow the steps below to clone the repository, set up the environment, and run the project.

## Table of Contents

- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)

## Requirements

- Python 3.8+
- Git
- [Poetry](https://python-poetry.org/) (for dependency management)
- Virtual environment tool (optional but recommended)

## Setup Instructions

### 1. Clone the repository

Clone this repository to your local machine using `git`:

```bash
git clone https://github.com/TranNhanGIS/python-boilerplate.git
cd python-boilerplate
```

### 2. Install the packages

Ensure you have Poetry installed for package management. If not, you can install it via pip:

```bash
pip install poetry
```

Once Poetry is installed, use it to install all dependencies listed in the pyproject.toml file:

```bash
poetry install
```

### 3. Activate the virtual environment (optional but recommended)
After installing the dependencies, you can activate the virtual environment created by Poetry:

```bash
poetry shell
```

## Running the Project
Navigate to the project directory and run the Scrapy spider:

```bash
cd diadiem247
scrapy crawl locations
```

This will start the Scrapy spider named locations.

## Project Structure
The project follows a standard Scrapy layout:

```bash
python-boilerplate/
├── diadiem247/
    ├── diadiem247/           # Main Scrapy project folder
    │   ├── spiders/          # Folder containing spider definitions
    │   ├── __init__.py       # Marks this folder as a Python package
    │   └── settings.py       # Project-wide settings
    ├── pyproject.toml        # Poetry configuration file for dependencies
    ├── README.md             # Project documentation (this file)
    └── scrapy.cfg           # Scrapy configuration file
```

Custom Settings
You can modify the settings.py file within the diadiem247 folder to change Scrapy settings, such as user agents, pipelines, concurrency, etc.