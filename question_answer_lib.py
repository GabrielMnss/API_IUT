from datetime import datetime
import random

import pandas as pd
import main as main
from SQL_connect import connection, cursor, engine


def get_question_theme(theme):
    try:
        if connection.is_connected():
            db_result = []
            cursor.callproc('get_questions_answers', [theme])
            for r in cursor.stored_results():
                db_result.append(r.fetchall())
            db_result = db_result[0]
            random.shuffle(db_result)
            print(db_result)
            result = pd.DataFrame(db_result, columns=['questionID', 'themeID', 'question', 'answer', 'surplus', 'type',
                                                      'reward']).drop(
                'answer', axis=1)
            return result
    except ValueError:
        return None


def get_answers(user_answers):
    user_ans = user_answers['user_ans']
    user_ans = pd.DataFrame(user_ans)[['id', 'user_response']]
    user_ans = user_ans[user_ans.columns[::-1]]

    user_id = user_answers['userID']

    if connection.is_connected():
        db_result = []
        cursor.callproc('get_questions_answers', [user_answers['theme']])
        for r in cursor.stored_results():
            db_result.append(r.fetchall())
        db_result = db_result[0]
        db_result = pd.DataFrame(db_result,
                                 columns=['id', 'theme', 'question', 'real_response', 'surplus', 'type', 'reward'])[
            ['real_response', 'id', 'reward']]

        db_result = db_result.loc[(db_result['id'].isin(user_ans['id']))]

        infos = check_responses(user_ans, db_result)

        actualise_new_wins(infos, user_id)
        return infos


def check_responses(user_rep, db_rep):
    total_reward = 0

    user_rep = user_rep.sort_values('id')
    db_rep = db_rep.sort_values('id')
    user_rep = user_rep.drop_duplicates(subset=['id'], keep=False)

    print(user_rep)
    print(db_rep)

    try:
        for i in range(len(user_rep)):
            if int(user_rep.loc[i, 'user_response']) == int(db_rep.loc[i, 'real_response']):
                total_reward += db_rep.loc[i, 'reward']
    except ValueError:
        return {'reward': int(total_reward)}
    return {'reward': int(total_reward)}


def actualise_new_wins(infos, user_id):
    reward = infos['reward']

    x = {"userID": user_id, "score": reward, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    new_wins = pd.DataFrame(x, index=[0])

    if connection.is_connected():
        new_wins.to_sql('last_users_score', engine, if_exists='append', index=False)
        sql_query = "Update user_information set totalWins = totalWins + " + str(reward) + " where userID = " + str(user_id)
        cursor.execute(sql_query)
        connection.commit()
