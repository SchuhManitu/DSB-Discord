KLASSE = "9d"
WEEBHOOK_URL = "https://discord.com/api/webhooks/943903174224392203/TVyIqkEpBgY_fx48WMekqVNfVAJahiUYkwD9f15Guk4I_bBP280HLXalri8HNr5bIrXv"
#
#
#      
#REQUIRES: 
#
# requests
# dsbapi
#
##########################

import requests
import time
import sys
import time
import pickle
import dsbapi
import os


if not os.path.isfile("dsb_simplified.pickle"):
        with open('dsb_cache', 'wb') as file:
            pickle.dump([[]], file)
        with open('dsb_msg.pkl', 'wb') as file:
            pickle.dump([], file)

print('checking internet connection...')

while True:
    urls = ["https://www.dsbmobile.de/"]
    timeout = 5
    for url in urls:
        try:
            request = requests.head(url, timeout=timeout)
            print("dsb server erreicht")
            break
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("kein internet/server down")
            time.sleep(30)
            continue
    break



class DSB():
    def __init__(self, username, password, clss, weebhook_url):
        self.dsbclient = dsbapi.DSBApi(username, password)
        self.clss = clss
        self.weebhook_url = weebhook_url

    def fetch(self, testmode):

        msg = 'error'
        entries = self.dsbclient.fetch_entries()

        with open('dsb_cache', 'rb') as file:
            cache = pickle.Unpickler(file)
            cache = cache.load()
        with open('dsb_msg.pkl', 'rb') as file:
            old_messages = pickle.Unpickler(file)
            old_messages = old_messages.load()      
            
        origin_old_messages = old_messages

        for i2 in [lesson for day in entries for lesson in day if self.clss in lesson['type']]:  
          if i2 not in [lesson for day in cache for lesson in day if self.clss in lesson['type']]:
            type = i2['lesson']
            if type == 'Entfall':
                msg = 'Am ' + i2['day'] +  ' dem ' + i2['date'] + ' entfällt die ' + i2['class'] + '. Stunde (' + i2['subject'] + ')'
            elif type == 'Vertretung':
                msg = 'Am ' + i2['day'] +  ' dem ' + i2['date'] + ' wird die ' + i2['class'] + '. Stunde (' + i2['subject'] + ') vertreten '
            else:
                msg = 'Am ' + i2['day'] +  ' dem ' + i2['date'] + ' ist die ' + i2['class'] + '. Stunde (' + i2['subject'] + ') als \'' + type + '\' gekenzeichnet.'

            if i2['new_subject'] != '---':
                msg += '\nMehr Infos: ' + i2['new_subject']

            if '?' in i2['room']:
                room = i2['room'].split('?')
                room = '~' + room[0] + '~ ' + room[1]
                
                msg += '\nRaum: ' + room
            

            if msg in origin_old_messages:
                with open('dsb_cache', 'wb') as file:
                    pickle.dump(entries, file)
                print('Duplicate: ' + msg)
                
                continue

            old_messages.append(msg)

            if ' - ' in i2['class']:
                old_messages.append(msg.replace(i2['class'] + '. Stunde', i2['class'].split(' - ')[0] + '. Stunde'))
                old_messages.append(msg.replace(i2['class'] + '. Stunde', i2['class'].split(' - ')[1] + '. Stunde'))
            elif len(i2['class']) == 1:
                old_messages.append(msg.replace(i2['class'] + '. Stunde', i2['class'] + ' - ' + str(int(i2['class']) + 1) + '. Stunde'))

            self.send_dc(username='Vertretungsplan', title="", description=msg.replace('~', '~~'), color="466985", url=self.weebhook_url)

            print(msg)

        with open('dsb_cache', 'wb') as file:
            pickle.dump(entries, file)
        with open('dsb_msg.pkl', 'wb') as file:
            pickle.dump(old_messages, file)


    def send_dc(self, username, title, description, color, url): 
        data = {
            "username": username,
            "content" : ' ',
            "embeds" : [
                {
                    "title": title,
                    "description": description,
                    "color": color
                }
            ]
        }

        result = requests.post(url, json = data)
        print(result.text)


if __name__ == '__main__':

    dsb = DSB("259042", "wHB739ZkGK365", KLASSE, WEEBHOOK_URL)

    print('Starte fetcher')
    while True:
        try:
            dsb.fetch(testmode=False)
        except:
            def send(msg):
                import requests 
                url = "https://discord.com/api/webhooks/943903174224392203/TVyIqkEpBgY_fx48WMekqVNfVAJahiUYkwD9f15Guk4I_bBP280HLXalri8HNr5bIrXv"
                data = {
                    "content" : msg,
                    "username" : "FEHLER"
                }
                result = requests.post(url, json = data)

                try:
                    result.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(err)
                else:
                    pass

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('Fehler')
            print(sys.exc_info()) 
            send(f'Name: dsb mobile [dc] // Typ: {exc_type} / Info: {exc_obj} / File: {fname} / Line: {exc_tb.tb_lineno} / Version: unaviable')
        time.sleep(500)




