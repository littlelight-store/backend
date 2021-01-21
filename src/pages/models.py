from django.db import models


# Create your models here.


class PromotedBlock(models.Model):
    description = models.CharField(max_length=40)
    title = models.CharField(max_length=40)
    image = models.ImageField(upload_to="pages/game-page/")

    link_to = models.ForeignKey("services.Service", on_delete=models.CASCADE)


class LimitedOffer(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    promo = models.CharField(max_length=30)


class ServiceOfTheWeek(models.Model):
    title = models.CharField(max_length=20)

    description = models.CharField(max_length=100)

    link_to = models.ForeignKey("services.Service", on_delete=models.CASCADE)

    background_image = models.ImageField(upload_to="pages/game-page/of-the-week/")


class GamePage(models.Model):
    game = models.CharField(max_length=20, db_index=True, primary_key=True)

    total_boosters = models.IntegerField(default=0)

    block_1 = models.ForeignKey(
        "pages.PromotedBlock",
        on_delete=models.CASCADE,
        related_name="block_1",
        blank=True,
        null=True,
    )
    block_2 = models.ForeignKey(
        "pages.PromotedBlock",
        on_delete=models.CASCADE,
        related_name="block_2",
        blank=True,
        null=True,
    )

    offer = models.ForeignKey(
        "pages.LimitedOffer",
        on_delete=models.CASCADE,
        related_name="pages",
        blank=True,
        null=True,
    )

    service_of_the_week = models.ForeignKey(
        "pages.ServiceOfTheWeek",
        on_delete=models.CASCADE,
        related_name="service_of_the_week",
        blank=True,
        null=True,
    )
