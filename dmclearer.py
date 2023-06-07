import httpx
import time
import os
from dotenv import load_dotenv
load_dotenv()
token=os.getenv('token')
user_agent=os.getenv('user_agent')
x_super_properties=os.getenv('x_super_properties')

class accounts:
    def __init__(self,token):
        self.session = httpx.Client(cookies={"locale": "en-US"},
        headers={"Pragma": "no-cache",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "DNT": "1",
        "Host": "discord.com",
        "Referer": f"https://discord.com",
        "Sec-Fetch-Dest": "empty", 
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "User-Agent": user_agent,
        "X-Discord-Locale": "en-GB",
        "X-Super-Properties": x_super_properties},timeout=30)
        self.session.headers["X-Fingerprint"] = self.session.get(
        "https://discord.com/api/v9/experiments", timeout=30).json().get("fingerprint")
        self.session.headers["Origin"]="https://discord.com"
        self.session.headers["Authorization"] = token

    def getMessage(self, messageId, channelId):
        req = self.session.get(
            f"https://discord.com/api/v9/channels/{channelId}/messages?limit=1&around={messageId}")
        return req.json() 

    def delmessage(self,messageId,channel):
        link=f"https://discord.com/api/v9/channels/{channel}/messages/{messageId}"
        req=self.session.delete(link)
        time.sleep(1.2)
        print(f"MSG ID : {messageId} , {req.status_code}, {req.text}")
    
    def channel_info(self,channel_id):
        req = self.session.get(f"https://discord.com/api/v9/channels/{channel_id}")
        return req.json()

    def self_info(self):
        req=self.session.get("https://discord.com/api/v9/users/@me")
        return req.json()


    def scrape_message(self,channelid):
        message_list=[]
        author_data=[]
        try:
            req=self.session.get(f"https://discord.com/api/v9/channels/{channelid}/messages?limit=100")


            last_message_id=req.json()[-1]['id']

            for message in req.json():
                #ignore empty messages
                # if message['content']=='':
                #     continue
                # else:
                message_list.append(message)

                author_data.append(message['author'])


            while True:
                print("start "+last_message_id)
                req=self.session.get(f"https://discord.com/api/v9/channels/{channelid}/messages?before={last_message_id}&limit=100")
                if len(req.json())==0:
                    break
                last_message_id=req.json()[-1]['id']
                for message in req.json():
                    # if message['content']=='':
                    #     continue
                    # else:
                    message_list.append(message)
                    author_data.append(message['author'])
                print("looping "+str(last_message_id))

            print(last_message_id)

            #reverse the list
            message_list.reverse()
            return message_list,author_data
        except:
            return None,None 


if __name__=="__main__":


    choice=input("\n1.Get Messages\n2.Delete Messages\n3.Exit\n")
    channel=input("Channel id :")
    while choice!="3":

        if choice=="1":
            session=accounts(token)
            user_info=session.self_info()
            response=session.channel_info(channel)
            if "message" in response and response["message"]=="Missing Access":
                print("Server not joined by token\nJoin server first")
            elif "message" in response and response["message"]=="Invalid Form Body":
                print("Response Invalid Form Body\nCheck channel id")
            elif "message" in response and response["message"]=="Unknown Channel":
                print("Unknown Channel\nCheck channel id")
            elif "message" in response and response["message"]=="404: Not Found":
                print("404: Not Found\nCheck channel id. No such channel exists")
            elif "id" in response:
                message_list,data=session.scrape_message(channel)

                with open(f"messages.txt", "w") as fp:
                    for message in message_list:
                        if message['author']['username']==user_info["username"]:
                            fp.write(f"{message['id']}\n")
            else:
                print("Unknown Error or not handled")
                print(response)

        elif choice=="2":
            session=accounts(token)

            with open("messages.txt") as f:
                messages = f.read().splitlines()
            print("Deleting messages")
            for message in messages:
                session.delmessage(message,channel)

        choice=input("\n1.Get Messages\n2.Delete Messages\n3.Exit\n")