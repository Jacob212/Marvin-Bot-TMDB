import sqlite3

__all__ = ['get_account_details', 'setup_account', 'update_access_token', 'update_list_id']

CONN = sqlite3.connect("discord.db")
C = CONN.cursor()
C.execute("CREATE TABLE IF NOT EXISTS accounts (userName TEXT NOT NULL,discordID INTEGER NOT NULL PRIMARY KEY UNIQUE,accessToken  TEXT UNIQUE,accountID TEXT UNIQUE,listID INTEGER UNIQUE);")
CONN.commit()

def get_account_details(discord_id):
    C.execute("SELECT accessToken, accountID, listID FROM accounts WHERE discordID = ?;", (discord_id,))
    return C.fetchone()

def setup_account(discordName, discord_id, access_token, account_id, list_id):
    C.execute("INSERT INTO accounts VALUES(?,?,?,?,?)", (discordName, discord_id, access_token, account_id, list_id))
    CONN.commit()

def update_access_token(discord_id, access_token):
    C.execute("UPDATE accounts set accessToken = ? WHERE discordID = ?;", (access_token, discord_id))
    CONN.commit()

def update_list_id(discord_id, list_id):
    C.execute("UPDATE accounts SET listID = ? WHERE discordID = ?;", (list_id, discord_id))
    CONN.commit()
