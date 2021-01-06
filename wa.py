import json
import requests
import datetime
import time

#loading the previous data
r=open('db.json','r')
db=json.load(r)
r.close()
#survey questions
try:
    f=open('que.json','w')
    survey_questions=json.load(f)
    f.close
except:
    survey_questions=['What is your name?','What is your Email','Your city?',
                        'Your Country...?',
                    'How often you use social media in a day?',
                    'For how much Time you use computer in a day?',
                    'Enter Your Favourite Food',
                    'Your Favourite Picnic Destination']

#set admins
admin=[]
try:
    f=open('admin.json','w')
    admin=json.load(f)
    f.close
except:
    admin=['phone no@c.us']#add admin phone number here preceded by country code
    r=open('admin.json','w')
    json.dump(admin,r,indent=4)
    r.close()

#Api url
#add your api instance and token id
# after obtaining from chat-api and scanning QR code from your Mobile
APIUrl = 'chat-api_instance_link' 
token = 'chat-api_token-12345'
#api message parameter

last=len(survey_questions)
limit=10

last_msg_no=db['lastMessageNumber']
sl=5

#whats app bot class
class WABot():    
    def __init__(self, json):
        self.json = json
        #print(json)
        db['lastMessageNumber']=json['lastMessageNumber']
        self.dict_messages = json['messages']
        self.APIUrl = 'https://eu144.chat-api.com/instance212603/'
        self.token = 'i90pm5iqqj6pn5qx'
  
    def send_requests(self, method, dat):
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(dat), headers=headers)
        print(answer.json())
        
    def send_message(self, chatID, text):
        try:

            data = {"chatID" : chatID,
                    "body" : text,
                    "phone":int(chatID[:chatID.find('@')])
                    } 
        except:
            data = {"chatID" : chatID,
                    "body" : text,
            }

        #print(data) 
        self.send_requests('sendMessage', data)        

    def welcome(self,chatID, noWelcome = False):
        welcome_string = ''
        if (noWelcome == False):
            welcome_string = "Hi I am WhatsApp Bot...\nCreated by coder_nobody.."
        else:
            welcome_string ="""                            
Incorrect command
Commands:
1.  chatid  - show ID of the current chat
2.  time  - show server time
3.  me  - show your nickname
4.  geo - get bot's location
5.  /survey   - start giving the survey
6.  /results  - view your answers
7.  /finish   - finish the test
8.  /questions - view the questions
9.  /admin  - view admin commands
"""
        self.send_message(chatID, welcome_string)

    def geo(self, chatID):
            data = {
                    "lat" : '00.8870601',
                    "lng" : '00.0957255',
                    "address" :'Aligarh',
                    "chatId" : chatID,
                    "phone":  int(chatID[:chatID.find('@')])
            }
            self.send_requests('sendLocation', data)
                 
    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%d:%m:%Y')
        self.send_message(chatID, time)

    def show_chat_id(self,chatID):
        self.send_message(chatID, f"Chat ID : {chatID}")

    def me(self, chatID, name):
        self.send_message(chatID, name) 
    
    def set_limit(self,num):
        global n_msg
        n_msg=int(num) 
        print("msg limit set to :",num) 
    
    def set_delay(self,num):
        global sl
        sl=int(num)
        print("Time limit set to :",num) 
    
    def add_question(self,que):
        global last
        last+=1
        survey_questions.append(que)
        f=open('que.json','w')
        json.dump(survey_questions,f,indent=6)
        f.close()
    
    def rem_question(self,no):
        global last
        if(no<1 or no >last):
            self.send_message(chatID, 'incorrect question no entered!!')
            return
        survey_questions.pop(no-1)
        last-=1
        f=open('que.json','w')
        json.dump(survey_questions,f,indent=6)
        f.close()

    def view_question(self,id):
        txt=''
        i=1
        for q in survey_questions:
            
            txt+= str(i)+'. '+q+'\n'
            i+=1

        self.send_message(id, txt)  

    def adminf(self,id):
        txt='''
Admin commands:
These can only be invoked by the admin of the bot and specify the parameter after space
1. setlimit##**  - to set no of chat results to load in 1 api call
2. setdelay##**  - to set time btw api calls 
3. remque##**  - to remove question from survey specify question no
4. addque##**  - to add a question
5. addadmin##** - to add admin
        '''
        self.send_message(id, txt)
        
    def addadm(self,id):
        admin.append(id)
        print("added the admin\nAdmins..:\n",admin)
        r=open('admin.json','w')
        json.dump(admin,r,indent=4)
        r.close()

    def finish(self,id):
        if len(db[id]['survey_answers']) >0:                               
            la=db[id]['last_question']
            for x in range(la-1,last):
                db[id]['survey_answers'].append((survey_questions[la],"Not Answered...")) 
            
            db[id]['last_question']= 0
            db[id]['previous_answers'].append(db[id]['survey_answers'])
            db[id]['survey_answers']=[]
            db[id]['survey']+=1
            self.send_message(id,'Thank You For Your participation.')
        else:
            self.send_message(id,'You have not started any test yet')
    
    def results(self,id):
        if db[id]['survey']==0:
            self.send_message(id,'You need to give or complete  survey to view results..')
        else:
            txt=''
            i=1
            for sr in db[id]['previous_answers']:
                txt='Survey:'+str(i)+'\n\n'
                i+=1
                for q,a in sr:
                    txt+='Que:  '+q+'\n'
                    txt+='Ans:  '+a+'\n\n'
                self.send_message(id,txt)

    def processing(self):
        if self.dict_messages != []:
            for message in self.dict_messages:
                if message["messageNumber"]>last_msg_no and (not message['fromMe']):                   
                    text = message['body'].split()
                    id  = message['chatId']
                    print(message['senderName'],"  :  ",message['body'])                  
                    if not (id in db):
                        db[id]={
                            'survey':0,
                            'survey_answers':[],
                            'previous_answers':[],
                            'last_question':0
                            
                        }
                    if text[0].lower() == 'hi'or text[0].lower() == 'hello':
                        self.welcome(id)
                    elif text[0].lower()=='/survey':
                        self.send_message(id,survey_questions[db[id]['last_question']])
                        db[id]['last_question']+=1                            
                    elif text[0].lower()=='/results':
                        self.results(id)
                    elif text[0].lower() == 'time':
                            self.time(id)
                    elif text[0].lower() == 'chatid':
                            self.show_chat_id(id)
                    elif text[0].lower() == 'geo':
                        self.geo(id)
                    elif text[0]=='setlimit##**':
                        try:
                            if(id in admin):
                                self.set_limit(text[1])
                            else:
                                self.send_message(id,'ERROR: You do not have the admin rights')
                            
                        except:
                            continue
                    elif text[0]=='setdelay##**':                        
                        if(id in admin):
                            self.set_delay(text[1])
                        else:
                            self.send_message(id,'ERROR: You do not have the admin rights')
                    elif text[0]=='remque##**':                        
                        if(id in admin):
                            self.rem_question(int(text[1]))
                        else:
                            self.send_message(id,'ERROR: You do not have the admin rights')
                    elif text[0]=='/questions': 
                        self.view_question(id) 
                    elif text[0]=='/admin': 
                        self.adminf(id) 
                    elif text[0]=='addadmin##**': 
                        if(id in admin):
                            self.addadm(text[1]+'@c.us')
                        else:
                            self.send_message(id,'ERROR: You do not have the admin rights')
                    elif text[0]=='addque##**':                        
                        if(id in admin):
                                self.add_question(message['body'][message['body'].rfind('*')+1:])
                        else:
                            self.send_message(id,'ERROR: You do not have the admin rights')
                    elif text[0].lower() == 'me':
                            self.me(id, message['senderName'])
                    elif text[0].lower() == '/finish':
                        self.finish(id)                        
                    else:
                        la=db[id]['last_question']
                        if la>0 and la<last:                               
                            db[id]['survey_answers'].append((survey_questions[la-1],message['body']))
                            self.send_message(id,survey_questions[la])
                            db[id]['last_question']+=1
                        elif la==last:
                            db[id]['survey_answers'].append((survey_questions[la-1],message['body']))
                            db[id]['survey']+=1
                            db[id]['last_question']=0
                            db[id]['previous_answers'].append(db[id]['survey_answers'])
                            db[id]['survey_answers']=[]
                            self.send_message(id,'Survey is completed..\nThank You For Your participation..')
                        else:
                            self.welcome(id, True)


#loop to run
def infloop():
    global last_msg_no
    last_msg_no=db['lastMessageNumber']
    url = f"{APIUrl}{'messages'}?token={token}&lastMessageNumber={str(last_msg_no)}&last=&chatId=&limit={str(limit)}&min_time=&max_time="
    r=requests.get(url)
    bot=WABot(r.json())
    bot.processing()
    time.sleep(sl)
    r=open('db.json','w')
    json.dump(db,r,indent=4)
    r.close()

# mainloop
while(1):
    try:   
        infloop()
    except:
        continue




