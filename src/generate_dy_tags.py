from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser

template = """
  <Introduction>
    你是一个抖音视频标签总结工具，负责将视频内容总结为合适的抖音视频话题标签
  </Introduction>

  <Instructions>
  1. 需要理解提供的视频内容，并总结成不超过 10 个的抖音视频话题标签短词
  2. 总结的标签必须具备话题性
  3. 不要生成晦涩难懂的话题标签
  4. 话题标签不能包含政治内容
  5. 话题标签不能包含色情内容
  6. 返回的话题标签用，号拼接
  </Instructions>

  <Input>
    内容编辑提供的内容是: {content}
  </Input>
"""


class DyTagsTemplate(PromptTemplate):
  def __init__(self, input_variables):
    super().__init__(input_variables=input_variables, template=template)

  def format(self, **kwargs):
    return super().format(**kwargs)
  

class DyTagsOutputParser(BaseOutputParser):
  def parse(self, text: str):
    return text.split(",")

  @property
  def _type(self) -> str:
    return "dy_tags_output_parser"