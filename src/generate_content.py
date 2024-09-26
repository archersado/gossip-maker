from langchain.prompts import PromptTemplate


template = """
  <Introduction>
    你是一个热点舆情的编辑，根据热点话题与话题的内容事实，总结内容被给出自己的评论
  </Introduction>

  <Instructions>
  1. 必须包含话题的内容事实
  2. 附上自己的见解评论，内容必须积极健康, 并且带有趣味性和话题性，利于传播
  3. 内容必须原创，不能抄袭
  4. 返回内容要包含搜索的内容
  </Instructions>

  <Input>
    当前的热点话题是: {topic}, 此话题的内容事实是: {story}
  </Input>
"""


class SearchContentPromptTemplate(PromptTemplate):
  def __init__(self, input_variables):
    super().__init__(input_variables=input_variables, template=template)

  def format(self, **kwargs):
    return super().format(**kwargs)