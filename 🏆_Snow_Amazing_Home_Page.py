import streamlit as st
import pandas as pd
import boto3
import json
import botocore
from botocore.exceptions import ClientError
import snowflake.connector
import time

st.set_page_config(
		page_title="You\'re Snow Amazing! Badge Mgmt",
		page_icon= "🏆"
)

# st.write('defining the creds function')
st.image('https://learn.snowflake.com/asset-v1:snowflake+X+X+type@asset+block@snow_amazing_banner.png')

def get_secret():
	client_config = botocore.config.Config(
    		max_pool_connections=15,
	)

	# Create a Secrets Manager client
	boto_session = boto3.session.Session()
	client = boto_session.client(
	service_name='secretsmanager',
	region_name='us-east-1',
	config=client_config
	)
	try:
		get_secret_value_response = client.get_secret_value(SecretId='amazing_app_sherpa_connection')

		secret = json.loads(get_secret_value_response['SecretString'])

                #global connection_parameters

		account = str(secret['account'])
		user= str(secret['user'])
		password=str(secret['password'])
		role = str(secret['role'])
		warehouse = str(secret['warehouse'])
		database = str(secret['database'])
		schema = str(secret['schema'])

		connection_parameters = {
                        "account": account,
                        "user": user,
                        "password": password,
                        "role": role,
                        "warehouse": warehouse,
                        "database": database,
                        "schema": schema
		}

		st.session_state['sf_params'] = connection_parameters

		st.session_state['sf_acct']= account
		st.session_state['sf_user'] =user 
		st.session_state['sf_pwd']=password
		st.session_state['sf_role']=role
		st.session_state['sf_wh']=warehouse
		st.session_state['sf_db']=database
		st.session_state['sf_schema']=schema
		
	except ClientError as e:
		raise e


get_secret()


if 'auth_status' not in st.session_state:
	st.session_state['auth_status'] = 'not_authed'

def initialize_user_info():   # session is open but not authed
	# st.session_state['sf_params'] = None
	st.session_state['auth_status'] = 'not_authed'
	# all profile fields get set back to nothing
	st.session_state['given_name'] = ''
	st.session_state['middle_name'] = ''
	st.session_state['family_name'] = ''
	st.session_state['badge_email'] = ''
	st.session_state['display_name'] = ''
	st.session_state['display_format'] = ''
	st.session_state['display_name_flag'] = 'False'
	# workshop/account fields are set back to nothing 
	st.session_state['workshop_choice'] = '' 
	st.session_state['account_locator'] = ''
	st.session_state['account_identifier'] = ''
	st.session_state['new_record'] = False
	st.session_state['edited_acct_loc'] =''
	st.session_state['edited_acct_id'] =''

def get_user_profile_info():
	#start over with authentication and populating vars
	this_user_sql =  (f"select badge_given_name, badge_middle_name, badge_family_name, display_name, display_format, badge_email "
       			f"from UNI_USER_BADGENAME_BADGEEMAIL where UNI_ID=trim('{st.session_state.uni_id}') "
                	f"and UNI_UUID=trim('{st.session_state.uni_uuid}')")
	cur.execute(this_user_sql)
	user_results_pd_df = cur.fetch_pandas_all()
	
	user_rows = user_results_pd_df.shape[0]

	if user_rows>=1:
		# if at least one row was found then the key must have been correct so we consider the user authorized
		st.session_state['auth_status'] = 'authed'

		# 1 row found means the UNI_ID is legit and can be used to look up other information
		# all user vars need to be checked to make sure they aren't empty before we set session vars

		if user_results_pd_df['BADGE_GIVEN_NAME'].iloc[0] is not None:
        		st.session_state['given_name'] = user_results_pd_df['BADGE_GIVEN_NAME'].iloc[0]

		if user_results_pd_df['BADGE_MIDDLE_NAME'].iloc[0] is not None:
        		st.session_state['middle_name'] = user_results_pd_df['BADGE_MIDDLE_NAME'].iloc[0]

		if user_results_pd_df['BADGE_FAMILY_NAME'].iloc[0] is not None:
        		st.session_state['family_name'] = user_results_pd_df['BADGE_FAMILY_NAME'].iloc[0]

		if user_results_pd_df['BADGE_EMAIL'].iloc[0] is not None:
         		st.session_state['badge_email'] = user_results_pd_df['BADGE_EMAIL'].iloc[0]

		if user_results_pd_df['DISPLAY_NAME'].iloc[0] is not None:
			st.session_state['display_name'] = user_results_pd_df['DISPLAY_NAME'].iloc[0]
			st.session_state['display_name_flag'] = 'True'
		else:
			st.session_state['display_name'] = "Please go to the :star: page to generate a DISPLAY NAME for your badge(s)."
			st.session_state['display_name_flag'] = "False"

		#if user_results_pd_df['display_format'] is not None:
		st.session_state['display_format'] = str(user_results_pd_df['DISPLAY_FORMAT'].iloc[0])
	else: # no rows returned
		st.markdown(":red[There is no record of the UNI_ID/UUID combination you entered. Please double-check the info you entered.] ")
		st.markdown(":red[A common mistake is to introduce extra characters during the copy/paste process. Please make sure no extra characters are included]")


with st.sidebar:
	st.sidebar.header("User")
	uni_id = st.text_input('Enter your learn.snowflake.com UNI ID:')
	uni_uuid = st.text_input('Enter the secret UUID displayed on the DORA is Listening Page of any Workshop:')
	find_my_uni_record = st.button("Find my UNI User Info")
	# st.session_state

# Page Header
st.header('You\'re Snow Amazing!')
st.write('Welcome to the learn.snowflake.com Workshop Badge Management app!')
st.write('Using this app you can manage your badge name and email and you can view your results.')


if find_my_uni_record:
	# reset all session vars
	initialize_user_info()


	# Set uni_id and key to entries on form
	st.session_state['uni_id'] = uni_id.strip()
	st.session_state['uni_uuid'] = uni_uuid.strip()

	# session = Session.builder.configs(st.session_state.sf_params).create()    
	cnx = snowflake.connector.connect(
					user = st.session_state.sf_user,
					password = st.session_state.sf_pwd,
					account = st.session_state.sf_acct,
					database = st.session_state.sf_db,
					warehouse = st.session_state.sf_wh,
					role = st.session_state.sf_role,
					schema = st.session_state.sf_schema,
                                        insecure_mode=True
        )
	cur = cnx.cursor()
	# this will query the db and if finds a match will populate profile vars
	get_user_profile_info()


if st.session_state.auth_status == 'authed':
	# st.write(st.session_state.display_format)
	st.subheader("We Found You!")
	st.markdown("**GIVEN NAME:** " + st.session_state.given_name)
	st.markdown("**MIDDLE/ALTERNATE NAME:** "+ st.session_state.middle_name) 
	st.markdown("**FAMILY NAME:** " + st.session_state.family_name)
	st.markdown("**EMAIL:** " + st.session_state.badge_email)
	if st.session_state.display_name_flag != "False":
		st.markdown("**Name Will Display on Badge as:** :green[" + st.session_state.display_name + "]")
	else:
		md_str =  "**Name Will Display on Badge As:** :red[" + st.session_state.display_name + "]"       
		st.markdown(md_str)
		st.write("-----")
		st.markdown("*If your display name has not been generated, or you would like to make changes to your name, email, or display name, go to the :pencil2: page and make edits there.")
		# time.sleep(1500)
		# st.session_state.auth_status = 'not_authed'
else:
   	st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar.]")
