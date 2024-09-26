import requests
import time

class VideoMaker():
  entrypoint: str
  theme: str
  content: str
  keywords: str
  
  
  def __init__(self, entrypoint: str, ) -> None:
    self.entrypoint = entrypoint



  def create_video(self, theme: str, content: str, keywords: str):
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
      "voice_name": "zh-CN-XiaoyiNeural",
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

  def run(self, theme: str, content: str, keywords: str):
    task_id = self.create_video(theme, content, keywords)
    print(task_id, 'task_id')
    video_url = self.get_task_polling(task_id)
    print(video_url)