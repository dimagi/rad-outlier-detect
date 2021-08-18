# RAD Outlier Detect

This repository contains scripts that use the outlier detection algorithm developed by [Ben Birnbaum](https://github.com/benb111/outlier-detect) to generate research outputs centered around CommCare projects. These include:

1. A script to run the base algorithm with.
2. A script to generate a **Supervisor Card** that presents project supervisors with a list of frontline workers in their orgnanizations that exhibit anamolous behavior.
3. Helper functions to format the output from the algorithm.

## Data Required

* **CommCare Form Submission History**. The scripts here rely on CommCare data; in order to take advantage of its functionality, you must select a form from an existing CommCare application and download its form submission history. This history contains a detailed overview of every time the form in question was submitted by a health worker. This can be accessed in one of two ways:
    1. Manually exporting the form data from the application in CommCare HQ. This is located in the *Data* tab, and allows you to filter by which dates you want to get data from.
    2. Using CommCare's Data Export Tool (DET), which allows you to take advantage of CommCare's API to retrieve a variety of data from your projects.

After selecting a form, download its data and enter the relevant information pertaining to it in **settings.py**.

## Settings

As mentioned above, there is relevant information related to the required data that needs to be put into the **settings.py** file. This information includes:

* **PROJECT** - the name of the CommCare project. This is used when generating a path to save results in. The name of the folder the results will be saved in will be the string entered here.
* **FORMS** - a list of names of forms to run the algorithm on. These names should match the file or database table exactly, as the script will loop through this list to read and process each form.
* **FORM_USER_ID** - the ID that distinguishes each interviewer. In CommCare, this is usually 'username', but incase there is a different field, the option to fill that in is offered here.
* **AVOID_RESPONSES** - a list of strings to exclude when running the algorithm. Because the algorithm works by getting a frequency count of each answer value for every question, an option to not count certain choices is available.
* **ANSWER LIMIT** - a integer that incidates how many answer choices a question can have before being considered as non-categorical.
* **DATES** - a list of tuples with dates that indicate a start and stop point. The scripts are configured to run the algorithm on set intervals of the data available, so one may view how an interviewer's outlier scores are changing over time.
* SQL Server Access Variables - the scripts are configured to read the form data from a remote server. To access it, these variables are available to read in the data using SQLAlchemy.

Here is an example settings file -

```py
PROJECT = 'health_project'
FORMS = ['flu_check', 'pregnancy_outcomes']
FORM_USER_ID = 'username'
AVOID_RESPONSES = [' ']
ANSWER_LIMIT = 4
DATES = [('2019-01-01', '2020-01-01')]

PROJECT_PATH = 'sql_table_path'
DB = 'health_project'
POSTGRES_ADDRESS = 'health.project'
POSTGRES_PORT = '5555'
POSTGRES_USERNAME = 'flw'
POSTGRES_PASSWORD = '123health'
POSTGRES_DBNAME = 'health_project_data'
```

## Usage

1. Once you've downloded or cloned this repository, you need to first make sure the necessary libararies are installed on your machine. You can do this easily by running the following command:

```bash
pip install -r requirements.txt
```

2. Once the proper libraries have been installed, open the repository on your code editor of choice. We recommend using Visual Studio Code for this, as it has a built in interactive window and is known to work.

3. Before proceeding, ensure that **settings.py** is filled in with the correct values. See the previous section to get an overview of what data is required.

4. The default version of this script is configured to loop through the list of forms provided in the settings file, read the form from the server (or, from a local parquet file if available), clean it (to hash the usernames or remove unneccessary columns), and run the algorithm.

```bash
python3 run_outlier_detect.py --settings=sample_settings
```

5. To save the output above, you can add a line underneath the run code to generate a csv of the results to the path of your choice, as below:

```py
    # This is already in the script:
    df_results = run_algorithm(df_form_cleaned, questions)
    
    # You can insert this line to save the results:
    df_results.to_csv('results.csv')
```

6. Using the saved output of this primary script, you can run **generate_supervisor_card.py** to create a spreadsheet that contains formatted cells that allow CommCare to easily read the algorithm results and generate intuitive Supervisor Cards. These cards contain the top 3 highest scored questions for every interviewer, presenting their surprising behavior in easy-to-read statements.

```bash
python3 generate_supervisor_card.py --settings=sample_settings
```
