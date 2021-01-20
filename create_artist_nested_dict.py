# -------------------------------------------------------- Imports
import os   # For environment variables
from spotipy.oauth2 import SpotifyClientCredentials     # For spotify API
import spotipy      # For Spotify API
import lyricsgenius     # For genius API
import json     # For saving the nested dictionary to json file, for upload in AWS s3
import difflib      # For comparing two strings
import sys      # For command line arguments from user
import logging      # For AWS s3 file upload
import boto3      # For AWS s3 file upload
from botocore.exceptions import ClientError      # For AWS s3 file upload
import re       # For regex matching when splitting song words arr
from unidecode import unidecode     # To take care of the \u
# --------------------------------------------------------- Functions: Accessability/Support
def access_libraries_function():
    """
    Returns: the connected library variables to allow the library functions
    """
    print('Status: Function Start:[access_libraries_function]')
    try:
        # Connect to spotipy API library
        client_credentials_manager = SpotifyClientCredentials(client_id=os.environ.get('SPOTIFY_CLIENT_ID'), client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'))
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Connect to genius API library
        genius = lyricsgenius.Genius(os.environ.get('GENIUS_ACCESS_TOKEN'))
        print('Status: Function End:[access_libraries_function]. Result: successfully connected to both APIs')
        return sp, genius
    except:
        print('Status: Function End:[access_libraries_function]. Result: did not connect to both APIs')
        return False
# --------------------------------------------------------- Functions: Song Checks
def check_if_song_contains_feat(input_song_spotify):
    """
    Args: input_song_spotify
    Returns: Boolean if the song contains the word 'feat' in the title
    """
    print('Status: Function Start:[check_if_song_contains_feat]')
    if 'feat.' in input_song_spotify.lower() or 'ft' in input_song_spotify.lower() or '(with' in input_song_spotify.lower():
        print('Status: Function End:[check_if_song_contains_feat]. Result: yes, song contains the word feat')
        return True
    print('Status: Function End:[check_if_song_contains_feat]. Result: No, the song does not contains the word feat')
    return False
def check_if_song_is_censored(input_song_spotify):
    """
    Args: input_song_spotify
    Returns: if the song contains a censor symbol *
    """
    print('Status: Function Start:[check_if_song_is_censored]')
    for i in range(len(input_song_spotify)):
        if input_song_spotify[i] == '*':
            print('Status: Function End:[check_if_song_is_censored]. Result: yes, song does contain *')
            return True
    print('Status: Function End:[check_if_song_is_censored]. Result: no, song does not contain *')
    return False
def check_if_song_starts_with_intro_outro(input_song_spotify):
    """
    Args: input song
    Returns: if song starts with only the word intro or outro
    """
    print('Status: Function Start:[check_if_song_starts_with_intro_outro]')
    if (input_song_spotify[:5].lower() == 'intro' and len(input_song_spotify) == 5) or (input_song_spotify[:5].lower() == 'outro' and len(input_song_spotify) == 5):
        print('Status: Function End:[check_if_song_starts_with_intro_outro]. Result: yes, song does include only word intro or outro')
        return True
    else:
        print('Status: Function End:[check_if_song_starts_with_intro_outro]. Result: no, song does not include only word intro or outro')
        return False
def check_if_song_is_split_with_slash(input_song_spotify):
    """
    Args: Input song spotify
    Returns: Boolean if song has a '\' or '/'
    """
    print('Status: Function Start:[check_if_song_is_split_with_slash]')
    song_words_arr = input_song_spotify.split(' ')
    for word in song_words_arr:
        if word == '\\' or word == '/':
            print('Status: Function End:[check_if_song_is_split_with_slash]. Result: Yes, found a slash in the song')
            return True
    print('Status: Function End:[check_if_song_is_split_with_slash]. Result: No, did not find a slash in the song')
    return False
def check_if_song_has_dash(input_song_spotify):
    """
    Args: Input song spotify
    Returns: Boolean if song has a '-'
    """
    print('Status: Function Start:[check_if_song_has_dash]')
    for i in input_song_spotify:
        if i == '-':
            print('Status: Function End:[check_if_song_has_dash]. Result: Yes, found dash in the song')
            return True
    print('Status: Function End:[check_if_song_has_dash]. Result: No, did not find dash in the song')
    return False
def check_if_song_has_parentheses(input_song_spotify):
    """
    Args: Input song spotify
    Returns: Boolean if song has a '('
    """
    print('Status: Function Start:[check_if_song_has_parentheses]')
    for i in input_song_spotify:
        if i == '(':
            print('Status: Function End:[check_if_song_has_parentheses]. Result: Yes, found parentheses in the song')
            return True
    print('Status: Function End:[check_if_song_has_parentheses]. Result: No, did not find parentheses in the song')
    return False
# --------------------------------------------------------- Functions: Change song
def change_song_name_remove_feat_onward(input_song_spotify):
    """
    Args: input_song_spotify
    Returns: spotify song name without the word feat onward. Example 'featuring Kanye West' would be removed from the song name
    """
    print('Status: Function Start:[change_song_name_remove_feat_onward]')
    song_name_spotify_without_feat_arr = []
    song_name_spotify_words_arr = input_song_spotify.split(' ')
    for word in song_name_spotify_words_arr:
        #if 'feat.' in word or 'ft' in word or '(with' in word:
        if word.lower() == 'feat.' or word.lower() == '(feat.' or word.lower() == 'ft' or word.lower() == '(ft' or word.lower() == '(with':
            break
        song_name_spotify_without_feat_arr.append(word)
    print('Status: Function End:[change_song_name_remove_feat_onward]. Result: song_name_spotify returned without the word feat onward: ' + ' '.join(song_name_spotify_without_feat_arr))
    return ' '.join(song_name_spotify_without_feat_arr)
def change_album_name_remove_last_word_from_album(input_album_name):
    """
    Args: album name to search for
    Returns: album name without the last word. This is because of album names that end in "deluxe" or "explicit"
    """
    print('Status: Function Start:[change_album_name_remove_last_word_from_album]')
    album_title_words = input_album_name.split(' ')
    shortened_album_name = ' '.join(album_title_words[:-1])
    print('Status: Function End:[change_album_name_remove_last_word_from_album]. Result: returns shortened album name without the last word: ' + shortened_album_name)
    return shortened_album_name
def change_song_name_to_first_part_of_slash(input_song_spotify):
    """
    Args: input song spotify
    Returns: the first part of the song name, before the dash
    """
    print('Status: Function Start:[change_song_name_to_first_part_of_slash]')
    first_part_song_arr = []
    song_words_arr = input_song_spotify.split(' ')
    for word in song_words_arr:
        if word == '\\' or word == '/':
            break
        first_part_song_arr.append(word)
    print('Status: Function End:[change_song_name_to_first_part_of_slash]. Result: returned the first part of the song before the slash: ' + ' '.join(first_part_song_arr))
    return ' '.join(first_part_song_arr)
def change_song_name_to_without_dash(input_song_spotify):
    """
    Args: input song spotify
    Returns: the first part of the song name, before the dash
    """
    print('Status: Function Start:[change_song_name_to_without_dash]')
    song_name_until_parentheses_arr = []
    for i in input_song_spotify:
        if i == '-':
            break
        song_name_until_parentheses_arr.append(i)
    print('Status: Function End:[change_song_name_to_without_dash]. Result: returned the song name before the -: ' + ''.join(song_name_until_parentheses_arr))
    return ''.join(song_name_until_parentheses_arr)
def change_song_name_to_without_parentheses(input_song_spotify):
    """
    Args: input song spotify
    Returns: the first part of the song name, before the dash
    """
    print('Status: Function Start:[change_song_name_to_without_parentheses]')
    song_name_until_parentheses_arr = []
    for i in input_song_spotify:
        if i == '(':
            break
        song_name_until_parentheses_arr.append(i)
    print('Status: Function Start:[change_song_name_to_without_parentheses]. Result: returned the song name before the parentheses: ' + ''.join(song_name_until_parentheses_arr))
    return ''.join(song_name_until_parentheses_arr)
# --------------------------------------------------------- Functions: Test Cases song
def low_word_match_score_spotify_vs_genius_test_cases(word_match_score_spotify_vs_genius, song_name_spotify, album_id_genius, album_name_spotify, artist_name_spotify, search_result_num_genius, genius):
    """
    Args: word_match_score_spotify_vs_genius, song_name_spotify, album_id_genius, album_name_spotify, artist_name_spotify
    Returns: The most accurate song based on changes/test cases. If nothing found then returns nothing
    """
    print('Status: Function Start:[low_word_match_score_spotify_vs_genius_test_cases]')
    # Check if song contains word 'feat.' in the title
    if word_match_score_spotify_vs_genius < .55:
        song_name_spotify_contains_feat = check_if_song_contains_feat(song_name_spotify)
        if song_name_spotify_contains_feat == True:
            song_name_spotify_without_feat = change_song_name_remove_feat_onward(song_name_spotify)
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_spotify_without_feat, artist_name_spotify, search_result_num_genius, genius)
    # Check if song has censored '*' in the title
    if word_match_score_spotify_vs_genius < .55:
        song_is_censored = check_if_song_is_censored(song_name_spotify)
        if song_is_censored == True:
            uncensored_input_song_genius = get_uncensored_song_name_from_genius(album_id_genius, song_name_spotify, genius)
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(uncensored_input_song_genius, artist_name_spotify, search_result_num_genius, genius)
    # Check if song begins with just intro or outro
    if word_match_score_spotify_vs_genius < .55:
        song_starts_with_intro_outro = check_if_song_starts_with_intro_outro(song_name_spotify)
        if song_starts_with_intro_outro == True:
            cleaned_song_name_spotify = song_name_spotify + ' ' + album_name_spotify
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(cleaned_song_name_spotify, artist_name_spotify, search_result_num_genius, genius)
    # Check if song is 2 seperate songs: Example "Cameras / Good Ones Go (Interlude) - Drake". Thats two songs, genius cannot find match for that input
    if word_match_score_spotify_vs_genius < .55:
        song_split_slash = check_if_song_is_split_with_slash(song_name_spotify)
        if song_split_slash == True:
            song_name_first_part_slash = change_song_name_to_first_part_of_slash(song_name_spotify)
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_first_part_slash, artist_name_spotify, search_result_num_genius, genius)
    # Check if song has "-" after the song title: Example "HYFR (Hell Yeah F***ing Right) - Album Explicit - Drake"
    if word_match_score_spotify_vs_genius < .55:
        song_dash_present = check_if_song_has_dash(song_name_spotify)
        if song_dash_present == True:
            song_name_wout_dash = change_song_name_to_without_dash(song_name_spotify)
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_wout_dash, artist_name_spotify, search_result_num_genius, genius)
    # Check if song has "()" after the song title: Example "HYFR (Hell Yeah F***ing Right) - Drake"
    if word_match_score_spotify_vs_genius < .55:
        song_parentheses_present = check_if_song_has_parentheses(song_name_spotify)
        if song_parentheses_present == True:
            song_name_wout_parentheses = change_song_name_to_without_parentheses(song_name_spotify)
            pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_wout_parentheses, artist_name_spotify, search_result_num_genius, genius)
    # Last Check add interlude to the title
    if word_match_score_spotify_vs_genius < .55:
        print('Status: Last Check: Adding the word "Interlude" at the end of song')
        pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_spotify + ' interlude', artist_name_spotify, search_result_num_genius, genius)
    print('Status: Function End:[low_word_match_score_spotify_vs_genius_test_cases]. Result: returns results of test cases/changes')
    return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
def check_if_song_match_spotify_genius(input_song_name_spotify, input_song_index, input_album_songs_arr_genius):
    """
    Args: input_song_name_spotify, input_song_index, input_album_songs_arr_genius
    Returns: pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
    """
    print('Status: Function Start:[check_if_song_match_spotify_genius]')
    try:
        # Compare the spotify song with the same index song on the genius album
        word_match_score_spotify_vs_genius = difflib.SequenceMatcher(None, input_song_name_spotify.lower(), input_album_songs_arr_genius[input_song_index][0].lower()).ratio()
        # Compare the words for the min number of characters
        if word_match_score_spotify_vs_genius < .55:
            smaller_word_length = 0
            if len(input_song_name_spotify) < len(input_album_songs_arr_genius[input_song_index][0]):
                smaller_word_length = len(input_song_name_spotify)
            else:
                smaller_word_length = len(input_album_songs_arr_genius[input_song_index][0])
            word_match_score_spotify_vs_genius = difflib.SequenceMatcher(None, input_song_name_spotify[:smaller_word_length].lower(), input_album_songs_arr_genius[input_song_index][0][:smaller_word_length].lower()).ratio()
        if word_match_score_spotify_vs_genius > .55:
            pulled_song_id_genius = input_album_songs_arr_genius[input_song_index][1]
            pulled_song_title_genius = input_album_songs_arr_genius[input_song_index][0]
            print('Status: Function End:[check_if_song_match_spotify_genius]. Result: Successfully matched spotify song to genius song, did not have to loop through all songs in genius album')
            return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
        # In case the album songs are in different orders, loop through the whole album comparing 1 by 1
        else:
            for song_title_genius, song_id_genius in input_album_songs_arr_genius:
                word_match_score_spotify_vs_genius = difflib.SequenceMatcher(None, input_song_name_spotify.lower(), song_title_genius.lower()).ratio()
                if word_match_score_spotify_vs_genius > .55:
                    pulled_song_id_genius = song_id_genius
                    pulled_song_title_genius = song_title_genius
                    print('Status: Function End:[check_if_song_match_spotify_genius]. Result: Successfully matched spotify song to genius song, after looping through all songs in genius album')
                    return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
        pulled_song_id_genius = ''
        pulled_song_title_genius = ''
        word_match_score_spotify_vs_genius = 0
        print('Status: Function End:[check_if_song_match_spotify_genius]. Result: Failed, did not match spotify song to genius song')
        return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
    except:
        pulled_song_id_genius = ''
        pulled_song_title_genius = ''
        word_match_score_spotify_vs_genius = 0
        print('Status: Function End:[check_if_song_match_spotify_genius]. Result: Failed, did not match spotify song to genius song')
        return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
# --------------------------------------------------------- Functions: Sportify Pull
def get_artist_obj_from_spotify(input_artist_name, sp):
    """
    Returns: the first matching artist object from Spotify
    """
    print('Status: Function Start:[get_artist_obj_from_spotify]')
    results = sp.search(q='artist:' + input_artist_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        print('Status: Function End:[get_artist_obj_from_spotify]. Successfully got artist object')
        return items[0]
    else:
        print('Status: Function End:[get_artist_obj_from_spotify]. Did not find artist object')
        return None
# --------------------------------------------------------- Functions: Genius Pull
def get_artist_id_genius(input_artist_name_spotify, genius):
    """
    Returns: artist id from genius if found
    """
    print('Status: Function Start:[get_artist_id_genius]')
    artist_searched_genius = genius.search(input_artist_name_spotify)
    try:
        artist_id_genius = artist_searched_genius['hits'][0]['result']['primary_artist']['id']
    except:
        artist_id_genius = 'not found'
    print('Status: Function End:[get_artist_id_genius]. Result: genius pulled artist id: ' + str(artist_id_genius))
    return artist_id_genius
def get_album_name_and_id_genius(input_album_name_spotify, genius):
    """
    Returns: the album object pulled from rap genius search bar result
    """
    print('Status: Function Start:[get_album_name_and_id_genius]')
    # create variables to be returned
    searched_album_object_genius = genius.search_albums(input_album_name_spotify)
    try:
        pulled_album_name_genius = searched_album_object_genius['sections'][0]['hits'][0]['result']['name']
        pulled_album_id_genius = searched_album_object_genius['sections'][0]['hits'][0]['result']['id']
    except:
        pulled_album_name_genius = 'not found'
        pulled_album_id_genius = 'not found'
    print('Status: Function End:[get_album_name_and_id_genius]. Result: pulled_album_name_genius: ' + str(pulled_album_name_genius) + ' and pulled_album_id_genius: ' + str(pulled_album_id_genius))
    return pulled_album_name_genius, pulled_album_id_genius
def get_uncensored_song_name_from_genius(input_genius_album_id, input_song_spotify, genius):
    """
    Args: Album id and song name
    Returns: the uncensored written version of a song name
    """
    print('Status: Function Start:[get_uncensored_song_name_from_genius]')
    # Create empty variable/array
    album_tracks_uncensored_arr = []
    uncensored_input_song_genius = ''
    # Get album tracks from genius, store them in an array
    album_tracks_obj_genius = genius.album_tracks(input_genius_album_id)
    if album_tracks_obj_genius:
        for i in range(len(album_tracks_obj_genius['tracks'])):
            album_tracks_uncensored_arr.append(album_tracks_obj_genius['tracks'][i]['song']['title'])
        # Sort through the album tracks array and test which one is the closest match to the censored version
        for i in album_tracks_uncensored_arr:
            word_match_score_spotify_vs_genius = difflib.SequenceMatcher(None, input_song_spotify, i).ratio()
            if word_match_score_spotify_vs_genius > .55:
                uncensored_input_song_genius = i
                break
        print('Status: Function End:[get_uncensored_song_name_from_genius]. Result: uncensored song name from genius: ' + uncensored_input_song_genius)
        return uncensored_input_song_genius
    print('Status: Function End:[get_uncensored_song_name_from_genius]. Result: no uncensored song name version found from genius: ' + input_song_spotify)
    return input_song_spotify
def get_song_object_from_genius(input_song_spotify, input_artist_name_spotify, search_result_num_genius, genius):
    """
    Args: input_song_spotify, input_artist_name_spotify. These go into rap genius search bar
    Returns: the song object pulled from rap genius search bar result
    """
    print('Status: Function Start:[get_song_object_from_genius]')
    # create variables to be returned
    pulled_song_id_genius = ''
    pulled_song_title_genius = ''
    word_match_score_spotify_vs_genius = 0
    # Search the song object
    song_object_genius = genius.search_songs(input_song_spotify + ' ' + input_artist_name_spotify)
    try: 
        pulled_song_id_genius = song_object_genius['hits'][search_result_num_genius]['result']['id']
        pulled_song_title_genius = song_object_genius['hits'][search_result_num_genius]['result']['title']
        # Approximate match testing the spotify song title vs genius song title
        word_match_score_spotify_vs_genius = difflib.SequenceMatcher(None, input_song_spotify.lower(), pulled_song_title_genius.lower()).ratio()
        if word_match_score_spotify_vs_genius < .55:
            print('genius pulled incorrect title: \"' + pulled_song_title_genius + '\"')
            print('vs. the input_song_spotify: ' + input_song_spotify)
            print('got a word_match_score_spotify_vs_genius of : ' + str(word_match_score_spotify_vs_genius))
            word_match_score_spotify_vs_genius = 0
    # If a song_object is not founud in search
    except:
        word_match_score_spotify_vs_genius = 0
    print('Status: Function End:[get_song_object_from_genius]. Result: from genius[song_id, song_title] and a word match score')
    return pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius
def get_album_songs_arr_and_album_song_count_genius(input_genius_album_id, genius):
    """
    Args: input_genius_album_id
    Returns: album songs in arr, and album song count
    """
    print('Status: Function Start:[get_album_songs_arr_and_album_song_count_genius]')
    # Create variables
    album_songs_arr_genius = []
    album_songs_count_genius = 0
    # Get album object from genius
    album_tracks_obj_genius = genius.album_tracks(input_genius_album_id)
    # Loop though to append songs to arr and count total songs
    if album_tracks_obj_genius:
        for i in range(len(album_tracks_obj_genius['tracks'])):
            pulled_song_title_genius = album_tracks_obj_genius['tracks'][i]['song']['title']
            pulled_song_id_genius = album_tracks_obj_genius['tracks'][i]['song']['id']
            album_songs_arr_genius.append((pulled_song_title_genius, pulled_song_id_genius))
            album_songs_count_genius += 1
    print('Status: Function End:[get_album_songs_arr_and_album_song_count_genius]. Result: album_songs_arr_genius: ' + str(album_songs_arr_genius) + ' and album_songs_count_genius: ' + str(album_songs_count_genius))
    return album_songs_arr_genius, album_songs_count_genius
# --------------------------------------------------------- Functions: Create Nested Dictionary song
def create_artist_discography_nested_dict(input_spotify_artist_object, sp, genius):
    """
    Returns: Nested dictionary with artist{}, album{}, song{}, lyrics[] and more info about song
    """
    print('Status: Function Start:[create_artist_discography_nested_dict]')
    # Get artist name from spotify artist object
    artist_name_spotify = input_spotify_artist_object['name']
    # Get artist id from Spotify and Genius
    artist_id_spotify = input_spotify_artist_object['id']
    artist_id_genius = get_artist_id_genius(artist_name_spotify, genius)
    # Create the nested dictionary and Add Key/Value to dictionary
    dict = {}
    dict[artist_name_spotify] = {}
    dict[artist_name_spotify]['artist_image_spotify'] = ''
    if input_spotify_artist_object['images']:
        dict[artist_name_spotify]['artist_image_spotify'] = input_spotify_artist_object['images']
    dict[artist_name_spotify]['artist_id_spotify'] = artist_id_spotify
    dict[artist_name_spotify]['artist_id_genius'] = artist_id_genius
    dict[artist_name_spotify]['total_albums_spotify'] = 0
    #dict[artist_name_spotify]['artist_sentiment_analysis'] = {}
    dict[artist_name_spotify]['artist_total_word_count_dict'] = {}
    dict[artist_name_spotify]['artist_total_words_counted'] = 0
    dict[artist_name_spotify]['artist_total_unique_words_counted'] = 0
    dict[artist_name_spotify]['album_names_spotify'] = {}
    dict[artist_name_spotify]['genius_artist_album_song_lyrics_not_found'] = []
    # Create empty array to store album names
    albums_arr_spotify = []
    # Search spotify for input artist albums
    results = sp.artist_albums(input_spotify_artist_object['id'], album_type='album')
    # Get total number of albums
    total_albums_spotify = results['total']
    dict[artist_name_spotify]['total_albums_spotify'] = total_albums_spotify
    albums_arr_spotify.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums_arr_spotify.extend(results['items'])
    # Album name set, so less duplicate albums
    unique_album_name_spotify_set = set()
    for album_obj_spotify in albums_arr_spotify:
        album_name_spotify = album_obj_spotify['name']
        album_id_spotify = album_obj_spotify['id']
        # Get album_id from genius
        album_name_genius, album_id_genius = get_album_name_and_id_genius(album_name_spotify, genius)
        shortened_album_name_spotify = album_name_spotify
        while len(shortened_album_name_spotify) > 0 and album_name_genius == 'not found':
            shortened_album_name_spotify = change_album_name_remove_last_word_from_album(shortened_album_name_spotify)
            album_name_genius, album_id_genius = get_album_name_and_id_genius(shortened_album_name_spotify, genius)
        # Skip albums that end with the word acapella, because it is usually already being taken into account by the regular version of the album
        if 'acappella' in album_name_spotify.lower() or 'a cappella' in album_name_spotify.lower():
            continue
        if album_name_spotify not in unique_album_name_spotify_set:
            # Get spotify album image
            try:
                album_image_spotify = album_obj_spotify['images']
            except:
                album_image_spotify = "No album image found"
            album_songs_arr_genius, album_songs_count_genius = get_album_songs_arr_and_album_song_count_genius(album_id_genius, genius)
            # Add Key/Value to dictionary
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify] = {}
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_name_genius'] = album_name_genius
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_image_spotify'] = album_image_spotify
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_id_spotify'] = album_id_spotify
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_id_genius'] = album_id_genius
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['total_songs_spotify'] = album_obj_spotify['total_tracks']
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['total_songs_genius'] = album_songs_count_genius
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_release_date_spotify'] = album_obj_spotify['release_date']
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_lyrics_accuracy_score'] = 0
            # dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_artist_sentiment_analysis'] = {}
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_artist_total_word_count_dict'] = {}
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_artist_total_words_counted'] = 0
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_artist_total_unique_words_counted'] = 0
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'] = {}
            # Add to the unique set
            unique_album_name_spotify_set.add(album_name_spotify)
            print('album_name_spotify: ' + album_name_spotify)
            print('album_name_genius: ' + str(album_name_genius))
            # Search spotify for input artist album songs
            lyrics_accuracy_score_tracker_for_songs = 0
            tracks_arr_spotify = []
            results = sp.album_tracks(album_obj_spotify['id'])
            tracks_arr_spotify.extend(results['items'])
            while results['next']:
                results = sp.next(results)
                tracks_arr_spotify.extend(results['items'])
            for song_index, track in enumerate(tracks_arr_spotify):
                song_name_spotify = track['name']
                print('song_name_spotify: ' + song_name_spotify)
                # Add Key/Value to dictionary
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify] = {}
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_lyrics_original'] = []
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_artist_lyrics_cleaned_up'] = []
                # dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_artist_sentiment_analysis'] = {}
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_artist_total_word_count_dict'] = {}
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_artist_total_words_counted'] = 0
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_artist_total_unique_words_counted'] = 0
                #-------------------------------------------------------------------------------------------
                # Set the search variables
                pulled_song_id_genius = ''
                pulled_song_title_genius = ''
                word_match_score_spotify_vs_genius = 0
                #-------------------------------------------------------------------------------------------
                # 1st Search is seeing if spotify song in spotify album id matches a genius song in genius album id
                if len(album_songs_arr_genius) != 0:
                    print('Status: Start 1st Search is seeing if spotify song in spotify album id matches a genius song in genius album id')
                    pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius = check_if_song_match_spotify_genius(song_name_spotify, song_index, album_songs_arr_genius)
                #-------------------------------------------------------------------------------------------
                # 2nd Lookup the song in genius search bar
                if word_match_score_spotify_vs_genius < .55:
                    print('Status: Start 2nd Lookup the song in genius search bar')
                    pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius  = get_song_object_from_genius(song_name_spotify, artist_name_spotify, 0, genius)
                #-------------------------------------------------------------------------------------------
                # 3rd Lookup the song in genius search bar after test case manipulations to song title
                if word_match_score_spotify_vs_genius < .55:
                    print('Status: Start 3rd Lookup the song in genius search bar after test case manipulations to song title')
                    pulled_song_id_genius, pulled_song_title_genius, word_match_score_spotify_vs_genius = low_word_match_score_spotify_vs_genius_test_cases(word_match_score_spotify_vs_genius, song_name_spotify, album_id_genius, album_name_spotify, artist_name_spotify, 0, genius)
                #-------------------------------------------------------------------------------------------
                print('pulled_song_id_genius: ' + str(pulled_song_id_genius))
                print('pulled_song_title_genius: ' + pulled_song_title_genius)
                print('word_match_score_spotify_vs_genius: ' + str(word_match_score_spotify_vs_genius))
                lyrics_accuracy_score_tracker_for_songs += word_match_score_spotify_vs_genius
                if word_match_score_spotify_vs_genius == 0:
                    # Add Key/Value to dictionary
                    dict[artist_name_spotify]['genius_artist_album_song_lyrics_not_found'].append((artist_name_spotify, album_name_spotify, song_name_spotify))
                    pulled_song_id_genius = 'not found'
                    pulled_song_title_genius = 'not found'
                # Get song lyrics
                pulled_song_lyrics = genius.lyrics(pulled_song_id_genius)
                # Add Key/Value to dictionary
                dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_songs_spotify'][song_name_spotify]['song_lyrics_original'].append(pulled_song_lyrics)
                print('- - - - - - - - - - -')
            lyrics_accuracy_score_tracker_for_album_overall = lyrics_accuracy_score_tracker_for_songs / album_obj_spotify['total_tracks']
            dict[artist_name_spotify]['album_names_spotify'][album_name_spotify]['album_lyrics_accuracy_score'] = lyrics_accuracy_score_tracker_for_album_overall
    print('Status: Function End:[create_artist_discography_nested_dict]. Result: Nested Dictionary')
    return dict
# --------------------------------------------------------- Functions: JSON
def export_dictionary_as_json(dict, artist_name_spotify_cleaned_up):
    """
    Args: dictionary
    Returns: saves the dictionary as json file to specified location
    """
    print('Status: Function Start:[export_dictionary_as_json]')
    json_file_output_location = "/tmp/"
    json_file_output_name = "output_spotify_genius_nested_dict_" + artist_name_spotify_cleaned_up + ".json"
    with open(json_file_output_location + json_file_output_name, "w") as outfile:
        json.dump(dict, outfile)
        print('Status: Function End:[export_dictionary_as_json]. Result: Successfully exported nested dictionary as JSON file')
        return json_file_output_location, json_file_output_name
    print('Status: Function End:[export_dictionary_as_json]. Result: Did not successfully export nested dictionary as JSON file')
    return False, False
# --------------------------------------------------------- Functions: AWS s3
def upload_file(s3_client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    print('Status: Function Start:[upload_file]')
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
    # Upload the file
    #s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print('Status: Function End:[upload_file]. Result: Successfully uploaded file to AWS s3')
        return True
    except ClientError as e:
        logging.error(e)
        print('Status: Function End:[upload_file]. Result: Did not upload file to AWS s3')
        return False
    return 'none'
def search_if_artist_obj_in_s3(s3_client, s3_bucket_name, s3_file_name_full):
    """
    Returns: If artist dict is already stored in s3, then return the s3 object, otherwise false
    """
    print('Status: Function Start:[search_if_artist_obj_in_s3]')
    try:
        # See if s3 object exists
        s3_object = s3_client.get_object(
            Bucket = s3_bucket_name, 
            Key = s3_file_name_full
        )
        print('Status: Function End:[search_if_artist_obj_in_s3]. Result: Success, artist obj found in s3')
        return s3_object
    except:
        print('Status: Function End:[search_if_artist_obj_in_s3]. Result: No, artist obj not found in s3')
        return False
def get_artist_number_of_albums_s3(s3_object, artist_name_spotify):
    """
    Returns: number of albums that artist has stored in s3
    """
    print('Status: Function Start:[get_artist_number_of_albums_s3]')
    # This gets the data as a string type
    s3_data_as_str = s3_object['Body'].read().decode('utf-8')
    # Load data as dictionary
    s3_data_as_dict = json.loads(s3_data_as_str)
    number_of_albums_s3 = s3_data_as_dict[artist_name_spotify]['total_albums_spotify']
    print('Status: Function End:[get_artist_number_of_albums_s3]. Result: Returned number of albums: ' + str(number_of_albums_s3))
    return number_of_albums_s3
def cleanup_artist_name_for_s3_saving(artist_name_input):
    """
    Returns: Removes special characters from artist name like beyoncÉ or jay-z or a$ap rocky
    """
    print('Status: Function Start:[cleanup_artist_name_for_s3_saving]')
    # remove all non alphanumeric and underscores from artist name and make it lowercase
    pattern = re.compile(r'\W+')
    try:
        artist_name_input = re.sub(pattern, '', artist_name_input)
        # Remove all accents from letters. Example beyoncé --> beyonce
        try:
            artist_name_input = unidecode(artist_name_input)
        except:
            pass
    except:
        pass
    artist_name_input = artist_name_input.lower()
    print('Status: Function END:[cleanup_artist_name_for_s3_saving]. Result: artist name: ' + artist_name_input)
    return artist_name_input
#=============================================================================================================================== MAIN PROGRAM RUN
def run(artist_name_html_form):
    # Access API libraries
    sp, genius = access_libraries_function()
    # Create AWS s3 client
    s3_client = boto3.client('s3')
    # Get argument from webpage
    user_input_artist = artist_name_html_form
    # Get artist object from spotify
    artist_object_spotify = get_artist_obj_from_spotify(user_input_artist, sp)
    # Get artist name as it appears in spotify
    artist_name_spotify = artist_object_spotify['name']
    # Clean up the artist name for saving into s3
    artist_name_spotify_cleaned_up = cleanup_artist_name_for_s3_saving(artist_name_spotify)
    # Check if artist is already stored in s3
    s3_bucket_name = 'artistinformation'
    s3_file_name_prefix = 'output_spotify_genius_nested_dict_'
    s3_file_name_full = s3_file_name_prefix + artist_name_spotify_cleaned_up + '.json'
    # Pull object from s3
    s3_object = search_if_artist_obj_in_s3(s3_client, s3_bucket_name, s3_file_name_full)
    total_albums_artist_s3 = 0
    # If artist nested dictionary is already in s3 then get their total number of albums
    if s3_object:
        total_albums_artist_s3 = get_artist_number_of_albums_s3(s3_object, artist_name_spotify)
    # Get total number of albums for artist on spotify
    albums_dict_spotify = sp.artist_albums(artist_object_spotify['id'], album_type='album')
    total_albums_artist_spotify = albums_dict_spotify['total']
    # Compare the two total number of albums
    if total_albums_artist_s3 < total_albums_artist_spotify:
        # Create artist master nested dictionary from artist object
        artist_master_dict = create_artist_discography_nested_dict(artist_object_spotify, sp, genius)
        # Export nested dictionary to json file
        json_file_output_location, json_file_output_name = export_dictionary_as_json(artist_master_dict, artist_name_spotify_cleaned_up)
        # Upload dict to aws s3
        result_s3_upload = upload_file(s3_client, json_file_output_location + json_file_output_name, s3_bucket_name, json_file_output_name)
    else:
        print('Status: Artist discography already up to date and stored in AWS s3')
    return artist_name_spotify

if __name__ == '__main__':
    run(artist_name_html_form)