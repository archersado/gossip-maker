import requests
import time
import os
from typing import List
from config import BASE_DIR
import re
from material_maker_comfy.material_marker import MaterialMaker

class VideoMaker():
  entrypoint: str
  theme: str
  content: str
  keywords: str
  
  
  def __init__(self, entrypoint: str, ) -> None:
    self.entrypoint = entrypoint



  def create_video(self, theme: str, content: str, keywords: str, material_path: List[str] = []):
    body = {
      "video_subject": theme,
      "video_script": content,
      "video_terms": keywords,
      "video_aspect": "9:16",
      "video_concat_mode": "random",
      "video_clip_duration": 5,
      "video_count": 1,
      "video_source": "pexels",
      "video_materials": [
        {
          "provider": "pexels",
          "url": "",
          "duration": 0
        }
      ],

      "video_language": "",
      "voice_name": "zh-CN-XiaoxiaoNeural",
      "voice_volume": 1,
      "voice_rate": 1,
      "bgm_type": "random",
      "bgm_file": "",
      "bgm_volume": 0.2,
      "font_name": "STHeitiMedium.ttc",
      "text_fore_color": "#FFFFFF",
      "text_background_color": "transparent",
      "font_size": 60,
      "stroke_color": "#000000",
      "subtitle_enabled": True,
      "stroke_width": 1.5,
      "n_threads": 2,
      "paragraph_number": 5
    }
    
    # body = {
    #   "video_subject": theme,
    #   "video_script": content,
    #   "video_terms": keywords,
    #   "video_aspect": "9:16",
    #   "video_concat_mode": "random",
    #   "video_clip_duration": 5,
    #   "video_count": 1,
    #   "video_source": "local",
    #   "video_materials": map(lambda m: { "provider": "local", "url": m }, material_path),
    #   "video_language": "",
    #   "voice_name": "zh-CN-XiaoyiNeural",
    #   "voice_volume": 1,
    #   "voice_rate": 1,
    #   "bgm_type": "random",
    #   "bgm_file": "",
    #   "bgm_volume": 0.2,
    #   "font_name": "STHeitiMedium.ttc",
    #   "text_fore_color": "#FFFFFF",
    #   "text_background_color": "transparent",
    #   "font_size": 60,
    #   "stroke_color": "#000000",
    #   "subtitle_enabled": True,
    #   "stroke_width": 1.5,
    #   "n_threads": 2,
    #   "paragraph_number": 5
    # }
    
    try:
      response = requests.post(f"{self.entrypoint}/api/v1/videos", json=body, headers={"Content-Type": "application/json"})
      response.raise_for_status()
      print(response.json())
      task_id = response.json().get('data').get('task_id')
      return task_id
    except requests.exceptions.RequestException as e:
      print(e, 'e')


  def get_task_polling(self, task_id):
    while True:
      try:
        response = requests.get(f"{self.entrypoint}/api/v1/tasks/{task_id}")
        response.raise_for_status()
        data = response.json().get('data')
        print(data, 'data')
        print(data.get('progress'), 'progress')
        progress = data.get('progress')
        state = data.get('state')
        if state == -1:
          raise Exception('task failed')
        if progress == 100:
          video_url = data.get('videos')[0]
          return video_url;
        else:
          time.sleep(10)
      except requests.exceptions.RequestException as e:
        print(e)

  async def create_video_material(self, theme: str, content: str):
    material_maker = MaterialMaker(theme=theme, content=content)
    return await material_maker.run()


  def run(self, theme: str, content: str, keywords: str):
    task_id = self.create_video(theme, content, keywords)
    video_url = self.get_task_polling(task_id)
    pattern = r"/tasks/(.+)"
    match = re.search(pattern, video_url)
    if match:
      file_path = match.group(1)
      return self.download_video(file_path=file_path, file_name=task_id)


  def download_video(self, file_path: str, file_name: str):
    save_path = os.path.join(BASE_DIR, 'videos', f"{file_name}.mp4")
    try:
      response = requests.get(f"{self.entrypoint}/api/v1/download/{file_path}")
      response.raise_for_status()
      with open(save_path, 'wb') as f:
        f.write(response.content)
      print(f"视频已保存到 {file_path}")
      return save_path
    except requests.exceptions.RequestException as e:
      print(e)          

  async def run_v2(self, theme: str, content: str, keywords: str):
    material_path = self.create_video_material(theme, content)
    task_id = self.create_video(theme, content, keywords, material_path)
    print(task_id, 'task_id')
    video_url = self.get_task_polling(task_id)
    print(video_url)