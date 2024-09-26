from src.search_top import SearchTopic
from src.moonshot import MoonshootChat
import os

llm = MoonshootChat(
  api_key=os.environ.get("MOONSHOT_API_KEY")
)

def test_search_top():
  topic = SearchTopic(10)
  hot = topic.getWeiboHot()

  content = llm.run(hot[0])
  print(content)

