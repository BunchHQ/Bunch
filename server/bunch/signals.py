from django.db.models.signals import post_save
from django.dispatch import receiver

from bunch.models import Bunch, Member, RoleChoices


@receiver(post_save, sender=Bunch)
def create_owner_member(
    sender, instance: Bunch, created, **kwargs
):
    if not created:
        return

    owner_user = instance.owner
    if not owner_user:
        return

    if Member.objects.filter(
        bunch=instance,
        user=owner_user,
        role=RoleChoices.OWNER,
    ).exists():
        # already created, probably via API
        return

    if owner_user:
        Member.objects.create(
            bunch=instance,
            user=owner_user,
            role=RoleChoices.OWNER,
        )
