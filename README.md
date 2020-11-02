File_Proccessing application
===================
Input: 
- mixtape.json: data file including users, songs and playlists
- changes.json: changes including:
    - `add_new_playlist`
    - `remove_playlist`
    - `add_song_to_playlist`

Output:
- output.json: result file with the changes listed in `changes.json` applied to `mixtape.json`

# How to run it

Pre-requirement: Python 3.x and pip 20.x

```buildoutcfg
git clone https://github.com/jameswang2015/file_processing.git
cd file_processing/
python -m venv .venv
source ./.venv/bin/activate
pip install pydantic
python main.py mixtape.json changes.json
```

# Rules for each functions

Some rules are designed as followings.

- `add_new_playlist`:
    - if user_id doesn't exist in users, the new playlist won't be created
    - the new playlist_id is generated as `max_existing_playlist_id + 1`
- `remove_playlist`:
    - if playlist_id does not exist, print the info and don't perform removal
- `add_song_to_playlist`:
    - if `song` or `playlist` does not exist, print the info and don't perform addition
    - if `sone` is already in `playlist`, print the info and don't perform addition
- Pydantic model is used for data validation. If the given `change_detail` does not meet the model requirement,
  a `ValidationError` traceback is printed and the application will be terminated, meaning all following changes won't
  be performed. This behaviour can be modified as requested, for example, we can catch this error and make application
  continue with following changes.
  See the [documentation of the Pydantic library](https://pydantic-docs.helpmanual.io/) for more information. 

# How to scale up
- vary large maxtape.json input file  
  If the json input file is too large to fit in memory, we can't use `json.load()` to load it in whole. Rather, we need
  some streaming tool like `ijson` to read json as streaming. 
  
  We could also consider to put this into database and create three tables for `users`, `songs` and `playlists`, 
  respectively. Then we can leverage database sql and primary/foreign key constraints to handle this. 
  
- vary large changes.json file  
  we can read this changes.json as streaming, each iteration pass one change, and then handle this change one by one.