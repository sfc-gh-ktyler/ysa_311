import streamlit as st
import pandas as pd
import snowflake.connector
import time

#if 'sf_pwd' in st.session_state:
#	st.write('Still logged in')
	#session = Session.builder.configs(st.session_state.sf_params).create()

def get_user_profile_info():
	#start over with authentication and populating vars
	this_user_sql =  (f"select badge_given_name, badge_middle_name, badge_family_name, display_name, badge_email "
			f"from UNI_USER_BADGENAME_BADGEEMAIL where UNI_ID=trim('{st.session_state.uni_id}') "
			f"and UNI_UUID=trim('{st.session_state.uni_uuid}')")
	cur.execute(this_user_sql)
	user_results_pd_df = cur.fetch_pandas_all()
	user_rows = user_results_pd_df.shape[0]

	if user_rows>=1:
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
		else:
			st.session_state['display_name'] = "PLEASE GO TO THE DISPLAY NAME TAB TO GENERATE A DISPLAY NAME FOR YOUR BADGE"
			st.dataframe(user_results_pd_df)
	else: # no rows returned
		st.markdown(":red[There is no record of the UNI_ID/UUID combination you entered. Please double-check the info you entered, check the FAQs tab below for tips on FINDING YOUR INFO, and try again]") 

####################### PAGE CONTENTS ###########
st.subheader(":pencil2: Edit your Badge Name or Badge Email")
st.write("Please use any characters or alphabet you would like. This app can accept all accented characters and alphabets!")
if 'auth_status' not in st.session_state or st.session_state.auth_status == 'not_authed': 
	st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")
elif st.session_state.auth_status == 'authed':
	with st.form("badge_name_and_email"):
		st.write("Confirm Your Name for Any Badges That Might Be Issued")     
		edited_given = st.text_input("Given Name (Name used to greet you)", st.session_state.given_name)
		edited_middle = st.text_input('Middle Name/Nickname/Alternate-Spelling (Optional)', st.session_state.middle_name)
		edited_family = st.text_input('Family Name', st.session_state.family_name)
		edited_email = st.text_input("The Email Address You Want Your Badge Sent To (does not have to match UNI, Snowflake Trial, or Work):", st.session_state.badge_email)
		submit_edits = st.form_submit_button("Update My Badge Name & Badge Email")  

	if submit_edits:
		try:
			cnx = snowflake.connector.connect(
                                        user = st.session_state.sf_user,
                                        password = st.session_state.sf_pwd,
                                        account = st.session_state.sf_acct,
                                        database = st.session_state.sf_db,
                                        warehouse = st.session_state.sf_wh,
                                        role = st.session_state.sf_role,
                                        schema = st.session_state.sf_schema,
                                        insecure_mode = True
			)
			cur = cnx.cursor()
			this_update_sql = (f"call AMAZING.APP.UPDATE_BADGENAME_BADGEEMAIL_SP('{st.session_state.uni_id}','{st.session_state.uni_uuid}',"
					f"'{edited_given}', '{edited_middle}', '{edited_family}',"
					f"'{edited_email}')")
			# st.write(this_update_sql)
			cur.execute(this_update_sql)

			get_user_profile_info() 
			st.success('Badge Name & Email Updated', icon='🚀')
		except:
			st.error('Something went wrong. Please check your entries and try again.')
		time.sleep(3)
		cur.close()
		# st.switch_page("🏆_Snow_Amazing_Home_Page")

