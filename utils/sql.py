import sqlite3

__all__ = ['get_account_details','setup_account','update_access_token','update_list_id']

CONN = sqlite3.connect("discord.db")
C = CONN.cursor()
C.execute("CREATE TABLE IF NOT EXISTS accounts (userName TEXT NOT NULL,discordID INTEGER NOT NULL PRIMARY KEY UNIQUE,accessToken  TEXT UNIQUE,accountID TEXT UNIQUE,listID INTEGER UNIQUE);")
CONN.commit()

def get_account_details(discordID):
    C.execute("SELECT accessToken, accountID, listID FROM accounts WHERE discordID = ?;", (discordID,))
    return C.fetchone()

def setup_account(discordName, discordID, access_token, accountID, listID):
    C.execute("INSERT INTO accounts VALUES(?,?,?,?,?)", (discordName, discordID, access_token, accountID, listID))
    CONN.commit()

def update_access_token(discordID, access_token):
    C.execute("UPDATE accounts set accessToken = ? WHERE discordID = ?;", (access_token, discordID))
    CONN.commit()

def update_list_id(discordID, listID):
    C.execute("UPDATE accounts SET listID = ? WHERE discordID = ?;", (listID, discordID))
    CONN.commit()