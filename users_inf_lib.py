import datetime
import json

import pandas as pd
import main as main
from SQL_connect import connection, cursor, engine


# def get historic
def get_user_historic(user_id):
    try:
        if connection.is_connected():
            result = []
            datas = []

            cursor.callproc('get_user_historic', [user_id])
            for r in cursor.stored_results():
                result = r.fetchall()
            for x in result:
                datas.append(list(x))

            let = True
            while let:
                let = False
                for i in range(len(datas) - 1):
                    if (datas[i+1][2] - datas[i][2]).days > 1:
                        let = True
                        datas.insert(i+1, [datas[i][0], 0, datas[i][2] + datetime.timedelta(hours=20)])
                        break
            print(datas)
            return datas[0:10]
    except ValueError:
        return None


# get ranking
def get_user_ranking():
    try:
        if connection.is_connected():
            columns = []

            cursor.execute("SELECT * FROM user_information")
            for column in cursor.description:
                columns.append(column[0])

            result = pd.DataFrame(cursor.fetchall(), columns=columns)
            result = result.sort_values(by='totalWins', ascending=False)
            return result[0:10].to_json(orient='records')
        return None
    except ValueError:
        return None


# connection
def user_exist_in_db(email, password):
    try:
        columns = []
        cursor.execute("SELECT * FROM user_information")
        for column in cursor.description:
            columns.append(column[0])

        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        for i in range(len(df)):
            if df['email'][i] == email and df['password'][i] == password and df['verified'][i] == 1:
                return 2, df.iloc[i]
            if df['email'][i] == email and df['password'][i] != password or df['email'][i] == email:
                return 1, None
        return 0, None
    except ValueError as e:
        return 0, None


def try_connection(email, password):
    try:
        if connection.is_connected():
            exist, infos = user_exist_in_db(email, password)
            if exist == 2:
                return True, infos, None
            if exist == 1:
                return True, None, None
            else:
                return False, None, None
    except ValueError:
        return False, ValueError, None


def add_user_db(password, email, pseudo):
    exist, infos = user_exist_in_db(email, password)
    if exist == 0:
        user = {"pseudo": pseudo, "email": email, "password": password}
        new_user = pd.DataFrame(user, index=[0])
        new_user.to_sql('user_information', engine, if_exists='append', index=False)
        connection.commit()


def verify_user(password, email, pseudo):
    sql_query = f"Update user_information set verified = 1 where email = %s"
    cursor.execute(sql_query, (email,))
    connection.commit()
