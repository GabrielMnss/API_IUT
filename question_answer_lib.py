from datetime import datetime
import random
from API.AIverify import verifyForOpenQuestions
import pandas as pd
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
            result = pd.DataFrame(db_result, columns=['questionID', 'themeID', 'question', 'answer', 'surplus', 'type',
                                                      'reward']).drop(
                'answer', axis=1)
            return result
    except ValueError:
        return None


def get_answers(user_answers):
    user_id = user_answers['userID']

    for ans in user_answers['user_ans']:
        if ans['type'] == 'qcm':
            cursor.callproc('qcm_verify', (ans['id'], ans['user_response'], user_id))

        if ans['type'] == 'ope':
            user_answer = ans['user_response']
            sql_query = f"Select answer, reward from question_answer where questionID = {ans['id']}"
            cursor.execute(sql_query)
            connection.commit()
            resp = cursor.fetchall()[0]
            real_answer = resp[0]
            reward = resp[1]
            if verifyForOpenQuestions(real_answer, user_answer):
                cursor.callproc('Add_reward', (user_id, reward))


def actualise_new_wins(infos, user_id):
    reward = infos['reward']

    x = {"userID": user_id, "score": reward, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    new_wins = pd.DataFrame(x, index=[0])

    if connection.is_connected():
        new_wins.to_sql('last_users_score', engine, if_exists='append', index=False)
        sql_query = "Update user_information set totalWins = totalWins + " + str(reward) + " where userID = " + str(
            user_id)
        cursor.execute(sql_query)
        connection.commit()
