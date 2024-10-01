from crud import create_tea, delete_tea, create_wisdom
from tea_metadata import edit_tea_info


class SAC:
    """Separated Arguments Command"""
    CURRENT_COMMAND = {}
    COMMAND_FUNC = {
        'add_tea': create_tea,
        'add_wisdom': create_wisdom,
        'edit_tea_info': edit_tea_info,
    }

    @staticmethod
    def prepare(command, message=None, user_id=None, extra_args=None):
        user_id = message.from_user.id if message is not None else user_id
        if not user_id:
            return
        if user_id in SAC.CURRENT_COMMAND:
            SAC.CURRENT_COMMAND.pop(user_id)
        func = SAC.COMMAND_FUNC.get(command, None)
        if func:
            SAC.CURRENT_COMMAND[user_id] = {}
            SAC.CURRENT_COMMAND[user_id]['func'] = func
            if extra_args:
                SAC.CURRENT_COMMAND[user_id]['args'] = extra_args
            if message is not None:
                args = message.text.split(' ')[1:]
                if args:
                    return SAC.launch(user_id, ' '.join(args))
        return None

    @staticmethod
    def launch(user_id, message_text):
        if user_id in SAC.CURRENT_COMMAND:
            comm = SAC.CURRENT_COMMAND.pop(user_id)
            func = comm.get('func', None)
            if func:
                args = comm.get('args', {})
                return func(user_id, message_text, **args)
            return 'Бип-боп-буп-чай'

