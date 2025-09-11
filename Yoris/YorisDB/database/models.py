from decimal import Decimal

from django.db import models


class Chat(models.Model):
    TYPE_CHOICES = (
        ("supergroup", "supergroup"),
        ("channel", "channel"),
        ("group", "group"),
    )
    LANG_CHOICES = (
        ("en", "English"),
        ("ru", "Russian"),
    )
    id = models.BigAutoField(primary_key=True)
    chat_name = models.CharField(max_length=100, db_column="name")
    username = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    welcome_message = models.TextField(null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default="group")
    lang = models.CharField(max_length=100, choices=LANG_CHOICES, default="ru")
    is_short_info_enabled = models.BooleanField(default=False)
    mute_period = models.IntegerField(default=60)
    warn_period = models.IntegerField(default=60 * 24 * 7)
    warn_limit = models.IntegerField(default=3)

    @property
    def name(self):
        if self.chat_name:
            return self.chat_name
        if self.username:
            return self.username
        return self.pk


class User(models.Model):
    MODE_CHOICES = (
        ("yoris", "yoris coins"),
        ("chips", "chips for casino")
    )
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    linked_chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    yoris_coin_balance = models.IntegerField(default=0)
    chips_balance = models.IntegerField(default=0)
    mode = models.CharField(max_length=5, choices=MODE_CHOICES, default="yoris")

    @property
    def name(self):
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return f"{self.first_name}"
        if self.username:
            return f"{self.username}"
        return self.pk

    @property
    def link(self):
        if self.username:
            return "https://t.me/" + self.username
        return "tg://openmessage?user_id=" + str(self.id)

class ChatMember(models.Model):
    STATUS_CHOICES = (
        ("active", "состоит в чате"),
        ("restricted", "состоит в чате с ограничениями"),
        ("kicked", "удален с чата"),
        ("banned", "заблокирован"),
        ("left", "покинул чат"),
    )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    nick = models.CharField(max_length=30, null=True, blank=True)
    motto = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_tg_admin = models.BooleanField(default=False)
    tg_admin_title = models.CharField(max_length=30, null=True, blank=True)
    is_citizen = models.BooleanField(default=False)
    spouse = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    role_level = models.IntegerField(default=0)
    clan = models.ForeignKey("Clan", on_delete=models.SET_NULL, null=True, blank=True)
    main_club = models.ForeignKey("Club", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="chats")
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, related_name="members")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "chat")

    @property
    def name(self):
        return f'Участник {self.user.name} чата {self.chat.name}'


class Credits(models.Model):
    LENDER_TYPES_CHOICES = (
        ("system", "система"),
        ("user", "пользователь"),
    )
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="credits")
    return_date = models.DateField()
    lender_type = models.CharField(max_length=10, choices=LENDER_TYPES_CHOICES, default="system")
    lender_user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="given_credits")
    principal = models.DecimalField(max_digits=18, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    repaid = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    issued_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()


class Relation(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="relations")
    partner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    is_main = models.BooleanField(default=False)
    hp = models.IntegerField(default=100)
    level = models.ForeignKey("RelationLevel", on_delete=models.SET_NULL, null=True, blank=True)


class RelationLevel(models.Model):
    name = models.CharField(max_length=100)
    required_hp = models.IntegerField(default=100)
    level = models.IntegerField(default=1)


class Action(models.Model):
    name = models.CharField(max_length=100)
    required_level = models.ForeignKey("RelationLevel", on_delete=models.CASCADE, related_name="actions")
    cooldown = models.DurationField(null=True, blank=True)
    price = models.PositiveIntegerField(default=0)


class Note(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    number = models.PositiveIntegerField()
    text = models.TextField()

    class Meta:
        unique_together = ("name", "user", "number", "chat")


class BookMark(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    number = models.PositiveIntegerField()
    message_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ("name", "user", "number", "chat")


class Reward(models.Model):
    EMOJI_CHOICES = [
        ("🎗", "rank 1"),
        ("🥉", "rank 2"),
        ("🥈", "rank 3"),
        ("🥇", "rank 4"),
        ("🎖", "rank 5"),
        ("🏅", "rank 6"),
        ("🏆", "rank 7"),
        ("🏵", "rank 8"),
    ]
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="rewards")
    by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="given_rewards")
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    rank = models.CharField(max_length=2, choices=EMOJI_CHOICES, default="🎗")


class Clan(models.Model):
    TYPE_CHOICES = (
        ("opened", "opened"),
        ("closed", "closed"),
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    leader = models.OneToOneField("ChatMember", on_delete=models.SET_NULL, null=True, blank=True, related_name="lead_clan")
    number = models.PositiveIntegerField()
    type = models.CharField(max_length=6, choices=TYPE_CHOICES, default="opened")
    members = models.PositiveIntegerField(default=1)


class Club(models.Model):
    TYPE_CHOICES = (
        ("opened", "opened"),
        ("closed", "closed"),
    )
    leader = models.ForeignKey("ChatMember", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=6, choices=TYPE_CHOICES, default="opened")


class SystemMessages(models.Model):
    LANG_CHOICES = (
        ("en", "English"),
        ("ru", "Russian"),
    )
    key = models.CharField(max_length=255)
    chat_id = models.BigIntegerField(null=True, blank=True)
    lang = models.CharField(max_length=2, choices=LANG_CHOICES, default="ru")
    text = models.TextField()


class Emojis(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    chat_id = models.BigIntegerField(null=True, blank=True)
    symbol = models.CharField(max_length=10)


class RPCommands(models.Model):
    name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    emoji = models.CharField(max_length=2)
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)


class Prefix(models.Model):
    prefix = models.CharField(max_length=50)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)


class Activity(models.Model):
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    member = models.ForeignKey("ChatMember", on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Mute(models.Model):
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    until_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    reason = models.TextField(null=True, blank=True)
    was_admin = models.BooleanField(default=False)
    tg_admin_title = models.CharField(max_length=255, blank=True, null=True)


class Warn(models.Model):
    warn_id = models.IntegerField()
    chat = models.ForeignKey("Chat", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    until_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    reason = models.TextField(blank=True, null=True)
