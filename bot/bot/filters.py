from telebot.custom_filters import AdvancedCustomFilter


class IsInAdminList(AdvancedCustomFilter):
    """
    Check users is admin.

    Example:

    @bot.message_handler(admins=(ADMIN_ID1, ADMIN_ID2, ...))
    @bot.message_handler(admins=[ADMIN_ID1, ADMIN_ID2, ...])
    """

    key = "admins"

    def check(self, message, text):
        # Перебираем каждый элемент списка и преобразуем его в число.
        admins = [int(x) for x in text]

        return message.from_user.id in admins
