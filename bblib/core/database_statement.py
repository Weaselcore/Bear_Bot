from enum import Enum


class SqlStatement(Enum):

    CHECK_TABLES = 'SELECT count(name) FROM sqlite_master WHERE type = "table" AND name = ?'

    # All insert Statements.
    INSERT_ID = "INSERT INTO gambler_stat (_id, money_amount) values(?, 0)"
    INSERT_GUILD = "INSERT OR REPLACE INTO guild (guild_id, name, creation_date) values(?, ?, ?)"

    # All update statements.
    UPDATE_NICKNAME = "UPDATE gambler_stat SET nickname = ? WHERE _id = ?"
    UPDATE_MONEY = "UPDATE gambler_stat SET money_amount = ? WHERE _id = ?"
    UPDATE_BANK = "UPDATE gambler_stat SET bank_amount = ? WHERE _id = ?"
    UPDATE_LAST_STOLEN_ID = "UPDATE gambler_stat SET last_stolen_id = ? WHERE _id = ?"
    UPDATE_LAST_REDEEMED = "UPDATE gambler_stat SET last_redeemed = ? WHERE _id = ?"
    UPDATE_LAST_BANK_DATETIME = "UPDATE gambler_stat SET last_bank_datetime = ? WHERE _id = ?"
    UPDATE_LAST_STOLEN_DATETIME = "UPDATE gambler_stat SET last_stolen_datetime = ? WHERE _id = ?"
    UPDATE_TOTAL_GAINED = "UPDATE gambler_stat SET total_gained = ? WHERE _id = ?"
    UPDATE_TOTAL_LOST = "UPDATE gambler_stat SET total_lost = ? WHERE _id = ?"

    # All select statements
    GET_ROW = "SELECT * FROM gambler_stat WHERE _id=?"
    GET_ID = "SELECT _id FROM gambler_stat WHERE _id=?"
    GET_NICKNAME = "SELECT nickname FROM gambler_stat WHERE _id=?"
    GET_MONEY = "SELECT money_amount FROM gambler_stat WHERE _id=?"
    GET_BANK = "SELECT bank_amount FROM gambler_stat WHERE _id=?"
    GET_LAST_STOLEN_ID = "SELECT last_stolen_id FROM gambler_stat WHERE _id=?"
    GET_LAST_REDEEMED = "SELECT last_redeemed FROM gambler_stat WHERE _id=?"
    GET_LAST_BANK_DATETIME = "SELECT last_bank_datetime FROM gambler_stat WHERE _id=?"
    GET_LAST_STOLEN_DATETIME = "SELECT last_stolen_datetime FROM gambler_stat WHERE _id=?"
    GET_TOTAL_GAINED = "SELECT total_gained FROM gambler_stat WHERE _id=?"
    GET_TOTAL_LOST = "SELECT total_lost FROM gambler_stat WHERE _id=?"

    # Specific command queries.
    GET_LEADER = "SELECT _id, nickname, money_amount, bank_amount FROM gambler_stat ORDER BY money_amount + " \
                 "bank_amount DESC LIMIT ? "

    # Create table statements.
    CREATE_GUILD_TABLE = """CREATE TABLE guild(
                                guild_id integer PRIMARY KEY,
                                name text NOT NULL,
                                creation_date timestamp);"""

    CREATE_MEMBER_TABLE = """CREATE TABLE member(
                                _id integer NOT NULL PRIMARY KEY,
                                name text NOT NULL,
                                creation_date timestamp);"""

    CREATE_GAMBLER_STAT_TABLE = """CREATE TABLE gambler_stat(
                                _id integer NOT NULL PRIMARY KEY,
                                nickname text DEFAULT NULL,
                                money_amount integer DEFAULT 0,
                                bank_amount integer DEFAULT 0,
                                last_stolen_id integer,
                                last_redeemed timestamp,
                                last_bank_datetime timestamp,
                                last_stolen_datetime timestamp,
                                total_gained integer DEFAULT 0,
                                total_lost integer DEFAULT 0);"""
