from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from prettytable import PrettyTable
import urllib2
import urllib
import json
import textwrap

from model import SongFinder, Base

engine = create_engine('sqlite:///songs.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database

session = DBSession()

# Declaring the static variables for configuration.
api_key = "5120626c22645c776a9a863c9b0859c4"
musix_match_url = "http://api.musixmatch.com/ws/1.1/"

# Returns a list of songs that match the criteria.
def song_find(query_string):
	"""
	This is a function that returns list of songs based on the query passed
	"""
	full_url = musix_match_url + "track.search?q_track=" + urllib.quote(query_string) + "&apikey=" + api_key + "&json"
	try:
		request_stmt = urllib2.Request(full_url)
		data = urllib2.urlopen(request_stmt)
		the_page = data.read()
		lyrics = json.loads(the_page.decode("utf-8"))
		data.close()
		list_tracks = lyrics['message']['body']['track_list']
		list_of_all_songs = []
		song_number = 0
		for tracks in list_tracks:
			song_details = []
			get_track_id = tracks['track']['track_id']
			get_song_name = tracks['track']['track_name']
			get_song_album_name = tracks['track']['album_name']
			get_song_artist_name = tracks['track']['artist_name']
			song_details.insert(0, get_track_id)
			song_details.insert(1, get_song_name)
			song_details.insert(2, get_song_album_name)
			song_details.insert(3, get_song_artist_name)
			list_of_all_songs.append(song_details)
			track_table = PrettyTable(['Track Id', 'Track Name', 'Album Name', 'Artist Name'])
			track_table.add_row([get_track_id, get_song_name, get_song_album_name, get_song_artist_name])
			song_number += 1	
		print track_table
		
	except urllib2.URLError as e:
		print e.reason

song_find('back to december')		

def song_view(track_id):
	"""This function returns the song lyrics"""
	try:
		find_song = session.query(SongFinder).filter(SongFinder.song_id == track_id).one()
		print 'Getting lyrics from Database'
		print find_song.song_lyrics
		
	except MultipleResultsFound:
		find_song = session.query(SongFinder).filter(SongFinder.song_id == track_id).all()
		for item in find_song:
			print item.song_lyrics
	except NoResultFound:
		print "Getting lyrics from the API"
		full_url = musix_match_url + "track.lyrics.get?track_id=" + track_id + "&apikey=" + api_key + "&json"

		try:
			request_stmt = urllib2.Request(full_url)
			data = urllib2.urlopen(request_stmt)
			the_page = data.read()
			lyrics = json.loads(the_page.decode("utf-8"))
			data.close()
			print lyrics["message"]["body"]["lyrics"]["lyrics_body"]
		except urllib2.URLError as e:
			print e.reason
song_view('15953433')


def song_clear():
	"""
     This function clears the entire database
	"""
	try:
		deleted_rows = session.query(SongFinder).delete()
		session.commit()
		print "Database cleared successfully."
 	except:
 		session.rollback()
 	
song_clear() 

def song_clear_single_song(track_id):
	"""This function clears a single song from the database."""	
	try:
		song_deleted = session.query(SongFinder).filter(SongFinder.song_id == track_id).delete()
		session.commit()
		print "Song deleted successfully"
	except:
		session.rollback()	

def song_save(track_id):
	"""This function saves the song to the database."""
	full_url = musix_match_url + "track.lyrics.get?track_id=" + track_id + "&apikey=" + api_key + "&json"
	request_stmt = urllib2.Request(full_url)
	try:
		data = urllib2.urlopen(request_stmt)
		the_page = data.read()
		lyrics = json.loads(the_page.decode("utf-8"))
		data.close()
		lyrics_content = lyrics["message"]["body"]["lyrics"]["lyrics_body"]
		song_found = SongFinder(track_id, lyrics_content)
		session.add(song_found)
		session.commit()
	except urllib2.URLError as e:
		print e.reason

song_save('15953433')

