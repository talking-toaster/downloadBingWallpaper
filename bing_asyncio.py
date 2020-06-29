# -*- encoding:utf8 -*-

import re
import asyncio

import aiohttp
import aiofiles


class Bing:
    def __init__(self):
        self.queue = asyncio.Queue(120)

    async def getImagData(self, num, rank=''):
        async with aiohttp.ClientSession() as session:
            for page in range(num):
                async with session.get(
                        f"https://bing.ioliu.cn/{rank}?p={page+1}"
                ) as response:
                    html = await response.text()
                    url = re.findall('src="http://h1.ioliu.cn/.*?">', html)
                    text = re.findall("<h3>.*?</h3>", html)
                    data = re.findall(r'<em class="t">\d*</em>', html)
                    #
                    # print(text[0])
                    [
                        await self.queue.put([
                            url[i][5:-1].replace('640x480.jpg',
                                                 '1920x1080.jpg'),
                            text[i][4:-5].replace("©", "").replace(
                                " ", "").replace("/", '_').replace("\\", "_"),
                            data[3 * i + 2][14:-5]
                        ]) for i in range(12)
                    ]
            await self.queue.put(["exit"])

    async def download(self, path="D:/Code/MyCode/PythonCode/bing/"):
        async with aiohttp.ClientSession() as session:
            while True:
                imgData = await self.queue.get()
                if imgData[0] == "exit":
                    break
                # print("data", imgData[1])
                async with session.get(imgData[0]) as response:
                    async with aiofiles.open(path + f"{imgData[1]}.jpg",
                                             "wb") as f:
                        await f.write(await response.read())
                self.queue.task_done()

    def run(self, rank, num, path="D:/Code/MyCode/PythonCode/bing/"):
        if rank == "date":
            tasks = [
                asyncio.ensure_future(self.getImagData(num)),
                asyncio.ensure_future(self.download(path))
            ]
        elif rank == "rank":
            tasks = [
                asyncio.ensure_future(self.getImagData(num, "ranking")),
                asyncio.ensure_future(self.download(path))
            ]
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(asyncio.wait(tasks))
        except KeyboardInterrupt:
            all_tasks = asyncio.Task.all_tasks()
            for task in all_tasks:
                print("cancel task")
                print(task.cancel())
            loop.stop()  # 只是将stopping的标记置位true
            loop.run_forever()  # 在stop后一定要运行这段代码，不然会抛异常
        finally:
            loop.close()


if __name__ == "__main__":

    bing = Bing()
    bing.run("date", 1, r"C:\Users\32536\Pictures\壁纸/")
