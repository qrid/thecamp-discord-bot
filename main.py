import asyncio
import os
from urllib.request import Request, urlopen
import discord
import json
import requests
import datetime
import webbrowser
import base64
import io
from pprint import pprint
from discord.ext import commands
from PIL import Image
from discord_buttons_plugin import *
from dotenv import load_dotenv

load_dotenv(verbose=True)

bot = commands.Bot(command_prefix="!")
buttons = ButtonsClient(bot)
token = os.environ.get('DISCORD_TOKEN')
url = os.environ.get('HOST')


@bot.event
async def on_ready():
    print('Logged in Bot: ', bot.user.name)
    print('Bot id: ', bot.user.id)
    print('Connection successful')
    print('-' * 30)

    game = discord.Game(name="인편 보낼 준비")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.command(aliases=['ㅎㅇ', '안녕'])
async def hello(ctx):
    await ctx.send("{}, 하이하이".format(ctx.author.mention))


@bot.command(aliases=['버전'])
async def version(ctx):
    await ctx.send("version : 0.1.4.5")


@bot.command(aliases=['전역', '언제옴', '디데이', 'dday', 'd-day', '달성률', '몇퍼'])
async def when(ctx):
    today = datetime.date.today()
    go = datetime.date(2022, 4, 11)
    comeback = datetime.date(2023, 10, 10)

    left = comeback - today
    percentage = 100 * (today - go) / (comeback - go) if 100 * (today - go) / (comeback - go) > 0 else 0
    progress = '🟦' * int(percentage / 5) + '⬜' * (20 - int(percentage / 5))

    embed = discord.Embed(title="전역 카운터")
    embed.add_field(name=f"{left.days}일 남았습니다.", value=f"달성률 {progress}", inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['사이트', '주소'])
async def link_button(ctx):
    await buttons.send(
        channel=ctx.channel.id,
        components=[
            ActionRow([
                Button(
                    label="규진 인편 쓰러가기",
                    style=ButtonType().Link,
                    url=url
                )
            ])
        ]
    )


@bot.command(aliases=['ㅇㅍ', '인편', 'dv'])
async def button(ctx, *, msg):
    try:
        text = msg.split('/')
        sender, subject, content = text[0], text[1], '/'.join(text[2:])
        image = ""
        try:
            image = ctx.message.attachments[0].url
        except:
            pass

        embed = discord.Embed(title="인편", description=f'{ctx.author.mention}님이 보내실 내용입니다')
        embed.add_field(name="보낸이", value=sender, inline=False)
        embed.add_field(name="제목", value=subject, inline=False)
        embed.add_field(name="내용", value=content, inline=False)
        embed.set_image(url=image)
        embed.set_footer(text=f"30초 후 자동으로 취소됩니다.")

        await buttons.send(
            embed=embed,
            channel=ctx.channel.id,
            components=[
                ActionRow([
                    Button(
                        label="전송",
                        style=ButtonType().Primary,
                        custom_id="send_button"
                    ),
                    Button(
                        label="취소",
                        style=ButtonType().Danger,
                        custom_id="cancel_button"
                    )
                ])
            ]
        )
        await asyncio.sleep(30)

    except:
        await ctx.send("예) !인편 {보낸이}/{제목}/{내용} \n 으로 부탁드립니다.")
        await asyncio.sleep(30)


@buttons.click
async def send_button(ctx):
    await ctx.reply("전송 완료")

    sender = ctx.message.embeds[0].fields[0].value
    subject = ctx.message.embeds[0].fields[1].value + "    (From discord)"
    content = ctx.message.embeds[0].fields[2].value
    image_url = ctx.message.embeds[0].image.url
    image = None

    if image_url != discord.Embed.Empty:
        image_ext = image_url[-3:]
        print(image_url, image_ext)

        req = requests.get(image_url)
        image_bytes = req.content
        image_bytes.decode().replace('data:application/octet-stream', 'data:image/' + image_ext).encode()

    data = {"sender": sender, "subject": subject, "content": content}
    test = requests.post('https://httpbin.org/post', data=data, files={'image': image})
    r = requests.post(url + "letter/", data=data, files={'image': image})
    print(r.status_code)
    print("----------test----------")
    print(test.json())

    await asyncio.sleep(3)


@buttons.click
async def cancel_button(ctx):
    await ctx.reply("취소되었습니다.")
    await asyncio.sleep(3)


bot.run(token)
