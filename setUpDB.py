import sqlite3
db = sqlite3.connect('twitterDB.db')

db.execute("CREATE TABLE tweets (id INTEGER PRIMARY KEY, tweetID VARCHAR(30) NOT NULL, tweet BLOB NOT NULL, archiveID INTEGER NOT NULL, position INTEGER NOT NULL)")
db.execute("CREATE TABLE archives (id INTEGER PRIMARY KEY, userID INTEGER NOT NULL, archive_name VARCHAR(30) NOT NULL)")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name char(30) NOT NULL, password char(30) NOT NULL, display_name char(30) NOT NULL)")
db.execute("CREATE TABLE archiveUsers (archiveID INTEGER NOT NULL, sharedUserID INTEGER NOT NULL)")

db.commit()
