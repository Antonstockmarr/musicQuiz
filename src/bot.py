# bot.py
from asyncio.tasks import sleep
import os

import operator
import random
import discord
from discord import player
from dotenv import load_dotenv
from fuzzywuzzy import fuzz

import asyncio
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

SPOTIFY_CLIENT_ID=os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET=os.getenv('SPOTIFY_CLIENT_SECRET')


class MusicQuiz:
    
    def load_playlist_data(self, playlist_id):
        
        self.playlist_id = playlist_id
        self.tracks = []
        #TODO: fix track limit
        n_tracks_limit = 10
    
        offset = 0
        playlist_info = self.sp.playlist_items(self.playlist_id,
                                 offset=offset,
                                 limit = n_tracks_limit,
                                 fields='items.track.id, items.track.name, items.track.artists,total',
                                 additional_types=['track'])
    
        self.n_songs = len(playlist_info['items'])

        for i in range(self.n_songs):
            id = playlist_info['items'][i]['track']['id']
            artist = playlist_info['items'][i]['track']['artists'][0]['name']
            track_name = playlist_info['items'][i]['track']['name']
            self.tracks.append({'id': id, 'artist': artist.lower(), 'track_name': track_name.lower()})
        
        print('Playlist med %d tracks er blevet loadet' % self.n_songs)

    def check_guess(self, guess):

        artist = self.current_artist.lower().strip()
        track_name = self.current_track_name.lower().strip()

        guess = guess.lower().strip()

        artist_correct = fuzz.partial_ratio(guess, artist) > 90
        track_name_correct = fuzz.partial_ratio(guess, track_name) > 90

        #TODO: Scores

        return artist_correct, track_name_correct

    def start_quiz_(
        self, 
        playlist_id,
        voice_channel, 
        text_channel, 
        hidden_channel_name="hidden",
    ):

        # Spotify API for playlist import
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id= SPOTIFY_CLIENT_ID, 
                client_secret=SPOTIFY_CLIENT_SECRET
                )
            )

        self.load_playlist_data(playlist_id=playlist_id)
        random.shuffle(self.tracks)

        self.tracks_iter = iter(self.tracks)

        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.hidden_channel = discord.utils.get(
            text_channel.guild.channels, 
            name=hidden_channel_name,
        )

        self.current_track = None

        #TODO: get current members in voice channel and 0-init dict
        self.player_scores = {
            "Anton" : 1000,
            "Søren" : 2,
            "Simon" : 2,
            "Elizabeth" : 2
        }

        ## Get players, reset score, print welcome message...
        
        return [voice_channel.connect()]

    def guess_(self, guess, player):

        artist_correct, track_name_correct = self.check_guess(guess)

        if not self.artist_guessed and artist_correct:
            self.artist_guessed = True
            # Give point...
        if not self.track_name_guessed and track_name_correct:
            self.track_name_guessed = True

        if self.artist_guessed and self.track_name_guessed:
            return self.next_round_()
        else:
            return []


    def stop_(self):
            
        return [
            self.hidden_channel.send(f"/stop"),
            client.voice_clients[0].disconnect(),
        ]

    def play_song_(self, song_name):

        return [
            self.hidden_channel.send(f"/play {song_name}")
        ]

    def next_round_(self):

        #TODO: current round flag
        next_song = next(self.tracks_iter)
        
        self.current_id = next_song["id"]
        self.current_artist = next_song["artist"]
        self.current_track_name = next_song["track_name"]

        self.artist_guessed = False
        self.track_name_guessed = False

        return (
            self.play_song_(f"{self.current_artist} {self.current_track_name}")
            + self.scoreboard_(desc="Current standings:")
        )

    def scoreboard_(self, desc=None):

        player_scores = self.player_scores
        players = player_scores.keys()

        sorted_scores = sorted(player_scores.items(), key=lambda x: -x[1])
    
        lead_player, lead_score = sorted_scores[0]

        if desc is None:
            desc = lead_player + f" is in the lead with a score of {lead_score}!!"

        embed_var = discord.Embed(title="Scoreboard", description=desc, color=0x00ff00)

        for player in players:
            embed_var.add_field(name=player, value=f"Score: {player_scores[player]}", inline=False)
        
        return [
            self.text_channel.send(embed=embed_var)
        ]

mq = MusicQuiz()
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    author = message.author

    if message.content.startswith('~start'):

        _, playlist_id = message.content.split()

        for awaitable in mq.start_quiz_(
            playlist_id=playlist_id,
            voice_channel=author.voice.channel,
            text_channel=message.channel,
            hidden_channel_name="hidden",
            ):
            await awaitable

        for awaitable in mq.next_round_():
            await awaitable

    elif message.content == "~next round":

        for awaitable in mq.next_round_():
            await awaitable

    elif message.content.startswith('~score'):
            
        for awaitable in mq.scoreboard_():
            await awaitable

    elif message.content.startswith('~stop'):
            
        for awaitable in mq.stop_():
            await awaitable

    #TODO: add flag for ongoing round
    else:
        if message.author.bot: # and check flag
            return

        guess = message.content
        player = message.author.id
        for awaitable in mq.guess_(guess, player):
            await awaitable

client.run(TOKEN)