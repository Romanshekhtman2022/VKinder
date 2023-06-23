# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_user, check_user
from config import comunity_token, acces_token
from core import VkTools



class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.params={}
        self.offset=0
       


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
    def result_send (self,params, user_id, user):
        
        
        
        photos_user = self.api.get_photos(user['id'])                  
        
        attachment = ''
        for photo in photos_user:
            attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
        
        self.message_send(user_id,
                            f'Встречайте {user["name"]} ссылка: vk.com/id{user["id"]} ',
                            attachment=attachment
                            ) 
         #здесь логика для добавленяи в бд
        add_user(user_id, user['id'])  
        
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        
        for event in longpoll.listen():
            
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                
                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    if self.params['city'] is None:
                        self.message_send(event.user_id, 'В каком городе Вы живете?')
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['city']= event.text
                                break
                               
                    
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}')
                elif command == 'поиск':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Начинаем поиск')
                    self.users = self.api.search_users(self.params, self.offset)
                    keysend = False
                    while keysend == False:
                        if self.users:
                            user = self.users.pop()
                            #здесь логика для проверки бд
                            res = check_user(event.user_id, user['id'])
                            
                            if res == False:
                                self.result_send (self.params, event.user_id, user)
                                keysend = True
                        else:
                            self.offset += 10
                            self.users = self.api.search_users(self.params, self.offset)
                    self.message_send(event.user_id, f'Поиск закончен')    
                        
                    #users = self.api.search_users(self.params)
                    #user = users.pop()
                    #здесь логика для проверки бд
                    #photos_user = self.api.get_photos(user['id'])                  
                    #
                    #attachment = ''
                    #for photo in photos_user:
                        #attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                    
                    #self.message_send(event.user_id,
                                      #f'Встречайте {user["name"]} ссылка: vk.com/id{user["id"]} ',
                                      #attachment=attachment
                                      #) 
                   
                   
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()

            
