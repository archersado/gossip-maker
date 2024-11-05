
import torch
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.moonshot import Moonshot
from langchain_core.output_parsers import BaseOutputParser

from diffusers import StableVideoDiffusionPipeline, StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import load_image, export_to_video



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
  1. 分镜内容切割要准确
  2. 分镜内容的描述要足够充分
  3. 每个分镜图片生产的视频长度不会超过 5 秒
  4. 分镜的提示词均为英文
  5. 以标准的序列化字符串数组格式返回，返回为一个字符串列表，其中每个列表项中为对应的分镜图像提示词
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

  def run(self):

    # sd_pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1", torch_dtype=torch.float16)
    # sd_pipe.scheduler = DPMSolverMultistepScheduler.from_config(sd_pipe.scheduler.config)
    # sd_pipe = sd_pipe.to("mps")
    # sd_pipe.enable_attention_slicing()    

    # for prompt in self.createPrompt().get('content'):
      # image = sd_pipe(prompt, num_inference_steps=15, height=512, width=768).images[0]
      # image.save(prompt + ".png")


      # pipe = StableVideoDiffusionPipeline.from_pretrained(
      #     "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
      # )
      # pipe.enable_model_cpu_offload()
      # pipe.enable_attention_slicing() 
      # # Load the conditioning image
      # image = image.resize((1024, 576))

      # generator = torch.manual_seed(42)
      # frames = pipe(image, decode_chunk_size=8, generator=generator).frames[0]
      # export_to_video(frames, prompt + ".mp4", fps=7)
    pipe = StableVideoDiffusionPipeline.from_pretrained(
      "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
      )
    pipe = pipe.to("cpu") 
    pipe.enable_model_cpu_offload()
    pipe.unet.enable_forward_chunking()
    pipe.enable_attention_slicing() 
    image = load_image("Victoria's Secret Fashion Show 2024 banner.png")
      # Load the conditioning image
    image = image.resize((1024, 576))

    generator = torch.manual_seed(42)
    frames = pipe(image, decode_chunk_size=2, generator=generator).frames[0]
    export_to_video(frames, "Victoria's Secret Fashion Show 2024 banner" + ".mp4", fps=7)


  