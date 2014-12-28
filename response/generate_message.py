# -*- coding: utf-8 -*-

reply_txt ="""<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>"""



reply_news ="""<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <Content><![CDATA[]]></Content>
    <ArticleCount>1</ArticleCount>
    <Articles>
        <item>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[%s]]>
	    </Description>
            <PicUrl><![CDATA[%s]]></PicUrl>
            <Url><![CDATA[]]></Url>
        </item>
    </Articles>
    <FuncFlag>0</FuncFlag>
</xml>"""

def gen_msg_news(toUserName, fromUserName, postTime, 
	title, description, picUrl):
    msg_news = reply_news % (toUserName, fromUserName, 
		postTime, title, description, picUrl)
    return msg_news

def gen_msg_txt(toUserName, fromUserName, postTime, content_txt):
    msg_txt = reply_txt % (toUserName, fromUserName,
		postTime, content_txt)
    return msg_txt

