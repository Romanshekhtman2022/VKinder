# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_user, check_user
from config import comunity_token, acces_token
from core import VkTools
from datetime import datetime



class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.params={}
        self.offset=0
        self.interface_a = vk_api.VkApi(token=acces_token)
        self.count_search = 0
        
       


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

    def check_params (self,params, user_id, longpoll):
        vkcity_count={}   
        city_key=False
        if self.params['city'] is None:
            self.message_send(user_id, 'В каком городе Вы живете?')
        #логика проверки введеного города, но она не очень правильная, нужен другой метод
            while city_key == False:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        
                        vkcity = self.interface_a.method('database.getCities',
                                        {'country_id': 1,
                                        'q': event.text
                                        }
                                    )
                        vkcity_count = vkcity['count']
                        if vkcity_count > 0:
                            city_key=True
                            vkcity_i=vkcity.get('items')
                         
                            self.params['city']= vkcity_i[0]['id']
                            break
                        else:
                            self.message_send(user_id, 'Город введен ошибочно, попробуйте еще раз')
                        
        if self.params['bdate'] is None:
            data_key = False
            self.message_send(user_id, 'У Вас не указана дата рождения, укажите пожалуйста в формате День.Месяц.Год.')
            while data_key == False:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        try:
                            date = event.text
                            
                            date = datetime.strptime(date, '%d.%m.%Y')
                            self.params['bdate']= event.text
                            data_key = True
                            
                            break
                        except ValueError:
                            self.message_send(user_id, 'Вы некорректно ввели дату, укажите пожалуйста в формате День.Месяц.Год.')
                            continue
                    break
        self.message_send(user_id, 'Введите команду "Поиск" для продолжения.')

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        
        for event in longpoll.listen():
            
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                
                if command == 'привет':
                    
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, 
                                      f'Здравствуй {self.params["name"]}\n'
                                      f"Вас приветствует бот VKinder!\n" 
                                      f"Я найду для Вас пару\n"                                                      
                                      f"Критерии: город пользователя, возраст в промежутке от -5 лет до +5 лет"
                                      f" от Вашего пользователя.\n"
                                      f"Чтобы начать поиск введите команду 'начать поиск'.\n"
                                      f"Для окончания работы с ботом введите команду 'пока'"
                                      )
                    self.check_params(self.params, event.user_id, longpoll)
                                        
                    
                    
                elif command == 'поиск':
                    if self.params:
                        self.message_send(event.user_id, f'Начинаем поиск')
                    else:
                        self.params = self.api.get_profile_info(event.user_id)
                        self.message_send(event.user_id, 
                                      f'Здравствуй {self.params["name"]}\n'
                                      f"Вас приветствует бот VKinder!\n" 
                                      f"Я найду для Вас пару\n"                                                      
                                      f"Критерии: город пользователя, возраст в промежутке от -5 лет до +5 лет"
                                      f" от Вашего пользователя.\n"
                                      f"Чтобы начать поиск введите команду 'начать поиск'.\n"
                                      f"Для окончания работы с ботом введите команду 'пока'"
                                      )
                        self.check_params(self.params, event.user_id, longpoll)

                    
                    if self.count_search == 0:
                        self.users = self.api.search_users(self.params, self.offset)
                        self.count_search = 1
                       
                        
                    keysend = False
                    while keysend == False:
                        
                        if self.users:
                            
                            user = self.users.pop()
                            
                            #здесь логика для проверки бд
                            res = check_user(event.user_id, user['id'])
                            
                            if res == False:
                                self.offset += 50
                                self.result_send (self.params, event.user_id, user)
                                keysend = True
                        else:
                            self.offset =+ 60 
                            self.users = self.api.search_users(self.params, self.offset)
                            
                    self.message_send(event.user_id, f'Поиск закончен')    
                        
                    
                   
                   
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()

            
