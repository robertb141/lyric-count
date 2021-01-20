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
    Args: None
    Returns: the connected library variables to allow the library functions
    """
    print('Status: Function Start:[access_libraries_function]')
    try:
        """
        # Connect to spotipy API library
        client_credentials_manager = SpotifyClientCredentials(client_id=os.environ.get('SPOTIFY_CLIENT_ID'), client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'))
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        """
        # Connect to genius API library
        genius = lyricsgenius.Genius(os.environ.get('GENIUS_ACCESS_TOKEN'))
        print('Status: Function End:[access_libraries_function]. Result: successfully connected to genius')
        #return sp, genius
        return genius
    except:
        print('Status: Function End:[access_libraries_function]. Result: did not connect to genius')
        return False
# --------------------------------------------------------- Functions: AWS s3
def get_artist_master_dict_from_s3(s3_client, s3_bucket_name, s3_file_name_full):
    """
    Returns: return artist object as nested dict
    """
    print('Status: Function Start:[get_artist_master_dict_from_s3]')
    try:
        # See if s3 object exists
        s3_object = s3_client.get_object(
            Bucket = s3_bucket_name, 
            Key = s3_file_name_full
        )
        s3_data_as_str = s3_object['Body'].read().decode('utf-8')
        s3_data_as_dict = json.loads(s3_data_as_str)
        print('Status: Function End:[get_artist_master_dict_from_s3]. Result: Success, artist obj found in s3 and returned as nested dict')
        return s3_data_as_dict
    except:
        print('Status: Function End:[get_artist_master_dict_from_s3]. Result: No, artist obj not found in s3')
        return False
def cleanup_artist_name_for_s3_saving(artist_name_input):
    """
    Returns: Removes special characters from artist name like beyoncÉ or jay-z or a$ap rocky
    """
    print('Status: Function Start:[cleanup_artist_name_for_s3_saving]')
    # remove all non alphanumeric and underscores from artist name and make it lower
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
def search_if_artist_obj_in_s3(s3_client, s3_bucket_name, s3_file_name_full):
    """
    Args: user_input_artist
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
def get_artist_total_word_count_s3(s3_object, user_input_artist):
    """
    Args: s3_object, user_input_artist
    Returns: number of albums that artist has stored in s3
    """
    print('Status: Function Start:[get_artist_total_word_count_s3]')
    # This gets the data as a string type
    s3_data_as_str = s3_object['Body'].read().decode('utf-8')
    # Load data as dictionary
    s3_data_as_dict = json.loads(s3_data_as_str)
    artist_total_word_count_s3 = s3_data_as_dict[user_input_artist]['artist_total_words_counted']
    print('Status: Function End:[get_artist_total_word_count_s3]. Result: Returned word count: ' + str(artist_total_word_count_s3))
    return artist_total_word_count_s3
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
# --------------------------------------------------------- Functions: dictionary manipulation
def check_if_artist_name_in_line_one(artist_name, song_part_line_one):
    """
    Returns: If the artist name is in the first line
    """
    #print('Status: Function Start:[check_if_artist_name_in_line_one]')
    # If the song part is just one word then it is usually safe to assume that the artist said it
    line_one_word_count = 1
    try:
        line_one_words_arr = song_part_line_one.split(' ')
        line_one_word_count = len(line_one_words_arr)
    except:
        pass
    # remove all non alphanumeric and underscores from artist name and make it lower
    pattern = re.compile(r'\W+')
    try:
        artist_name = re.sub(pattern, '', artist_name)
        # Remove all accents from letters. Example beyoncé --> beyonce
        try:
            artist_name = unidecode(artist_name)
        except:
            pass
    except:
        pass
    artist_name = artist_name.lower()
    # remove all non alphanumeric and underscores from line one and make it lower
    try:
        song_part_line_one = re.sub(pattern, '', song_part_line_one)
        # Remove all accents from letters. Example beyoncé --> beyonce
        try:
            song_part_line_one = unidecode(song_part_line_one)
        except:
            pass
    except:
        pass
    song_part_line_one = song_part_line_one.lower()
    # Search if within substring
    if re.search(artist_name, song_part_line_one):
        #print('Status: Function End:[check_if_artist_name_in_line_one]. Result: Artist name is in line 1')
        return True
    elif line_one_word_count == 1 or line_one_words_arr[-1][:-1].isnumeric():
        #print('Status: Function End:[check_if_artist_name_in_line_one]. Result: Line 1 is only 1 word, so assumed that it is the artist words')
        return True
    else:
        #print('Status: Function End:[check_if_artist_name_in_line_one]. Result: Artist name not in line 1')
        return False
def check_change_if_word_starts_ends_with_special_characters(word):
    """
    Returns: If a word starts or ends with special characters, return the word without them
    """
    special_chars_arr = ['"', "'", ',', '.', '!', '?', '-', '(', ')', ';', ':', '*', '/']
    while (len(word) != 0 and word[0] in special_chars_arr) or (len(word) != 0 and word[-1] in special_chars_arr):
        if len(word) != 0 and word[0] in special_chars_arr:
            word = word[1:]
        if len(word) != 0 and word[-1] in special_chars_arr:
            word = word[:-1]
    return word
def get_artist_words_only_from_song(song_lyrics_original, artist_name):
    """
    Returns: only the artists words in a song
    """
    print('Status: Function Start:[get_artist_words_only_from_song]')
    # Words said only by the artist array
    song_level_words_artist_only_arr = []
    song_level_words_unique_artist_only_arr = []
    # Separate by song part
    song_parts_separated_arr = song_lyrics_original.split('[')
    # If the song cannot be split into parts
    if len(song_parts_separated_arr) == 1:
        print('status: song parts = 1 when checking for [] parts')
        # for a song that does not start with '[]' in the first line. Example: Jay-Z Versus Interlude song and Beach is Better
        song_part_lines_separated_arr = song_lyrics_original.split('\n')
        # Clean up the song parts to get rid of the \u - unidecode within words and lines
        for i in range(len(song_part_lines_separated_arr)):
            try:
                song_part_lines_separated_arr[i] = unidecode(song_part_lines_separated_arr[i])
            except:
                pass
        for song_line in song_part_lines_separated_arr:
            # Seperate song line by song word
            song_part_words_separated_arr = song_line.split(' ')
            for word in song_part_words_separated_arr:
                if len(word) == 0:
                    continue
                word = check_change_if_word_starts_ends_with_special_characters(word)
                # Add to the word arrays
                word = word.lower()
                song_level_words_artist_only_arr.append(word)
                if word not in song_level_words_unique_artist_only_arr:
                    song_level_words_unique_artist_only_arr.append(word)
    # If the song is in fact split into parts, most of the time this is the case
    else:
        # Clean up the song parts to get rid of the \u - unidecode within words and lines
        for i in range(len(song_parts_separated_arr)):
            try:
                song_parts_separated_arr[i] = unidecode(song_parts_separated_arr[i])
            except:
                pass
        # Loop through the cleaned song parts
        for song_part in song_parts_separated_arr:
            # Separate song part by song line
            song_part_lines_separated_arr = song_part.split('\n')
            for song_line in song_part_lines_separated_arr[1:]:
                # Check if artist name is in the song part first line
                artist_name_in_line_one = check_if_artist_name_in_line_one(artist_name, song_part_lines_separated_arr[0])
                if artist_name_in_line_one:
                    # Seperate song line by song word
                    song_part_words_separated_arr = song_line.split(' ')
                    for word in song_part_words_separated_arr:
                        if len(word) == 0:
                            continue
                        word = check_change_if_word_starts_ends_with_special_characters(word)
                        # Add to the word arrays
                        word = word.lower()
                        song_level_words_artist_only_arr.append(word)
                        if word not in song_level_words_unique_artist_only_arr:
                            song_level_words_unique_artist_only_arr.append(word)
    print('Status: Function END:[get_artist_words_only_from_song]. Result: array with only the song words from artist')
    return song_level_words_artist_only_arr, song_level_words_unique_artist_only_arr
def get_song_word_count_dict(song_level_words_artist_only_arr):
    """
    Returns: word count dictionary
    """
    dict = {}
    for word in song_level_words_artist_only_arr: 
        dict[word] = dict.get(word, 0) + 1
    #return dictin reverse count order
    return sorted(dict.items(), key=lambda x: x[1], reverse=True)
def loop_through_album_insert_lyric_word_count_info(artist_master_dict):
    """
    Returns: The song with only artist words in an array
    """
    print('Status: Function Start:[loop_through_album_insert_lyric_word_count_info]')
    # Access AWS comprehend
    #s3_client_comprehend = boto3.client('comprehend')
    artist_name = list(artist_master_dict.keys())[0]
    # Loop through artist dictionary
    for key_artist_item, value_artist_item in artist_master_dict.items():
        print('key_artist_item: ' + key_artist_item)
        # For every newly looped artist (only 1 in this case) set these arrays to blank
        artist_level_words_artist_only_arr = []
        artist_level_words_unique_artist_only_arr = []
        # artist_level_sentiment_analysis_total_positive = 0
        # artist_level_sentiment_analysis_total_negative = 0
        # artist_level_sentiment_analysis_total_neutral = 0
        # artist_level_sentiment_analysis_total_mixed = 0
        num_albums_with_artist = 0
        # Loop through every album dict
        for key_album_name, value_album_dict in artist_master_dict[artist_name]['album_names_spotify'].items():
            print('key_album_name: ' + key_album_name)
            # For every newly looped album set these arrays to blank
            album_level_words_artist_only_arr = []
            album_level_words_unique_artist_only_arr = []
            # album_level_sentiment_analysis_total_positive = 0
            # album_level_sentiment_analysis_total_negative = 0
            # album_level_sentiment_analysis_total_neutral = 0
            # album_level_sentiment_analysis_total_mixed = 0
            num_songs_with_artist = 0
            # Loop through every song dict
            for key_song_name, value_song_dict in value_album_dict['album_songs_spotify'].items():
                print('- - - new song - - -')
                print('key_song_name: ' + key_song_name)
                try:
                    # Loop through every song dict, lyrics array
                    for song_lyrics_original in value_song_dict['song_lyrics_original']:
                        # Get the song words arr and unique song words arr for only the artist in the song (no features)
                        song_level_words_artist_only_arr, song_level_words_unique_artist_only_arr = get_artist_words_only_from_song(song_lyrics_original, artist_name)
                        # Append the word analysis at the song level
                        value_song_dict['song_artist_lyrics_cleaned_up'] = song_level_words_artist_only_arr
                        value_song_dict['song_artist_total_words_counted'] = len(song_level_words_artist_only_arr)
                        value_song_dict['song_artist_total_unique_words_counted'] = len(song_level_words_unique_artist_only_arr)
                        song_word_count_dict = get_song_word_count_dict(song_level_words_artist_only_arr)
                        value_song_dict['song_artist_total_word_count_dict'] = song_word_count_dict
                        # Append the word analysis at the album level
                        value_album_dict['album_artist_total_words_counted'] += len(song_level_words_artist_only_arr)
                        for word in song_level_words_artist_only_arr:
                            album_level_words_artist_only_arr.append(word)
                        for word in song_level_words_unique_artist_only_arr:
                            if word not in album_level_words_unique_artist_only_arr:
                                album_level_words_unique_artist_only_arr.append(word)
                        # Append the word analysis at the artist level
                        artist_master_dict[artist_name]['artist_total_words_counted'] += len(song_level_words_artist_only_arr)
                        for word in song_level_words_artist_only_arr:
                            artist_level_words_artist_only_arr.append(word)
                        for word in song_level_words_unique_artist_only_arr:
                            if word not in artist_level_words_unique_artist_only_arr:
                                artist_level_words_unique_artist_only_arr.append(word)
                        # Get sentiment analysis of the song
                        # song_level_words_one_long_string = ' '.join(song_level_words_artist_only_arr)
                        # if len(song_level_words_one_long_string) != 0:
                            # Get the song sentiment analysis
                            # song_level_sentiment_score = get_song_lyrics_sentiment_score(s3_client_comprehend, song_level_words_one_long_string)
                            # value_song_dict['song_artist_sentiment_analysis'] = song_level_sentiment_score
                            # Add to get total sum of album sentiment analysis
                            # album_level_sentiment_analysis_total_positive += value_song_dict['song_artist_sentiment_analysis']['Positive']
                            # album_level_sentiment_analysis_total_negative += value_song_dict['song_artist_sentiment_analysis']['Negative']
                            # album_level_sentiment_analysis_total_neutral += value_song_dict['song_artist_sentiment_analysis']['Neutral']
                            # album_level_sentiment_analysis_total_mixed += value_song_dict['song_artist_sentiment_analysis']['Mixed']
                            # num_songs_with_artist += 1
                except:
                    continue
            # Append the word analysis at the album level
            value_album_dict['album_artist_total_unique_words_counted'] = len(album_level_words_unique_artist_only_arr)
            album_word_count_dict = get_song_word_count_dict(album_level_words_artist_only_arr)
            value_album_dict['album_artist_total_word_count_dict'] = album_word_count_dict
            # Assign the album level sentiment analysis
            # value_album_dict['album_artist_sentiment_analysis']['Positive'] = album_level_sentiment_analysis_total_positive / num_songs_with_artist
            # value_album_dict['album_artist_sentiment_analysis']['Negative'] = album_level_sentiment_analysis_total_negative / num_songs_with_artist
            # value_album_dict['album_artist_sentiment_analysis']['Neutral'] = album_level_sentiment_analysis_total_neutral / num_songs_with_artist
            # value_album_dict['album_artist_sentiment_analysis']['Mixed'] = album_level_sentiment_analysis_total_mixed / num_songs_with_artist
            # Add to the total artist level sentiment analysis
            # artist_level_sentiment_analysis_total_positive += value_album_dict['album_artist_sentiment_analysis']['Positive']
            # artist_level_sentiment_analysis_total_negative += value_album_dict['album_artist_sentiment_analysis']['Negative']
            # artist_level_sentiment_analysis_total_neutral += value_album_dict['album_artist_sentiment_analysis']['Neutral']
            # artist_level_sentiment_analysis_total_mixed += value_album_dict['album_artist_sentiment_analysis']['Mixed']
            # num_albums_with_artist += 1
        # Append the word analysis at the artist level
        value_artist_item['artist_total_unique_words_counted'] = len(artist_level_words_unique_artist_only_arr)
        artist_word_count_dict = get_song_word_count_dict(artist_level_words_artist_only_arr)
        # Assign the artist level sentiment analysis
        # value_artist_item['artist_total_word_count_dict'] = artist_word_count_dict
        # value_artist_item['artist_sentiment_analysis']['Positive'] = artist_level_sentiment_analysis_total_positive / num_albums_with_artist
        # value_artist_item['artist_sentiment_analysis']['Negative'] = artist_level_sentiment_analysis_total_negative / num_albums_with_artist
        # value_artist_item['artist_sentiment_analysis']['Neutral'] = artist_level_sentiment_analysis_total_neutral / num_albums_with_artist
        # value_artist_item['artist_sentiment_analysis']['Mixed'] = artist_level_sentiment_analysis_total_mixed / num_albums_with_artist
    print('Status: Function END:[loop_through_album_insert_lyric_word_count_info]. Result: Inserted Array of words only spoken by the artist into the nested dictionary array')
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
#=============================================================================================================================== MAIN PROGRAM RUN
def run(artist_name_html_form):
    # Create AWS s3 client
    s3_client = boto3.client('s3')
    user_input_artist = artist_name_html_form
    # Clean up the artist name for saving into s3
    artist_name_spotify_cleaned_up = cleanup_artist_name_for_s3_saving(user_input_artist)
    # Check if artist is already stored in s3
    s3_bucket_name = 'artistinformation'
    s3_file_name_prefix = 'output_spotify_genius_nested_dict_'
    s3_file_name_full = s3_file_name_prefix + artist_name_spotify_cleaned_up + '.json'
    s3_object = search_if_artist_obj_in_s3(s3_client, s3_bucket_name, s3_file_name_full)
    artist_total_word_count_s3 = 0
    if s3_object:
        artist_total_word_count_s3 = get_artist_total_word_count_s3(s3_object, user_input_artist)
        if artist_total_word_count_s3 != 0:
            print('File already in s3, returning nested dict')
            artist_master_dict = get_artist_master_dict_from_s3(s3_client, s3_bucket_name, s3_file_name_full)
        else:
            # Pull the artist master nested dictionary from AWS s3
            artist_master_dict = get_artist_master_dict_from_s3(s3_client, s3_bucket_name, s3_file_name_full)
            # Go into each song and clean up the lyrics
            loop_through_album_insert_lyric_word_count_info(artist_master_dict)
            # Export nested dictionary to json file
            json_file_output_location, json_file_output_name = export_dictionary_as_json(artist_master_dict, artist_name_spotify_cleaned_up)
            # Upload dict to aws s3
            result_s3_upload = upload_file(s3_client, json_file_output_location + json_file_output_name, s3_bucket_name, json_file_output_name)
    else:
        artist_master_dict = 'File AA03_combined, not successfully updated for this artist'
    return artist_master_dict

if __name__ == '__main__':
    run(artist_name_html_form)