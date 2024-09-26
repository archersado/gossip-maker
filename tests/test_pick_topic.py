from src.search_top import SearchTopic
from src.pick_topic import PickTopicPromptTemplate, PickTopicOutputParser
from langchain.chains import LLMChain
from langchain_community.llms.moonshot import Moonshot
import os

llm = Moonshot(
  model_name="moonshot-v1-8k", 
  api_key=os.environ.get("MOONSHOT_API_KEY")
)

def test_search_top():
  topic = SearchTopic(10)
  hot = topic.getWeiboHot()
  prompt = PickTopicPromptTemplate({ "topic": ", ".join(hot), "n": 3 })

  chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    output_key="content",
    output_parser=PickTopicOutputParser()
  )
  result = chain.invoke(input={"topic": ", ".join(hot), "n": 3})
  print(result)

