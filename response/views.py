from django.shortcuts import render
from django.http import HttpResponse
import hashlib, time, re
from xml.etree import ElementTree as ET
from django.utils.datastructures import MultiValueDictKeyError
import logging
from django.views.decorators.csrf import csrf_exempt
from models import Users, virtualmachines
import httplib
import urllib2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from .basic import *
import generate_message
import memcache
import re
from django.contrib import auth

# Create your views here.
matplotlib.use('Agg')
memCache_path = "127.0.0.1:11211"
key_file = "./files/key_file.pem"
cert_file = "./files/cert_file.pem"
image_file_path = "./files/"
logger = logging.getLogger('django')
token = "mytoken"
signature = "f24649c76c3f3d81b23c033da95a7a30cb7629cc"
nonce = '1505845280'


@csrf_exempt
def weixin(request):


    wechat = WechatBasic(token=token)
    mc = memcache.Client([memCache_path],debug=True)
#    Users.auth('dbuser','passw0rd')
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
	    reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime, 
			"Please input command")
	    return HttpResponse(reply_msg)
	if content == "website":
	    reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime,
		 	"Our website: http://ptopenlab.com")
	    return HttpResponse(reply_msg)
	if content == "B":
	    if check_new_user(toUserName):
		reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime,
			"Please tell us your email address registered "
		        +"in SuperVessel cloud via wechat message.")
	        return HttpResponse(reply_msg)
	    else:
		cur_user=Users.objects(wechat_user_id=toUserName).first()
		cur_supervessel_account=cur_user.supervessel_account
		if not cur_supervessel_account:
		    reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
		            "Your email account is empty. Please send us your"
			    +" email registred in supervessel cloud. Then you"
			    +" could get further value-added services")
  		    return HttpResponse(reply_msg)
      		else:
		    users_list=get_users_info()
	            put_users_memcache(users_list, mc)
		    cur_user = mc.get(str(cur_supervessel_account))
	
		    if cur_user:
			logger.info(toUserName + " have registered")
			cur_user_bluepoint = cur_user["balance"];
			return HttpResponse(gen_user_news(
				toUserName, fromUserName, postTime,
				cur_user_bluepoint))
		    else:
			logger.info(toUserName + " haven't registred")
		        reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
 		            "Your email account is "
			    +cur_supervessel_account
			    +" . But it is not found in SuperVessel."
			    +" If you want to update it, please send us"
			    +" the email address in message again")
	 	        return HttpResponse(reply_msg)
 	    
        if content == "news":
	    generate_image(image_file)
	    title = "This is your information on SuperVessel"
	    description = "You have 10 blue points"
	    picUrl = "http://182.92.229.136/image/"
	    reply_msg = generate_message.gen_msg_news(
		    toUserName, fromUserName, postTime,
		    title, description, picUrl)
            logger.info(reply_msg)
	    return HttpResponse(reply_msg)
 
	#if re.match('@', content):
        if re.search("@.*" , content):
	    check_new_user(toUserName)
	    add_supervessel_account(toUserName, content)    
	    reply_msg = generate_message.gen_msg_txt(
		    toUserName, fromUserName, postTime, 
		    "We updated your email address with "+content)	    
            return HttpResponse(reply_msg)	    
	
	else:
	    if check_new_user(toUserName):
		reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime,
			"Please tell us your email address registered "
		        +"in SuperVessel cloud via wechat message.")
	        return HttpResponse(reply_msg)
	    else:
		cur_user=Users.objects(wechat_user_id=toUserName).first()
		cur_supervessel_account=cur_user.supervessel_account
		if not cur_supervessel_account:
		    reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
		            "Your email account is empty. Please send us your"
			    +" email registred in supervessel cloud. Then you"
			    +" could get further value-added services")
  		    return HttpResponse(reply_msg)
      		else:
		    users_list=get_users_info()
	            put_users_memcache(users_list, mc)
		    cur_user = mc.get(str(cur_supervessel_account))
	
		    if cur_user:
			logger.info(toUserName + " have registered")
			description = gen_news_description(cur_user)
			cur_user_bluepoint = cur_user["balance"];

			return HttpResponse(gen_user_news(
				toUserName, fromUserName, postTime,
				description))
		    else:
			logger.info(toUserName + " haven't registred")
		        reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
 		            "Your email account is "
			    +cur_supervessel_account
			    +" . But it is not found in SuperVessel."
			    +" If you want to update it, please send us"
			    +" the email address in message again")
	 	        return HttpResponse(reply_msg)
 	    
    else:
	return HttpResponse("invalid request")


def check_new_user(wechat_u_id):
#    user = auth.authentication(username = 'dbuser', password = 'passw0rd')
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
    logger.info("Update email account: "+wechat_u_id + " " + content);


def get_users_info():
#    headers = {"Content-type": "application/x-www-form-urlencoded",
#            "Accept": "application/json",
#	    "Content-type":"application/xml; charset=utf=8"}
#    conn = httplib.HTTPSConnection("www.ptopenlab.com",443,key_file,cert_file,
#		timeout=10.0 )
    try:
        request = urllib2.Request(
		"https://www.ptopenlab.com/cloudlab/api/user/account")
    except HTTPError, e:
	logger.error("The server couldn't fulfill the request")
	logger.error("Error code is ", e.code)
    except URLError, e:
        logger.error("Failed to reach server")
        logger.error("Reasons ", e.reason)
    else:
	try:
            response = urllib2.urlopen(request)
	except URLError, e:
	    if hasattr(e, 'reason'):
		logger.error("We failed to reach a server.")
		logger.error("Reason: ", e.reason)
	    elif hasattr(e, 'code'):
		logger.error("The server couldn/'t fulfill the request.")
		logger.error("Error code: ", e.code)
	else:
            users_info = response.read()
#            logger.info(users_info)
            return users_info
 
def put_users_memcache(users_info, memCache):
    users_info_json = json.loads(users_info)
    for user_info_json in users_info_json:
	memCache.set(str(user_info_json["username"]), user_info_json)

def generate_image(image_file):
    fig = plt.figure(figsize=(3,1.4))
    fig.suptitle('Resource usage', fontsize=10)
    plt.xlabel('date', fontsize=3)
    plt.ylabel('seconds', fontsize=3)
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    x = np.linspace(-3,3,10)
    y = np.sin(x)
    plt.plot(x, y, '--*r')    
    fig.savefig(image_file)

def show_image(request, param1):
    image_file_name = image_file_path + param1 + ".png"
    image_data = open(image_file_name,"rb").read()
    return HttpResponse(image_data, content_type="image/png")

def gen_user_news(toUserName, fromUserName, postTime, description):
    image_file_name = image_file_path + toUserName + postTime + ".png"
    generate_image(image_file_name)
    title = "This is your information on SuperVessel"
#    description = "You have " + str(bluepoints) + " blue points"
    picUrl = "http://182.92.229.136/images/" + toUserName + postTime
    reply_msg = generate_message.gen_msg_news(
	    toUserName, fromUserName, postTime,
	    title, description, picUrl)
    return reply_msg

def gen_news_description(current_user):
    bluepoints = current_user['balance']
    description = "You have " + str(bluepoints) + " blue points.\n"
    num_vm = len(virtualmachines.objects(
			supervessel_account = current_user['username']))
    logger.info(str(num_vm))
    vm_list = virtualmachines.objects(
			supervessel_account = current_user['username'])
    for vm in vm_list:
        vm_info = "VM: " + vm.vm_name + "  active time: " + str(vm.cpu_usage) + "s\n"
#	description = description.join(vm_info)
  	description = description + vm_info
        logger.info(description)
    return description

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
