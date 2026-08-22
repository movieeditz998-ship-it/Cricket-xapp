import streamlit as st
import random
import time

st.set_page_config(page_title="Cricket Game Prototype", layout="wide")

LANG_MAP = {
    'English': 'en',
    'Hindi': 'hi',
    'Kannada': 'kn'
}

# Utilities
def simple_commentary(lang, event, player=None, runs=None, over_ball=None, team=None):
    if lang == 'English':
        if event == 'start':
            return f"Match started. {team} batting. Overs: {overs_selected}"
        if event == 'ball':
            if runs == 0:
                return f"{over_ball}: Dot ball from {player}."
            if runs == 1:
                return f"{over_ball}: Single for {player}."
            if runs == 2:
                return f"{over_ball}: Two runs by {player}."
            if runs == 3:
                return f"{over_ball}: Three runs! {player} runs well."
            if runs == 4:
                return f"{over_ball}: FOUR! {player} clears the ropes." 
            if runs == 6:
                return f"{over_ball}: SIX! Massive hit by {player}."
        if event == 'wicket':
            return f"{over_ball}: WICKET! {player} is out."
        if event == 'wide':
            return f"{over_ball}: Wide ball."
        if event == 'bye':
            return f"{over_ball}: Bye."
    elif lang == 'Hindi':
        if event == 'start':
            return f"मैच शुरू हुआ। {team} बल्लेबाजी कर रहा है। ओवर: {overs_selected}"
        if event == 'ball':
            if runs == 0:
                return f"{over_ball}: डॉट गेंद {player} से।"
            if runs == 4:
                return f"{over_ball}: चौका! {player} ने बेहतरीन शॉट मारा।"
            if runs == 6:
                return f"{over_ball}: छक्का! भारी शॉट {player} द्वारा।"
        if event == 'wicket':
            return f"{over_ball}: विकेट! {player} आउट।"
    else:  # Kannada (simple templates)
        if event == 'start':
            return f"ಮ್ಯಾಚ್ ಪ್ರಾರಂಭವಾಗಿದೆ. {team} ಬ್ಯಾಟಿಂಗ್. ಓವರ್‌ಗಳು: {overs_selected}"
        if event == 'ball':
            if runs == 4:
                return f"{over_ball}: ಫೋರ್! {player} ಚೆನ್ನಾಗಿ ಹಿಟ್ ಮಾಡಿದರು."
            if runs == 6:
                return f"{over_ball}: ಸಿಕ್ಸ್! ಭಾರೀ ಹಿಟ್ {player}."
        if event == 'wicket':
            return f"{over_ball}: ವಿಕೆಟ್! {player} ಔಟ್." 
    return ""

# Simple ball outcome generator influenced by pitch and rain
def ball_outcome(pitch, rain_chance):
    # base probabilities
    # returns: ('runs', runs or None, 'type') types: run, wicket, wide, bye
    r = random.random()
    # adjust factors
    pitch_factor = {'dry': 0.05, 'green': 0.12, 'good': 0.08}
    rain_factor = rain_chance / 100.0
    wicket_prob = 0.05 + pitch_factor.get(pitch, 0.08) + rain_factor*0.03
    wide_prob = 0.02 + rain_factor*0.01
    bye_prob = 0.01 + rain_factor*0.01
    # runs probabilities
    if r < wicket_prob:
        return ('wicket', None, 'wicket')
    r -= wicket_prob
    if r < wide_prob:
        return ('wide', 1, 'wide')
    r -= wide_prob
    if r < bye_prob:
        return ('bye', 1, 'bye')
    r -= bye_prob
    # runs outcome
    # heavier rain and green pitch lower boundary hitting
    run_scale = max(0.5, 1.0 - rain_factor*0.6)
    # probabilities for 0,1,2,3,4,6
    probs = [0.25*run_scale, 0.45*run_scale, 0.08, 0.02, 0.15*run_scale, 0.05*run_scale]
    # normalize
    s = sum(probs)
    probs = [p/s for p in probs]
    choice = random.choices([0,1,2,3,4,6], probs)[0]
    return ('run', choice, 'run')

# Simple match simulator
def simulate_innings(batting_team, bowling_team, overs, pitch, rain_chance, lang):
    total_balls = overs * 6
    score = 0
    wickets = 0
    ball_no = 0
    commentary = []
    batsmen = batting_team['playing_XI']
    striker_idx = 0
    non_striker_idx = 1
    next_batsman = 2
    current_over = 0
    while ball_no < total_balls and wickets < 10:
        ball_no += 1
        over_ball = f"{(ball_no-1)//6}.{(ball_no-1)%6+1}"
        outcome_type, val, typ = ball_outcome(pitch, rain_chance)
        if outcome_type == 'wicket':
            wickets += 1
            commentary.append(simple_commentary(lang, 'wicket', player=batsmen[striker_idx], over_ball=over_ball))
            # new batsman
            if next_batsman < len(batsmen):
                striker_idx = next_batsman
                next_batsman += 1
            else:
                break
        elif outcome_type == 'wide' or outcome_type == 'bye':
            score += val
            commentary.append(simple_commentary(lang, outcome_type, player=batsmen[striker_idx], over_ball=over_ball))
        elif outcome_type == 'run':
            runs = val
            score += runs
            commentary.append(simple_commentary(lang, 'ball', player=batsmen[striker_idx], runs=runs, over_ball=over_ball))
            if runs % 2 == 1:
                striker_idx, non_striker_idx = non_striker_idx, striker_idx
        # end of over swap
        if ball_no % 6 == 0:
            current_over += 1
            striker_idx, non_striker_idx = non_striker_idx, striker_idx
            commentary.append(f"End of over {current_over}. Score: {score}/{wickets}")
    return {'score': score, 'wickets': wickets, 'balls': ball_no, 'commentary': commentary}


st.title("🏏 Cricket Game Prototype (Branch: feature/match-simulator)")

# Left: Match setup
with st.sidebar:
    st.header("Match Setup")
    match_type = st.selectbox("Match Type", ['Quick Match', 'T20', 'ODI', 'Test (simplified)', 'IPL'])
    overs_opt = {'Quick Match':5, 'T20':20, 'ODI':50, 'Test (simplified)':90, 'IPL':20}
    overs_default = overs_opt.get(match_type, 5)
    overs_selected = st.selectbox("Overs", [2,5,10,20,50], index=[2,5,10,20,50].index(overs_default if overs_default in [2,5,10,20,50] else 5))
    rain_choice = st.selectbox("Rain Chance", ['0%','25%','50%','75%','90%'])
    rain_percent = int(rain_choice.replace('%',''))
    pitch = st.selectbox("Pitch Type", ['dry','green','good'])
    lang = st.selectbox("Commentary Language", list(LANG_MAP.keys()))
    autoplay = st.checkbox("Autoplay (simulate full match)", value=True)

# Create two example teams with 15 players
def default_team(name_prefix):
    return {
        'name': name_prefix,
        'squad': [f"{name_prefix} Player {i+1}" for i in range(15)],
        'playing_XI': [f"{name_prefix} Player {i+1}" for i in range(11)]
    }

team_a = default_team('TeamA')
team_b = default_team('TeamB')

col1, col2 = st.columns([1,1])
with col1:
    st.subheader('Home Team')
    team_a_name = st.text_input('Team A Name', value=team_a['name'])
    # allow picking playing XI
    players_a = st.multiselect('Select 11 players for Team A (from 15)', team_a['squad'], default=team_a['playing_XI'])
    if len(players_a) == 11:
        team_a['playing_XI'] = players_a
    else:
        st.info('Select exactly 11 players for Team A. Using default XI until 11 selected.')

with col2:
    st.subheader('Away Team')
    team_b_name = st.text_input('Team B Name', value=team_b['name'])
    players_b = st.multiselect('Select 11 players for Team B (from 15)', team_b['squad'], default=team_b['playing_XI'])
    if len(players_b) == 11:
        team_b['playing_XI'] = players_b
    else:
        st.info('Select exactly 11 players for Team B. Using default XI until 11 selected.')

# Start match
if st.button('Start Match'):
    st.session_state['match_running'] = True
    st.session_state['inning1'] = None
    st.session_state['inning2'] = None

if st.session_state.get('match_running'):
    st.markdown('### Inning 1: ' + team_a_name + ' batting')
    with st.spinner('Simulating innings...'):
        innings1 = simulate_innings({'playing_XI': team_a['playing_XI']}, {'playing_XI': team_b['playing_XI']}, overs_selected, pitch, rain_percent, lang)
        st.session_state['inning1'] = innings1
    st.success(f"End of Inning 1: {team_a_name} scored {innings1['score']}/{innings1['wickets']} in {innings1['balls']} balls")
    st.markdown('### Inning 2: ' + team_b_name + ' batting')
    with st.spinner('Simulating innings...'):
        innings2 = simulate_innings({'playing_XI': team_b['playing_XI']}, {'playing_XI': team_a['playing_XI']}, overs_selected, pitch, rain_percent, lang)
        st.session_state['inning2'] = innings2
    st.success(f"End of Inning 2: {team_b_name} scored {innings2['score']}/{innings2['wickets']} in {innings2['balls']} balls")

    # Show summary and commentary tabs
    if st.session_state.get('inning1') and st.session_state.get('inning2'):
        i1 = st.session_state['inning1']
        i2 = st.session_state['inning2']
        if i1['score'] > i2['score']:
            result_text = f"{team_a_name} won by {i1['score'] - i2['score']} runs"
        elif i2['score'] > i1['score']:
            remaining = 10 - i2['wickets']
            result_text = f"{team_b_name} won by { (overs_selected*6 - i2['balls'])//6 } overs and { (overs_selected*6 - i2['balls'])%6 } balls" if i2['score']>i1['score'] else 'Tie'
        else:
            result_text = 'Match tied'
        st.header('Match Result')
        st.write(result_text)

        tabc1, tabc2 = st.tabs(['Scorecard', 'Commentary'])
        with tabc1:
            st.subheader(team_a_name)
            st.write(f"Score: {i1['score']}/{i1['wickets']} in {i1['balls']} balls")
            st.subheader(team_b_name)
            st.write(f"Score: {i2['score']}/{i2['wickets']} in {i2['balls']} balls")
        with tabc2:
            st.subheader('Inning 1 Commentary')
            for c in i1['commentary']:
                st.write(c)
            st.subheader('Inning 2 Commentary')
            for c in i2['commentary']:
                st.write(c)

    st.session_state['match_running'] = False

st.markdown("---")
st.write("This is an early playable prototype pushed to branch feature/match-simulator. To play online, deploy the repo on Streamlit Community Cloud selecting the branch feature/match-simulator and the file app_game.py as the main file.")
