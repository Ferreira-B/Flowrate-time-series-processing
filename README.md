### **What is it?**

The **WISDom – Flowrate time series processing** is a software tool that allows the processing of unevenly and evenly spaced flowrate time series for use in multiple engineering computer applications, namely, for creating early warning systems against failures, for the calibration of hydraulic models or for pipe bursts detection and location. 

### **Main features**

The current software implements the methodology proposed by Ferreira et al. (2022) and includes four main steps:

1. Automatic identification of anomalous values
2. Time series reconstruction in short duration gaps
3. Time step normalization
4. Time series reconstruction in long duration gaps.

The Flowrate time series processing tool presents a modular structure. Thus, it allows the complete processing of the time series (using the four modules sequentially) or the exclusive use of a specific module. 

### **Where to get it**


The standalone application for Windows OS can be downloaded using the following link: https://github.com/Ferreira-B/Flowrate-time-series-processing/releases/download/status/WISDom_1.1.0.zip

![image](https://user-images.githubusercontent.com/92049028/185946163-bb420944-a4f3-4537-8a1e-303db2a6a93f.png)

### **Documentation**
The User's manual can be accessed using the following link: https://github.com/Ferreira-B/Flowrate-time-series-processing/raw/main/Manual.pdf

### **Source code**

The application was developed in Python using the Tkinter package and the source code is currently hosted on GitHub at: https://github.com/Ferreira-B/Flowrate-time-series-processing

A brief explanation of each file is given:
- Manual.pdf contains the user's manual;
- Research_paper.pdf contains the original research paper by Ferreira et al. (2022) upon which the software was developed;
- GUI4.9.2.py contains the source code for the computer application;
- functions_clean.py contains the developed python functions for the processing of unevenly spaced flowrate time series;
- functions_forecast.py contains the developed python functions for the reconstruction of flowrate time series;
- dictionary.csv contains the list of software terms in both English and Portuguese;
- _____.png contains the logos of the R&D team;
- icon.ico contains the software icon;
- Holidays.csv contains a list of holidays and can be edited by the user;
- Input.csv and Historic_records.csv contain raw time series and already processed flowrate time series. These files can be used to test the tool;
- requirements.txt contains the list of python libraries and their associated version.
- The datasets folder contains the flowrate datasets from three water utilities and they were used in the development and validation stages.

### **Cite us**

Ferreira, B., Carriço, N., Barreira, R., Dias, T., & Covas, D. (2022). Flowrate time series processing in engineering tools for water distribution networks. Water Resources Research, 58, e2022WR032393. https://doi.org/10.1029/2022WR032393.

