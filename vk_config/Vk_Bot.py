from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_config.tokens import token_bot

vk = vk_api.VkApi(token=token_bot)
longpoll = VkLongPoll(vk)


def write_msg(user_id, messages, attachments=''):
    vk.method('messages.send',
              {'user_id': user_id, 'message': messages, 'random_id': randrange(10 ** 7), 'attachment': attachments})


def dialog():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                user_message = (user_id, request)
                return user_message
