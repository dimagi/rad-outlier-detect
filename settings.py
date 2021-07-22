# The name of the form to run the algorithm on.
# Ex. flu_check
FORMS = ['']

# A list of question IDs to avoid running the algorithm on.
# It is recommended to add metadata columns and non-categorical questions here. A few have been pre-added that are common metadata properties in CommCare.
# Ex. ['cough', 'pregancy_check']
COLUMNS_TO_AVOID = ['id', 'number', 'caseid', 'name']

# Specify end dates to filter form data by time.
BY_DATES = []

# If you're accessing data from a server, fill in the credentials here.
DB = ''
POSTGRES_ADDRESS = ''
POSTGRES_PORT = ''
POSTGRES_USERNAME = ''
POSTGRES_PASSWORD = ''
POSTGRES_DBNAME = ''
