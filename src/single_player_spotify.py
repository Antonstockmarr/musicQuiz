#%% Imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from fuzzywuzzy import fuzz
import random

#%% Load client_id and client_secret for spotify
f1 = open('../spotify_keys/clientid_ez.txt')
client_id = f1.read()
f1.close()
f2 = open('../spotify_keys/clientsecret_ez.txt')
client_secret = f2.read()
f2.close()

#%% Define game
class SinglePlayerMusicQuiz():
    def __init__(self, client_id, client_secret):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(client_id= client_id, client_secret=client_secret))

    def load_playlist_data(self, playlist_id):
        print('Musikquizzen starter!')
        self.playlist_id = playlist_id
        self.tracks = []
        n_tracks_limit = 10
    
        offset = 0
        playlist_info = self.sp.playlist_items(self.playlist_id,
                                 offset=offset,
                                 limit = n_tracks_limit,
                                 fields='items.track.id, items.track.name, items.track.artists,total',
                                 additional_types=['track'])
    
        self.n_songs = playlist_info['total']
        for i in range(self.n_songs):
            id = playlist_info['items'][i]['track']['id']
            artist = playlist_info['items'][i]['track']['artists'][0]['name']
            track_name = playlist_info['items'][i]['track']['name']
            self.tracks.append({'id': id, 'artist': artist.lower(), 'track_name': track_name.lower()})
        print('Playlist med %d tracks er blevet loadet' % self.n_songs)

    def start_music_quiz(self):
        print('Musikquiz starter!')
        print('Husk at skrive dit svar på følgende form: kunster - sangnavn')
        track_order = random.sample(range(self.n_songs), self.n_songs)
        total_score = 0
        max_score = 2*self.n_songs
        for round in range(self.n_songs):
            print('Round %d!' % round)
            print(self.tracks[round])
            guess = input()
            artist_correct, track_name_correct = check_guess(self.tracks[round], guess)
            score = (artist_correct + track_name_correct)
            print('Score = %d' % score)
            total_score += score
        print('Music quiz is done')
        acc = total_score/max_score*100
        print('FINAL SCORE: %d/%d (%f %%)' % (total_score, max_score, acc))

def check_guess(track, guess):
    artist_guess, track_guess = guess.lower().split('-')
    artist_correct = fuzz.partial_ratio(artist_guess, track['artist']) > 90
    track_name_correct = fuzz.partial_ratio(track_guess, track['track_name']) > 90
    return artist_correct, track_name_correct
    


# %%  Play music quiz
playlist_id = 'spotify:playlist:5W6gkJKrdne72cnaTebm8e' # Test playlist
mq = SinglePlayerMusicQuiz(client_id, client_secret) 
mq.load_playlist_data(playlist_id)
mq.start_music_quiz()

# %%
