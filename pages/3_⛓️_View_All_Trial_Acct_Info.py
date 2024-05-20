import streamlit as st
import pandas as pd
import snowflake.connector

#if 'sf_params' in st.session_state:
#	session = Session.builder.configs(st.session_state.sf_params).create()

def get_user_workshop_acct_info():
   # get a table of all the entries this user has made
   workshops_sql =  (f"select award_desc, ACCOUNT_IDENTIFIER, account_locator " 
                     f"from AMAZING.APP.USER_LINK_ROWS where UNI_ID=trim('{st.session_state.uni_id}') " 
                     f"and UNI_UUID=trim('{st.session_state.uni_uuid}')") 
   cur.execute(workshops_sql)
   workshops_results = cur.fetch_pandas_all()
   workshops_rows = workshops_results.shape[0]

   # show the entries
   if workshops_rows>=1:
       st.write("You have entered account info for the following badge workshops:")
       st.dataframe(workshops_results, hide_index=True)
   else:
      st.markdown(":blue[You have not created links for any badges, yet. Go to the next page to enter info about your Snowflake Trial Account.]")

st.subheader(":chains: View Trial Account Information You've Entered")
st.write("Entering your trial account information LINKS it to your work in learn.snowflake.com. Below are the links you have already created. Every badge workshop must have both Account ID information and Account Locator information. Please go to the :link: page to add information.")

if 'auth_status' not in st.session_state or st.session_state.auth_status == 'not_authed': 
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")

elif st.session_state.auth_status == 'authed':
   try:
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
     # display of info for all registered workshops
     get_user_workshop_acct_info()
     #st.dataframe(workshops_results, hide_index=True)
     st.markdown('----------')
     st.markdown(":red[**BOTH Acct ID and Acct Locator are required before any NEW badges can be issued. This information can be added on the :link: page.*]")
     st.markdown(":gray[**If you are pursuing a badge (for example DLKW) and there is not a row above for that badge (for example a row for DLKW) your badge cannot be issued.*]")
     st.markdown(":gray[**New badges require BOTH values, while past badges may NOT have required both values.*]")
     cur.close()
   except:
     st.error('Something went wrong. Try refreshing the browswer, or signing in again') 
else:
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")


