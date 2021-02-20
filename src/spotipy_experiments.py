redirect_uri = 'https://example.com/callback/'
#%% Authorize to do public things (without connecting to my account...) 
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(client_id= client_id, client_secret=client_secret))

#%%



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
test = sp.playlist_items(playlist_id,
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


