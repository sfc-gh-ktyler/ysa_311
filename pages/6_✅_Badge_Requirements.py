import streamlit as st
import time
import snowflake.connector

#if 'sf_params' in st.session_state:
#	session=Session.builder.configs(st.session_state.sf_params).create()

if "current_interest" not in st.session_state:
   st.session_state['current_interest']='DWW'

def update_3_and_4():
   time.wait(2)

def get_user_workshop_acct_info():
   # get a table of all the entries this user has made
   workshop_sql =  (f"select award_desc, ACCOUNT_IDENTIFIER, account_locator " 
                     f"from AMAZING.APP.USER_LINK_ROWS where UNI_ID=trim('{st.session_state.uni_id}') " 
                     f"and UNI_UUID=trim('{st.session_state.uni_uuid}') and award_desc like '%" + st.session_state.current_interest+ "%' ") 
   cur.execute(workshop_sql)
   workshop_results = cur.fetch_pandas_all()
   row_exists = workshop_results.shape[0]
   if row_exists == 0:
      st.session_state.link_row_exists = False
      emoji_3 = ":x:"
      label_3 = ":red[Please create a link row for this workshop that will tie your Snowflake Trial to your learning account.]"
   else: 
      # user_results_pd_df['BADGE_FAMILY_NAME'].iloc[0]
      if workshop_results['ACCOUNT_IDENTIFIER'].iloc[0] is None:
         emoji_3 = ":x:"
         label_3 = (":red[Please enter the Account Identifier of your Snowflake Trial Account in the Link Row for this workshop.]")
      else:
         if workshop_results['ACCOUNT_LOCATOR'].iloc[0] is None:
            emoji_3 = ":x:"
            label_3 = (":red[Please enter the Account Locator of your Snowflake Trial Account in the Link Row for this workshop.]")
         else: 
            st.session_state.link_row_exists = True
            emoji_3 = ":white_check_mark:"
            label_3 = "Your link row for " + st.session_state.current_interest + " seems complete and up to date."
   st.markdown(emoji_3 + " **STEP 3:** For EVERY BADGE you hope to receive, you will need to see a row on the :chains: page.")
   st.markdown(label_3)
   st.write("Your Link row for " + st.session_state.current_interest+ ":")
   st.dataframe(workshop_results, hide_index=True, use_container_width=True)
   st.markdown("To create or edit the info on the :chains: page, use the :link: page. Without this LINK established for each badge, DORA does not know who is doing the work so she cannot issue the badge.")         
   st.markdown("Every badge entry on the :chains: page should have both Account Locator and Account ID field completed.")
   st.markdown("")
   st.markdown("*Some older entries where you have already received your badge may have empty values. That is okay for older badges but for NEW badges, ALL columns MUST be complete.*")
   st.markdown('---------------------')

   missing_sql =  (f"select step, max(account_locator) as note from "
                  f"(select badge_acro, step, '***MISSING TEST - SKIPPED, FAILED, OR INVALIDATED***' as account_locator "
                  f"from amazing.app.step_master_list where badge_acro = '{st.session_state.current_interest}' "
                  f"union select badge_acro, step, account_locator from amazing.app.all_my_tests "
                  f"where badge_acro = '{st.session_state.current_interest}' and uni_id = '{st.session_state.uni_id}' "
                  f"and valid = True and passed = True) sub group by badge_acro, step "
                  f"having max(account_locator) like '%***%' order by step; "
                  )
   cur.execute(missing_sql)
   missing_results = cur.fetch_pandas_all()
   missing_rows = missing_results.shape[0]
   if missing_rows > 6:
      emoji_4 = ":x:"
      label_4 = ":red[You are missing more than 6 DORA checks. There are some common issues that cause you to be missing so many tests. #1 - You entered the WRONG ACCOUNT LOCATOR in your Link row. #2- Your tests are older than 90 days. #3 - You haven't run any DORA checks or you are running them incorrectly (leaving off the green grader line).]"
   elif missing_rows > 0 and missing_rows <7:
      emoji_4 = ":x:"
      label_4 = ":red[Please correct any issues with tests that are causing them to fail or be marked INVALID.]"
   else: 
      emoji_4 = ":white_check_mark:"
      label_4 = ":green[Your Lab Work seems to be complete.]"
   st.markdown(emoji_4 + " **STEP 4:** For EVERY BADGE you hope to recieve, you need to complete every DORA check and see both PASSED and VALID for that test.") 
   st.write(label_4)
   if missing_rows > 0:
      st.dataframe(missing_results, hide_index=True, use_container_width=True)






st.subheader(":white_check_mark: Badge Requirements")
st.write("Please check the requirements listed on this page to make sure you have completed every needed step. FIX YOUR ISSUES before asking for help.")

# st.write("*This app is new as of April 9th, 2024. You may have used other methods to get badges in the past. The concepts are the same but the methods have changed.*")
st.markdown('----------')

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
   if st.session_state.display_name is None:
     emoji_1 = ":x:"  
   else:
     emoji_1 = ":white_check_mark:"
     label_1 =  "**YOUR NAME:** :blue[ " + st.session_state.given_name + " " + st.session_state.middle_name + " " + st.session_state.family_name +"]"
     label_1a = "**BADGE WILL BE SENT TO:**  :blue[ " + st.session_state.badge_email + "]"
	
   st.markdown(emoji_1 + " **STEP 1:** Tell us your name and email. We start with your Community profile information but you can make changes.") 
   st.markdown(label_1)
   st.markdown(label_1a)
   st.markdown("*Edit these on the :pencil2:  page and the :star: page.*") 

   st.markdown('----------')


   if "DISPLAY NAME" in st.session_state.display_name:
     emoji_2 = ":x:"
     label_2 = ":red[YOU HAVE NOT GENERATED A DISPLAY NAME FOR YOUR BADGE]"
   else:
     emoji_2 = ":white_check_mark:"
     label_2 = "**YOU CHOSE DISPLAY NAME:** :green[ " + st.session_state.display_name + "]"
  
   st.markdown(emoji_2 + " **STEP 2:** Generate a Display Name. :green[(This is NEW!)]") 
   st.markdown(label_2)
   st.markdown("*The Display Name feature gives you full control over how your name is displayed on any badge that is issued. This is done on the :star: page.*") 
   st.markdown("")
   
   st.markdown('------------')

   st.subheader("Repeat Steps 3 & 4 For EVERY NEW BADGE You Pursue")
   with st.form("current_workshop_interest"):
      st.session_state.current_interest=st.selectbox("I want to check my status for:"
                                 , ("DWW","CMCW", "DABW", "DLKW", "DNGW")
                                 )
      workshop_chosen = st.form_submit_button("Load Info on My Chosen Workshop")
   st.markdown('---------------------')

   # SECTIONS FOR STEPS 3 & 4 ARE GENERATED BY FUNCTION - driven by form choice
   get_user_workshop_acct_info()
   
   # st.write(":blue[THIS SECTION IS STILL UNDER CONSTRUCTION. WE WILL HAVE INTERACTIVE FEEDBACK BY APRIL 30, 2024. PLEASE CHECK BACK.]")
   # st.markdown(":blue[To check this for yourself look for test 1, then look for test 2, then 3. 4, 5,6...all the way through till the end. Make sure no tests are missing.]")
   st.markdown(":blue[If you find that one of your tests is missing, be sure to run the DORA check until it passes at least once.]")
   st.markdown("*View your tests on the :robot_face: page. Filter down to PASSED and VALID. These are the only tests DORA considers.*")
   st.markdown("*A test that PASSED but IS NOT VALID is a test that was CHANGED BY YOU.DO NOT CHANGE TESTS.*")
   st.markdown("*You can FAIL any or all tests many times as long as you pass each test at least one time (and it is valid). When each test has at least one VALID/PASSED entry you can receive your badge.*")

   st.markdown('---------------------')

   st.subheader("More Troubleshooting Tips")
   st.markdown("Did you make one of these common mistakes?")
   st.markdown(":no_entry_sign:  Have you received this badge already? We check the UNI ID before issueing. We don't issue twice to the same UNI ID.")
   st.markdown(":no_entry_sign:  Has someone using the same Snowflake Trial Account already received the badge? We don't issue twice on the same Trial Account.")
   st.markdown(":no_entry_sign:  Did mis-spell your email? It happens so often. If you did this, you'll have to file a ticket to get it corrected.")
   cur.close()  
else:
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")

