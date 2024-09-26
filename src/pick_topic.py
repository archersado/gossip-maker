from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser

import json

template = """
  <Introduction>
    你是一个负责民生新闻话题板块的总编，工作职能是筛选编辑输入的热点话题，挑选{n}个最具有新闻性、话题性的热点, 并给出挑选理由
  </Introduction>

  <Instructions>
  1. 话题不能包含政治内容
  2. 话题不能包含色情内容
  3. 话题应当具备一定的传播性
  4. 话题如果具备趣味性、猎奇性可以优先考虑
  5. 要贴近百姓日常生活
  6. 以标准 JSON List 格式返回，每个话题项中，话题名称放在 topic 属性中，理由放在 reason 属性中, 
  </Instructions>

  <Input>ji
    编辑输入的热点话题是: {topic}
  </Input>
"""


class PickTopicPromptTemplate(PromptTemplate):
  def __init__(self, input_variables):
    super().__init__(input_variables=input_variables, template=template)

  def format(self, **kwargs):
    return super().format(**kwargs)
  

class PickTopicOutputParser(BaseOutputParser):
  def parse(self, text: str):
    print(text);
    return json.loads(text)

  @property
  def _type(self) -> str:
    return "pick_topic_output_parser"