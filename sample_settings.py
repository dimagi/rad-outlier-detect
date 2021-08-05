# The name of the project.
PROJECT = ''

# The name of the form to run the algorithm on.
# Ex. flu_check
FORMS = ['']

# The user ID column in the form.
# ex. 'username'
FORM_USER_ID = ''

# A list of question IDs to avoid running the algorithm on.
# It is recommended to add metadata columns and non-categorical questions here. A few have been pre-added that are common metadata properties in CommCare.
# Ex. ['cough', 'pregancy_check']
COLUMNS_TO_AVOID = ['id', 'app_id', 'received_on', 'formid']

# Specify stard and end dates to filter form data by time.
# Ex. [('2019-01-01', '2019-04-01')]
DATES = []

# If you're accessing data from a server, fill in the credentials here.
PROJECT_PATH = ''
DB = ''
POSTGRES_ADDRESS = ''
POSTGRES_PORT = ''
POSTGRES_USERNAME = ''
POSTGRES_PASSWORD = ''
POSTGRES_DBNAME = ''
