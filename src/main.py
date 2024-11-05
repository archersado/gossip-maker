from search_top import SearchTopic
from pick_topic import PickTopicPromptTemplate, PickTopicOutputParser
from generate_content import SearchContentPromptTemplate
from video_maker import VideoMaker
from moonshot import MoonshootChat
from generate_keywords import KeywordsPromptTemplate
from generate_dy_tags import DyTagsTemplate, DyTagsOutputParser
from video_act import VideoActPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms.moonshot import Moonshot
from config import BASE_DIR
from uploader.dy import douyin_cookie_auth, douyin_setup, DouYinVideo
import os
import asyncio


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
get_topic_result = get_topic.invoke(input={"topic": ", ".join(hot), "n": 3})
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
video_maker = VideoMaker(entrypoint="http://localhost:8502")

for topic in topics:
  story = llmSearch.run(topic)
  print(topic, story)
  result = gossip_maker_chain.invoke({ "topic": topic, "story": story })
  content = result.get("content")
  keywords = result.get('keywords')
  video_path = video_maker.run(topic, result.get('video_content'), keywords)
  account_file = os.path.join(BASE_DIR, "account.json")
  if douyin_cookie_auth(account_file,type) == False:
    asyncio.run(douyin_setup(account_file))
  prompt = DyTagsTemplate(input_variables=["content"])
  tag_chain = LLMChain(
    llm=llm, 
    prompt=prompt, 
    output_key="tags",
    output_parser=DyTagsOutputParser()
  )
  tag_result = tag_chain.invoke(input={"content": content})
  tags = tag_result.get('tags')

  print(topic, video_path, tags)
  app = DouYinVideo(
    title = topic,
    file_path = video_path,
    tags=tags,
    # publish_date = datetime.now(),
    account_file=account_file,
    location='上海-上海')
  asyncio.run(app.main(), debug=False)   
