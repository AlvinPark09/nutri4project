import os
import sys
import urllib.request
# client_id = "fr2pmzwe08"
# client_secret = "uzTbsKj83c57qTJNlHRbeIsTiwDdVoZLKDod8UBh"
# encText = urllib.parse.quote("반갑습니다 네이버")
# data = "speaker=nara&volume=0&speed=0&pitch=0&format=mp3&text=" + encText
# url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
# request = urllib.request.Request(url)
# request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
# request.add_header("X-NCP-APIGW-API-KEY",client_secret)
# response = urllib.request.urlopen(request, data=data.encode('utf-8'))
# rescode = response.getcode()
# if(rescode==200):
#     print("TTS mp3 저장")
#     response_body = response.read()
#     with open('1111.mp3', 'wb') as f:
#         f.write(response_body)
# else:
#     print("Error Code:" + rescode)


def voice(name):
    client_id = "fr2pmzwe08"
    client_secret = "uzTbsKj83c57qTJNlHRbeIsTiwDdVoZLKDod8UBh"
    encText = urllib.parse.quote(name)
    data = "speaker=nsinu&volume=0&speed=0&pitch=0&format=mp3&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode == 200):
        response_body = response.read()
        with open('foodname.mp3', 'wb') as f:
            f.write(response_body)
    else:
        errormsg = ("Error Code:" + rescode)
        return errormsg

voice('안녕하세요. 하지메 마시떼 와따시와 리코데스. 도조 요로시꾸 오네가이 시마스')