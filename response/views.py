#!/usr/bin/python
#encoding:utf-8
import sys
import os
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
import json
from .basic import *
import generate_message
import memcache
import re
from django.contrib import auth
import generate_bit_students_file
import send_email
from get_info_user import get_cur_cpu_usage
from generate_figure import generate_days_trend_curve,generate_cur_cpu_bar

# Create your views here.
matplotlib.use('Agg')
memCache_path = "127.0.0.1:11211"

key_file = "./files/key_file.pem"
cert_file = "./files/cert_file.pem"
bit_students_file_xls = "./files/bit_students_file.xls"

image_file_path = "./files/"
no_vm_running_image = image_file_path + "no_vm_running.png"
logger = logging.getLogger('django')
wechat_token = "mytoken"
signature = "f24649c76c3f3d81b23c033da95a7a30cb7629cc" #for Wechat
APPSECRET = "1322de6faef0680c4ee3cd2f922e58fb"	#for Wechat
APPID = "wx882aec4c013c1ab0" #for Wechat
nonce = '1505845280'
num_days = 9
active_image_file = ""

USER_PRO = "user"
MANAGE_PRO = "management"
BIT_BIGDATA_TEACHER = "bit_bigdata_teacher"


smtp_server = "smtp.sendgrid.com"
mail_user = "admin@ptopenlab.com"
mail_passwd = "ibm123crl"
mail_from = "Admin of SuperVessel"

@csrf_exempt
def weixin(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    wechat = WechatBasic(token=wechat_token)
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
        try:	
	    content = xml.find("Content").text
        except AttributeError, e:
	    content = None

        fromUserName = xml.find("ToUserName").text
        logger.info("ToUser:" + fromUserName)
	toUserName = xml.find("FromUserName").text
#        logger.info("FromUser: " + toUserName)
	postTime = str(int(time.time()))
	if not content:
	    check_new_user(toUserName)
 	    add_account_property(toUserName, USER_PRO)
	    reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime, 
			"欢迎来到 SuperVessel，按任意键可以查看您在SuperVessel上的资源状态")
	    return HttpResponse(reply_msg)

	if content == "crl123super":
	    check_new_user(toUserName)
	    add_account_property(toUserName, MANAGE_PRO)    
	    reply_msg = generate_message.gen_msg_txt(
		    toUserName, fromUserName, postTime, 
		    "我们已经把您添加到management组别")	    
            return HttpResponse(reply_msg)

	if content == "p0wer4bit":
	    check_new_user(toUserName)
	    add_account_property(toUserName, BIT_BIGDATA_TEACHER)
	    reply_msg = generate_message.gen_msg_txt(
		    toUserName, fromUserName, postTime,
		    "您是北邮负责大数据的老师，发送 students ，可以获得学生大数据平台的使用统计邮件")
	    return HttpResponse(reply_msg)

	if content=="getalluser":
	    ACCESS_TOKEN = wechat.get_access_token()
            try:
		url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=" + ACCESS_TOKEN
		logger.info(url)
                request = urllib2.Request(url)
	    except urllib2.HTTPError, e:
        	logger.error("The server couldn't fulfill the request")
	        logger.error("Error code is ", e.code)
	    except urllib2.URLError, e:
        	logger.error("Failed to reach server")
	        logger.error("Reasons ", e.reason)
	    else:
        	try:
	            response = urllib2.urlopen(request)
	        except urllib2.URLError, e:
        	    if hasattr(e, 'reason'):
                	logger.error("We failed to reach a server.")
	                logger.error("Reason: ", e.reason)
        	    elif hasattr(e, 'code'):
                	logger.error("The server couldn/'t fulfill the request.")
	                logger.error("Error code: ", e.code)
        	else:
	            users_info = response.read()
	            logger.info(users_info)
	    	    reply_msg = generate_message.gen_msg_txt(
		    	toUserName, fromUserName, postTime, 
		    	"已经收到所有用户ID更新")	   
	
            	return HttpResponse(reply_msg)	    
	    



	if (content=="students") or (content=="Students") or (content=="students ") or (content=="Students "):

	    check_new_user(toUserName)

	    if check_property(toUserName, BIT_BIGDATA_TEACHER):
		generate_bit_students_file.gen_students_xls(bit_students_file_xls)
		cur_user=Users.objects(wechat_user_id=toUserName).first()	
		cur_supervessel_account=cur_user.supervessel_account
		mail_subject = "Summary of resource activity status for BIT Big Data course"
		mail_text = "本邮件是当前大数据课程中，学生作业资源使用的统计，数值仅供参考，谢谢！"
		attached_files=[]
		attached_files.append(bit_students_file_xls)
		to_address=[]
		to_address.append(cur_supervessel_account)
		if cur_supervessel_account:
		    send_email.send_mail(smtp_server, mail_user, mail_passwd, 
				mail_from, to_address,
				mail_subject, mail_text,
				attached_files)
		    reply_msg = generate_message.gen_msg_txt(
		    	toUserName, fromUserName, postTime, 
		    	"文件已经生成，并发送到您的邮箱: "+cur_supervessel_account)	   
		else:
		    reply_msg = generate_message.gen_msg_txt(
		    	toUserName, fromUserName, postTime, 
		    	"对不起，您还没有登记您的电子邮箱。")	   
	
            	return HttpResponse(reply_msg)	    
	    else:
                reply_msg = generate_message.gen_msg_txt(
                        toUserName, fromUserName, postTime,
                        "对不起，您不是注册老师")
                return HttpResponse(reply_msg)

	    

        if re.search("@.*" , content):
	    check_new_user(toUserName)
	    add_supervessel_account(toUserName, content)    
	    reply_msg = generate_message.gen_msg_txt(
		    toUserName, fromUserName, postTime, 
		    "我们已经把您的邮箱地址更新为："+content)	    
            return HttpResponse(reply_msg)	    
	
	else:
	    if check_new_user(toUserName):
		reply_msg = generate_message.gen_msg_txt(
			toUserName, fromUserName, postTime,
			"您还没有登记电子邮箱信息。请直接输入 "
		        +"您在SuperVessel云上注册的电子邮箱地址。")
	        return HttpResponse(reply_msg)
	    else:
		cur_user=Users.objects(wechat_user_id=toUserName).first()
		cur_supervessel_account=cur_user.supervessel_account
		if not cur_supervessel_account:
		    reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
		            "您的邮箱信息是空的。如果您想在微信平台上获得SuperVessel"
			    +" 云平台的增值服务，请直接输入您在SuperVessel云上的注册邮箱。"
			    +" 如果您是新用户，请直接进入 http://ptopenlab.com")
  		    return HttpResponse(reply_msg)
      		else:
#		    users_list=get_users_info()
#	            put_users_memcache(users_list, mc)
		    try:
		        cur_user = mc.get(str(cur_supervessel_account))
		    except:
			cur_user = False
			logger.info("User input has some problem")

		    if cur_user:
			logger.info(toUserName + " have registered")
                        active_image_file = image_file_path + toUserName + postTime + ".png"
#			logger.info( active_image_file)
			description = gen_news_description(cur_user, active_image_file)
			cur_user_bluepoint = cur_user["balance"];

			return HttpResponse(gen_user_news(
				toUserName, fromUserName, postTime,
				description))
		    else:
			logger.info(toUserName + " haven't registred")
		        reply_msg = generate_message.gen_msg_txt(
			    toUserName, fromUserName, postTime,
 		            "您的邮箱地址是 "
			    +cur_supervessel_account
			    +" . 但未在 SuperVessel中注册."
			    +" 如果您要更新它，请把您的邮箱地址在本微信公众号发送给我们。")
	 	        return HttpResponse(reply_msg)
 	    
    else:
	return HttpResponse("invalid request")


def check_new_user(wechat_u_id):
#    user = auth.authentication(username = 'dbuser', password = 'passw0rd')
    this_user = Users.objects(wechat_user_id=wechat_u_id)
    if not this_user:
	this_user = Users(wechat_user_id = wechat_u_id, 
		user_property = USER_PRO)
	this_user.save()
	logger.info("Added new user")
        return True
    else:
	logger.info("Exiting User")
	return False

def check_property(wechat_u_id, property_str):
    this_user = Users.objects(wechat_user_id=wechat_u_id).first()    
    if this_user.user_property == property_str:
	logger.info("This user is " + property_str)
	return True
    else:
	logger.info("The user with id " + wechat_u_id + " is not teacher")	
	return False
	

def add_supervessel_account(wechat_u_id, content):
    Users.objects(wechat_user_id=wechat_u_id).update_one(set__supervessel_account=content)
    logger.info("Update email account: "+wechat_u_id + " " + content)

def add_account_property(wechat_u_id, property_str):
    this_user = Users.objects(wechat_user_id=wechat_u_id).first()
    Users.objects(wechat_user_id=wechat_u_id).update_one(
		set__user_property=property_str)
    logger.info("Add the account " + wechat_u_id + " into " + property_str + " group")


def get_users_info():
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

#def get_access_token():

#    try:
#	file_obj = open(token_file,'r')
#	token_stream = file_obj.read()
#	file_obj.close()
#    except:
#        logger.error("Access token file is not exist")
#    else:
#        return token_stream


def put_users_memcache(users_info, memCache):
    users_info_json = json.loads(users_info)
    for user_info_json in users_info_json:
	memCache.set(str(user_info_json["username"]), user_info_json)

# This is the activity trend curve of past number of days of an user

def show_image(request, param1):
    image_file_name = image_file_path + param1 + ".png"
    image_data = open(image_file_name,"rb").read()
    return HttpResponse(image_data, content_type="image/png")

def gen_user_news(toUserName, fromUserName, postTime, description):
#    image_file_name = image_file_path + toUserName + postTime + ".png"
    title = "您在 SuperVessel 云平台上的使用信息"
#    description = "You have " + str(bluepoints) + " blue points"
    picUrl = "http://182.92.229.136/images/" + toUserName + postTime
    reply_msg = generate_message.gen_msg_news(
	    toUserName, fromUserName, postTime,
	    title, description, picUrl)
    return reply_msg

def gen_news_description(current_user, image_file):
    bluepoints = current_user['balance']
    description = "您有 " + str(bluepoints) + " 个蓝点.\n"
    num_vm = len(virtualmachines.objects(
			supervessel_account = current_user['username']))
#    logger.info(str(num_vm))
    vm_list = virtualmachines.objects(
			supervessel_account = current_user['username'])
    active_list = []
    for i in range(num_days):
	active_list.append(0)
    for vm in vm_list:
        vm_info = "虚拟机: " + vm.vm_name + "  当天活跃时间: " + str(vm.cpu_usage_list[num_days-1]) + "秒, 网络字节: " + str(vm.network_usage_list[num_days-1]) + "K\n"
	for i in range(num_days):
   	    active_list[i] = active_list[i] + vm.cpu_usage_list[i]
#	description = description.join(vm_info)
  	description = description + vm_info
#        logger.info(description)
#    logger.info(str(active_list))
#    logger.info(active_image_file)

#    generate_days_trend_curve(image_file, num_days, active_list)
    result = get_cur_cpu_usage(current_user['username'])
    logger.info(result)
    if (result):
        cpu_usage_list = result['cpu_usage_list'][0]
        name_list = result['name_list'][0]
        generate_cur_cpu_bar(image_file, name_list, cpu_usage_list)
    else:
        cmd = "cp " + no_vm_running_image + " " + image_file
        os.system(cmd)
	logger.info(cmd)
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
