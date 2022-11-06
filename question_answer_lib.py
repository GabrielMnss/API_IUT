from datetime import datetime
import random
from AIverify import verifyForOpenQuestions
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
    column_names = ['questionID', 'themeID', 'question', 'answer', 'surplus', 'type', 'reward']
    compare_list = {'real_answers': [], 'user_answers': []}
    for ans in user_answers['user_ans']:
        if ans['type'] == 'qcm':
            compare_list['user_answers'].append(ans['user_response'])
            cursor.callproc('qcm_verify', (ans['id'], ans['user_response'], user_id))
            for real_ans in cursor.stored_results():
                compare_list['real_answers'].append(dict(zip(column_names, real_ans.fetchone())))
        if ans['type'] == 'ope':
            user_answer = ans['user_response']
            sql_query = f"Select answer, reward, question from question_answer where questionID = {ans['id']}"
            cursor.execute(sql_query)
            connection.commit()
            resp = cursor.fetchall()[0]
            real_answer = resp[0]
            reward = resp[1]
            question = resp[2]
            resultIA = verifyForOpenQuestions(real_answer, user_answer)
            compare_list['real_answers'].append(dict(zip(['answer', 'type', 'question'], [real_answer, 'ope',question])))
            compare_list['user_answers'].append([str(user_answer), str(resultIA)])
            if resultIA > 0.7:
                cursor.callproc('Add_reward', (user_id, reward))
    return compare_list


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
