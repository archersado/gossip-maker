from langchain.prompts import PromptTemplate


template = """
  <Introduction>
  你是一个内容关键字提取器，根据给出的视频内容文案来提取出视频关键字。
  </Introduction>
  <Requirement>
  1.要求关键字必须简洁，能高度总结内容，并易于筛选视频内容
  2.返回的关键字用，号拼接
  3.返回的关键字翻译成英文
  4.关键字不超过 3 个
  </Requirement>
            
  用户给出的视频内容是:{video_content}
  请提取出对应的视频关键字。
"""

class KeywordsPromptTemplate(PromptTemplate):
  def __init__(self, input_variables):
    super().__init__(input_variables=input_variables, template=template)

  def format(self, **kwargs):
    return super().format(**kwargs)