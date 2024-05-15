import streamlit as st
import pandas as pd
import snowflake.connector

#if 'sf_params' in st.session_state:
#	session=Session.builder.configs(st.session_state.sf_params).create()

st.subheader(":robot_face: View All DORA Tests You Have Run in the Last 90 Days")
st.write("Click on column headings to sort. Use the drop list to filter the checks to just a single workshop.")
st.write("You can search the table of results by rolling your cursor over the header and choosing the magnifying lens symbol.")

if 'auth_status' not in st.session_state or st.session_state.auth_status == 'not_authed': 
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")

elif st.session_state.auth_status == 'authed':
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
         mw_choice = st.selectbox("Filter to show workshop records for:", ("DWW", "CMCW", "DABW", "DLKW", "DNGW" ))
         passed_valid = st.radio(
                            "Which tests do you want to see?",
                                ["All Tests", "Only Passed", "Only Passed & Valid"],
                            index=0,
         )

         st.write("You have chosen to see:", passed_valid)

        
         if mw_choice:
                if mw_choice == 'CMCW':
                     st.markdown(':blue[Remember that for tests CMCW10, CMCW11 and CMCW14, you must run them from your ACME Account, not your Main Account.]')

                all_my_tests_sql =  (f"select * "
                                    f"from AMAZING.APP.ALL_MY_TESTS where UNI_ID=trim('{st.session_state.uni_id}') "
                                    f"and badge_acro=trim('{mw_choice}')")
                cur.execute(all_my_tests_sql)
                all_my_tests_pd_df = cur.fetch_pandas_all()
		# all_my_tests_df = session.table("AMAZING.APP.ALL_MY_TESTS").filter((col('uni_id')== st.session_state.uni_id) & (col('badge_acro')== mw_choice))
                amt_rows = all_my_tests_pd_df.shape[0]
                # st.dataframe(all_my_tests_pd_df)
                        
                if amt_rows > 0:    
                        if passed_valid == "All Tests":
                                filtered_df = all_my_tests_pd_df
                        elif passed_valid == "Only Passed":
                                filtered_df = all_my_tests_pd_df[all_my_tests_pd_df["PASSED"] == True]
                        elif passed_valid == "Only Passed & Valid":
                                filtered_df = all_my_tests_pd_df[(all_my_tests_pd_df["PASSED"] == True) & (all_my_tests_pd_df["VALID"] == True)]
                        else:
                                filtered_df = all_my_tests_pd_df
                        st.dataframe(filtered_df
                                , column_order=["VALID","STEP","ACCOUNT_LOCATOR","PASSED", "DORA_TIMESTAMP", "LEARNER_SENT"]
                                , column_config={ 
                                 "VALID": "Check is Valid"        
                                , "STEP": "DORA Check #"
                                ,"ACCOUNT_LOCATOR": "Acct Loc"
                                , "PASSED": "Passed"
                                ,"DORA_TIMESTAMP": "Submission Date/Time"
                                ,"LEARNER_SENT": "Check Details"},    
                                hide_index=True,
                                height=900
                        )
         
                        st.write("NOTE: If no rows are loaded make sure you have created your LINK row correctly. The LINK row for each workshop must be ACCURATE before DORA checks can be shown. If you have confirmed your LINK row is accurate, consider whether the app may have timed out. Try logging in again if some time has passed (more than 15 minutes idle) since you first logged in.")

else: # not authed
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")                                        

