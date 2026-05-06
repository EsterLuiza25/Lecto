from datetime import timedelta

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from accounts.models import UserProfile
from progress.models import Achievement, CoinTransaction, ReadingProgress, UserAchievement


READING_BADGES = [
    ("leitor-bronze", "Leitor Bronze", 10, "Concluiu 10 leituras no Lecto."),
    ("leitor-prata", "Leitor Prata", 50, "Concluiu 50 leituras no Lecto."),
    ("leitor-ouro", "Leitor Ouro", 100, "Concluiu 100 leituras no Lecto."),
]


def process_completed_reading(user, text, completed_at=None, coin_reward=5):
    completed_at = completed_at or timezone.now()

    with transaction.atomic():
        progress, _ = ReadingProgress.objects.select_for_update().get_or_create(user=user, text=text)
        if progress.status == "completed":
            return {
                "progress": progress,
                "coins_awarded": 0,
                "badges_awarded": [],
                "streak": getattr(user.profile, "reading_streak", 0) if hasattr(user, "profile") else 0,
            }

        progress.status = "completed"
        progress.completed_at = completed_at
        progress.coins_awarded = coin_reward
        progress.save(update_fields=["status", "completed_at", "coins_awarded"])

        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
        profile.coin_balance += coin_reward
        update_reading_streak(profile, completed_at)
        profile.save(
            update_fields=[
                "coin_balance",
                "reading_streak",
                "longest_reading_streak",
                "last_read_at",
                "updated_at",
            ]
        )

        CoinTransaction.objects.create(
            user=user,
            amount=coin_reward,
            reason="reading_completed",
            related_text=text,
        )

        badges_awarded = award_reading_badges(user, profile)

    return {
        "progress": progress,
        "coins_awarded": coin_reward,
        "badges_awarded": badges_awarded,
        "streak": profile.reading_streak,
    }


def update_reading_streak(profile, completed_at):
    previous = profile.last_read_at
    if not previous:
        profile.reading_streak = 1
    else:
        elapsed = completed_at - previous
        if elapsed > timedelta(hours=24):
            profile.reading_streak = 1
        elif completed_at.date() > previous.date():
            profile.reading_streak += 1

    profile.longest_reading_streak = max(profile.longest_reading_streak, profile.reading_streak)
    profile.last_read_at = completed_at


def completed_read_count(user):
    return (
        ReadingProgress.objects.filter(user=user, status="completed")
        .values("text_id")
        .distinct()
        .count()
    )


def category_reading_stats(user):
    if not user or not user.is_authenticated:
        return []

    rows = (
        ReadingProgress.objects.filter(user=user, status="completed")
        .values("text__category__name", "text__category__slug")
        .annotate(total=Count("text_id", distinct=True))
        .order_by("-total", "text__category__name")
    )
    return [
        {
            "name": row["text__category__name"],
            "slug": row["text__category__slug"],
            "total": row["total"],
            "expertise": expertise_label(row["total"]),
        }
        for row in rows
    ]


def expertise_label(total):
    if total >= 50:
        return "Especialista ouro"
    if total >= 25:
        return "Especialista prata"
    if total >= 10:
        return "Especialista bronze"
    if total >= 3:
        return "Explorando"
    return "Primeiros passos"


def award_reading_badges(user, profile=None):
    total_reads = completed_read_count(user)
    awarded = []

    for slug, name, threshold, description in READING_BADGES:
        if total_reads < threshold:
            continue
        achievement, _ = Achievement.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description_pt": description,
                "coin_reward": 0,
                "is_active": True,
            },
        )
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
        )
        if created:
            awarded.append(user_achievement)
            if achievement.coin_reward and profile:
                profile.coin_balance += achievement.coin_reward
                profile.save(update_fields=["coin_balance", "updated_at"])
                CoinTransaction.objects.create(
                    user=user,
                    amount=achievement.coin_reward,
                    reason="achievement",
                )

    return awarded
