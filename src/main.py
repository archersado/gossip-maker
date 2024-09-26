from search_top import SearchTopic
from pick_topic import PickTopicPromptTemplate, PickTopicOutputParser
from generate_content import SearchContentPromptTemplate
from video_maker import VideoMaker
from moonshot import MoonshootChat
from generate_keywords import KeywordsPromptTemplate
from video_act import VideoActPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms.moonshot import Moonshot
import os

llm = Moonshot(
  model_name="moonshot-v1-8k", 
  api_key=os.environ.get("MOONSHOT_API_KEY")
)

llmSearch = MoonshootChat(
  api_key=os.environ.get("MOONSHOT_API_KEY")
)


topic = SearchTopic(10)
hot = topic.getWeiboHot()
prompt = PickTopicPromptTemplate(input_variables=["topic", "n"])

get_topic = LLMChain(
  llm=llm, 
  prompt=prompt, 
  output_key="content",
  output_parser=PickTopicOutputParser()
)
get_topic_result = get_topic.invoke(input={"topic": ", ".join(hot), "n": 1})
result = get_topic_result.get('content')
print(result, type(result))
topics = [ topic.get('topic') for topic in result ]

search_content_chain = LLMChain(
  llm=llm,
  prompt = SearchContentPromptTemplate(input_variables=["topic", "story"]),
  output_key = "content",
)
video_act_chain = LLMChain(
  llm=llm,
  prompt = VideoActPromptTemplate(input_variables=["content"]),
  output_key = "video_content",
)
keywords_chain = LLMChain(
  llm=llm,
  prompt = KeywordsPromptTemplate(input_variables=["video_content"]),
  output_key = "keywords",
)
gossip_maker_chain = SequentialChain(
    chains=[search_content_chain, video_act_chain, keywords_chain],
    input_variables=["topic", "story"],
    output_variables=["topic", "video_content", "keywords", "content"],
  )
video_maker = VideoMaker(entrypoint="http://127.0.0.1:8502")

for topic in topics:
  story = llmSearch.run(topic)
  print(topic, story)
  result = gossip_maker_chain.invoke({ "topic": topic, "story": story })
  print(result.get('content'))
  video_maker.run(result.get('topic'), result.get('video_content'), result.get('keywords'))
  
