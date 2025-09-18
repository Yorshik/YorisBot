from collections import defaultdict

from asgiref.sync import sync_to_async
from django.db.models import Q
import YorisDB.database.models as yoris_models


@sync_to_async
def get_cubes_stats(chat):
    members = yoris_models.ChatMember.objects.filter(chat=chat).select_related("user")
    user_ids = [m.user.id for m in members]
    users_dict = {m.user.id: m.user for m in members}
    wins = defaultdict(int)
    losses = defaultdict(int)
    draws = defaultdict(int)
    games = yoris_models.CubeActivity.objects.filter(
        chat=chat
    ).filter(
        Q(player1_id__in=user_ids) | Q(player2_id__in=user_ids)
    ).only("winner_id", "loser_id")

    for game in games:
        if game.is_draw:
            if game.player1_id:
                draws[game.player1_id] += 1
            if game.player2_id:
                draws[game.player2_id] += 1
        if game.winner_id:
            wins[game.winner_id] += 1
        if game.loser_id:
            losses[game.loser_id] += 1

    lines = [f"Статистика кубов в чате {chat.name}. Победы/ничьи/проигрыши/процент побед."]
    index = 1
    for user_id in user_ids:
        user = users_dict[user_id]
        w = wins[user_id]
        d = draws[user_id]
        l = losses[user_id]
        total = w + l
        winrate = round(w / total * 100) if total > 0 else 0
        lines.append(f"{index}. {user.name}. Победы - {w}, Ничьи - {d}, Проигрыши - {l}. Процент победы: {winrate}%")
        index += 1
    return "\n".join(lines)