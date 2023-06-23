from datetime import datetime 
from vk_api.exceptions import ApiError
import vk_api
from config import acces_token
from pprint import pprint



class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)
       
       
      
       

    def get_profile_info(self, user_id):
        
        try:
            info, = self.api.method('users.get',
                                {'user_id': user_id,
                                'fields': 'city,bdate,sex,relation,home_town' 
                                }
                                )
        except ApiError as e:
            info={}
            print (f'error={e}')

        user_info = {'name': info['first_name'] + ' '+ info['last_name'] if 
                        'first_name' in info and 'last_name' in info else None,
                        'id':  info.get('id'),
                        'bdate': info.get('bdate') if 'bdate' in info else None,
                        'home_town': info.get('home_town'),
                        'sex': info.get('sex'),
                        'city': info.get('city')['id'] if info.get ('city') is not None else None
                    }
        
        
        return user_info
        
        
    
    def search_users(self, params, offset):
        try:
            sex = 1 if params['sex'] == 2 else 2
            city = params['city']
            curent_year = datetime.now().year
            user_year = int(params['bdate'].split('.')[2])
            age = curent_year - user_year
            age_from = age - 5
            age_to = age + 5
            
            users = self.api.method('users.search',
                                    {'count': 10,
                                    'offset': offset,
                                    'age_from': age_from,
                                    'has_photo':1,
                                    'age_to': age_to,
                                    'age_from': age_to,
                                    'sex': sex,
                                    'city': city,
                                    'status': 6,
                                    'is_closed': False
                                    }
                                )
        except ApiError as e:
            users=[]
            print (f'error={e}')
        
        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        
        return res

    def get_photos(self, user_id):
        try:
            photos = self.api.method('photos.get',
                                    {'user_id': user_id,
                                    'album_id': 'profile',
                                    'extended': 1
                                    }
                                    )
            try:
                photos = photos['items']
            except KeyError:
                return []
            
            res = []
        except ApiError as e:
            photos={}
            print (f'error={e}')

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res [:3]


if __name__ == '__main__':
    
    bot = VkTools(acces_token)
    params = bot.get_profile_info(618152955)
    users = bot.search_users(params,10)
    whorksheet =users.pop()

    pprint(bot.get_photos(whorksheet['id']))
    pprint (users)
    pprint (whorksheet['id'])
