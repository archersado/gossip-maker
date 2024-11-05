from src.uploader.dy import DouYinVideo, douyin_cookie_auth, douyin_setup
from src.uploader.cfg import BASE_DIR
from datetime import datetime
import asyncio
import os

def test_upload():
  account_file = os.path.join(BASE_DIR, "account.json")
  if douyin_cookie_auth(account_file,type) == False:
    asyncio.run(douyin_setup(account_file))

  video_title = '测试视频'
  video_path = '/Users/archersado/workspace/mygit/gossip-maker/videos/final-1 (12).mp4'
  app = DouYinVideo(
      title = video_title,
      file_path = video_path,
      tags=['测试话题'],
      # publish_date = datetime.now(),
      account_file=account_file,
      location='上海-上海')
  asyncio.run(app.main(), debug=False) 

