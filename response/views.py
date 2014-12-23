from django.shortcuts import render
from django.http import HttpResponse
import hashlib, time, re
from xml.etree import ElementTree as ET
from django.utils.datastructures import MultiValueDictKeyError
import logging
from django.views.decorators.csrf import csrf_exempt


#import django.utils.log import logger
from .basic import *

# Create your views here.

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
	toUserName = xml.find("FromUserName").text
	postTime = str(int(time.time()))
	if not content:
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Please input command"))
	if content == "a":
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Hello to BizUser"))
	else:
	    return HttpResponse(reply % (
		toUserName, fromUserName, postTime, "Function is under develop"))
    else:
	return HttpResponse("invalid request")

 


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
