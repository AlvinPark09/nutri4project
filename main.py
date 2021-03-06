from typing import Optional
from urllib import response
from fastapi import FastAPI, Response, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie, FastAPI
from PIL import Image

import urllib.request
from pygame import mixer  # Load the popular external library
import time
import os
from gtts import gTTS
import get_food_list
import pickle
import datetime
import my_func
import requests
import json
import pandas as pd

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/img', StaticFiles(directory='img'), name='img')
app.mount('/image', StaticFiles(directory='image'), name='image')
app.mount('/pred_image', StaticFiles(directory='pred_image'), name='pred_image')
templates = Jinja2Templates(directory="templates")



@app.get('/', response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request })


@app.get("/kakao")
async def kakao():
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = "http://localhost:8000/oauth"
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response

@app.get('/oauth')
async def kakaoAuth(response: Response, code: Optional[str]="NONE"):
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = 'http://localhost:8000/oauth'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}'
    _res = requests.post(_url)
    _result = _res.json()
    response = RedirectResponse('http://localhost:8000/info/{}'.format(_result['access_token']))
    return response

@app.get('/info/{KEY}', response_class=HTMLResponse)
async def user_info(response: Response, request: Request, KEY: Optional[str]):
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    url = "https://kapi.kakao.com/v2/user/me?property_keys=[\"kakao_account.email\", \"kakao_account.age_range\", \"kakao_account.gender\"]"
    headers = {
      'Authorization': f'Bearer {KEY}'
    }
    
    response = requests.request("GET", url, headers=headers)
    data = response.json()['kakao_account']
    
    with open('./data/data.json', 'w') as outfile:
      json.dump(data, outfile)

    return templates.TemplateResponse("main.html", {"request": request })

@app.post('/print', response_class=HTMLResponse)
async def get_page(request: Request, img_s: UploadFile = File(...), disease : str= Form(...)):
    ## ????????? ????????????
    f = open('./disease/disease.txt', 'w')
    f.write(f'{disease}')
    f.close()
    ## ???????????? {img_s.filename}?????? image????????? ?????? ????????????
    file_location = f"./image/{img_s.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img_s.file.read())
    
    ## ????????? ?????? ????????????
    with open('data/data.json', "r") as json_file:
      json_data = json.load(json_file)
      
    email = json_data['email']
    if json_data['gender'] == 'male':
      gender = '??????'
    else:
      gender = '??????'
    age_range = json_data['age_range']

    ## ???????????? ????????? ?????? ?????? ?????? ??? ?????? ????????? ??????
    my_func.pred(file_location)

    pred_file = file_location.split('/')[-1]
    pred_file_path = "../pred_image/result/"+pred_file
    global food_list
    food_list = my_func.get_result()
      
    ## ????????? ????????? ??????????????? ???????????? print ????????? ?????? ??????
    df = pd.DataFrame(my_func.nutrition_info(food_list)[1])
    food_info = df.to_html()
    
    
    
    ## histoty histogram
    nutri_reco = my_func.nutri_reco()
    condition = ((nutri_reco['??????'] == gender) & (nutri_reco['??????'] == age_range))
    nutri_reco_id = nutri_reco[condition]['??????(g/???)']
    nutri_reco_id = list(nutri_reco_id)
    energe = my_func.nutri_limit(['??????', gender, age_range])
    
    nutri_addition = my_func.nutri_add(food_list)
    nutri_list = list(nutri_addition.values())
    for i in range(len(nutri_reco_id)):
          if i == 0:
            nutri_list[i] = round((nutri_list[i] / list(energe['????????????\n(1???)'])[0])*300, 2)  
          else:
            nutri_list[i+1] = round((nutri_list[i+1] / nutri_reco_id[i])*100, 2)
    nutri_list = nutri_list[:-2]

    dise_nutri = my_func.nutri_limit([disease, gender, age_range])
    df2 = dise_nutri[['????????????', '????????????\n(1???)', '??????', '????????????']]
    df2 = df2.set_index('????????????')
    dise_info = df2.to_html()
    
    temp = my_func.calc_nutri(gender, age_range, food_list)
    temp = pd.DataFrame(temp)
    temp.columns = ['???????????????']
    temp = temp.style.hide_index()
    message = temp.to_html()
  
    my_func.voice('????????? ?????????????????????. ?????????????????? ????????? ?????????')
    fn = app.url_path_for('static', path='/voice.mp3')
 
    return templates.TemplateResponse("print.html", {"request": request, 'food_names': food_list, 
                                                     'email':email, 'gender':gender, 'age_range':age_range, 
                                                     'disease':disease, 'img_path':pred_file_path, 'nutri_list':nutri_list,
                                                     'dise_info':dise_info, 'message':message,
                                                     'food_info': food_info, 'fn': fn

                                                     }
                                      )
    
@app.get('/his', response_class=HTMLResponse)
async def get_history(request: Request):
  f = open('./disease/disease.txt', 'r')
  disease = f.readline()
  f.close()
  
  my_func.voice('??????. ?????????????????? ????????? ?????????')

  ## ????????? ?????? ????????????
  with open('data/data.json', "r") as json_file:
    json_data = json.load(json_file)
    
  email = json_data['email']
  if json_data['gender'] == 'male':
    gender = '??????'
  else:
    gender = '??????'
  age_range = json_data['age_range']
  food_list = get_food_list.get_food_list()
  
  # ?????? ????????? ??????
  now = datetime.datetime.now()
  cur_time = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
  
  nutri_add2 = my_func.nutri_add(food_list)
  record_list = [email, cur_time, gender, age_range]
  
  
  for nutri in nutri_add2.values():
        record_list.append(nutri)
  my_func.add_record([record_list])      
  
  ## histoty histogram
  nutri_reco = my_func.nutri_reco()
  condition = ((nutri_reco['??????'] == gender) & (nutri_reco['??????'] == age_range))
  nutri_reco_id = nutri_reco[condition]['??????(g/???)']
  nutri_reco_id = list(nutri_reco_id)
  history = my_func.id_history([email])
  
  condition2 = (history.groupby(['id', 'date']).sum().reset_index()['date'] == cur_time)
  nutri_list = history.groupby(['id', 'date']).sum().reset_index()[condition2].iloc[0].values[2:]
  
  energy = my_func.nutri_limit(['??????', gender, age_range])
  nutri_list = nutri_list[:-2]
  
  for i in range(len(nutri_reco_id)):
        if i == 0:
          nutri_list[i] = (nutri_list[i] / list(energy['????????????\n(1???)'])[0])*100  
        else:
          nutri_list[i+1] = (nutri_list[i+1] / nutri_reco_id[i])*100
          
  for idx, nutri in enumerate(nutri_list):
        nutri_list[idx] = round(nutri,2)
  
  nutri_list = list(nutri_list)
  
  energy_list = my_func.nutri_limit([disease, gender, age_range])
  nutri_name = energy_list["????????????"]
  nutri_std = energy_list["????????????\n(1???)"].values
  
  unit = energy_list["??????"]
  
  cur_index = []
  nutri_name = nutri_name.values
  
  for idx, column in enumerate(history.groupby(['id', 'date']).sum().reset_index()[condition2].columns):
      for name in nutri_name:
        if column == '?????????(kcal)':
            if '??????' == name:
                cur_index.append(idx)
        elif column.split('(')[0] == name:
              cur_index.append(idx)
  
  having = history.groupby(['id', 'date']).sum().reset_index()[condition2].iloc[:,cur_index].values[0]
  for i in range(len(nutri_std)):
    having[i] = round((having[i] / nutri_std[i])*100, 2)
    
  for i in range(len(nutri_name)):
        nutri_name[i] += unit[i]
  
  having = list(having)
  
  nutri_name = list(nutri_name)

  return templates.TemplateResponse("history.html", {"request": request, 'nutri_list':nutri_list, 'nutri_name':nutri_name, 'having':having})

@app.get('/use', response_class=HTMLResponse)
async def get_use(request: Request):
  return templates.TemplateResponse("manual.html", {"request": request})