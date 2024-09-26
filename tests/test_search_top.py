from src.search_top import SearchTopic

def test_search_top():
  topic = SearchTopic(10)
  topic.getWeiboHot()
  print(topic.weiboHot)

