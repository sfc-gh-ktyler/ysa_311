import streamlit as st
import pandas as pd
import snowflake.connector


#if 'sf_params' in st.session_state:
#        session=Session.builder.configs(st.session_state.sf_params).create()

st.subheader(":sports_medal: View All Essentials Badges Earned By Your Uni ID")
st.write("Badges issued in the last 20 minutes may not yet be visible.")
st.write("If you do not see your badge here, please check the :white_check_mark: Badge Requirements page. It can help you troubleshoot.")

if 'auth_status' in st.session_state and st.session_state.auth_status == 'authed':
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
        all_my_badges_sql =  (f"select * from AMAZING.APP.BADGE_LOOKUP where UNI_ID=trim('{st.session_state.uni_id}')")
        cur.execute(all_my_badges_sql)
        all_my_badges_pd_df = cur.fetch_pandas_all()
	# st.dataframe(all_my_badges_pd_df)
        badge_rows = all_my_badges_pd_df.shape[0]

        if badge_rows > 0:                         
                st.dataframe(all_my_badges_pd_df
                                , column_order=["AWARD_ACRONYM","BADGE_URL","EMAIL","ISSUED_AT"]
                                , column_config={ 
                                "AWARD_ACRONYM": "Badge"       
                                ,"BADGE_URL": st.column_config.LinkColumn("Link to Badge")        
                                ,"EMAIL": "Email on Badge"
                                ,"ISSUED_AT": "Time/Date Issued"                                
                                },    
                                hide_index=True,
                                height=200
        )
        else:
                st.markdown(":red[Sorry, we do not show that you have earned any badges, yet]")

else: # not authed
        st.markdown(":red[Please sign in using your UNI_ID and UUID in the sidebar of the homepage.]")                                        

