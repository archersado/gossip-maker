from typing import *
 
import os
import json
 
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
 

class MoonshootChat():
    cleint: OpenAI
    api_key: str

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://api.moonshot.cn/v1",
            api_key=os.environ.get("MOONSHOT_API_KEY"),
        )

    def search_impl(self, arguments: Dict[str, Any]) -> Any:
        return arguments
    

    def completion(self, messages) -> Choice:
        completion = self.client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=messages,
            temperature=0.3,
            tools=[
                {
                    "type": "builtin_function",  # <-- 使用 builtin_function 声明 $web_search 函数，请在每次请求都完整地带上 tools 声明
                    "function": {
                        "name": "$web_search",
                    },
                }
            ]
        )
        return completion.choices[0]


    def run(self, message: str):
        messages = [
            {"role": "system", "content": "你是一个内容搜索引擎，根据用户提供的话题来搜索该话题最新内容并进行总结, 包含内容事实叙述，不要返回引用内容"},
        ]
        messages.append(
            {
                "role": "user",
                "content": f"用户的期望搜索的话题是: {message}"
            }
        )

        finish_reason = None
        while finish_reason is None or finish_reason == "tool_calls":
            choice = self.completion(messages)
            finish_reason = choice.finish_reason
            if finish_reason == "tool_calls":  # <-- 判断当前返回内容是否包含 tool_calls
                messages.append(choice.message)  # <-- 我们将 Kimi 大模型返回给我们的 assistant 消息也添加到上下文中，以便于下次请求时 Kimi 大模型能理解我们的诉求
                for tool_call in choice.message.tool_calls:  # <-- tool_calls 可能是多个，因此我们使用循环逐个执行
                    tool_call_name = tool_call.function.name
                    tool_call_arguments = json.loads(tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列化一下
                    if tool_call_name == "$web_search":
                        tool_result = self.search_impl(tool_call_arguments)
                    else:
                        tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
    
                    # 使用函数执行结果构造一个 role=tool 的 message，以此来向模型展示工具调用的结果；
                    # 注意，我们需要在 message 中提供 tool_call_id 和 name 字段，以便 Kimi 大模型
                    # 能正确匹配到对应的 tool_call。
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call_name,
                        "content": json.dumps(tool_result),  # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                    })
    
        return choice.message.content  # <-- 在这里，我们才将模型生成的回复返回给用户        
    