# The name of the project.
PROJECT = 'lwala'

# The name of the form to run the algorithm on.
# Ex. flu_check
FORMS = ['lwala_people_update_person']

# The user ID column in the form.
# ex. 'username'
FORM_USER_ID = 'username'

# A list of question IDs to avoid running the algorithm on.
# It is recommended to add metadata columns and non-categorical questions here. A few have been pre-added that are common metadata properties in CommCare.
# Ex. ['cough', 'pregancy_check']
AVOID_RESPONSES = []

# Specify start and end dates to filter form data by time.
# Ex. [('2019-01-01', '2019-04-01')]
DATES = [('2020-01-01', '2020-02-01'), 
         ('2020-02-01', '2020-03-01'), 
         ('2020-03-01', '2020-04-01'), 
         ('2020-04-01', '2020-05-01'),
         ('2020-05-01', '2020-06-01'),
         ('2020-06-01', '2020-07-01'),
         ('2020-07-01', '2020-08-01'),
         ('2020-08-01', '2020-09-01'),
         ('2020-09-01', '2020-10-01'),
         ('2020-10-01', '2020-11-01'),
         ('2020-11-01', '2020-12-01'),
         ('2020-12-01', '2021-01-01')]

# If you're accessing data from a server, fill in the credentials here.
PROJECT_PATH = 'outlier_detect'
DB = 'lwala'
POSTGRES_ADDRESS = 'rad-rds.cu1mtdz0xu2w.ap-south-1.rds.amazonaws.com'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'div_ai'
POSTGRES_PASSWORD = 'WeNXsteaDvNqtVL_@FZr7apywK!gT*'
POSTGRES_DBNAME = 'div_ai'
