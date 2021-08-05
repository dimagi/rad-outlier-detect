# The name of the project.
PROJECT = 'crs'

# The name of the form to run the algorithm on.
# Ex. flu_check
FORMS = ['pregnancy_counsel']

# The user ID column in the form.
# ex. 'username'
FORM_USER_ID = 'username'

# A list of question IDs to avoid running the algorithm on.
# It is recommended to add metadata columns and non-categorical questions here. A few have been pre-added that are common metadata properties in CommCare.
# Ex. ['cough', 'pregancy_check']
COLUMNS_TO_AVOID = ['id', 'form.mobile_number', 'form.date_birth', 'received_on', 'formid', 'form.village_name', 'username', 'form.full_name', 'form_link', 'completed_time', 'started_time', 'form.fathers_name', 'form.date_abortion', 'form.date_still_birth', 'form.cur_count_b', 'form.date_maternal_death', 'form.days_until_next_visit', 'form.date_of_visit_42', 'form.date_of_visit_21', 'form.date_of_visit_28', 'form.date_last_visit', 'form.date_of_visit_3', 'form.date_of_visit_7', 'form.date_of_visit_14', 'form.prev_form_count', 'form.cur_form_count', 'form.baby_next_visit_date', 'form.block', 'form.time_repeat_baby', 'form.home_date_next_visit', 'form.date_of_visit_1', 'form.institutional_date_next_visit', 'form.lmp', 'form.edd', 'form.birth_registration_number', 'form.date_of_visit_1_home_visit', 'form.baby_name_proxy', 'case_name', 'form_name']

# Specify stard and end dates to filter form data by time.
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
PROJECT_PATH = 'public'
DB = 'lwala'
POSTGRES_ADDRESS = 'rad-rds.cu1mtdz0xu2w.ap-south-1.rds.amazonaws.com'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'div_ai'
POSTGRES_PASSWORD = 'WeNXsteaDvNqtVL_@FZr7apywK!gT*'
POSTGRES_DBNAME = 'div_ai'
