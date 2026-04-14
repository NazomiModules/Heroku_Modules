'''
█▄░█ ▄▀█ ▀█ █▀█ █▀▄▀█ █   █▀▄▀█ █▀█ █▀▄ █░█ █░░ █▀▀ █▀
█░▀█ █▀█ █▄ █▄█ █░▀░█ █   █░▀░█ █▄█ █▄▀ █▄█ █▄▄ ██▄ ▄█

Канал: https://t.me/Nazomi_Modules

--------------------------------------------------------------------
Автор: @Murex55
Название: NazomiBananas
Описание: Бананы… автодобыча бананов
--------------------------------------------------------------------
'''

# meta developer: @Nazomi_Modules
__version__ = (1, 0, 0)

import asyncio
import re
from telethon import events
from .. import loader, utils

@loader.tds
class NazomiBananas(loader.Module):
    '''Автодобыча бананов'''
    strings = {'name': 'NazomiBananas'}

    def __init__(self):
        self.start = asyncio.Event()
        self.stop = asyncio.Event()
        self.patterns = ((re.compile(r'(\d+)\s*ч'), 3600), (re.compile(r'(\d+)\s*мин'), 60), (re.compile(r'(\d+)\s*с'), 1))

    async def client_ready(self):
        await self.request_join('Nazomi_Modules', 'Здесь находятся все наши модули!')

        if self.get('bananastatus', False):
            self.start.set()

        asyncio.create_task(self.auto_banans())

    async def send_wait(self, text, pattern=None):
        fut = asyncio.get_running_loop().create_future()

        async def on_new(event):
            if not fut.done():
                fut.set_result(event.message)

        try:
            self.client.add_event_handler(on_new, events.NewMessage(chats=5522271758, incoming=True, from_users=5522271758, pattern=pattern))
            my_msg = await self.client.send_message(5522271758, text)
            return my_msg, await asyncio.wait_for(fut, 10)
        except asyncio.TimeoutError:
            return my_msg, None
        except Exception:
            return None, None
        finally:
            try:
                self.client.remove_event_handler(on_new)
            except Exception:
                pass

    def parse_time(self, text):
        total_time = 0
        for pattern, multiplier in self.patterns:
            match = pattern.search(text)
            if match:
                total_time += int(match.group(1)) * multiplier
        return total_time

    async def interruptible_sleep(self, delay):
        try:
            await asyncio.wait_for(self.stop.wait(), delay)
        except asyncio.TimeoutError:
            pass

    @loader.command()
    async def nb(self, message):
        '''Включить/выключить автодобычу бананов'''
        current = not self.get('bananastatus', False)
        self.set('bananastatus', current)

        if current:
            self.start.set()
            await utils.answer(message, '<b><emoji document_id=5357302605984835438>🍌</emoji> Добыча бананов включена</b>')
        else:
            self.start.clear()
            self.stop.set()
            await utils.answer(message, '<b><emoji document_id=5462990652943904884>😴</emoji> Добыча бананов выключена</b>')

    async def banans(self):
        my_msg, bot_msg = await self.send_wait('Сорвать бананы', pattern=r'⏳🍌 Попробуй через|Ты сорвал\(а\)')
        if not bot_msg:
            if my_msg:
                try:
                    await my_msg.delete()
                except Exception:
                    pass
            return await self.interruptible_sleep(300)

        if '⏳🍌 Попробуй через' in bot_msg.raw_text:
            try:
                await self.client.delete_messages(5522271758, [my_msg.id, bot_msg.id])
            except Exception:
                pass
            wait_time = self.parse_time(bot_msg.raw_text)
            return await self.interruptible_sleep(max(wait_time, 300) + 2)
        elif 'Ты сорвал(а)' in bot_msg.raw_text:
            await self.interruptible_sleep(2)
            my_msg, bot_msg = await self.send_wait('Банановая удача', pattern=r'🍀 Повезло! Теперь|😥 В этот раз не повезло')
            if not bot_msg:
                if my_msg:
                    try:
                        await my_msg.delete()
                    except Exception:
                        pass
                return await self.interruptible_sleep(300)

            if '🍀 Повезло! Теперь' in bot_msg.raw_text:
                wait_time = self.parse_time(bot_msg.raw_text)
                return await self.interruptible_sleep(max(wait_time, 300) + 2)
            elif '😥 В этот раз не повезло' in bot_msg.raw_text:
                my_msg, bot_msg = await self.send_wait('Сорвать бананы', pattern=r'⏳🍌 Попробуй через')
                if not bot_msg:
                    if my_msg:
                        try:
                            await my_msg.delete()
                        except Exception:
                            pass
                    return await self.interruptible_sleep(300)
                try:
                    await self.client.delete_messages(5522271758, [my_msg.id, bot_msg.id])
                except Exception:
                    pass
                wait_time = self.parse_time(bot_msg.raw_text)
                return await self.interruptible_sleep(max(wait_time, 300) + 2)
        else:
            try:
                await self.client.delete_messages(5522271758, [my_msg.id, bot_msg.id])
            except Exception:
                pass
            return await self.interruptible_sleep(300)

    async def auto_banans(self):
        while True:
            await self.start.wait()
            self.stop.clear()
            try:
                await self.banans()
            except Exception:
                await self.interruptible_sleep(300)
