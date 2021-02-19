#%% Imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


#%% Load client_id and client_secret for spotify
f1 = open('../spotify_keys/clientid_ez.txt')
clientid = f1.read()
f1.close()
f2 = open('../spotify_keys/clientsecret_ez.txt')
client_secret = f2.read()
f2.close()

#%% Authorize to do public things (without connecting to my account...) 
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(client_id= clientid, client_secret=client_secret))

birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'

results = sp.artist_albums(birdy_uri, album_type='album')
albums = results['items']
while results['next']:
    results = spotify.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])


# %% Authorize using my spotify account
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(client_id= clientid, client_secret=client_secret, redirect_uri = 'https://example.com/callback/'))
# Copy paste url when prompted

#%%
results = sp.current_user_playlists(limit=50)
for i, item in enumerate(results['items']):
    print("%d %s" % (i, item['name']))

# %% NEXT STEP: Play song here... 