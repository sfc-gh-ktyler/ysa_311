import streamlit as st
import pandas as pd
import time
import snowflake.connector

#if 'sf_params' in st.session_state:
#	session = Session.builder.configs(st.session_state.sf_params).create()


if 'aid_legit' not in st.session_state:
   st.session_state.aid_legit = False
if 'al_legit' not in st.session_state:
   st.session_state.al_legit = False
if 'subform_toggle' not in st.session_state:
   st.session_state.subform_toggle = True #True is disabled
if 'subform_choice_title' not in st.session_state:
   st.session_state.subform_choice_title = ":red[Please Load or Create a Record to Edit by clicking button above]"

def reset_subform():
   st.session_state.subform_toggle = True #True is disabled
   # st.session_state['account_locator'] = None
   st.session_state.workshop_choice_title = ":grey[*Click Button to Load Workshop Record for Editing*]"

def validate_acct_loc(acct_loc):
   if acct_loc == None:
      st.markdown(":x: :red[This field cannot be blank]")
   elif len(acct_loc) < 7 or len(acct_loc) > 8:
      st.markdown(":x: :green[The ACCOUNT LOCATOR does not seem accurate. Please try again.]")
      st.session_state.aid_legit = False
   else: 
      st.markdown(":white_check_mark: :green[The ACCOUNT LOCATOR entered seems legit.]")
      st.session_state.aid_legit = True
      
def validate_acct_id(acct_id):
   if acct_id == None:
      st.markdown(":x: :red[This field cannot be blank]")
   elif len(acct_id) < 15 or len(acct_id) > 18:
      st.markdown(":x: :red[The ACCOUNT ID you entered does not seem accurate. Please try again.]")
      st.session_state.al_legit = False
   elif acct_id.find(".") < 0:
      st.markdown(":x: :red[The ACCOUNT ID does not seem accurate. Please try again.]")
      st.session_state.al_legit = False
   else: 
      st.markdown(":white_check_mark: :green[The ACCOUNT ID entered seems legit.]")
      st.session_state.al_legit = True

def validate_acme(acme_acct_loc):
   if acme_acct_loc is None:
      st.session_state.acme_legit = True
   elif acme_acct_loc =='':
      st.session_state.acme_legit = True   
   elif acme_acct_loc == 'ACME':
      st.markdown(':x: :red[Your ACME ACCOUNT LOCATOR is not "ACME", that is the Account NAME. Please try again.]')
   elif len(acme_acct_loc) < 7 or len(acme_acct_loc) > 8:
      st.markdown(":x: :red[Your ACME ACCOUNT LOCATOR does not seem accurate. Please try again.]")
      st.session_state.acme_legit = False
   else: 
      st.markdown(":white_check_mark: :green[The ACME ACCOUNT LOCATOR you entered seems legit.]")
      st.session_state.acme_legit = True


def get_workshop_info():   
   st.session_state.account_locator = ''
   st.session_state.account_identifier = ''
   st.session_state.acme_acct_loc = ''
   st.session_state.aid_legit = False
   st.session_state.al_legit = False
   st.session_state.acme_legit = False
   st.session_state.new_record = 'False'
   for_edits_sql =  (f"select organization_id ||\'.\'|| account_name as ACCOUNT_IDENTIFIER, account_locator, acme_acct_loc " 
                   f"from AMAZING.APP.USER_ACCOUNT_INFO_BY_COURSE where type = 'MAIN' "
                   f"and UNI_ID= trim('{st.session_state.uni_id}') and UNI_UUID=trim('{st.session_state.uni_uuid}') " 
                   f"and award_desc='{st.session_state.workshop_choice}'")
   # st.write(for_edits_sql)
   cur.execute(for_edits_sql)
   for_edits_pd_df = cur.fetch_pandas_all()
   for_edits_pd_df_rows = for_edits_pd_df.shape[0]

   # if the data row doesnt exist just seed it with blanks
   if for_edits_pd_df_rows == 1:
      st.session_state.new_record= 'False'
      if for_edits_pd_df['ACCOUNT_LOCATOR'].iloc[0] is not None:
         st.session_state['account_locator'] = for_edits_pd_df['ACCOUNT_LOCATOR'].iloc[0] 
      if for_edits_pd_df['ACCOUNT_IDENTIFIER'].iloc[0] is not None:
         st.session_state['account_identifier'] = for_edits_pd_df['ACCOUNT_IDENTIFIER'].iloc[0]  
      if for_edits_pd_df['ACME_ACCT_LOC'].iloc[0] is not None:
         st.session_state['acme_acct_loc'] = for_edits_pd_df['ACME_ACCT_LOC'].iloc[0]
   elif for_edits_pd_df_rows == 0:
      st.write('You have not previously entered account information for this workshop. Please add the information below.')
      st.session_state.new_record= 'True'
      st.session_state.edited_acme = '' # if a new record, it can't be acme so acme is blank
   else:
      st.write("there should only be 1 or zero rows.") 


st.subheader(":link: Add or Edit Trial Account LINK Rows for Workshops")
# drop list with option button for editing

if 'auth_status' not in st.session_state or st.session_state.auth_status == 'not_authed': 
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")
elif st.session_state.auth_status == 'authed':
# TOP FORM 
   #with st.form("select a workshop"):
   st.session_state.subform_toggle = False   #subform is open - not disabled
   st.session_state.workshop_choice =  st.selectbox("Choose Workshop/Badge want to enter/edit account info for:"
                                                      , ('<Choose a Workshop>','Badge 1: DWW', 'Badge 2: CMCW', 'Badge 3: DABW', 'Badge 4: DLKW', 'Badge 5: DNGW')
                                                      , key=1 , on_change=reset_subform())
   load_or_create = st.button("Load or Create Workshop Acct Info")
      
   if load_or_create:
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
         if st.session_state.workshop_choice == '<Choose a Workshop>':
            st.session_state.workshop_choice = ':red[NO WORKSHOP CHOSEN]'
            st.markdown(":red[Please choose a workskhop from the list before clicking the button.]")
            st.session_state.account_locator = ''
            st.session_state.account_identifier = ''
            st.session_state.subform_toggle = True #subform is disabled
         else:   
            st.session_state.workshop_choice_title = "Edit Trial Account Info for :blue[" + st.session_state.workshop_choice + "]"
            st.session_state.subform_toggle= False #subform can be edited
            get_workshop_info()
   st.markdown("----------")
   
   # SUBFORM
   with st.form("edit_acct_info"):
      st.markdown("**" + st.session_state.workshop_choice_title + "**")
      edited_acct_id = st.text_input("Enter Your Account Identifier as found in your Snowflake Account:", st.session_state.account_identifier, disabled=st.session_state.subform_toggle)
      edited_acct_loc = st.text_input("Enter Your Account Locator as found in your Snowflake Account:", st.session_state.account_locator, disabled=st.session_state.subform_toggle)
      edited_acme = None
      # this section just controls whether the ACME field is showing
      # this is for people who come back to edit their entry prior to creating the ACME account and might
      # be confused by the extra field -- we have to show it, but we also let them know it's okay not to fill it in
      if st.session_state.workshop_choice == 'Badge 2: CMCW' and st.session_state.new_record == 'False':
         edited_acme = st.text_input("ACME Account Locator:",st.session_state.acme_acct_loc)
         st.markdown(":gray[*ACME entry should be blank until after Lesson 4 when you set up the ACME account.*]")
      submit_button = st.form_submit_button("Update Trial Account Info", disabled=st.session_state.subform_toggle)

      if submit_button: 
         cnx = snowflake.connector.connect(
                                        user = st.session_state.sf_user,
                                        password = st.session_state.sf_pwd,
                                        account = st.session_state.sf_acct,
                                        database = st.session_state.sf_db,
                                        warehouse = st.session_state.sf_wh,
                                        role = st.session_state.sf_role,
                                        schema = st.session_state.sf_schema)
         cur = cnx.cursor()
         if st.session_state.workshop_choice != '<Choose a Workshop>' and st.session_state.workshop_choice != ':red[NO WORKSHOP CHOSEN]':
            validate_acct_id(edited_acct_id)
            validate_acct_loc(edited_acct_loc)
            
            # this section controls what happens after submission - it is designed to accept a blank acme field 
            # or validate it if its not blank (and reassure that being blank is okay
            if st.session_state.workshop_choice == 'Badge 2: CMCW' and st.session_state.new_record == 'False':
               validate_acme(edited_acme)  
               st.markdown("*ACME entry should be blank until after Lesson 4 when you set up the ACME account.*")

            # this section is after both the main entries have been validated 
            if st.session_state.al_legit == True and st.session_state.aid_legit==True:
               st.session_state.edited_acct_id = edited_acct_id

               st.session_state.edited_acct_loc = edited_acct_loc
               validate_acme(edited_acme)
               
               if st.session_state.workshop_choice == 'Badge 2: CMCW' and st.session_state.acme_legit == True and st.session_state.new_record == 'False':
                  update_sql = (f"call AMAZING.APP.CMCW_UPDATE_ACCT_INFO_SP('{st.session_state.uni_id}','{st.session_state.uni_uuid}',"
                                f" '{edited_acct_id}','{edited_acct_loc}','{edited_acme}')")
                  st.write(update_sql)
                  cur.execute(update_sql)
                  # session.call('AMAZING.APP.CMCW_UPDATE_ACCT_INFO_SP', st.session_state.uni_id, st.session_state.uni_uuid, 
                  # edited_acct_id, edited_acct_loc, edited_acme)
                  st.success('Snowflake Trial Account Workshop Data Updated', icon='🚀')
               else:   
                  update_sql = (f"call AMAZING.APP.ADD_ACCT_INFO_SP('{st.session_state.new_record}','{st.session_state.uni_id}','{st.session_state.uni_uuid}',"
                                f" '{st.session_state.workshop_choice}','{edited_acct_id}','{edited_acct_loc}','MAIN')")
                  # st.write(update_sql)
                  cur.execute(update_sql)
                  st.success('Snowflake Trial Account Workshop Data Updated', icon='🚀')
               
               if st.session_state.al_legit == True and st.session_state.aid_legit==True and st.session_state.acme_legit==True:
                  time.sleep(2)
                  st.session_state.account_locator = ''
                  st.session_state.account_identifier = ''
                  st.switch_page("pages/3_⛓️_View_All_Trial_Acct_Info.py")

else: # not authed
   st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")

st.markdown('-------')
st.subheader('How to find your Trial Account Information:')
st.image('https://learn.snowflake.com/asset-v1:snowflake+X+X+type@asset+block@dil_1.png','Finding your Account ID')
st.image('https://learn.snowflake.com/asset-v1:snowflake+X+X+type@asset+block@dil_3.png','Finding your Account Locator')




