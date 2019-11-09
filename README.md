# Setup

* Ensure all required python dependencies are installed:

```
pip install -r requirements.txt
```

* Ensure SAMPLE_SPREADSHEET_ID and SAMPLE_RANGE_NAME are set appropriately:
  * SAMPLE_SPREADSHEET_ID: ID of google doc to read game's players and winners from
  * SAMPLE_RANGE_NAME: string specifying spreadsheet name and the range of 8 columns to slice game data from it. Columns must be ordered "Winner,P1,P2,P3,P4,P5,P6,Winner2", where P5, P6, and Winner2 may be blank. For example, 'All Rated Games!D2:K'. [Click here](https://support.google.com/docs/topic/1361472?hl=en) for more details on Google Docs syntax.

* To calculate Trueskill ratings, run:

```
python get_all_catan_games.py
```