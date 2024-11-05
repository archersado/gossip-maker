from stable_diffusion_videos import StableDiffusionWalkPipeline
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.moonshot import Moonshot
from langchain_core.output_parsers import BaseOutputParser
import requests
import time
import json

llm = Moonshot(
  model_name="moonshot-v1-128k", 
  api_key=os.environ.get("MOONSHOT_API_KEY")
)

template = """
  <Introduction>
    你是一个负责将视频文案转换成视频分镜图像提示词的工具，根据输入的视频文案，生成对应的视频分镜图像的提示词，便于图像生成模型根据提示词来生成合适的视频分镜
  </Introduction>

  <Instructions>
  1. 分镜内容切割要准确
  2. 分镜内容的描述要足够充分
  3. 每个分镜图片生产的视频长度不会超过 5 秒
  4. 以序列化 string JSON List 字符串格式返回，每个列表项中为对应的分镜图像提示词, 类型是字符串, 用英文引号包裹
  5. 控制一下分
  </Instructions>

  <Input>ji
    输入视频文案是: {content}
  </Input>
"""


class VideoImagePromptTemplate(PromptTemplate):
  def __init__(self, input_variables):
    super().__init__(input_variables=input_variables, template=template)

  def format(self, **kwargs):
    return super().format(**kwargs)


class VideoImageOutputParser(BaseOutputParser):
  def parse(self, text: str):
    print(text);
    return json.loads(text)

  @property
  def _type(self) -> str:
    return "video_img_output_parser"

class VideoMaker():
  entrypoint: str
  theme: str
  content: str
  keywords: str
  apiKey: str
  output_file_name: str

  def __init__(self, theme, content) -> None:
    self.theme = theme
    self.content = content;
    self.apiKey = os.environ.get("MINIMAX_API_KEY")
    self.output_file_name = ''


  def createPrompt(self): 
    prompt = VideoImagePromptTemplate(input_variables=['content'])
    image_prompts = LLMChain(
      llm=llm, 
      prompt=prompt, 
      output_key="content",
      output_parser=VideoImageOutputParser()
    )
    result = image_prompts.invoke({ 'content': self.content })
    return result

  def run(self):
    prompt_list = self.createPrompt()
    for prompt in prompt_list.get('content'):
      task_id = self.invoke_video_generation(prompt)
      print("-----------------已提交视频生成任务-----------------")
      while True:
          time.sleep(30)
          file_id, status = query_video_generation(task_id)
          if file_id != "":
              fetch_video_result(file_id)
              print("---------------生成成功---------------")
              break
          elif status == "Fail" or status == "Unknown":
              print("---------------生成失败---------------")
              break

  def invoke_video_generation(self, prompt)->str:
    url = "https://api.minimax.chat/v1/video_generation"
    payload = json.dumps({
      "prompt": prompt,
      "model": "video-01"
    })
    headers = {
      'authorization': 'Bearer ' + os.environ.get("MINIMAX_API_KEY"),
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    task_id = response.json()['task_id']
    print("视频生成任务提交成功，任务ID："+task_id)
    return task_id

def query_video_generation(task_id: str):
    url = "https://api.minimax.chat/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + os.environ.get("MINIMAX_API_KEY")
    }
    response = requests.request("GET", url, headers=headers)
    status = response.json()['status']
    if status == 'Queueing':
        print("...队列中...")
        return "", 'Queueing'
    elif status == 'Processing':
        print("...生成中...")
        return "", 'Processing'
    elif status == 'Success':
        return response.json()['file_id'], "Finished"
    elif status == 'Fail':
        return "", "Fail"
    else:
        return "", "Unknown"


def fetch_video_result(self, file_id: str):
    print("---------------视频生成成功，下载中---------------")
    url = "https://api.minimax.chat/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+os.environ.get("MINIMAX_API_KEY"),
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    download_url = response.json()['file']['download_url']
    print("视频下载链接：" + download_url)
    video_path = os.path.join(os.getcwd(), 'videos')
    file_name = os.path.join(video_path, self.theme + file_id + '.mp4')
    with open(file_name, 'wb') as f:
        f.write(requests.get(download_url).content)
    print("已下载在："+ file_name)
