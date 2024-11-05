import pytest
from src.video_maker_svd import VideoMaker
from src.material_maker_comfy.material_marker import MaterialMaker
# from src.video_maker_minimax import VideoMaker
content="""
烧烤配可口可乐。
"""

@pytest.mark.asyncio
async def test_video_maker():
  material_maker = MaterialMaker(theme="烧烤配可口可乐", content=content)
  await material_maker.run()
  # video_pvideo_makerath = video_maker.run('烧烤配可口可乐', ['BBQ', 'Coca-Cola', 'Summer'])

