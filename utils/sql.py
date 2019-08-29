import sqlite3

CONN = sqlite3.connect("discord.db")
C = CONN.cursor()
C.execute("CREATE TABLE IF NOT EXISTS accounts (userName TEXT NOT NULL,discordID INTEGER NOT NULL PRIMARY KEY UNIQUE,accessToken  TEXT UNIQUE,accountID TEXT UNIQUE,listID INTEGER UNIQUE);")
C.execute("CREATE TABLE IF NOT EXISTS shows (name TEXT NOT NULL, tmdbID INTEGER NOT NULL PRIMARY KEY UNIQUE);")
C.execute("""CREATE TABLE IF NOT EXISTS subs (
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
    discordID INTEGER NOT NULL, 
    tmdbID INTEGER NOT NULL, 
    FOREIGN KEY(discordID) REFERENCES accounts(discordID) ON DELETE CASCADE, 
    FOREIGN KEY(tmdbID) REFERENCES shows(tmdbID) ON DELETE CASCADE,
    CONSTRAINT one_sub UNIQUE (
        discordID, tmdbID
        )
    );""")
CONN.commit()

def get_account_details(discord_id):
    C.execute("SELECT accessToken, accountID, listID FROM accounts WHERE discordID = ?;", (discord_id,))
    return C.fetchone()

def setup_account(discord_name, discord_id, access_token, account_id, list_id):
    C.execute("INSERT INTO accounts VALUES(?,?,?,?,?);", (discord_name, discord_id, access_token, account_id, list_id))
    CONN.commit()

def update_account(discord_id, access_token, account_id, list_id):
    C.execute("UPDATE accounts set access_token = ?, account_id = ?, list_id = ? WHERE dsicordID = ?;", (access_token, account_id, list_id, discord_id))
    CONN.commit()

def update_access_token(discord_id, access_token):
    C.execute("UPDATE accounts set accessToken = ? WHERE discordID = ?;", (access_token, discord_id))
    CONN.commit()

def update_list_id(discord_id, list_id):
    C.execute("UPDATE accounts SET listID = ? WHERE discordID = ?;", (list_id, discord_id))
    CONN.commit()

def get_show(tmdb_id):
    C.execute("SELECT tmdbID FROM shows WHERE tmdbID = ?;", (tmdb_id,))
    return C.fetchone()

def add_show(name, tmdb_id):
    C.execute("INSERT INTO shows VALUES(?,?);", (name, tmdb_id))
    CONN.commit()

def get_sub(discord_id, tmdb_id):
    C.execute("SELECT discordID, tmdbID FROM subs WHERE discordID = ? AND tmdbID = ?;", (discord_id, tmdb_id))
    return C.fetchone()

def add_sub(discord_id, tmdb_id):
    C.execute("INSERT INTO subs VALUES(?,?,?);", (None, discord_id, tmdb_id))
    CONN.commit()

def remove_sub(discord_id, tmdb_id):
    C.execute("DELETE FROM subs WHERE discordID = ? AND tmdbID = ?", (discord_id, tmdb_id))
    CONN.commit()

def get_subs(tmdb_id):
    C.execute("SELECT discordID FROM subs WHERE tmdbID = ?", (tmdb_id,))
    return C.fetchall()
