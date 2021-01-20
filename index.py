# ------------------------------------- Imports
from flask import Flask, redirect, url_for, render_template, request, session     # Flask is an object of WSGI application 
from datetime import timedelta      # This is for setting how long session data should be stored for
import create_artist_nested_dict        # Python script
import add_analysis_to_nested_dict       # Python script
import json     # For saving the nested dictionary to json file, for upload in AWS s3
from itertools import islice    # For looping through n elements in a dictionary
import os   # For environment variables
import logging      # For AWS s3 file upload
import boto3      # For AWS s3 file upload
from botocore.exceptions import ClientError      # For AWS s3 file upload
# ------------------------------------- Functions
def get_artist_name_nested_dict_function(artist_master_dict):
    """
    Returns: Artist name
    """
    print('Status: Function Start:[get_artist_name_nested_dict_function]')
    artist_name = list(artist_master_dict.keys())[0]
    print('Status: Function End:[get_artist_name_nested_dict_function]. Result: artist name pulled')
    return artist_name
def get_album_information_nested_dict_function(artist_master_dict, artist_name_official_master_dict):
    """
    Returns: Album names from nested dict
    """
    print('Status: Function Start:[get_album_information_nested_dict_function]')
    album_information_tuple_arr = []
    for key_album_name, value_album_dict in artist_master_dict[artist_name_official_master_dict]['album_names_spotify'].items():
        # Pull the album information from the artist nested dict
        album_song_count = artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][key_album_name]['total_songs_spotify']
        album_images = artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][key_album_name]['album_image_spotify']
        album_information_tuple_arr.append((key_album_name, album_song_count, album_images))
    print('Status: Function End:[get_album_information_nested_dict_function]. Result: album name and album song count tuple arr complete')
    return album_information_tuple_arr
def get_artist_image_nested_dict_function(artist_master_dict, artist_name_official_master_dict):
    """
    Returns: Artist image from nested dict
    """
    artist_images = []
    print('Status: Function Start:[get_artist_image_nested_dict_function]')
    for key_artist_item, value_artist_item in artist_master_dict.items():
        for key_image_name  in artist_master_dict[artist_name_official_master_dict]['artist_image_spotify']:
            artist_images.append(key_image_name)
    print('Status: Function End:[get_artist_image_nested_dict_function]. Result: artist images')
    return artist_images
def get_artist_album_analysis_results(artist_master_dict, selected_albums_from_html_form, artist_name_official_master_dict):
    """
    Returns: Analysis for the selected albums and overall artist of those selected albums
    """
    print('Status: Function Start:[get_artist_album_analysis_results]')
    # If user 'selects all' albums
    if 'Select_All_Albums' in selected_albums_from_html_form:
        selected_albums_from_html_form = []
        for key_album_name, value_album_dict in artist_master_dict[artist_name_official_master_dict]['album_names_spotify'].items():
            selected_albums_from_html_form.append(key_album_name)
    # The values to pull from the master artist nested dict
    search_these_when_looping_arr = ['album_name', 'album_image_spotify', 'total_songs_spotify', 'album_release_date_spotify', 'album_lyrics_accuracy_score', 'album_artist_total_word_count_dict', 'album_artist_total_words_counted', 'album_artist_total_unique_words_counted']
    # Album level analysis on selected albums START
    # Array at all albums level
    all_selected_albums_album_level_analysis = []
    # Loop through the user selected albums
    for i_album_name in selected_albums_from_html_form:
        # Array at single album level
        album_level_analysis = []
        # Loop through artist master nested dict to find matching album name
        for key_album_name, value_album_dict in artist_master_dict[artist_name_official_master_dict]['album_names_spotify'].items():
            if key_album_name == i_album_name:
                # Loop through album nested dict and add all analysis points to an array
                for i_search_term in search_these_when_looping_arr:
                    album_key = i_search_term
                    if i_search_term == 'album_name':
                        album_value = key_album_name
                    else:
                        album_value = artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][key_album_name][i_search_term]
                        if i_search_term == 'album_lyrics_accuracy_score':
                            album_value = str(round(album_value * 100, 2)) + '%'
                    # Append to the single album level
                    album_level_analysis.append((album_key, album_value))
        # Append to the all albums level
        all_selected_albums_album_level_analysis.append(album_level_analysis)
    # Album level analysis on selected albums END
    # Artist level analysis on selected albums START
    # Compile all the selected album data into one for the artist summary
    all_selected_albums_artist_level_analysis = [
        ['total_songs_spotify', 0],
        ['album_lyrics_accuracy_score', 0],
        ['album_artist_total_word_count_dict', {}],
        ['album_artist_total_words_counted', 0],
        ['album_artist_total_unique_words_counted', 0],
        ['artist_total_albums_selected', len(all_selected_albums_album_level_analysis)] ]
    # Set variables to be put into the artist level analysis nested dict
    total_songs_spotify = 0
    album_lyrics_accuracy_score = 0
    album_artist_total_word_count_dict = {}
    album_artist_total_words_counted = 0
    album_artist_total_unique_words_counted = 0
    # Loop through the nested all seleceted albums level analysis
    for i_album_level_outer in all_selected_albums_album_level_analysis:
        for i_album_level_inner in i_album_level_outer:
            artist_key = i_album_level_inner[0]
            artist_value = i_album_level_inner[1]
            if artist_key == 'total_songs_spotify':
                total_songs_spotify += artist_value
                all_selected_albums_artist_level_analysis[0][1] = total_songs_spotify
            if artist_key == 'album_lyrics_accuracy_score':
                album_lyrics_accuracy_score += float(artist_value[:-1])
                all_selected_albums_artist_level_analysis[1][1] = str(round(album_lyrics_accuracy_score / len(selected_albums_from_html_form), 2)) + '%'
            if artist_key == 'album_artist_total_words_counted':
                album_artist_total_words_counted += artist_value
                all_selected_albums_artist_level_analysis[3][1] = album_artist_total_words_counted
            if artist_key == 'album_artist_total_word_count_dict':
                for i in artist_value:
                    album_artist_total_word_count_dict[i[0]] = album_artist_total_word_count_dict.get(i[0], 0) + i[1]
                all_selected_albums_artist_level_analysis[2][1] = album_artist_total_word_count_dict
            if artist_key == 'album_artist_total_unique_words_counted':
                album_artist_total_unique_words_counted = len(album_artist_total_word_count_dict.keys())
                all_selected_albums_artist_level_analysis[4][1] = album_artist_total_unique_words_counted
    # Artist level analysis on selected albums END
    print('Status: Function End:[get_artist_album_analysis_results]. Result: Album level and artist level analysis completed and stored in nested arr')
    return all_selected_albums_album_level_analysis, all_selected_albums_artist_level_analysis
def get_album_songs_analysis(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name):
    """
    Returns: Album songs analysis
    """
    print('Status: Function Start:[get_album_songs_analysis]')
    # The values to pull from the master artist nested dict
    search_these_when_looping_songs_arr = ['song_artist_total_word_count_dict', 'song_artist_total_words_counted', 'song_artist_total_unique_words_counted']
    all_album_songs_arr = []
    for k_song_name, v_song_name in artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][passed_in_selected_album_name]['album_songs_spotify'].items():
        one_song_arr = []
        k_song_element = 'song_name'
        v_song_element = k_song_name
        one_song_arr.append((k_song_element, v_song_element))
        for k_song_element_dict, v_song_element_dict in v_song_name.items():
            for i in search_these_when_looping_songs_arr:
                if k_song_element_dict == i:
                    one_song_arr.append((k_song_element_dict, v_song_element_dict))
        all_album_songs_arr.append(one_song_arr)
    print('Status: Function End:[get_album_songs_analysis]. Result: album analysis returned')
    return all_album_songs_arr
def get_album_image(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name):
    """
    Returns: Album image
    """
    print('Status: Function Start:[get_album_image]')
    image_links_arr = []
    for i in artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][passed_in_selected_album_name]['album_image_spotify']:
        image_links_arr.append(i)
    print('Status: Function End:[get_album_image]. Result: returned image links')
    return image_links_arr
def get_album_release_date(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name):
    """
    Returns: Album release date
    """
    print('Status: Function Start:[get_album_release_date]')
    album_release_date = artist_master_dict[artist_name_official_master_dict]['album_names_spotify'][passed_in_selected_album_name]['album_release_date_spotify']
    print('Status: Function End:[get_album_release_date]. Result: returned album_release_date')
    return album_release_date
def get_single_song_album_analysis(results_album_songs_level_analysis, song_name_selected_from_html):
    """
    Returns: single song arr
    """
    print('Status: Function Start:[get_single_song_album_analysis]')
    found_song_arr = []
    for i in results_album_songs_level_analysis:
        if i[0][1] == song_name_selected_from_html:
            found_song_arr = i
    print(found_song_arr)
    return found_song_arr
def get_artist_nested_dictionary(artist_name_from_session):
    """
    Returns: Artist master nested dict
    """
    print('Status: Function Start:[get_artist_nested_dictionary]')
    # Run python scripts for AWS s3
    artist_name_spotify = create_artist_nested_dict.run(artist_name_from_session)
    artist_master_dict = add_analysis_to_nested_dict.run(artist_name_spotify)
    print('Status: Function End:[get_artist_nested_dictionary]. Result: Pulled artist nested dict')
    return artist_master_dict
def get_artist_nested_dict_and_artist_name_call(artist_name_from_session):
    """
    Returns: Artist master nested dict and artist name
    """
    print('Status: Function Start:[get_artist_nested_dict_and_artist_name_call]')
    artist_master_dict = get_artist_nested_dictionary(artist_name_from_session)
    artist_name_official_master_dict = list(artist_master_dict.keys())[0]
    print('Status: Function End:[get_artist_nested_dict_and_artist_name_call]. Returns artist nested dict and artist name official')
    return artist_master_dict, artist_name_official_master_dict
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
def get_total_s3_hits(s3_object):
    """
    Args: s3_object, user_input_artist
    Returns: number of albums that artist has stored in s3
    """
    print('Status: Function Start:[get_total_s3_hits]')
    # This gets the data as a string type
    s3_data_as_str = s3_object['Body'].read().decode('utf-8')
    # Load data as dictionary
    s3_data_as_dict = json.loads(s3_data_as_str)
    total_hits = s3_data_as_dict['number_of_data_pulls_aws_s3']
    print('Status: Function End:[get_total_s3_hits]')
    return total_hits
def export_dictionary_as_json(data_pulls_dict):
    """
    Args: dictionary
    Returns: saves the dictionary as json file to specified location
    """
    print('Status: Function Start:[export_dictionary_as_json]')
    json_file_output_location = "/tmp/"
    json_file_output_name = 'aws_s3_access_counter.json'
    with open(json_file_output_location + json_file_output_name, "w") as outfile:
        json.dump(data_pulls_dict, outfile)
        print('Status: Function End:[export_dictionary_as_json]. Result: Successfully exported nested dictionary as JSON file')
        return json_file_output_location, json_file_output_name
    print('Status: Function End:[export_dictionary_as_json]. Result: Did not successfully export nested dictionary as JSON file')
    return False, False
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
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print('Status: Function End:[upload_file]. Result: Successfully uploaded file to AWS s3')
        return True
    except ClientError as e:
        logging.error(e)
        print('Status: Function End:[upload_file]. Result: Did not upload file to AWS s3')
        return False
    return 'none'
def aws_s3_hits_counter():
    """
    Returns: the amount of times that s3 was hit.
    """
    print('Status: Function Start:[aws_s3_hits_counter]')
    # Connect to s3
    s3_client = boto3.client('s3')
    # Look for object in s3
    s3_bucket_name = 'artistinformation'
    s3_file_name_full = 'aws_s3_access_counter.json'
    s3_object = search_if_artist_obj_in_s3(s3_client, s3_bucket_name, s3_file_name_full)
    if s3_object:
        total_hits = get_total_s3_hits(s3_object)
        # Add hits value
        total_hits += 1
        # Create a dictionary to re-upload into s3
        data_pulls_dict = {}
        data_pulls_dict['number_of_data_pulls_aws_s3'] = total_hits
        if total_hits < 2000:         # TOTAL HITS
            # Create as JSON
            json_file_output_location, json_file_output_name = export_dictionary_as_json(data_pulls_dict)
            # Upload information to s3
            upload_to_s3 = upload_file(s3_client, json_file_output_location + json_file_output_name, s3_bucket_name, json_file_output_name)
        return data_pulls_dict
# ------------------------------------- Webpages
# Flask constructor
app = Flask(__name__)
# To use a session, there has to be a secret key. The string should be something difficult to guess
app.secret_key = os.urandom(64)
# A decorator "@" is used to tell the application which URL uses which function
@app.route("/", methods=["POST", "GET"])
def home_page_function():
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[home_page_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    if request.method == "POST":
        # This request.form acts as a dictionary. Key: Value from HTML input tag
        artist_name_from_html_form = request.form["artist_name_html_form_to_python"]
        if artist_name_from_html_form == '':
            print('Status: Function End:[home_page_function]. Result: Did not find POST user input, remaining on current page')
            return render_template("home_page.html")
        # Set session variable, session acts like a dictionary
        session["session_key_artist_name_from_html_form"] = artist_name_from_html_form
        print('Status: Function End:[home_page_function]. Result: Found POST user input, redirecting webpage')
        # If POST input found then it will redirect to another webpage
        return redirect(url_for("artist_albums_page_redirect_function"))
    else:
        print('Status: Function End:[home_page_function]. Result: Did not find POST user input, remaining on current page')
        return render_template("home_page.html")
@app.route("/about")
def about_page_function():
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[about_page_function]')
    print('Status: Function End:[about_page_function]. Result: rendering page')
    return render_template("about_page.html")
@app.route("/artist_albums")
def artist_albums_page_redirect_function():
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[artist_albums_page_redirect_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    # Checking the session "dictionary"
    if "session_key_artist_name_from_html_form" in session:
        # Get input from user (for artist name)
        artist_name_from_session = session["session_key_artist_name_from_html_form"]
        artist_master_dict, artist_name_official_master_dict = get_artist_nested_dict_and_artist_name_call(artist_name_from_session)
        # Get the album overview information. Specific to this URL page only.
        album_information_tuple_arr = get_album_information_nested_dict_function(artist_master_dict, artist_name_official_master_dict)
        print('Status: Function End:[artist_albums_page_redirect_function]. Result: rendering page')
        return render_template("artist_albums_page.html",
                                album_information_tuple_arr_to_html = album_information_tuple_arr)
    else:
        print('Status: Function End:[artist_albums_page_redirect_function]. Result: There is no user input artist name stored in the session, redirects webpage back to home page')
        return redirect(url_for("home_page_function"))
@app.route('/analysis_albums_selected', methods=['GET', 'POST'])
def analysis_albums_selected_page_redirect_function():
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[analysis_albums_selected_page_redirect_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    if request.method == "POST":
        # Get the selected albums list
        selected_albums_from_html_form = request.form.getlist("album_names_selected_html_form_to_python")
        # If no albums were selected then user cannot move on
        if len(selected_albums_from_html_form) == 0:
            return redirect(url_for("artist_albums_page_redirect_function"))
        if "session_key_artist_name_from_html_form" in session:
            # Get input from user (for artist name)
            artist_name_from_session = session["session_key_artist_name_from_html_form"]
            artist_master_dict, artist_name_official_master_dict = get_artist_nested_dict_and_artist_name_call(artist_name_from_session)
            artist_images = get_artist_image_nested_dict_function(artist_master_dict, artist_name_official_master_dict)
            # If albums selected, loop through list and return the analysis points from nested dictionary
            all_selected_albums_album_level_analysis, all_selected_albums_artist_level_analysis = get_artist_album_analysis_results(artist_master_dict, selected_albums_from_html_form, artist_name_official_master_dict)
            # Loop through dict and get the first n elements of dict
            artist_top_10_word_count_arr = []
            for item in islice(all_selected_albums_artist_level_analysis[2][1].items(), 10):
                artist_top_10_word_count_arr.append(item)
            print('Status: Function End:[analysis_albums_selected_page_redirect_function]. Result: rendering page')
            return render_template("analysis_albums_selected_page.html",
                                    all_selected_albums_album_level_analysis_to_html = all_selected_albums_album_level_analysis,
                                    all_selected_albums_artist_level_analysis_to_html = all_selected_albums_artist_level_analysis,
                                    artist_name_official_master_dict_to_html = artist_name_official_master_dict,
                                    artist_images_to_html = artist_images,
                                    artist_top_10_word_count_arr_to_html = artist_top_10_word_count_arr)
        else:
            print('Status: Function End:[artist_albums_page_redirect_function]. Result: There is no user input artist name stored in the session, redirects webpage back to home page')
            return redirect(url_for("home_page_function"))
@app.route('/album_full_word_count_analysis', methods=['GET', 'POST'])
def album_full_word_count_function():
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[album_full_word_count_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    if request.method == "POST":
        checkbox_list_used = False
        selected_album_name_from_html_form = request.form.getlist("selected_album_artist_name_to_see_full_word_count_dict_from_html")
        if selected_album_name_from_html_form[0] == 'artist_word_count_summary_selected_html_form':
            checkbox_list_used = True
            checkbox_select_all_albums_default_from_html = request.form.getlist("checkbox_select_all_albums_default_from_html")
            selected_album_name_from_html_form = checkbox_select_all_albums_default_from_html
        if selected_album_name_from_html_form[0][:3] == 'rj~':
            selected_album_name_from_html_form[0] = selected_album_name_from_html_form[0][3:]
            return redirect(url_for("album_songs_full_word_count_function", passed_in_selected_album_name = selected_album_name_from_html_form[0]))
        if "session_key_artist_name_from_html_form" in session:
            # Get input from user (for artist name)
            artist_name_from_session = session["session_key_artist_name_from_html_form"]
            artist_master_dict, artist_name_official_master_dict = get_artist_nested_dict_and_artist_name_call(artist_name_from_session)
            artist_images = get_artist_image_nested_dict_function(artist_master_dict, artist_name_official_master_dict)
            # If albums selected, loop through list and return the analysis points from nested dictionary
            all_selected_albums_album_level_analysis, all_selected_albums_artist_level_analysis = get_artist_album_analysis_results(artist_master_dict, selected_album_name_from_html_form, artist_name_official_master_dict)
            print('Status: Function End:[album_full_word_count_function]. Result: rendering page')
            if checkbox_list_used == False:
                return render_template("album_word_count.html",
                                        all_selected_albums_album_level_analysis_to_html = all_selected_albums_album_level_analysis,
                                        all_selected_albums_artist_level_analysis_to_html = all_selected_albums_artist_level_analysis,
                                        artist_name_official_master_dict_to_html = artist_name_official_master_dict,
                                        artist_images_to_html = artist_images)
            else:
                return render_template("artist_word_count.html",
                                        all_selected_albums_album_level_analysis_to_html = all_selected_albums_album_level_analysis,
                                        all_selected_albums_artist_level_analysis_to_html = all_selected_albums_artist_level_analysis,
                                        artist_name_official_master_dict_to_html = artist_name_official_master_dict,
                                        artist_images_to_html = artist_images)
        else:
            print('Status: Function End:[album_full_word_count_function]. Result: There is no user input artist name stored in the session, redirects webpage back to home page')
            return redirect(url_for("home_page_function"))
@app.route('/album_songs_full_word_count_analysis/<passed_in_selected_album_name>', methods=['GET', 'POST'])
def album_songs_full_word_count_function(passed_in_selected_album_name):
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[album_songs_full_word_count_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    if "session_key_artist_name_from_html_form" in session:
        # Get input from user (for artist name)
        artist_name_from_session = session["session_key_artist_name_from_html_form"]
        artist_master_dict, artist_name_official_master_dict = get_artist_nested_dict_and_artist_name_call(artist_name_from_session)
        results_album_songs_level_analysis = get_album_songs_analysis(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name)
        image_links_arr = get_album_image(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name)
        album_release_date = get_album_release_date(artist_master_dict, artist_name_official_master_dict, passed_in_selected_album_name)
    else:
        print('Status: Function End:[album_songs_full_word_count_function]. Result: There is no user input artist name stored in the session, redirects webpage back to home page')
        return redirect(url_for("home_page_function"))
    return render_template("album_songs_word_count_overview_page.html",
                            results_album_songs_level_analysis_to_html = results_album_songs_level_analysis,
                            image_links_arr_to_html = image_links_arr,
                            passed_in_selected_album_name_to_html = passed_in_selected_album_name,
                            artist_name_official_master_dict_to_html = artist_name_official_master_dict,
                            album_release_date_to_html = album_release_date)
@app.route('/song_full_word_count_analysis/<album_name_passed_in_from_html>', methods=['GET', 'POST'])
def song_full_word_count_function(album_name_passed_in_from_html):
    """
    Returns: renders page for the URL decorator
    """
    print('Status: Function Start:[song_full_word_count_function]')
    # - - - - - - - Maintenance Start - - - - - - - - - -
    data_pulls_dict = aws_s3_hits_counter()
    if data_pulls_dict['number_of_data_pulls_aws_s3'] >= 2000:         # TOTAL HITS
        return render_template("maintenance_page.html")
    # - - - - - - - Maintenance End - - - - - - - - - -
    if request.method == "POST":
        song_name_selected_from_html = request.form['request_full_song_word_count_dict']
        # Get input from user (for artist name)
        artist_name_from_session = session["session_key_artist_name_from_html_form"]
        artist_master_dict, artist_name_official_master_dict = get_artist_nested_dict_and_artist_name_call(artist_name_from_session)
        results_album_songs_level_analysis = get_album_songs_analysis(artist_master_dict, artist_name_official_master_dict, album_name_passed_in_from_html)
        results_one_song_analysis = get_single_song_album_analysis(results_album_songs_level_analysis, song_name_selected_from_html)
        image_links_arr = get_album_image(artist_master_dict, artist_name_official_master_dict, album_name_passed_in_from_html)
        album_release_date = get_album_release_date(artist_master_dict, artist_name_official_master_dict, album_name_passed_in_from_html)
    else:
        print('Status: Function End:[song_full_word_count_function]. Result: There is no user input artist name stored in the session, redirects webpage back to home page')
        return redirect(url_for("home_page_function"))
    return render_template("album_songs_word_count_all_words_page.html",
                            artist_name_official_master_dict_to_html = artist_name_official_master_dict,
                            results_one_song_analysis_to_html = results_one_song_analysis,
                            image_links_arr_to_html = image_links_arr,
                            album_release_date_to_html = album_release_date,
                            album_name_to_html = album_name_passed_in_from_html )
#=============================================================================================================================== MAIN PROGRAM RUN
# Run the main program
if __name__ == "__main__":
    app.run(debug = True)