from __future__ import print_function
import pickle
import os.path
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import trueskill

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1tNLS0zec-WdHB0Ci3uTPY9Z2wIutwoj7UcKC6NXldxI'#ERICS: '1W_m-aqeXs3-rPIP561dKWw6Te1xZjDd6787ZmYyx00c'   #SAMPLE:'1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms' #
SAMPLE_RANGE_NAME = 'All Rated Games!D2:K' #'Class Data!A2:E'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        cols = ['Winner', 'Player1', 'Player2', 'Player3', 'Player4', 'Player5', 'Player6', 'Winner2']
        df = pd.DataFrame(values, columns = cols)
        print('Dataframe:\n%s' % df.head())
        df.to_csv('working.csv')
        # mu -> sigma, beta, tau ; recommendation by trueskill.org
        rec_sig_beta_tau = lambda mew: tuple([float(mew)/3.0, float(mew)/3.0/2.0, float(mew)/3.0])
        mu = 25
        sigma, beta, tau = rec_sig_beta_tau(mu)
        env = trueskill.TrueSkill(mu=mu, sigma=sigma, beta=beta, tau=tau, draw_probability=.75, backend='scipy')
        player_to_skill = get_true_skills(df)
        data = [(k, v.mu, v.sigma) for k, v in player_to_skill.items()]
        skills_df = pd.DataFrame(data, columns = ['Player', 'mu', 'sigma'])
        skills_df['TrueSkill'] = skills_df['mu'] - 3*skills_df['sigma'] # Definition of TrueSkill (used for leaderboards): 99% likelihood your skill is > this
        
        # Pretty up results
        skills_df.sort_values(by = ['TrueSkill', 'mu'], ascending = False, inplace = True)
        skills_df.reset_index(inplace = True)
        skills_df.index = skills_df.index + 1
        skills_df.index.name = 'Leaderboard Position'
        skills_df.to_csv('skills.csv', columns = ['Player', 'TrueSkill', 'mu', 'sigma'])

def get_true_skills(df, env = None):
    """Return true skills of all players in df.

    args:
        df (pd.DataFrame): games x [Winner, Player1, Player2,...,Playern, Winner2] dataframe
    """
    is_valid_player = lambda x: str(x) != 'nan' and str(x)
    if env is None:
        env = trueskill.TrueSkill()
    player_to_rating = dict([(player, trueskill.Rating()) for player in set(df.values.flatten())])
    for row_num, s in df.iterrows():
        players = [s['Player%d' % i] for i in range(1,7)]
        players = [player for player in players if is_valid_player(player)]
        try:
            if not is_valid_player(s['Winner']):
                raise ValueError
            winner_idx = players.index(s['Winner'])
        except ValueError:
            print('Game %d\'s winner is not a Player!' % row_num)
            continue
        if is_valid_player(s['Winner2']):
            ranks = [2 for i in players] # Losers!
            try:
                ranks[players.index(s['Winner2'])] = 1 # 2nd place!
            except:
                print('Game %d\'s 2nd winner is not a Player!' % row_num)
                continue
        else:
            ranks = [1 for i in players] # Losers!
        ranks[winner_idx] = 0 # Winner!
        new_ratings = env.rate([(player_to_rating[player],) for player in players], ranks)
        for i, player in enumerate(players):
            player_to_rating[player] = new_ratings[i][0] # team i's 1st player
    return player_to_rating


if __name__ == '__main__':
    main()