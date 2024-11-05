# -*- coding: utf-8 -*-
import asyncio
import traceback  
import os
import json
from config import CACHE_PATH
from datetime import datetime
from playwright.async_api import Playwright, async_playwright
from playwright.sync_api import sync_playwright


def deleteFile(account_file):
    if os.path.exists(account_file):
        try:
            os.remove(account_file)  
            print("文件已成功删除。")  
        except OSError as e:  
            print("删除文件时出错：", e)
            return False
        return True


def douyin_cookie_auth(account_file,type):
    if not os.path.exists(account_file):
        return False
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=account_file)
        # 创建一个新的页面
        page =context.new_page()
        # 访问指定的 URL
        page.goto("https://creator.douyin.com/creator-micro/content/upload")
        try:
            page.wait_for_selector("div:text('我是创作者')", timeout=5000)  # 等待5秒
            print("[+] 等待5秒 cookie 失效")
            #失效直接删除json文件
            deleteFile(account_file,type)
            context.close()
            browser.close()
            playwright.stop()
            return False
        except:
            print("[+] cookie 有效")
            context.close()
            browser.close()
            playwright.stop()
            return True

async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=account_file)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        try:
            await page.wait_for_selector("div.boards-more h3:text('抖音排行榜')", timeout=5000)  # 等待5秒
            print("[+] 等待5秒 cookie 失效")
            return False
        except:
            print("[+] cookie 有效")
            return True


async def douyin_setup(account_file_path):
    user_info = await douyin_cookie_gen(account_file_path)
    return user_info

def cache_data(key:str,value:str,timeout=60)->None:
  os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
  
  if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, 'r') as f:
      data = json.load(f)
  else:
      data = {}
  data[key] = value      
  # 写入数据到文件
  with open(CACHE_PATH, 'w') as f:
    json.dump(data, f)

def cache_get_data(key:str)-> any:
  if not os.path.exists(CACHE_PATH):  # 检查文件是否存在
      raise FileNotFoundError(f"Cache file not found: {CACHE_PATH}")
  with open(CACHE_PATH, 'r') as f:
    data = json.load(f)
  if key not in data:  # 检查键是否存在
    raise KeyError(f"Key not found in cache: {key}")
        
  return data[key]

def cache_delete(key:str)->None:
  if not os.path.exists(CACHE_PATH):  # 检查文件是否存在
      raise FileNotFoundError(f"Cache file not found: {CACHE_PATH}")
  with open(CACHE_PATH, 'r') as f:
    data = json.load(f)
  if key not in data:  # 检查键是否存在
    raise KeyError(f"Key not found in cache: {key}")
        
  del data[key] 
  with open(CACHE_PATH, 'w') as f:
    json.dump(data, f)

async def douyin_cookie_gen(account_file_path):
    try:
        async with async_playwright() as playwright:
            options = {
                'headless': False
            }
            # Make sure to run headed.
            browser = await playwright.chromium.launch(**options)
            # Setup context however you like.
            context = await browser.new_context()  # Pass any options
            # Pause the page, and start recording manually.
            page = await context.new_page()
            await page.goto(url="https://creator.douyin.com/",timeout=20000)
            # await page.wait_for_url(url="https://creator.douyin.com/",timeout=10000)
            # await page.locator('span.login').click() 不需要点击了
            # base64搞定
            img_element = page.locator('div.account-qrcode-QvXsyd div.qrcode-image-QrGzx7 img:first-child')
            await img_element.wait_for()
            # 截图然后返回给前端
            # await asyncio.sleep(3)  # 过3秒时间再截图
            # await page.screenshot(path=f"{account_id}_douyin_screenshot.png")
            # 检测当前url链接是否是https://creator.douyin.com/creator-micro/home
            num = 1
            while True:
                await asyncio.sleep(3)
                # 判断是否有已扫码显示，如果有跳出循环
                print(page.url)
                if 'creator.douyin.com/creator-micro/home' in page.url:
                    break
                # 判断是否要身份认证
                auth_div = page.get_by_text("身份验证")
                auth_visible = await auth_div.is_visible()
                if auth_visible:
                    # 说明需要验证码
                    # 点击接收短信验证码
                    await page.get_by_text("接收短信验证").click()
                    # 等一秒后
                    await asyncio.sleep(1)
                    # 点击验证码
                    await page.get_by_text("获取验证码").click()
                    num_two = 1
                    while True:
                        await asyncio.sleep(3)
                        # 判断是否获取到了缓存中的验证码
                        auth_number = cache_get_data(f"douyin_login_authcode")
                        if auth_number:
                            await page.get_by_placeholder('请输入验证码').nth(1).fill(auth_number)
                            # 然后点击验证按钮
                            await page.get_by_text("验证", exact=True).click()
                            await asyncio.sleep(2)
                            # 验证后删除需要验证码缓存
                            cache_delete(f"douyin_login_need_auth")
                            break
                        if num_two > 20:
                            # 输入验证码
                            break
                        # 多循环一次
                        num_two+=1
                if num > 13:
                    break
                num+=1
            # 判断cookie长度过短说明没登录，无需保存
            cookies = await context.cookies()
            # 默认没获取到用户信息
            user_info = False
            # 保存cookie长度不大于30不保存
            if len(cookies) > 30:
                # 直接获取用户数据然后返回
                third_id_cont = await page.get_by_text("抖音号：").inner_text()
                third_id = third_id_cont.split("：")[1]
                user_info = {
                    'account_id':third_id,#抖音号
                    'username':await page.locator("div.rNsML").inner_text(),#用户名
                    'avatar':await page.locator("div.t4cTN img").nth(0).get_attribute("src")#头像
                }
                # 保存cookie
                await context.storage_state(path=account_file_path)
                # 保存当前用户的登录状态，临时用来检测登陆状态用，只保存60s的状态检测
                cache_data(f"douyin_login_status",1,60)
                # 保存抖音账号的登录状态，时间一个周
                cache_data(f"douyin_login_status_third_{third_id}",1,604800)
            # 关闭浏览器
            await context.close()
            await browser.close()
            await playwright.stop()
            return user_info
    except:
        traceback.print_exc()
        return False

async def douyin_cookie_gen_home(account_file_path,account_id="",queue_id=""):
    try:
        async with async_playwright() as playwright:
            options = {
                'headless': False
            }
            # Make sure to run headed.
            browser = await playwright.chromium.launch(**options)
            # Setup context however you like.
            context = await browser.new_context()  # Pass any options
            # Pause the page, and start recording manually.
            page = await context.new_page()
            await page.goto(url="https://www.douyin.com/")
            await page.wait_for_url("https://www.douyin.com/",timeout=10000)
            # base64搞定
            login_btn = page.get_by_role("button", name="登录")
            await login_btn.click()
            img_element = page.locator('img.web-login-scan-code__content__qrcode-wrapper__qrcode')
            img_element_src = await img_element.get_attribute(name="src",timeout=10000)
            cache_data(f"douyin_login_ewm_{queue_id}",img_element_src)
            # 截图然后返回给前端
            # await asyncio.sleep(3)  # 过3秒时间再截图
            # await page.screenshot(path=f"{account_id}_douyin_screenshot.png")
            # await asyncio.sleep(40)  # 给用户40秒时间进行扫码登录
            # 等待过程换成循环，然后同时检测状态
            success_div = page.get_by_text("扫码成功")
            is_visible = await success_div.is_visible(timeout=50000)
            num = 1
            while True:
                await asyncio.sleep(3)
                # 判断是否有已扫码显示，如果有跳出循环
                is_visible = await success_div.is_visible()
                if is_visible:
                    # 保存记录一下说明已经扫码
                    cache_data(f"douyin_login_scan_{queue_id}",1,6)
                    break
                if num > 13:
                    break
                num+=1
            # 等待用户点击，再过6秒刷新页面然后保存cookie
            await asyncio.sleep(6)
            # 判断cookie长度过短说明没登录，无需保存
            cookies = await context.cookies()
            # 默认没获取到用户信息
            user_info = False
            # 保存cookie长度不大于36不保存
            if len(cookies) > 36:
                # 打开用户中心，选择用户数据然后返回
                page = await context.new_page()
                await page.goto("https://www.douyin.com/user/self")
                await page.wait_for_url("https://www.douyin.com/user/self")
                third_id_cont = await page.get_by_text("抖音号：").inner_text()
                third_id = third_id_cont.split("：")[1]
                user_info = {
                    'account_id':third_id,#抖音号
                    'username':await page.locator("h1").inner_text(),#用户名
                    'avatar':await page.locator("div.avatar-component-avatar-container img").nth(2).get_attribute("src")#头像
                }
                account_file = f"{account_file_path}/{account_id}_{third_id}_account.json"
                # 保存cookie
                await context.storage_state(path=account_file)
                # 保存当前用户的登录状态，临时用来检测登陆状态用，只保存60s的状态检测
                cache_data(f"douyin_login_status_{account_id}",1,60)
                # 保存抖音账号的登录状态，时间一个周
                cache_data(f"douyin_login_status_third_{account_id}_{third_id}",1,604800)
            # 关闭浏览器
            await context.close()
            await browser.close()
            await playwright.stop()
            return user_info
    except:
        return False

class DouYinVideo(object):
    def __init__(self, title, file_path, tags, account_file, publish_date = None,location="重庆市", preview_path = ""):
        self.title = title  # 视频标题
        self.file_path = file_path # 视频文件路径
        self.preview_path = preview_path # 视频预览图路径
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.date_format = '%Y年%m月%d日 %H:%M'
        self.local_executable_path = ""  # change me
        self.location = location

    async def set_schedule_time_douyin(self, page, publish_date):
        # 选择包含特定文本内容的 label 元素
        label_element = page.locator("label.radio--4Gpx6:has-text('定时发布')")
        # 在选中的 label 元素下点击 checkbox
        await label_element.click()
        await asyncio.sleep(1)
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M")
        
        await asyncio.sleep(1)
        await page.locator('.semi-input[placeholder="日期和时间"]').click()
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")

        await asyncio.sleep(1)

    async def handle_upload_error(self, page):
        print("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium 浏览器启动一个浏览器实例
        if self.local_executable_path:
            browser = await playwright.chromium.launch(headless=False, executable_path=self.local_executable_path)
        else:
            browser = await playwright.chromium.launch(headless=False)
        # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(storage_state=f"{self.account_file}")

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        print('[+]正在上传-------{}.mp4'.format(self.title))
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        print('[-] 正在打开主页...')
        await page.wait_for_url("https://creator.douyin.com/creator-micro/content/upload")
        # 点击 "上传视频" 按钮

        await page.wait_for_selector('.container-drag-icon', timeout=20000)  # 增加超时时间
        video_input = page.locator('input[type="file"]')
        await page.evaluate('document.querySelector("input[type=\'file\']").click()')
        # await video_input.click()
        # # await video_input.set_input_files(self.file_path)
        # await page.evaluate('''(filePath) => {
        #     const input = document.querySelector('input[type="file"][accept="video/*"]');
        #     const dataTransfer = new DataTransfer();
        #     const file = new File([new Blob()], filePath); // 创建一个虚拟文件
        #     dataTransfer.items.add(file);
        #     input.files = dataTransfer.files;
        # }''', self.file_path)
        await video_input.set_input_files(self.file_path)
        # async with page.expect_file_chooser() as fc_info:
        #     await page.locator('.container-drag-icon').click()  # 再次点击以确保文件选择器打开
        # file_chooser = await fc_info.value

        # await file_chooser.set_files(self.file_path)
            # try: 
        #   async def handle_file_chooser(file_chooser):吗ke
        #     await file_chooser.set_files(self.file_path, timeout=50000)

        #   page.on("filechooser", handle_file_chooser)
        #   # 点击选择文件按钮，会触发 filechooser 事件
        #   await file_selector.click() 
        # except Exception as e:
        #   print("发布视频失败，可能网页加载失败了\n", e)
        # await page.locator(".upload-btn--9eZLd").set_input_files(self.file_path)

        # 等待页面跳转到指定的 URL
        while True:
            # 判断是是否进入视频发布页面，没进入，则自动等待到超时
            try:
                await page.wait_for_url(
                    "https://creator.douyin.com/creator-micro/content/publish?enter_from=publish_page")
                break
            except:
                print("  [-] 正在等待进入视频发布页面...")
                await asyncio.sleep(0.1)

        # 填充标题和话题
        # 检查是否存在包含输入框的元素
        # 这里为了避免页面变化，故使用相对位置定位：作品标题父级右侧第一个元素的input子元素
        await asyncio.sleep(1)
        print("  [-] 正在填充标题和话题...")
        title_container = page.locator('input[placeholder="填写作品标题，为作品获得更多流量"]')
        if await title_container.count():
            await title_container.fill(self.title[:30])
        else:
            titlecontainer = page.locator(".notranslate")
            await titlecontainer.click()
            print("clear existing title")
            await page.keyboard.press("Backspace")
            await page.keyboard.press("Control+KeyA")
            await page.keyboard.press("Delete")
            print("filling new  title")
            await page.keyboard.type(self.title)
            await page.keyboard.press("Enter")
        css_selector = ".zone-container"
        for index, tag in enumerate(self.tags, start=1):
            print("正在添加第%s个话题" % index)
            await page.type(css_selector, "#" + tag)
            await page.press(css_selector, "Space")

        while True:
            # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
            try:
                #  新版：定位重新上传
                number = await page.locator('div div:has-text("重新上传")').count()
                if number > 0:
                    print("  [-]视频上传完毕")
                    break
                else:
                    print("  [-] 正在上传视频中...")
                    await asyncio.sleep(2)

                    if await page.locator('div.progress-div > div:has-text("上传失败")').count():
                        print("  [-] 发现上传出错了...")
                        await self.handle_upload_error(page)
            except:
                print("  [-] 正在上传视频中...")
                await asyncio.sleep(2)
        # 视频呢上传完毕后处理视频预览图
        await asyncio.sleep(5)
        # await page.get_by_text("上传封面").click()
        # preview_upload_div_loc = page.locator("div.semi-upload-drag-area")
        # # await upload_div_loc.wait_for()
        # async with page.expect_file_chooser() as fc_info:
        #     await preview_upload_div_loc.click()
        # preview_file_chooser = await fc_info.value
        # if self.preview_path:
        #   await preview_file_chooser.set_files(self.preview_path)
        # await page.get_by_role("button", name="完成").click()
        # 处理完预览图后
        # 更换可见元素
        # await page.locator('div.semi-select span:has-text("输入地理位置")').click()
        # await asyncio.sleep(1)
        # print("clear existing location")
        # await page.keyboard.press("Backspace")
        # await page.keyboard.press("Control+KeyA")
        # await page.keyboard.press("Delete")
        # await page.keyboard.type(self.location)
        # await page.locator('div[role="listbox"] [role="option"]').first.click()

        # 頭條/西瓜
        # third_part_element = '[class^="info"] > [class^="first-part"] div div.semi-switch'
        # 定位是否有第三方平台
        # if await page.locator(third_part_element).count():
        #     # 检测是否是已选中状态
        #     if 'semi-switch-checked' not in await page.eval_on_selector(third_part_element, 'div => div.className'):
        #         await page.locator(third_part_element).locator('input.semi-switch-native-control').click()

        # 定时发布
        if self.publish_date is not None:
            await self.set_schedule_time_douyin(page, self.publish_date)

        # 判断视频是否发布成功
        while True:
            # 判断视频是否发布成功
            try:
                publish_button = page.get_by_role('button', name="发布", exact=True)
                if await publish_button.count():
                    await publish_button.click()
                await page.wait_for_url("https://creator.douyin.com/creator-micro/content/manage",
                                        timeout=5000)  # 如果自动跳转到作品页面，则代表发布成功
                print("  [-]视频发布成功")
                break
            except:
                # 如果页面是管理页面代表发布成功
                current_url = page.url
                if "https://creator.douyin.com/creator-micro/content/manage" in current_url:
                    print("  [-]视频发布成功")
                    break
                else:        
                    print("  [-] 视频正在发布中...")
                    # await page.screenshot(full_page=True) 取消截屏
                    await asyncio.sleep(0.5)
        await context.storage_state(path=self.account_file)  # 保存cookie
        print('  [-]cookie更新完毕！')
        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()
        await playwright.stop()

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)