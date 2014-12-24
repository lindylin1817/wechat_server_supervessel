from django.shortcuts import render
from django.http import HttpResponse
import hashlib, time, re
from xml.etree import ElementTree as ET
from django.utils.datastructures import MultiValueDictKeyError
import logging
from django.views.decorators.csrf import csrf_exempt
from models import Users
import httplib
import numpy as np
import matplotlib
from matplotlib.pyplot import plot, savefig
from .basic import *

# Create your views here.
matplotlib.use('Agg')
key_file = "./files/key_file.txt"
cert_file = "./files/cert_file.txt"
image_file = "./files/tmp_image.png"
logger = logging.getLogger('django')
token = "mytoken"
signature = "f24649c76c3f3d81b23c033da95a7a30cb7629cc"
timestamp = '1406799650'
nonce = '1505845280'
#body_text = """
#<xml>
#<ToUserName><![CDATA[touser]]></ToUserName>
#<FromUserName><![CDATA[fromuser]]></FromUserName>
#<CreateTime>1405994593</CreateTime>
#<MsgType><![CDATA[text]]></MsgType>
#<Content><![CDATA[wechat]]></Content>
#<MsgId>6038700799783131222</MsgId>
#</xml>
#"""

reply ="""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>"""


@csrf_exempt
def weixin(request):
    logger.info('dfdf')

    wechat = WechatBasic(token=token)

    params = request.GET
#    try:
#        args = [token, params['timestamp'], params['nonce']]
#    except MultiValueDictKeyError:
#        logging.debug("Some error")
#        return HttpResponse('Some error')
#    args.sort()
#    if hashlib.sha1("".join(args)).hexdigest() == params['signature']:
 
    

    if wechat.check_signature(params['signature'],
				params['timestamp'],
				params['nonce']):
        logger.info('correct msg')
    else:
	logger.info('wrong msg')

    if request.body:
        xml = ET.fromstring(request.body)
	content = xml.find("Content").text
        fromUserName = xml.find("ToUserName").text
        logger.info("ToUser:" + fromUserName)
	toUserName = xml.find("FromUserName").text
        logger.info("FromUser: " + toUserName)
	postTime = str(int(time.time()))
	if not content:
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Please input command"))
	if content == "a":
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Our website: http://ptopenlab.com"))
	if content == "B":
	    users_list=get_users_info()
	    if check_new_user(fromUserName):
	        return HttpResponse(reply % (
		    toUserName, fromUserName, postTime, 
		    "Please tell us your email address registered "
		    +"in SuperVessel cloud via wechat message."))
	    else:
		cur_user=Users.objects(wechat_user_id=fromUserName).first()
		cur_supervessel_account=cur_user.supervessel_account
		if not cur_supervessel_account:
  		    return HttpResponse(reply % (
		        toUserName, fromUserName, postTime, 
		        "Your email account is empty. Please send us your"
			+" email registred in supervessel cloud. Then you"
			+" could get further value-added services"
                    ))
      		else:
	 	    return HttpResponse(reply % (
		        toUserName, fromUserName, postTime, 
		        "Your email account is "
			+cur_supervessel_account
			+" . If you want to update it, please send us"
			+" the email address in message again")
                    )
 	    
        if content == "C":
	    generate_image(image_file)

	if content.find('@'):
	    check_new_user(fromUserName)
	    add_supervessel_account(fromUserName, content)    
            return HttpResponse(reply % (
		    toUserName, fromUserName, postTime, 
		    "We updated your email address with "+content))	    
	
	else:
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Welcome to SuperVessel"))
    else:
	return HttpResponse("invalid request")

def check_new_user(wechat_u_id):
    this_user = Users.objects(wechat_user_id=wechat_u_id)
    if not this_user:
	this_user = Users(wechat_user_id = wechat_u_id)
	this_user.save()
	logger.info("Added new user")
        return True
    else:
	logger.info("Exiting User")
	return False

def add_supervessel_account(wechat_u_id, content):
    Users.objects(wechat_user_id=wechat_u_id).update_one(set__supervessel_account=content)

def get_users_info():
    headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
	    "Content-type":"application/xml; charset=utf=8"}
    conn = httplib.HTTPSConnection("www.ptopenlab.com",443,key_file,cert_file,True,10)
    conn.request("GET","/cloudlab/api/user/account","",headers)
    response = conn.getresponse()
    logger.info("Return code:"+ str(response.status)+ " reason:"
	    + response.reason)
    if response.status == 200:
        data = response.read()
	logger.info(data)
#        users_list = json.loads(data)
#        logger.info(users_list[0])
#	return users_list
	return 0
    else:
        logger.info("Error sending message,check your account")

def generate_image(image_file):
    logger.info("to generate image "+image_file)
    x = np.linspace(-4,4,30)
    y = np.sin(x)
    plot(x, y, '--*b')
    savefig(image_file)


"""
    if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
        wechat.parse_data(body_text)
        message = wechat.get_message()
        response = None
        if message.type == 'text':
	    if message.content == 'wechat':
	        response = wechat.response_text(u'^_^')
   	    else:
	        response = wechat.response_text(u'..')
        elif message.type == 'image':
	    response = wechat.response_text(u'..')
        else:
	    response = wechat.response_text(u'..')
        return HttpResponse(response)

"""
