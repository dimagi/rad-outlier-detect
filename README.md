# RAD Outlier Detect

This repository is an implementation of the outlier detection algorithm developed by [Ben Birnbaum](https://github.com/benb111/outlier-detect).

## Usage

1. Make sure you have access to a form submission file from a CommCare project, along with its form summary and annotations. If you have access to the RAD server, use a gzip file located in *data/forms/project_name*. 
    1. The form summary is located in the same folder with the same file name, except in *.csv* format.
    2. Annotations are located in *data/annotations/* as *project.csv*.
2. Fill the variables in the *settings.py* file with the appropiate values, based on the previous step.
3. Use the *requirements.txt* file to download all of the required libraries to run the script.
4. You can run the script through the interactive window (it's formatted to run as cells) or by running:

```bash
python3 generate_outlier_detect.py
```
