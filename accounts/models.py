from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction


class AvatarOption(models.Model):
    OPTION_TYPE_CHOICES = [
        ("preset", "Preset"),
        ("base_body", "Base body"),
        ("body_style", "Body style"),
        ("hair_style", "Hair style"),
        ("eyes", "Eyes"),
        ("accessory", "Accessory"),
        ("outfit", "Outfit"),
    ]

    name = models.CharField(max_length=80)
    option_type = models.CharField(
        max_length=20,
        choices=OPTION_TYPE_CHOICES,
        default="preset",
    )
    image_asset = models.FileField(upload_to="avatars/", blank=True)
    color_value = models.CharField(max_length=20, blank=True)
    coin_price = models.PositiveIntegerField(default=0)
    layer_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    required_category = models.ForeignKey(
        "reading.Category",
        on_delete=models.SET_NULL,
        related_name="avatar_options",
        blank=True,
        null=True,
        help_text="Categoria que precisa ser lida para liberar este item.",
    )
    required_category_reads = models.PositiveSmallIntegerField(
        default=0,
        help_text="Quantidade de textos concluidos na categoria exigida para compra.",
    )

    class Meta:
        ordering = ["layer_order", "option_type", "coin_price", "name"]
        indexes = [
            models.Index(fields=["option_type", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def asset_path(self):
        return self.image_asset.name if self.image_asset else ""

    def can_be_unlocked_by(self, user):
        return self.unlock_status_for(user)["can_unlock"]

    def category_read_count_for(self, user):
        if not user or not user.is_authenticated or not self.required_category_id:
            return 0
        from progress.models import ReadingProgress

        return (
            ReadingProgress.objects.filter(
                user=user,
                status="completed",
                text__category=self.required_category,
            )
            .values("text_id")
            .distinct()
            .count()
        )

    def unlock_status_for(self, user):
        if not user or not user.is_authenticated:
            return {
                "is_unlocked": self.coin_price == 0 and not self.required_category_id,
                "can_unlock": self.coin_price == 0 and not self.required_category_id,
                "has_enough_coins": self.coin_price == 0,
                "meets_read_requirement": not self.required_category_id,
                "coins_missing": self.coin_price,
                "reads_done": 0,
                "reads_missing": self.required_category_reads if self.required_category_id else 0,
                "reason": "login_required",
            }

        is_unlocked = (self.coin_price == 0 and not self.required_category_id) or UserAvatarUnlock.objects.filter(
            user=user,
            option=self,
        ).exists()
        profile = getattr(user, "profile", None)
        coin_balance = profile.coin_balance if profile else 0
        reads_done = self.category_read_count_for(user)
        meets_read_requirement = (
            not self.required_category_id or reads_done >= self.required_category_reads
        )
        has_enough_coins = coin_balance >= self.coin_price
        can_unlock = is_unlocked or (meets_read_requirement and has_enough_coins)

        reason = ""
        if not meets_read_requirement:
            reason = "read_requirement"
        elif not has_enough_coins:
            reason = "coins"

        return {
            "is_unlocked": is_unlocked,
            "can_unlock": can_unlock,
            "has_enough_coins": has_enough_coins,
            "meets_read_requirement": meets_read_requirement,
            "coins_missing": max(0, self.coin_price - coin_balance),
            "reads_done": reads_done,
            "reads_missing": max(0, self.required_category_reads - reads_done),
            "reason": reason,
        }

    def can_be_purchased_by(self, user):
        status = self.unlock_status_for(user)
        return status["can_unlock"] and not status["is_unlocked"]

    def clean(self):
        super().clean()
        if self.required_category_reads and not self.required_category:
            raise ValidationError("Informe uma categoria para exigir leituras por categoria.")
        if self.required_category and self.required_category_reads == 0:
            raise ValidationError("Informe uma quantidade minima de leituras maior que zero.")

    def requirement_label(self):
        if not self.required_category_id:
            return ""
        return f"{self.required_category_reads} leituras em {self.required_category.name}"

    def unlock_for(self, user):
        if not user or not user.is_authenticated:
            raise ValidationError("Usuario autenticado e obrigatorio para liberar item de avatar.")

        with transaction.atomic():
            profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
            status = self.unlock_status_for(user)
            if not status["meets_read_requirement"]:
                raise ValidationError(
                    f"Leia mais {status['reads_missing']} texto(s) em {self.required_category.name} para liberar este item."
                )
            if profile.coin_balance < self.coin_price:
                raise ValidationError(f"Faltam {self.coin_price - profile.coin_balance} moedinhas para liberar este item.")

            unlock = UserAvatarUnlock.objects.filter(user=user, option=self).first()
            if unlock:
                return unlock

            unlock = UserAvatarUnlock.objects.create(
                user=user,
                option=self,
                coin_price_paid=self.coin_price,
            )

            if self.coin_price:
                profile.coin_balance -= self.coin_price
                profile.save(update_fields=["coin_balance", "updated_at"])
                from progress.models import CoinTransaction

                CoinTransaction.objects.create(
                    user=user,
                    amount=-self.coin_price,
                    reason="avatar_purchase",
                )

            return unlock

    def legacy_can_be_unlocked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        if self.coin_price == 0:
            return True
        if UserAvatarUnlock.objects.filter(user=user, option=self).exists():
            return True
        profile = getattr(user, "profile", None)
        return bool(profile and profile.coin_balance >= self.coin_price)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=80, blank=True)
    current_level = models.ForeignKey(
        "reading.Level",
        on_delete=models.SET_NULL,
        related_name="users_at_level",
        blank=True,
        null=True,
    )
    avatar = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="profile_users",
        blank=True,
        null=True,
    )
    interests = models.ManyToManyField(
        "reading.Category",
        related_name="interested_users",
        blank=True,
    )
    coin_balance = models.PositiveIntegerField(default=0)
    reading_streak = models.PositiveIntegerField(default=0)
    longest_reading_streak = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return self.display_name or self.user.get_username()


class UserAvatar(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar_state",
    )
    base_body = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="base_body_users",
        blank=True,
        null=True,
        limit_choices_to={"option_type": "base_body"},
    )
    hair_style = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="hair_style_users",
        blank=True,
        null=True,
        limit_choices_to={"option_type": "hair_style"},
    )
    body_style = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="body_style_users",
        blank=True,
        null=True,
        limit_choices_to={"option_type": "body_style"},
    )
    outfit = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="outfit_users",
        blank=True,
        null=True,
        limit_choices_to={"option_type": "outfit"},
    )
    eyes = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="eyes_users",
        blank=True,
        null=True,
        limit_choices_to={"option_type": "eyes"},
    )
    accessories = models.ManyToManyField(
        AvatarOption,
        related_name="accessory_users",
        blank=True,
        limit_choices_to={"option_type": "accessory"},
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Avatar de {self.user.get_username()}"

    def iter_layers(self):
        layers = [self.base_body, self.body_style, self.hair_style, self.outfit, self.eyes]
        layers.extend(self.accessories.filter(is_active=True))
        return sorted(
            [layer for layer in layers if layer and layer.is_active],
            key=lambda option: (option.layer_order, option.option_type, option.name),
        )

    def asset_layers(self):
        return [
            {
                "name": layer.name,
                "type": layer.option_type,
                "asset_path": layer.asset_path,
                "layer_order": layer.layer_order,
            }
            for layer in self.iter_layers()
        ]


class UserAvatarUnlock(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar_unlocks",
    )
    option = models.ForeignKey(
        AvatarOption,
        on_delete=models.CASCADE,
        related_name="unlocks",
    )
    coin_price_paid = models.PositiveIntegerField(default=0)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-unlocked_at"]
        unique_together = ["user", "option"]

    def __str__(self):
        return f"{self.user.get_username()} liberou {self.option.name}"
