xh1scr unusual tiktok api wrapper
make task in asynchronous func
[
from xh1scr import TikTok
async def func():
	await TikTok.run('xh1c2')
	status = await TikTok.status()
	likes = await TikTok.likes()
	followers = await TikTok.followers()
	following = await TikTok.following()
	nickname = await TikTok.nickname()
	]
btw u can get list in run
[
from xh1scr import TikTok
async def func2():
	await TikTok.run(['xh1c2','example','example2','and','more'])
	status = await TikTok.status()
	likes = await TikTok.likes()
	followers = await TikTok.followers()
	following = await TikTok.following()
	nickname = await TikTok.nickname()
	]
###############RU###############
xh1scr это необычный ТикТок API Wrapper
Для работы с ним надо сделать task в асинхронной функции
(я знаю есть такое же API но с подключенной авторизацией и поиском по id но плюс моего API это удобство использования)
[
from xh1scr import TikTok
async def func():
	await TikTok.run('xh1c2') 
	status = await TikTok.status() 
	likes = await TikTok.likes()
	followers = await TikTok.followers()
	following = await TikTok.following()
	nickname = await TikTok.nickname()
	]
так же в run можно передать список значений
[
from xh1scr import TikTok
async def func2():
	await TikTok.run(['xh1c2','example','example2','and','more'])
	status = await TikTok.status()
	likes = await TikTok.likes()
	followers = await TikTok.followers()
	following = await TikTok.following()
	nickname = await TikTok.nickname()
	]

