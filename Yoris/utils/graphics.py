import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta

from asgiref.sync import sync_to_async
from django.db.models import Count
from django.db.models.functions import TruncDate
import YorisDB.database.models as yoris_models


def _build_stats_chart(data, title="Статистика") -> BytesIO:
    dates = [d.strftime("%d.%m") for d, _, _ in data]
    counts_midnight = [c for _, c, _ in data]
    counts_24h = [c for _, _, c in data]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(dates, counts_midnight, color="green", label="За календарные сутки")

    if data:
        last_idx = len(counts_midnight) - 1
        extra = counts_24h[last_idx] - counts_midnight[last_idx]

        if extra > 0:
            ax.bar(
                dates[last_idx],
                extra,
                bottom=counts_midnight[last_idx],
                color="orange",
                label="Последние 24 часа (дополнительно)"
            )
        elif extra < 0:
            ax.bar(
                dates[last_idx],
                counts_24h[last_idx],
                color="orange",
                label="Только последние 24 часа"
            )

    ax.set_title(title)
    ax.set_xlabel("Дни")
    ax.set_ylabel("Сообщений")
    ax.legend()

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf


@sync_to_async
def build_activity_stats(qs, title: str, days: int | None = 7) -> BytesIO:
    now = datetime.now()
    current_date = now.date()
    aggregated = (
        qs
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    day_counts = {x["day"]: x["count"] for x in aggregated}
    if days is None:
        if not day_counts:
            return _build_stats_chart([], title=title)
        start_date = min(day_counts.keys())
        end_date = max(day_counts.keys())
        total_days = (end_date - start_date).days + 1
    else:
        start_date = (now - timedelta(days=days - 1)).date()
        total_days = days
    last24_count = qs.filter(timestamp__gte=now - timedelta(hours=24)).count()
    data = []
    for i in range(total_days):
        day = start_date + timedelta(days=i)
        count_midnight = day_counts.get(day, 0)
        if day == current_date:
            data.append((day, count_midnight, last24_count))
        else:
            data.append((day, count_midnight, count_midnight))
    return _build_stats_chart(data, title=title)


async def get_chat_stats(chat, days: int | None = 7) -> BytesIO:
    qs = yoris_models.Activity.objects.filter(chat=chat)
    return await build_activity_stats(qs, title=f"Статистика чата {chat.name}", days=days)


async def get_user_stats(user, days: int | None = 7) -> BytesIO:
    qs = yoris_models.Activity.objects.filter(user=user)
    return await build_activity_stats(qs, title=f"Статистика пользователя {user.name}", days=days)


async def get_chat_member_stats(user, chat, days: int | None = 7) -> BytesIO:
    qs = yoris_models.Activity.objects.filter(chat=chat, user=user)
    return await build_activity_stats(qs, title=f"Статистика участника {user.name} чата {chat.name}", days=days)


@sync_to_async
def get_cubes_stats(chat) -> BytesIO:
    qs = (
        yoris_models.CubeActivity.objects
        .filter(chat=chat)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    if not qs:
        buf = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, "Нет данных", ha='center', va='center')
        plt.axis('off')
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return buf
    days = [row["day"].strftime("%Y-%m-%d") for row in qs]
    counts = [row["count"] for row in qs]
    plt.figure(figsize=(10, 5))
    plt.bar(days, counts, color="skyblue")
    plt.title(f"Активность кубов в чате {chat.name}")
    plt.xlabel("Дата")
    plt.ylabel("Количество игр")
    plt.grid(axis="y")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf
