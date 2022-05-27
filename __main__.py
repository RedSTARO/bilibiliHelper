import requests,json
from log import logger
from api import coinTodayExp,usernav,mangaSign,attentionVideo,popularVideo,liveSign,coinAdd,videoProgress,videoShare,silverNum,silver2coin
from setting import bili_jct,coinnum,select_like,headers,SCKEY
sendInfo = ""

# 通知到微信
def sendmsgtowx(title,desp):
    if SCKEY == '':
        logger.info('未配置推送微信')
        return
    else:
        url = "https://sctapi.ftqq.com/"+SCKEY+".send?title="+title+"&desp="+desp
        requests.get(url=url)
# 每日获取经验
class Exp:
    def __init__(self):
        global sendInfo
        # hasShare = 0
        self.getUserinfo()
        self.liveSign()
        self.mangaSign()
        self.getAttentionVideo()
        self.getPopularVideo()
        self.silverToCoins()
        self.share(self.popular_aidList[1]['aid'])
        self.report(self.popular_aidList[1]['aid'],self.popular_aidList[1]['cid'],1000)
        # 投币(关注up主新视频和热门视频)
        if(coinnum==0):
            logger.info('设置为白嫖模式，不再为视频投币')
            sendInfo += "设置为白嫖模式，不再为视频投币\n"
            return
        if self.money < 2:
            logger.info('硬币不足，终止投币')
            sendInfo += "硬币不足，终止投币\n"
            return
        for item in  self.popular_aidList:
            exp = self.getCoinTodayExp()
            if exp == 50:
                logger.info('今日投币经验已达成')
                sendInfo += "今日投币经验已达成\n"
                return
            self.coin(item['aid'])
    # 获取用户信息
    def getUserinfo(self):
        global sendInfo
        try:
            res = requests.get(url=usernav,headers=headers)
            user_res = json.loads(res.text)['data']
            money = user_res['money']
            uname = user_res['uname']
            self.uid = user_res['wallet']['mid']
            level_info = user_res['level_info']
            self.money = money
            logger.info('用户昵称：' + uname)
            sendInfo += "用户昵称:" + uname + "\n"
            logger.info('硬币余额：' + str(money))
            sendInfo += "硬币余额:" + str(money) + "\n"
            logger.info('当前等级：{},当前经验：{},下一级所需经验：{}'.format(level_info['current_level'],level_info['current_exp'],level_info['next_exp']-level_info['current_exp']))
            sendInfo += '当前等级：{},当前经验：{},下一级所需经验：{}'.format(level_info['current_level'],level_info['current_exp'],level_info['next_exp']-level_info['current_exp']) + "\n"
        except:
#             sendmsgtowx()
            logger.info('请求异常')
            sendInfo += "请求异常" + "\n"
    # 获取关注的up最新发布的视频
    def getAttentionVideo(self):
        global sendInfo
        url = attentionVideo+'?uid='+str(self.uid)+'&type_list=8&from=&platform=web'
        res = requests.get(url=url,headers=headers)
        video_list = []
        resDict = json.loads(res.text)['data']
        if('cards' in resDict):
            for item in resDict['cards']:
                video_list.append({'aid':json.loads(item['card'])['aid'],'cid':json.loads(item['card'])['cid']})
        self.attention_aidList = video_list
    def getCoinTodayExp(self):
        global sendInfo
        url = coinTodayExp
        res = requests.get(url=url,headers=headers)
        exp = json.loads(res.text)['data']
        # self.todayExp = exp
        return exp
    # 获取近期热门视频列表
    def getPopularVideo(self):
        global sendInfo
        url = popularVideo
        res = requests.get(url=url,headers=headers)
        video_list = []
        for item in json.loads(res.text)['data']['list']:
            video_list.append({'aid':item['aid'],'cid':item['cid']})
        self.popular_aidList = video_list
    # B站直播签到
    def liveSign(self):
        global sendInfo
        try:
            url = liveSign
            res = requests.get(url=url,headers=headers)
            logger.info('直播签到信息：'+json.loads(res.text)['message'])
            sendInfo += '直播签到信息：'+json.loads(res.text)['message'] + "\n"
        except:
            logger.info('请求异常')
            sendInfo += '请求异常'  + "\n"
    #  通过aid为视频投币
    def coin(self,aid):
        global sendInfo
        url = coinAdd
        post_data = {
            "aid": aid,
            "multiply": coinnum,
            "select_like": select_like,
            "cross_domain": "true",
            "csrf": bili_jct
        }
        res = requests.post(url=url,headers=headers,data=post_data)
        coinRes = json.loads(res.text)
        if coinRes['code'] == 0:
            # 投币成功
            logger.info('投币成功')
            sendInfo += '投币成功'  + "\n"
            self.getCoinTodayExp()
        else:
            logger.info('投币失败:' + coinRes['message'])
            sendInfo += '投币失败:' + coinRes['message']  + "\n"
    # 上报视频进度
    def report(self, aid, cid, progres):
        global sendInfo
        url = videoProgress
        post_data = {
            "aid": aid,
            "cid": cid,
            "progres": progres,
            "csrf": bili_jct
            }
        res = requests.post(url=url, data=post_data,headers=headers)
        Res = json.loads(res.text)
        if Res['code'] == 0:
            # 投币成功
            logger.info('上报视频进度成功')
            sendInfo += '上报视频进度成功'  + "\n"
            self.getCoinTodayExp()
        else:
            logger.info('上报视频进度失败：' + Res['message'])
            sendInfo += '上报视频进度失败：' + Res['message']  + "\n"
    #分享指定av号视频
    def share(self, aid):
        global sendInfo
        url = videoShare
        post_data = {
            "aid": aid,
            "csrf": bili_jct
            }
        res = requests.post(url=url, data=post_data,headers=headers)
        share_res = json.loads(res.text)
        if share_res['code'] == 0:
            self.hasShare = 1
            logger.info('视频分享成功')
            sendInfo += '视频分享成功'  + "\n"
        else:
            logger.info('每日任务分享视频：' + share_res['message'])
            sendInfo += '每日任务分享视频：' + share_res['message']  + "\n"
    #漫画签到
    def mangaSign(self):
        global sendInfo
        try:
            url = mangaSign
            post_data = {
                "platform": 'android'
            }
            res = requests.post(url=url,headers=headers,data=post_data)
            if json.loads(res.text)['code'] == 0:
                logger.info('漫画签到成功')
                sendInfo += '漫画签到成功'  + "\n"
            else:
                logger.info('漫画已签到或签到失败')
                sendInfo += '漫画已签到或签到失败'  + "\n"
        except:
            logger.info('漫画签到异常')
            sendInfo += '漫画签到异常'  + "\n"
    def silverToCoins(self):
        global sendInfo
        res1 = requests.get(url=silverNum,headers=headers)
        silver_num = json.loads(res1.text)['data']['silver']
        if silver_num < 700:
            logger.info('直播银瓜子不足700兑换硬币')
            sendInfo += '直播银瓜子不足700兑换硬币'  + "\n"
            return
        post_data = {
            "csrf_token": bili_jct,
            "csrf": bili_jct,
            # "visit_id": ""
        }
        res2 = requests.post(url=silver2coin,headers=headers,data=post_data)
        res_silver2Coins = json.loads(res2.text)
        if res_silver2Coins['code']==0:
            logger.info('直播银瓜子兑换结果：成功')
            sendInfo += '直播银瓜子兑换结果：成功'  + "\n"
        else:
            logger.info('直播银瓜子兑换结果：'+res_silver2Coins['msg'])
            sendInfo += '直播银瓜子兑换结果：'+res_silver2Coins['msg']  + "\n"

Exp()


sendmsgtowx('bilibiliHelper' , sendInfo)
print("Send text of log.log to WeCHat success.")


# -*- coding: UTF-8 -*-
# import threading
#
# # 任务执行间隔时间，下面是 1s 也就每秒执行一次
# INTERVAL_TIME = 86400
# runningTime = 0
# # INTERVAL_TIME = 10
# def task():
#     # 在这里写下你要执行的命令,例如打印 HelloWorld
#     Exp()
#     global runningTime
#     runningTime += 1
#     logger.info("BilibiliHelper is running! Running time : " + str(runningTime) + " day.")
#
# def cron():
#     task()
#     threading.Timer(INTERVAL_TIME, cron).start()
#
# # 调用 cron 函数，即开始任务
# cron()
