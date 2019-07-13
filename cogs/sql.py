import sqlite3

__all__ = ['new_member','new_watched','getWatchedID','updateWatched','checkWatched','getMovies','getMoviesLike','getMoviesLikeLimit','getLastFive','getLength']

conn = sqlite3.connect("Discord.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Movies (movieID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,titleType TEXT NOT NULL,primaryTitle  TEXT NOT NULL,originalTitle TEXT,season  INTEGER,episodes  INTEGER,releaseYear INTEGER,runtimeMinutes  INTEGER,language  TEXT,genre TEXT,tconst  TEXT NOT NULL, UNIQUE(season,tconst));")
c.execute("CREATE TABLE IF NOT EXISTS Members (userID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,discordID INTEGER NOT NULL UNIQUE,username  TEXT NOT NULL);")
c.execute("CREATE TABLE IF NOT EXISTS Watched (ID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,userID  INTEGER,`movieID` INTEGER,episode INTEGER,FOREIGN KEY(movieID) REFERENCES Movies(movieID) ON DELETE SET NULL,FOREIGN KEY(userID) REFERENCES Members(userID) ON DELETE SET NULL);")
conn.commit()

def new_member(discordID,name):
  c.execute("INSERT INTO Members VALUES(?,?,?)", (None,discordID,name))
  conn.commit()

def new_watched(discordID,primaryTitle,season,episode):
  c.execute("INSERT INTO Watched VALUES(?,(SELECT userID FROM Members WHERE discordID = ?),(SELECT movieID FROM Movies WHERE primaryTitle = ? and season = ?),?)", (None,discordID,primaryTitle,season,episode))
  conn.commit()

def getWatchedID(discordID,primaryTitle,titleType,genre,year,offset):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Movies.episodes, Movies.tconst, Movies.releaseYear, Movies.runtimeMinutes, Movies.genre, Movies.originalTitle, Watched.episode FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[userID] = Watched.[userID]) ON Movies.[movieID] = Watched.[movieID] WHERE (Members.discordID) = ? AND (Movies.primaryTitle) LIKE ? AND (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? AND (Movies.releaseYear) LIKE ? ORDER BY Movies.primaryTitle, Movies.season LIMIT ?,10;",(discordID,primaryTitle,titleType,genre,year,offset))
  return c.fetchall()

def updateWatched(discordID,primaryTitle,season,episode):
  c.execute("UPDATE Watched SET episode = ? WHERE (UserID = (SELECT UserID FROM Members WHERE DiscordID = ?)) AND (MovieID = (SELECT MovieID FROM Movies WHERE primaryTitle = ? AND season = ?));",(episode,discordID,primaryTitle,season))
  conn.commit()

def checkWatched(discordID,primaryTitle,season):#Checks to see if someone has already watched an episode already(False if the have not and True if they have)
  c.execute("SELECT Members.discordID, Movies.primaryTitle, Movies.season FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE (((Members.discordID) = ?) AND ((Movies.primaryTitle)=?) AND ((Movies.season)=?));",(discordID,primaryTitle,season))
  if c.fetchall() == []:
    return False
  else:
    return True

def getMovies():
  c.execute("SELECT Movies.primaryTitle, Movies.season, Movies.episodes FROM Movies ORDER BY Movies.primaryTitle, Movies.season;")
  return c.fetchall()

def getMoviesLike(genre,titleType):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Movies.episodes FROM Movies WHERE (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? ORDER BY Movies.primaryTitle, Movies.season;",(titleType,genre))
  return c.fetchall()

def getMoviesLikeLimit(primaryTitle,titleType,genre,year,offset):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Movies.episodes, Movies.tconst, Movies.releaseYear, Movies.runtimeMinutes, Movies.genre, Movies.originalTitle FROM Movies WHERE (Movies.primaryTitle) LIKE ? AND (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? AND (Movies.releaseYear) LIKE ? ORDER BY Movies.primaryTitle, Movies.season LIMIT ?,10;",(primaryTitle,titleType,genre,year,offset))
  return c.fetchall()

def getLastFive():
  c.execute("SELECT primaryTitle,season FROM Movies ORDER BY movieID DESC LIMIT 0,5")
  return c.fetchall()

def getLength():
  c.execute("SELECT count(*) FROM Movies")
  return c.fetchone()[0]