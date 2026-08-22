import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Cricket League Manager",
    page_icon="🏏",
    layout="wide"
)

# 2. Application Title & Header
st.title("🏏 Cricket League Dashboard & Manager")
st.write("Track your cricket tournament standings, add match scores, and analyze team statistics live.")

# 3. Session State Initialization (Acts as a temporary database)
if 'teams' not in st.session_state:
    st.session_state.teams = {
        'Mumbai Titans': {'Played': 5, 'Won': 4, 'Lost': 1, 'Points': 8, 'NRR': 1.25},
        'Delhi Capitals': {'Played': 5, 'Won': 3, 'Lost': 2, 'Points': 6, 'NRR': 0.45},
        'Bangalore Strikers': {'Played': 5, 'Won': 2, 'Lost': 3, 'Points': 4, 'NRR': -0.12},
        'Chennai Kings': {'Played': 5, 'Won': 1, 'Lost': 4, 'Points': 2, 'NRR': -1.58}
    }

if 'top_scorers' not in st.session_state:
    st.session_state.top_scorers = pd.DataFrame({
        'Player': ['Rohit Sharma', 'Virat Kohli', 'Rishabh Pant', 'MS Dhoni', 'Suryakumar Yadav'],
        'Team': ['Mumbai Titans', 'Bangalore Strikers', 'Delhi Capitals', 'Chennai Kings', 'Mumbai Titans'],
        'Runs': [245, 310, 198, 145, 215],
        'Strike Rate': [142.3, 135.5, 155.2, 160.0, 168.4]
    })

# 4. Sidebar Controls for Adding Dynamic Matches
st.sidebar.header("🕹️ Match Result Logger")
team_list = list(st.session_state.teams.keys())

winner = st.sidebar.selectbox("Select Winner Team", team_list)
loser = st.sidebar.selectbox("Select Loser Team", team_list)

if st.sidebar.button("Update League Table"):
    if winner == loser:
        st.sidebar.error("Error: Winner and Loser teams cannot be the same!")
    else:
        # Update Winner Stats
        st.session_state.teams[winner]['Played'] += 1
        st.session_state.teams[winner]['Won'] += 1
        st.session_state.teams[winner]['Points'] += 2
        
        # Update Loser Stats
        st.session_state.teams[loser]['Played'] += 1
        st.session_state.teams[loser]['Lost'] += 1
        
        st.sidebar.success(f"Successfully recorded: {winner} beat {loser}!")

# 5. Core Layout Split into Tabs
tab1, tab2, tab3 = st.tabs(["📊 Standings & Points Table", "🔥 Top Batsmen Tracker", "📈 Performance Analytics"])

with tab1:
    st.header("Current League Standings")
    # Convert data dictionary to Pandas Dataframe and sort by Points
    df_standings = pd.DataFrame.from_dict(st.session_state.teams, orient='index').reset_index()
    df_standings.rename(columns={'index': 'Team Name'}, inplace=True)
    df_standings = df_standings.sort_values(by=['Points', 'NRR'], ascending=False).reset_index(drop=True)
    
    # Styled tabular UI output - use color_gradient instead of style
    st.dataframe(df_standings, use_container_width=True)

with tab2:
    st.header("Orange Cap Leaderboard (Most Runs)")
    st.dataframe(st.session_state.top_scorers.sort_values(by='Runs', ascending=False).reset_index(drop=True), use_container_width=True)
    
    # Form layout wrapper to update player scores safely
    st.subheader("🏏 Update/Add Player Performance Data")
    with st.form("player_form", clear_on_submit=True):
        p_name = st.text_input("Player Name")
        p_team = st.selectbox("Player Team", team_list)
        p_runs = st.number_input("Runs Scored", min_value=0, step=1)
        p_sr = st.number_input("Strike Rate During Match", min_value=0.0, max_value=600.0, step=0.1)
        
        submit_player = st.form_submit_button("Submit Statistics")
        if submit_player and p_name:
            new_row = pd.DataFrame({'Player': [p_name], 'Team': [p_team], 'Runs': [int(p_runs)], 'Strike Rate': [p_sr]})
            st.session_state.top_scorers = pd.concat([st.session_state.top_scorers, new_row], ignore_index=True)
            st.rerun()

with tab3:
    st.header("Visual Analytics Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team Breakdown by Total Points Earned")
        df_standings = pd.DataFrame.from_dict(st.session_state.teams, orient='index').reset_index()
        fig_points = px.bar(df_standings, x='index', y='Points', color='index', 
                            labels={'index': 'Teams', 'Points': 'League Points'},
                            title="Total Points by Team")
        st.plotly_chart(fig_points, use_container_width=True)
        
    with col2:
        st.subheader("Runs vs Strike Rate Distribution")
        fig_scatter = px.scatter(st.session_state.top_scorers, x='Runs', y='Strike Rate',
                                 hover_name='Player', color='Team', size='Runs',
                                 title="Batsmen Efficiency Matrix")
        st.plotly_chart(fig_scatter, use_container_width=True)
