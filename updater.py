# Author: DelilahEve

import json
import zipfile
import traceback
import os

loaded = True
try:
	import aiohttp
except:
	print('module aiohttp is missing')
	loaded = False
try:
	import asyncio
except:
	print('module asyncio is missing')
	loaded = False
try:
	import aiofiles
except:
	print('module aiofiles is missing')
	loaded = False

owner = 'cadon'
repo = 'ARKStatsExtractor'

releasesURL = 'https://api.github.com/repos/{0}/{1}/releases'

tempZipName = 'ASB_Update_{0}.temp.zip'

class Updater:
	
	def __init__(self):
		self.url = releasesURL.format(owner, repo)
		
		self.is_started = False
		self._task = None
		
	async def start(self):
		if not self.is_started:
			self.is_started = True
			self._task = asyncio.ensure_future(self._run())
		
	async def run(self):
		print('Fetching releases data.')
		await self.fetch()
		
		print('Reading releases data.')
		self.parse()
		
		print('Downloading latest.')
		await self.downloadZip()
		
		print('Extracting...')
		await self.extractZip()
		
		print('Cleaning up.')
		self.cleanup()
		
		print('Update complete!')
		input('Press Enter to exit')
	
	async def fetch(self):
		contents = None
		async with aiohttp.ClientSession() as session:
			async with session.get(self.url) as response:
				contents = await response.text()
		
		cacheFile = open('temp.json', 'w')
		cacheFile.write(contents)
		cacheFile.close()
	
	def parse(self):
		with open('temp.json', encoding='utf-8', mode="r") as f:
			data = json.load(f)
			
			self.downloadURL = data[0]['assets'][0]['browser_download_url']
			self.zipName = tempZipName.format(data[0]['tag_name'])
	
	async def downloadZip(self):
		async with aiohttp.ClientSession() as session:
			async with session.get(self.downloadURL) as resp:
				if resp.status == 200:
					f = await aiofiles.open(self.zipName, mode='wb')
					await f.write(await resp.read())
					await f.close()
					
	async def extractZip(self):
		z = zipfile.ZipFile(self.zipName, 'r')
		z.extractall()
		z.close()

	def cleanup(self):
		items = ['temp.json', self.zipName]
		
		for f in items:
			if os.path.exists(f):
				os.remove(f)

if loaded:
	try:
		u = Updater()
		loop = asyncio.get_event_loop()
		loop.run_until_complete(u.run())
	except Exception:
		print('========================\nError\n========================')
		print(traceback.format_exc())
		input('Press Enter to exit')