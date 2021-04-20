import scrapy
import requests
import time
from dhooks import Webhook, Embed
from random import randint

found_sentences = ['Genial! Encontré más descuentos :grin:', 'Hey! He encontrado nuevos descuentos :smile:',
                   'Cool! Pude encontrar más juegos baratos! :smiley:', 'Bros y Sis! Encontré más decuentos :scream:',
                   'No lo puedo creer :laughing:, más juegos a bajo precio!', 'Miren! Más descuentos en juegooooos!']
continue_sentences = ['Esos por ahora, iré a buscar más :sweat_smile:', 'Si encuentro otros, los enviaré aquí! :smile:'
                      'Son todos de momento, si encuentro más lo sabrán! :sweat_smile:', 'Si encuentro más, les aviso!',
                      ':frowning: ya son todos, si veo más les comento!', 'No hay más por el momento :(']
free_sentences = ['Aprovechen a este que es gratis :laughing:', 'Este no le afecta al bolsillo, es free! :sunglasses:',
                  'Ponganse pilas que este no les va a costar nada de nada xD', 'ESTE ES TOTALMENTE GRAAAATIIIS!!!',
                  'Este no cuesta gente! Aprovechen :3', 'FREE FREE FREE, este es gratis! :nerd:']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43'}
webhook = "https://discord.com/api/webhooks/812705948430106654/" \
          "cheeIy4LXfNctoKxtFfFia0n0TBW5fiqpnrLyBVWqq230TbEZFHrcSgoTgSrhjT1aqPT" # Discord webhook
hook = Webhook(webhook)  # Initialize the webhook
url = 'https://gg.deals/deals/best-deals/'
title_comparison = []
first_running_checker = 0
while True:
    delay = 5*randint(1, 5)
    print(delay)
    current_hour = time.localtime()[3]

    try:
        # Extract data from the web url
        text = requests.get(url, headers=headers)
        html = text.content
        sel = scrapy.Selector(text=html)
        game_titles = sel.css('a.title::text').extract()
        game_links = sel.css('a.title::attr(href)').extract()
        prices = sel.css('span.numeric::text').extract()
        shop_link_start = 'https://gg.deals'
        shop_links = sel.css('a.shop-link::attr(href)').extract()
        discount_percentages = sel.css('span.discount-badge::text').extract()
        thumb_urls = sel.css('a.main-image>img::attr(src)').extract()
        # Compare if exists new discounts
        checker = True
        new_titles = []
        new_titles_idxs = []
        for i in range(0, len(game_titles)):
            if game_titles[i] not in title_comparison:
                checker = False
                new_titles.append(game_titles[i])
                new_titles_idxs.append(i)
        if not checker:
            title_comparison = game_titles
            hook.send(found_sentences[randint(0, 5)])
            time.sleep(2)
        else:
            print("There aren't any new discounts now :(")
            time.sleep(delay)
            continue
        # Send data to the discord bot
        if first_running_checker == 0:
            amount_of_games = int(len(new_titles) / 2) - 2
            first_running_checker = 1
        else:
            amount_of_games = len(new_titles)
        for idx in range(0, amount_of_games):
            new_idx = new_titles_idxs[idx]
            game_link = shop_link_start + game_links[new_idx]
            full_shop_link = shop_link_start + shop_links[new_idx]
            if prices[new_idx] == 'Free':
                hook.send(free_sentences[randint(0, 5)])
                time.sleep(2)
            embed = Embed(title=new_titles[idx], description='[Ver web del juego](' + game_link + ')',
                          color=0x5CDBF0,
                          timestamp='now')
            embed.add_field(name="% de Descuento", value=discount_percentages[new_idx])
            embed.add_field(name="Precio", value=prices[new_idx])
            embed.add_field(name="Comprar Ahora", value='[Comprar](' + full_shop_link + ')')
            embed.set_footer(text='Que disfrutes tu nuevo descuento!')
            embed.set_thumbnail(url=thumb_urls[new_idx])
            hook.send(embed=embed)
            time.sleep(2)
        hook.send(continue_sentences[randint(0, 5)])
        time.sleep(delay)
    except: 
        ig_link = 'https://www.instagram.com/rrequeena/'
        hook.send(':nauseated_face: no me siento bien, por favor avísenle a mi creador [@rrequeena](' +
                  ig_link + ') ese es su instagram :nauseated_face:')
        time.sleep(delay)
        break # End the script if something went wrong
