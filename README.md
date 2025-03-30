# Gaze-Tracking Application

## Overview

This application captures real-time gaze data using your webcam, guides you through a calibration process, and visualizes your gaze activity as a heatmap over a displayed advertisement. The system maps gaze points to screen coordinates and provides insights into how users view visual content.

## Features

- **Live Video Capture:** Initializes the webcam and captures live video feed.
- **Calibration Process:** Prompts the user to look at a grid of points for calibration.
- **Real-Time Gaze Tracking:** Tracks and maps gaze points to screen coordinates.
- **Heatmap Visualization:** Generates and displays a heatmap based on gaze activity.
- **Advertisement Display:** Shows an advertisement in full-screen mode after calibration.

## Installation

1. **Clone the Repository:**

   `
   git clone <repository-url>`
   
   `cd <repository-directory>`

3. **Install Python Dependencies**
Install all required dependencies using the provided requirements.txt file:

  `pip install -r requirements.txt`

Some users may experience issues installing the dlib library, which is required for facial landmark detection. If you encounter installation errors, try one of the following:
- Use the Conda Shell for installation:
  `conda install -c conda-forge dlib`

- Download and install a precompiled .whl file compatible with your Python version from Gohlke's repository:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib

## Usage

### Ensure Your Setup

- Make sure you are in the project’s root directory.
- Ensure that a working webcam is connected and accessible.

### Run the Application

The main entry point is the `main.py` script located in the `src/` directory. To start the application, run:


`python src/main.py`

Upon launch, the user will be prompted to look at a grid of points to calibrate gaze detection. This calibration helps the system accurately map your gaze to screen coordinates.

**Once calibration is complete:**

- A full-screen advertisement will be shown.
- The system will track your gaze and generate a heatmap overlay in real time, showing which parts of the screen you focused on.

