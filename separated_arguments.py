from crud import create_tea, delete_tea, create_wisdom


class SAC:
    """Separated Arguments Command"""
    CURRENT_COMMAND = {}
    COMMAND_FUNC = {
        'add_tea': create_tea,
        'add_wisdom': create_wisdom,
    }

    @staticmethod
    def prepare(command, message):
        user_id = message.from_user.id
        if user_id in SAC.CURRENT_COMMAND:
            SAC.CURRENT_COMMAND.pop(user_id)
        func = SAC.COMMAND_FUNC.get(command, None)
        if func:
            SAC.CURRENT_COMMAND[user_id] = func
            args = message.text.split(' ')[1:]
            if args:
                return SAC.launch(user_id, ' '.join(args))
        return None

    @staticmethod
    def launch(user_id, message_text):
        if user_id in SAC.CURRENT_COMMAND:
            func = SAC.CURRENT_COMMAND.pop(user_id)
            if func:
                return func(user_id, message_text)
            return 'Бип-боп-буп-чай'

