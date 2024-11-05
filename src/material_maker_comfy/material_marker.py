
import torch
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.moonshot import Moonshot
from langchain_core.output_parsers import BaseOutputParser
from material_maker_comfy.comfy import generate_video_material


print(torch.__version__)  
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
  1. 生成图像选用 stable diffusion 模型，因此提示词要符合 stable  diffusion 的提示词规范
  2. 提示词要包含核心主题
  3. 提示词要包含风格和细节描述
  4. 提示词要包含颜色和光线描述
  5. 提示词要包含构图描述
  6. 提示词要包含情感和氛围描述
  7. 每个分镜图片生产的视频长度不会超过 5 秒
  8. 分镜的提示词均为英文
  9. 以标准的序列化字符串数组格式返回，返回为一个字符串列表，其中每个列表项中为对应的分镜图像提示词
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

class MaterialMaker():
  entrypoint: str
  theme: str
  content: str
  keywords: str

  def __init__(self, theme, content) -> None:
    self.theme = theme
    self.content = content;


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

  async def run(self):
    output_path = []
    for prompt in self.createPrompt().get('content'):
      output = await generate_video_material(prompt)
      output_path.append(output)
    return output_path



  