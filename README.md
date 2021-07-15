# RAD Outlier Detect

This repository contains scripts that use the outlier detection algorithm developed by [Ben Birnbaum](https://github.com/benb111/outlier-detect) to generate research outputs centered around CommCare projects. These include:

1. A script to run the base algorithm with.
2. A script to generate a **Supervisor Card** that presents project supervisors with a list of frontline workers in their orgnanizations that exhibit anamolous behavior.
3. Helper functions to format the output from the algorithm.

## Data Required

* **CommCare Form Submission History**. The scripts here rely on CommCare data; in order to take advantage of its functionality, you must select a form from an existing CommCare application and download its form submission history. This history contains a detailed overview of every time the form in question was submitted by a health worker. This can be accessed in one of two ways:
    1. Manually exporting the form data from the application in CommCare HQ. This is located in the *Data* tab, and allows you to filter by which dates you want to get data from.
    2. Using CommCare's Data Export Tool (DET), which allows you to take advantage of CommCare's API to retrieve a variety of data from your projects.
* **Questions**. The algorithm works by comparing answer distributions for questions across all interviewers. In order to do this, it needs a specification of what questions to navigate. Gather a list of question IDs from yoru CommCare project that you wish to use to test for anamolous behavior.

After selecting a form, download its data and enter the relevant information pertaining to it in **settings.py**.

## Usage

1. Once you've downloded or cloned this repository, you need to first make sure the necessary libararies are installed on your machine. You can do this easily by running the following command:

```bash
pip install -r requirements.txt
```

2. Once the proper libraries have been installed, open the repository on your code editor of choice. We recommend using Visual Studio Code for this, as it has a built in interactive window and is known to work.

3. Before proceeding, ensure that **settings.py** is filled in with the correct values. See the previous section to get an overview of what data is required.

4. You can run the scripts in one of two ways:
    1. By running the script as you would any Python file, with the parameters for the settings file set:

    ```py
    python3 run_outlier_detect.py --settings=settings
    ```
    2. By running the script through the interactive window, cell by cell. You can access this through Visual Studio Code by hovering your mouse over any cell (indicated by a '%%') and clicking 'Run Cell' or by hitting Shift+Enter on any block of code. The output should appear automatically in a separate pane.