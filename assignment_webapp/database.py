#!/usr/bin/env python3
"""
MediaServer Database module.
Contains all interactions between the webapp and the queries to the database.
"""

import configparser
import json
import sys
from modules import pg8000

################################################################################
#   Welcome to the database file, where all the query magic happens.
#   My biggest tip is look at the *week 8 lab*.
#   Important information:
#       - If you're getting issues and getting locked out of your database.
#           You may have reached the maximum number of connections.
#           Why? (You're not closing things!) Be careful!
#       - Check things *carefully*.
#       - There may be better ways to do things, this is just for example
#           purposes
#       - ORDERING MATTERS
#           - Unfortunately to make it easier for everyone, we have to ask that
#               your columns are in order. WATCH YOUR SELECTS!! :)
#   Good luck!
#       And remember to have some fun :D
################################################################################

#############################
#                           #
# Database Helper Functions #
#                           #
#############################


#####################################################
#   Database Connect
#   (No need to touch
#       (unless the exception is potatoing))
#####################################################

def database_connect():
    """
    Connects to the database using the connection string.
    If 'None' was returned it means there was an issue connecting to
    the database. It would be wise to handle this ;)
    """
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'database' not in config['DATABASE']:
        config['DATABASE']['database'] = config['DATABASE']['user']

    # Create a connection to the database
    connection = None
    try:
        # Parses the config file and connects using the connect string
        connection = pg8000.connect(database=config['DATABASE']['database'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as operation_error:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(operation_error)
        return None

    # return the connection to use
    return connection

##################################################
# Print a SQL string to see how it would insert  #
##################################################

def print_sql_string(inputstring, params=None):
    """
    Prints out a string as a SQL string parameterized assuming all strings
    """

    if params is not None:
        if params != []:
           inputstring = inputstring.replace("%s","'%s'")
    
    print(inputstring % params)

#####################################################
#   SQL Dictionary Fetch
#   useful for pulling particular items as a dict
#   (No need to touch
#       (unless the exception is potatoing))
#   Expected return:
#       singlerow:  [{col1name:col1value,col2name:col2value, etc.}]
#       multiplerow: [{col1name:col1value,col2name:col2value, etc.}, 
#           {col1name:col1value,col2name:col2value, etc.}, 
#           etc.]
#####################################################

def dictfetchall(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    
    result = []
    if (params is None):
        print(sqltext)
    else:
        print("we HAVE PARAMS!")
        print_sql_string(sqltext,params)
    
    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    print(cols)
    returnres = cursor.fetchall()
    for row in returnres:
        result.append({a:b for a,b in zip(cols, row)})
    # cursor.close()
    return result

def dictfetchone(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    # cursor = conn.cursor()
    result = []
    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    returnres = cursor.fetchone()
    result.append({a:b for a,b in zip(cols, returnres)})
    return result



#####################################################
#   Query (1)
#   Login
#####################################################

def check_login(username, password):
    """
    Check that the users information exists in the database.
        - True => return the user data
        - False => return None
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT * FROM mediaserver.useraccount
        WHERE username = %s AND password = %s;
        """
        print(username)
        print(password)

        r = dictfetchone(cur,sql,(username,password))
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Is Superuser? - 
#   is this required? we can get this from the login information
#####################################################

def is_superuser(username):
    """
    Check if the user is a superuser.
        - True => Get the departments as a list.
        - False => Return None
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT isSuper
                 FROM mediaserver.useraccount
                 WHERE username=%s AND isSuper"""
        print("username is: "+username)
        cur.execute(sql, (username))
        r = cur.fetchone()              # Fetch the first row
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 b)
#   Get user playlists
#####################################################
def user_playlists(username):
    """
    Check if user has any playlists
        - True -> Return all user playlists
        - False -> Return None
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT M.collection_id, M.collection_name, COUNT(MS.media_id) AS count
        FROM mediaserver.mediacollection M NATURAL JOIN mediaserver.mediaCollectionContents MS
        WHERE username = %s
        GROUP BY M.collection_id, M.collection_name;
        """

        print("username is: "+username)
        r = dictfetchall(cur,sql,(username,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Playlists:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 a)
#   Get user podcasts
#####################################################
def user_podcast_subscriptions(username):
    """
    Get user podcast subscriptions.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
        FROM mediaserver.Podcast NATURAL JOIN mediaserver.Subscribed_Podcasts NATURAL JOIN mediaserver.UserAccount
        WHERE username = %s;
        """

        r = dictfetchall(cur,sql,(username,))
        print("return val is:")
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast subs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 c)
#   Get user in progress items
#####################################################
def user_in_progress_items(username):
    """
    Get user in progress items that aren't 100%
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
        FROM mediaserver.mediaitem NATURAL JOIN mediaserver.usermediaconsumption UM
        WHERE UM.username = %s AND progress <> 0 AND progress <> 100;
        """

        r = dictfetchall(cur,sql,(username,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting User Consumption - Likely no values:", sys.exc_info()[0])
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all artists
#####################################################
def get_allartists():
    """
    Get all the artists in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # Try executing the SQL and get from the database
        sql = """select 
            a.artist_id, a.artist_name, count(amd.md_id) as count
        from 
            mediaserver.artist a left outer join mediaserver.artistmetadata amd on (a.artist_id=amd.artist_id)
        group by a.artist_id, a.artist_name
        order by a.artist_name;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Artists:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all songs
#####################################################
def get_allsongs():
    """
    Get all the songs in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # Try executing the SQL and get from the database
        sql = """select 
            s.song_id, s.song_title, string_agg(saa.artist_name,',') as artists
        from 
            mediaserver.song s left outer join 
            (mediaserver.Song_Artists sa join mediaserver.Artist a on (sa.performing_artist_id=a.artist_id)
            ) as saa  on (s.song_id=saa.song_id)
        group by s.song_id, s.song_title
        order by s.song_id"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all podcasts
#####################################################
def get_allpodcasts():
    """
    Get all the podcasts in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select 
                p.*, pnew.count as count  
            from 
                mediaserver.podcast p, 
                (select 
                    p1.podcast_id, count(*) as count 
                from 
                    mediaserver.podcast p1 left outer join mediaserver.podcastepisode pe1 on (p1.podcast_id=pe1.podcast_id) 
                    group by p1.podcast_id) pnew 
            where p.podcast_id = pnew.podcast_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcasts:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Get all albums
#####################################################
def get_allalbums():
    """
    Get all the Albums in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select 
                a.album_id, a.album_title, anew.count as count, anew.artists
            from 
                mediaserver.album a, 
                (select 
                    a1.album_id, count(distinct as1.song_id) as count, array_to_string(array_agg(distinct ar1.artist_name),',') as artists
                from 
                    mediaserver.album a1 
			left outer join mediaserver.album_songs as1 on (a1.album_id=as1.album_id) 
			left outer join mediaserver.song s1 on (as1.song_id=s1.song_id)
			left outer join mediaserver.Song_Artists sa1 on (s1.song_id=sa1.song_id)
			left outer join mediaserver.artist ar1 on (sa1.performing_artist_id=ar1.artist_id)
                group by a1.album_id) anew 
            where a.album_id = anew.album_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Albums:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Query (3 a,b c)
#   Get all tvshows
#####################################################
def get_alltvshows():
    """
    Get all the TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT tvshow_id, tvshow_title, COUNT(episode)
        FROM mediaserver.TVShow NATURAL JOIN mediaserver.TVEpisode
        GROUP BY tvshow_id;
        """

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all movies
#####################################################
def get_allmovies():
    """
    Get all the Movies in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select 
            m.movie_id, m.movie_title, m.release_year, count(mimd.md_id) as count
        from 
            mediaserver.movie m left outer join mediaserver.mediaitemmetadata mimd on (m.movie_id = mimd.media_id)
        group by m.movie_id, m.movie_title, m.release_year
        order by movie_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one artist
#####################################################
def get_artist(artist_id):
    """
    Get an artist by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select *
        from mediaserver.artist a left outer join 
            (mediaserver.artistmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) amd
        on (a.artist_id=amd.artist_id)
        where a.artist_id=%s"""

        r = dictfetchall(cur,sql,(artist_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Artist with ID: '"+artist_id+"'", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (2 a,b,c)
#   Get one song
#####################################################
def get_song(song_id):
    """
    Get a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #  
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about a song    #
        # and the artists that performed it                                         #
        #############################################################################
        sql = """
        SELECT song_id, song_title, string_agg(artist_name,',') AS artists, length, md_value, md_type_name
                FROM mediaserver.Artist A
                    JOIN mediaserver.Song_Artists SA
                        ON (A.artist_id = SA.performing_artist_id)
                    NATURAL JOIN mediaserver.Song
                    NATURAL JOIN mediaserver.ArtistMetaData
                    NATURAL JOIN mediaserver.MetaData
                    NATURAL JOIN mediaserver.MetaDataType
                WHERE song_id = %s
                GROUP BY song_id, song_title, length, md_value, md_type_name;
        """

        r = dictfetchall(cur,sql,(song_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (2 d)
#   Get metadata for one song
#####################################################
def get_song_metadata(song_id):
    """
    Get the meta for a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
        FROM mediaserver.metadata 
            NATURAL JOIN mediaserver.metadatatype 
            NATURAL JOIN mediaserver.mediaitemmetadata m
        WHERE m.media_id = %s;
        """

        r = dictfetchall(cur,sql,(song_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting song metadata for ID: "+song_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (6 a,b,c,d,e)
#   Get one podcast and return all metadata associated with it
#####################################################
def get_podcast(podcast_id):
    """
    Get a podcast by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT podcast_id, podcast_title, podcast_uri, podcast_last_updated, md_value, md_type_name, md_id
        FROM mediaserver.podcast 
            NATURAL JOIN mediaserver.podcastmetadata 
            NATURAL JOIN mediaserver.metadata 
            NATURAL JOIN mediaserver.MetaDataType
        WHERE podcast_id = %s;
        """

        r = dictfetchall(cur,sql,(podcast_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (6 f)
#   Get all podcast eps for one podcast
#####################################################
def get_all_podcasteps_for_podcast(podcast_id):
    """
    Get all podcast eps for one podcast by their podcast ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT media_id, podcast_episode_title, podcast_episode_URI, podcast_episode_published_date, podcast_episode_length
        FROM mediaserver.PodcastEpisode
        WHERE podcast_id = %s
        ORDER BY podcast_episode_published_date DESC;
        """

        r = dictfetchall(cur,sql,(podcast_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcast Episodes for Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (7 a,b,c,d,e,f)
#   Get one podcast ep and associated metadata
#####################################################
def get_podcastep(podcastep_id):
    """
    Get a podcast ep by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
            SELECT media_id, podcast_episode_title, podcast_episode_URI, podcast_episode_published_date, podcast_episode_length, md_value, md_type_name, md_id
            FROM mediaserver.PodcastEpisode 
                NATURAL JOIN mediaserver.AudioMedia 
                NATURAL JOIN mediaserver.MediaItemMetaData 
                NATURAL JOIN mediaserver.Metadata 
                NATURAL JOIN mediaserver.MetaDataType
            WHERE media_id = %s;
        """

        r = dictfetchall(cur,sql,(podcastep_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast Episode with ID: "+podcastep_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 a,b)
#   Get one album
#####################################################
def get_album(album_id):
    """
    Get an album by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
        FROM mediaserver.album
            NATURAL JOIN mediaserver.albummetadata
            NATURAL JOIN mediaserver.metadata
            NATURAL JOIN mediaserver.metadatatype
        WHERE album_id = %s;
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 d)
#   Get all songs for one album
#####################################################
def get_album_songs(album_id):
    """
    Get all songs for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT song_id, song_title, artist_name
        FROM (mediaserver.album_songs 
            NATURAL JOIN mediaserver.song 
            NATURAL JOIN mediaserver.Song_Artists) 
            JOIN mediaserver.Artist 
                ON (performing_artist_id = artist_id)
        WHERE album_id = %s;
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums songs with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 c)
#   Get all genres for one album
#####################################################
def get_album_genres(album_id):
    """
    Get all genres for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT DISTINCT md_value, md_type_name, album_title, md_id
        FROM mediaserver.album 
            NATURAL JOIN mediaserver.album_songs 
            NATURAL JOIN mediaserver.Song S
            JOIN mediaserver.MediaItemMetaData M 
                ON S.song_id = M.media_id
            NATURAL JOIN mediaserver.metadatatype
            NATURAL JOIN mediaserver.metadata
        WHERE album_id = %s;
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums genres with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   May require the addition of SQL to multiple 
#   functions and the creation of a new function to
#   determine what type of genre is being provided
#   You may have to look at the hard coded values
#   in the sampledata to make your choices
#####################################################

#####################################################
#   Query (10)
#   Get all songs for one song_genre
#####################################################
def check_genre_type(genre_type_id):
    """
    Get all songs for a particular song_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT md_type_name
        FROM mediaserver.MetaDataType 
            NATURAL JOIN mediaserver.MetaData 
        WHERE md_id = %s;
        """

        r = dictfetchall(cur,sql,(genre_type_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting type with Genre ID: "+genre_type_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def get_genre_songs(genre_id):
    """
    Get all songs for a particular song_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT distinct song_id , song_title 
        FROM mediaserver.Song JOIN mediaserver.AudioMedia on (song_id = media_id) NATURAL JOIN mediaserver.MediaItem
            NATURAL JOIN mediaserver.MediaItemMetaData NATURAL JOIN mediaserver.MetaData NATURAL JOIN mediaserver.MetaDataType
        WHERE md_id = %s;
        """

        r = dictfetchall(cur,sql,(genre_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Songs with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   Get all podcasts for one podcast_genre
#####################################################
def get_genre_podcasts(genre_id):
    """
    Get all podcasts for a particular podcast_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT distinct podcast_id , podcast_title 
        FROM mediaserver.Podcast
            NATURAL JOIN mediaserver.podcastmetadata
            NATURAL JOIN mediaserver.MetaData 
            NATURAL JOIN mediaserver.MetaDataType
        WHERE  md_id = %s;
        """

        r = dictfetchall(cur,sql,(genre_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcasts with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (10)
#   Get all movies and tv shows for one film_genre
#####################################################
def get_genre_movies(genre_id):
    """
    Get all movies and tv shows for a particular film_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT distinct movie_id , movie_title
        FROM mediaserver.Movie 
            NATURAL JOIN mediaserver.VideoMedia 
            NATURAL JOIN mediaserver.MediaItem 
            NATURAL JOIN mediaserver.MetaData 
            NATURAL JOIN mediaserver.MetaDataType
        WHERE md_id = %s;
        """

        r = dictfetchall(cur,sql,(genre_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Movies with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def get_genre_shows(genre_id):
    """
    Get all movies and tv shows for a particular film_genre ID in your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT distinct tvshow_id, tvshow_title
        FROM mediaserver.MediaItem NATURAL JOIN mediaserver.MetaData NATURAL JOIN mediaserver.MetaDataType NATURAL JOIN mediaserver.TVShowMetaData NATURAL JOIN mediaserver.TVShow
        WHERE md_id = %s;
        """

        r = dictfetchall(cur,sql,(genre_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting tv shows with Genre ID: "+genre_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################

#   Get all genres
#####################################################
def get_allgenres():
    """
    Get all the TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
        FROM mediaserver.MetaData ;
        """

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (4 a,b)
#   Get one tvshow
#####################################################
def get_tvshow(tvshow_id):
    """
    Get one tvshow in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT *
                FROM mediaserver.TVShow
                    NATURAL JOIN mediaserver.TVShowMetaData
                    NATURAL JOIN mediaserver.MetaData
                    NATURAL JOIN mediaserver.MetaDataType
                WHERE tvshow_id = %s;
        """

        r = dictfetchall(cur,sql,(tvshow_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (4 c)
#   Get all tv show episodes for one tv show
#####################################################
def get_all_tvshoweps_for_tvshow(tvshow_id):
    """
    Get all tvshow episodes for one tv show in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT media_id, tvshow_episode_title, season, episode, air_date
        FROM mediaserver.tvepisode
        WHERE tvshow_id =%s
        ORDER BY season;
        """

        r = dictfetchall(cur,sql,(tvshow_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one tvshow episode
#####################################################
def get_tvshowep(tvshowep_id):
    """
    Get one tvshow episode in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select * 
        from mediaserver.TVEpisode te left outer join 
            (mediaserver.mediaitemmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) temd
            on (te.media_id=temd.media_id)
        where te.media_id = %s"""

        r = dictfetchall(cur,sql,(tvshowep_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################

#   Get one movie
#####################################################
def get_movie(movie_id):
    """
    Get one movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select *
        from mediaserver.movie m left outer join 
            (mediaserver.mediaitemmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) mmd
        on (m.movie_id=mmd.media_id)
        where m.movie_id=%s;"""

        r = dictfetchall(cur,sql,(movie_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Find all matching tvshows
#####################################################
def find_matchingtvshows(searchterm,searchterm_c):
    """
    Get all the matching TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    #cur_copy = "%" + str(searchterm_c) + "%"

    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT t.*, tnew.count AS count, string_agg(md_value,',') as md_value
        FROM mediaserver.tvshow t,
             (SELECT t1.tvshow_id, count(te1.media_id) AS count, md_value, md_type_name
              FROM mediaserver.tvshow t1 NATURAL JOIN mediaserver.TVEpisode te1 NATURAL JOIN mediaserver.tvshowmetadata NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
              GROUP BY t1.tvshow_id, md_value, md_type_name) tnew
        WHERE t.tvshow_id = tnew.tvshow_id AND (lower(tvshow_title) ~ lower(%s) OR DIFFERENCE(lower(tvshow_title), lower(%s)) > 2) AND md_type_name = 'film genre'
        GROUP BY t.tvshow_id, t.tvshow_title, count
        ORDER BY t.tvshow_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchterm_c,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def filter_tvshows_ep_count(searchterm, searchterm_c, input, genre_input):

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    #cur_copy = "%" + str(searchterm_c) + "%"

    try:
        sql = """
        SELECT t.*, tnew.count AS count, string_agg(md_value,',') as md_value
        FROM mediaserver.tvshow t,
            (SELECT t1.tvshow_id, count(te1.media_id) AS count, md_value, md_type_name
             FROM mediaserver.tvshow t1 NATURAL JOIN mediaserver.TVEpisode te1 NATURAL JOIN mediaserver.tvshowmetadata NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
             GROUP BY t1.tvshow_id, md_value, md_type_name) tnew
        WHERE t.tvshow_id = tnew.tvshow_id AND (lower(tvshow_title) ~ lower(%s) OR DIFFERENCE(lower(tvshow_title), lower(%s)) > 2) AND md_type_name = 'film genre' AND count > %s AND md_value = lower(%s)
        GROUP BY t.tvshow_id, t.tvshow_title, count
        ORDER BY t.tvshow_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchterm_c,input,genre_input,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (9)
#   Find all matching Movies
#####################################################
def find_matchingmovies(searchterm, searchtermCopy):

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    #cur_copy = "%" + str(searchtermCopy) + "%"
    try:
        sql = """
        SELECT m.movie_id, m.movie_title, m.release_year, string_agg(md_value,',') as md_value
                FROM mediaserver.movie m JOIN mediaserver.VideoMedia me1 ON (m.movie_id=me1.media_id)
                NATURAL JOIN mediaserver.mediaitem NATURAL JOIN mediaserver.mediaitemmetadata
                NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
        WHERE (lower(movie_title) ~ lower(%s) OR DIFFERENCE(lower(movie_title), lower(%s)) > 2)
        	AND md_type_name = 'film genre'
        GROUP BY m.movie_id, m.movie_title, m.release_year
        ORDER BY m.movie_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchtermCopy,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def filter_date(searchterm, searchterm_c, input, genre_input):

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    #cur_copy = "%" + str(searchterm_c) + "%"

    try:
        sql = """
        SELECT m.movie_id, m.movie_title, m.release_year, string_agg(md_value,',') as md_value
                FROM mediaserver.movie m JOIN mediaserver.VideoMedia me1 ON (m.movie_id=me1.media_id)
                NATURAL JOIN mediaserver.mediaitem NATURAL JOIN mediaserver.mediaitemmetadata
                NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
        WHERE (lower(movie_title) ~ lower(%s) OR DIFFERENCE(lower(movie_title), lower(%s)) > 2)
        	AND m.release_year > %s
        	AND md_type_name = 'film genre'
        	AND md_value = lower(%s)
        GROUP BY m.movie_id, m.movie_title, m.release_year
        ORDER BY m.movie_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchterm_c,input,genre_input,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def find_matchingsongs(searchterm,searchCopy):

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    #cur_copy = "%"+str(searchCopy)+"%"
    try:
        sql = """
        SELECT distinct s.song_id, s.song_title, s.length, snew.count AS count, string_agg(md_value,',') as md_value
        FROM mediaserver.song s,
            (SELECT s1.song_id, md_value, count(am1.media_id) as count, md_type_name
             FROM mediaserver.song s1 LEFT OUTER JOIN mediaserver.AudioMedia am1 ON (s1.song_id=am1.media_id) NATURAL JOIN mediaserver.mediaitem NATURAL JOIN mediaserver.mediaitemmetadata NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
             GROUP BY s1.song_id, md_value, md_type_name) snew
        WHERE s.song_id = snew.song_id and (lower(song_title) ~ lower(%s) OR DIFFERENCE(lower(song_title), lower(%s)) > 2) AND md_type_name = 'song genre'
        GROUP BY s.song_id, s.song_title, s.length, count
        ORDER BY s.song_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchCopy,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

def filter_genre(searchterm, searchterm_c, song_genre, input):

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        sql = """
        SELECT distinct s.song_id, s.song_title, s.length, snew.count AS count, string_agg(md_value,',') as md_value
        FROM mediaserver.song s,
                    (SELECT s1.song_id, md_value, count(am1.media_id) as count, md_type_name
                     FROM mediaserver.song s1 LEFT OUTER JOIN mediaserver.AudioMedia am1 ON (s1.song_id=am1.media_id) NATURAL JOIN mediaserver.mediaitem NATURAL JOIN mediaserver.mediaitemmetadata NATURAL JOIN mediaserver.metadata NATURAL JOIN mediaserver.metadatatype
                     GROUP BY s1.song_id, md_value, md_type_name) snew
                WHERE s.song_id = snew.song_id and (lower(song_title) ~ lower(%s) OR DIFFERENCE(lower(song_title), lower(%s)) > 2) AND md_type_name = 'song genre' AND md_value = lower(%s) AND s.length > %s
                GROUP BY s.song_id, s.song_title, s.length, count
                ORDER BY s.song_id;
        """

        r = dictfetchall(cur,sql,(searchterm,searchterm_c,song_genre,input,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Add a new Movie
#####################################################
def add_movie_to_db(title,release_year,description,storage_location,genre):
    """
    Add a new Movie to your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT 
            mediaserver.addMovie(
                %s,%s,%s,%s,%s);
        """

        cur.execute(sql,(storage_location,description,title,release_year,genre))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (8)
#   Add a new Song
#####################################################
def add_song_to_db(location, songdescription, title, songlength, songgenre, artistid):
    """
    Get all the matching Movies in your media server
    """

    conn = database_connect()

    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT
            mediaserver.addSong(
               %s,%s,%s,%s,%s,%s);
        """

        cur.execute(sql,(location, songdescription, title, songlength, songgenre, artistid))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get last Movie
#####################################################
def get_last_movie():
    """
    Get all the latest entered movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        select max(movie_id) as movie_id from mediaserver.movie"""

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

# Add by ourselves
def get_last_song():
    """
    Get all the latest entered song in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT max(song_id) AS song_id FROM mediaserver.song"""

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#  FOR MARKING PURPOSES ONLY
#  DO NOT CHANGE

def to_json(fn_name, ret_val):
    """
    TO_JSON used for marking; Gives the function name and the
    return value in JSON.
    """
    return {'function': fn_name, 'res': json.dumps(ret_val)}

# =================================================================
# =================================================================
