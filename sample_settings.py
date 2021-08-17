# The name of the project.
PROJECT = ''

# The name of the form to run the algorithm on.
# Ex. flu_check
FORMS = ['']

# The user ID column in the form.
# ex. 'username'
FORM_USER_ID = ''

# A list of survey responses to avoid, like blanks.
# Ex. ['missing', ' ']
AVOID_RESPONSES = []

# In order to weed out non-categorical questions, establish a limit to the number of answer choices a question can have before we consider it continuous/non-categorical.
ANSWER_LIMIT = 4

# Specify stary and end dates to filter form data by time.
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
