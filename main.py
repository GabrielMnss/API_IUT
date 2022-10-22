import pandas as pd
import uvicorn
from fastapi import FastAPI
import json
import mysql.connector
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import error_library as err_lib
from test_lib import get_test_lib
import users_inf_lib
from question_answer_lib import get_question_theme, get_answers
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

response = err_lib.Format_result()


@app.get('//get_test_list')
async def get_test_list():
    result = get_test_lib()
    response.error = None
    response.response = result
    return json.dumps(response.__dict__)


@app.get("//get_ranking")
async def get_ranking():
    result = users_inf_lib.get_user_ranking()

    response.error = None
    response.response = result
    return json.dumps(response.__dict__)


@app.post("//try_connect")
async def try_connect(data: Request):
    request = await data.json()
    password = request['password']
    username = request['username']
    if password and username is not None:
        can_connect, returned_result, error = users_inf_lib.try_connection(username, password)
        if can_connect:
            if returned_result is None:
                return json.dumps(err_lib.error502.__dict__)
            response.error = error
            response.response = {**json.loads(returned_result.to_json()), **{'can_connect': True}}
            return json.dumps(response.__dict__)
    return json.dumps(err_lib.error501.__dict__)


@app.post('//get_user_historic')
async def user_historic(data: Request):
    request = await data.json()
    user_id = int(request['id'])

    if user_id is not None:
        result = users_inf_lib.get_user_historic(user_id)

        response.error = None
        response.response = pd.DataFrame(result, columns=['userID', 'y', 'x']).drop('userID', axis=1).to_json(
            orient='records')
        return json.dumps(response.__dict__)
    else:
        response.error = err_lib.error501
        response.response = None
        return json.dumps(response.__dict__)


@app.post('//get_questions')
async def get_questions(data: Request):
    request = await data.json()
    theme = str(request['theme'])

    if theme is not None:
        result = get_question_theme(theme)
        response.error = None
        response.response = result.to_json(orient='records')
        return json.dumps(response.__dict__)
    else:
        response.error = err_lib.error501
        response.response = None
        return json.dumps(response.__dict__)


@app.post('//verify_answer')
async def verify_ans(data: Request):
    request = await data.json()
    infos = request["answer"]
    if infos is not None:
        result = get_answers(infos)
        response.error = None
        response.response = result
        return json.dumps(response.__dict__)
    else:
        response.error = err_lib.error501
        response.response = None
        return json.dumps(response.__dict__)


@app.post('//add_user')
async def add_user(data: Request):
    request = await data.json()
    if request is not None:
        password = request['password']
        email = request['email']
        pseudo = request['pseudo']
        users_inf_lib.add_user_db(password, email, pseudo)
        response.error = None
        response.response = ''
        return json.dumps(response.__dict__)


@app.post('//verify')
async def verify(data: Request):
    request = await data.json()
    if request is not None:
        password = request['password']
        email = request['email']
        pseudo = request['pseudo']
        users_inf_lib.verify_user(password, str(email), pseudo)
        response.error = None
        response.response = ''
        return json.dumps(response.__dict__)
