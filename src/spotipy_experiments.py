#%% Imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

#%% Load client_id and client_secret for spotify
f1 = open('../spotify_keys/clientid_ez.txt')
client_id = f1.read()
f1.close()
f2 = open('../spotify_keys/clientsecret_ez.txt')
client_secret = f2.read()
f2.close()

redirect_uri = 'https://example.com/callback/'
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
scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope, client_id= clientid, client_secret=client_secret, redirect_uri = 'https://example.com/callback/'))
#%%
# Shows playing devices
res = sp.devices()
print(res)

# Change track
sp.start_playback(uris=['spotify:track:6nzXkCBOhb2mxctNihOqbb'])

#%% 
scope = "user-read-playback-state,user-modify-playback-state"
sp_tester =  spotipy.Spotify(
            client_credentials_manager=SpotifyOAuth(
                scope=scope, 
                client_id= client_id, 
                client_secret=client_secret, 
                redirect_uri = redirect_uri))
#%%      
offset = 0 
test = sp_tester.playlist_items(playlist_id,
                                 offset=offset,
                                 fields='items.track.id, items.track.name, items.track.artists,total',
                                 additional_types=['track'])
#%%
n_songs = test['total']
track_ids = []
artists = []
track_names = []
for i in range(n_songs):
    track_ids.append(test['items'][i]['track']['id'])
    artists.append(test['items'][i]['track']['artists'][0]['name'])
    track_names.append(test['items'][i]['track']['name'])



# %% 
class SinglePlayerMusicQuiz():
    def __init__(self, client_id, client_secret, redirect_uri):
        scope = "user-read-playback-state,user-modify-playback-state"

        print('Browservindue vil poppe op. Acceptér og copy paste url ind i spotify')
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyOAuth(
                scope=scope, 
                client_id= client_id, 
                client_secret=client_secret, 
                redirect_uri = redirect_uri))

        print('Spil en sang på din spotify, så dit "device" er aktivt')

    def play_song(self, song_id):
        self.sp.start_playback(uris=[song_id])

    def start_playlist_quiz(self, playlist_id):
        print('Musikquizzen starter!')
        self.playlist_id = playlist_id
        self.track_ids = []
        self.artists = []
        self.track_names = []
        n_tracks_limit = 10
        

        offset = 0
        playlist_info = self.sp.playlist_items(self.playlist_id,
                                 offset=offset,
                                 limit = n_tracks_limit,
                                 fields='items.track.id, items.track.name, items.track.artists,total',
                                 additional_types=['track'])
    
        self.n_songs = playlist_info['total']
        for i in range(self.n_songs):
            self.track_ids.append(playlist_info['items'][i]['track']['id'])
            self.artists.append(playlist_info['items'][i]['track']['artists'][0]['name'])
            self.track_names.append(playlist_info['items'][i]['track']['name'])
        print(self.track_ids)
        print(self.track_names)
        print(self.artists)


# %%
playlist_id = 'spotify:playlist:5W6gkJKrdne72cnaTebm8e' # Test playlist

mq = SinglePlayerMusicQuiz(client_id, client_secret, redirect_uri) 

#%%
lizzo = 'spotify:track:0k664IuFwVP557Gnx7RhIl'
mq.play_song(lizzo)
# %%
mq.start_playlist_quiz(playlist_id)

# %%
