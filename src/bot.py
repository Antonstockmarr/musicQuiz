# bot.py
from asyncio.tasks import sleep
import os
import math
import operator
import random
import discord
from discord import player
from discord.flags import PublicUserFlags
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

        n_tracks_limit = 100

        offset = 0
        playlist_info = self.sp.playlist_items(self.playlist_id,
                                 offset=0,
                                 limit = n_tracks_limit,
                                 fields='items.track.id, items.track.name, items.track.artists,total',
                                 additional_types=['track'])
    
        self.n_songs = len(playlist_info['items'])

        self.player_scores = {}

        for i in range(self.n_songs):
            id = playlist_info['items'][i]['track']['id']
            artist = playlist_info['items'][i]['track']['artists'][0]['name']
            track_name = playlist_info['items'][i]['track']['name']
            self.tracks.append({'id': id, 'artist': artist, 'track_name': track_name})
        
        print('Playlist med %d tracks er blevet loadet' % self.n_songs)

    def check_guess(self, guess):

        artist = self.current_artist.lower().strip()
        track_name = self.current_track_name.lower().strip()

        track_name_splitted = track_name.split('-')
        track_name = track_name_splitted[0]

        track_name_splitted = track_name.split('(')
        track_name = track_name_splitted[0]

        track_name_splitted = track_name.split('/')
        track_name = track_name_splitted[0]

        guess = guess.lower().strip()

        artist_correct = fuzz.ratio(guess, artist) > 90
        track_name_correct = fuzz.ratio(guess, track_name) > 90

        return artist_correct, track_name_correct

    def start_quiz_(
        self, 
        playlist_id,
        voice_channel, 
        text_channel, 
        number_of_rounds, 
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

        self.rounds_total = min(len(self.tracks), number_of_rounds)
        self.current_round = 0

        random.shuffle(self.tracks)

        self.tracks_iter = iter(self.tracks)

        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.hidden_channel = discord.utils.get(
            text_channel.guild.channels, 
            name=hidden_channel_name,
        )

        self.current_track = None

        return [voice_channel.connect()]
        ## Get players, reset score, print welcome message...

    def exit_(self):

        return (
            [self.text_channel.send(f':fireworks: The music quiz is done!  See final standings below :fireworks:')]
         + self.scoreboard_("Final standings:")
         + self.stop_()
        )

    def guess_(self, guess, player):

        artist_correct, track_name_correct = self.check_guess(guess)
        
        awaitables = []

        if not self.artist_guessed and artist_correct:
            self.artist_guessed = True
            try:
                self.player_scores[player] += 1
            except KeyError:
                self.player_scores[player] = 1

            awaitables.append(self.text_channel.send(f':partying_face::musical_note: {player} correctly guessed the artist as "{self.current_artist}" ! Good job!'),)
            # Give point...
        if not self.track_name_guessed and track_name_correct:
            self.track_name_guessed = True
            try:
                self.player_scores[player] += 1
            except KeyError:
                self.player_scores[player] = 1

            awaitables.append(self.text_channel.send(f':partying_face::musical_note: {player} correctly guessed the song name as "{self.current_track_name}" ! Good job!'),)
            

        if self.artist_guessed and self.track_name_guessed:
            return awaitables + [asyncio.sleep(4)] + self.next_round_()
        else:
            return awaitables

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
        
        if self.current_round >= self.rounds_total:
            return self.exit_()

        self.current_round += 1

        try:
            next_song = next(self.tracks_iter)
        except StopIteration:
            return self.exit_()

        self.current_id = next_song["id"]
        self.current_artist = next_song["artist"]
        self.current_track_name = next_song["track_name"]
        self.current_skippers = set()

        self.artist_guessed = False
        self.track_name_guessed = False

        return (
            self.scoreboard_(desc="Current standings:")
            + [self.hidden_channel.send(f"/stop")]
            + [self.text_channel.send(f"Round {self.current_round}/{self.rounds_total}! :musical_note: Can you guess the song...?")]
            + [asyncio.sleep(1)]
            + [self.text_channel.send(f":three:")]
            + [asyncio.sleep(1)]
            + [self.text_channel.send(f":two:")]
            + [asyncio.sleep(1)]
            + [self.text_channel.send(f":one:")]
            + [asyncio.sleep(1)]
            + [self.text_channel.send(f"Guess! :arrow_forward: :musical_note: :ear:")]
            + self.play_song_(f"{self.current_artist} {self.current_track_name}")
        )

    def skip_(self, id_):

        self.current_skippers.add(id_)

        if ( len(self.voice_channel.voice_states) - 2 ) / 2 > len(self.current_skippers):
            return [self.text_channel.send(f"{len(self.current_skippers)} voted to skip. Need {math.ceil((len(self.voice_channel.voice_states) - 2 ) / 2)} people in order to skip track")]
        else:
            return [self.text_channel.send(f"Track skipped! ({self.current_track_name} by {self.current_artist})")] + self.next_round_()

    def scoreboard_(self, desc=None):

        player_scores = self.player_scores

        if len(player_scores) == 0:
            return []

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

        args = message.content.split()
        if len(args) == 1:
            await message.channel.send("Please specify spotify playlist id!")
        elif len(args) == 2:
            playlist_id = args[1]
            number_of_rounds = 15
        elif len(args) == 3:
            playlist_id = args[1]
            number_of_rounds = int(args[2])

        for awaitable in mq.start_quiz_(
            playlist_id=playlist_id,
            voice_channel=author.voice.channel,
            text_channel=message.channel,
            number_of_rounds=number_of_rounds,
            hidden_channel_name="hidden",
            ):
            await awaitable

        for awaitable in mq.next_round_():
            await awaitable

    elif message.content == "~skip":

        for awaitable in mq.skip_(message.author.id):
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
        player = message.author.display_name
        for awaitable in mq.guess_(guess, player):
            await awaitable

client.run(TOKEN)