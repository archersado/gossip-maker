

import requests

class SearchTopic:
  def __init__(self, topK):
    self.topK = topK
    self.weiboHot = []
  
  def getWeiboHot(self):
    try:
      url = "https://weibo.com/ajax/side/hotSearch"
      response = requests.get(url)
      res = response.json()
      print(res)
      if (res.get("ok") == 1):
        list = res.get("data").get("realtime")
        print(list)
        topics = [item.get("word") for item in list[:self.topK]]
        self.weiboHot = topics
        return topics
      else:
        return []
    except Exception as e:
      print(e)
      return []
    