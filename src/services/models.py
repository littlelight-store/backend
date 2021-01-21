from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.utils.text import slugify

from core.domain.entities.constants import ConfigurationType


class Season(models.Model):
    name = models.CharField(max_length=64, help_text="Название сезона")
    slug = models.CharField(max_length=64, help_text="Slug сезона", unique=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    class Meta:
        ordering = ["ordering"]

    category = models.ForeignKey(
        "services.Category",
        on_delete=models.CASCADE,
        related_name="services",
        related_query_name="services",
    )

    extra_categories = models.ManyToManyField("services.Category",)

    seasons = models.ManyToManyField(
        "services.Season",
        related_name="seasons",
        related_query_name="seasons",
        blank=True,
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(primary_key=True, editable=True)
    description = models.TextField(blank=True, null=True, help_text="On product page")

    option_type = models.CharField(max_length=128)

    ordering = models.IntegerField(default=0)
    keywords = models.TextField(default="", blank=True)

    is_hidden = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)

    important_information = JSONField(default=dict, blank=True)
    requirements = JSONField(default=dict, blank=True)

    extra_configs = JSONField(default=dict, blank=True)

    image_square = models.ImageField(blank=True, upload_to="uploaded_images")

    background_image = models.ImageField(blank=True, upload_to="uploaded_images_bg")
    card_image = models.ImageField(blank=True, upload_to="uploaded_images_bg")
    item_image = models.ImageField(blank=True, upload_to="uploaded_item_images")

    group_tags = models.ManyToManyField(
        "services.ServiceGroupTagORM",
        blank=True
    )

    booster_price = models.IntegerField(default=50)
    base_price = models.DecimalField(max_digits=5, decimal_places=0, null=True, blank=True)

    configuration_type = models.CharField(
        max_length=20,
        default=None,
        null=True,
        blank=True,
        choices=(
            (ConfigurationType.base_price.value, 'Base price'),
            (ConfigurationType.options_select.value, 'Options select'),
            (ConfigurationType.range_select.value, 'Range select'),
            (ConfigurationType.options_steps.value, 'Options steps'),
        )
    )

    at_least_one_option_required = models.BooleanField(
        default=False
    )

    you_will_get_content = RichTextField(default=None, blank=True, null=True)
    static_requirements = RichTextField(default=None, blank=True, null=True)
    static_description = RichTextField(default=None, blank=True, null=True)

    eta = models.CharField(max_length=20, default='1 day')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("services:service", kwargs={"slug": self.slug})


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["ordering"]

    site = models.ForeignKey(
        Site,
        blank=True,
        null=True,
        db_index=True,
        on_delete=models.SET_NULL,
        related_name="categories",
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(primary_key=True)

    layout = models.ForeignKey(
        "services.CategoryLayout", null=True, blank=True, on_delete=models.SET_NULL
    )

    background_image = models.ImageField(blank=True, upload_to="uploaded_images_bg")

    ordering = models.IntegerField(default=0)

    important_information = JSONField(default=dict, blank=True)
    requirements = JSONField(default=dict, blank=True)

    on_site = CurrentSiteManager()
    objects = models.Manager()

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("services:category", kwargs={"slug": self.slug})

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class ServiceConfig(models.Model):
    class Meta:
        ordering = ("ordering",)

    NORMAL = "normal"
    PRESTIGE = "prestige"

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="configs",
        related_query_name="configs",
    )

    title = models.CharField(max_length=200, verbose_name="Service mode name")
    description = models.CharField(
        max_length=500, verbose_name="Additional info", blank=True
    )

    price = models.DecimalField(max_digits=5, decimal_places=0)
    old_price = models.DecimalField(
        max_digits=5,
        decimal_places=0,
        blank=True,
        null=True,
        help_text="Optional discount",
    )

    extra_configs = JSONField(default=dict, blank=True)

    extra_configs_v2 = JSONField(default=dict, blank=True)
    extra_configs_v2_version = models.CharField(max_length=10, default="0.0.1")

    ordering = models.IntegerField(default=0)

    def __str__(self):
        if self.service:
            return f"{self.title} -- {self.service.title}"


class ServiceConfigPvp(models.Model):
    service = models.OneToOneField(
        "services.Service", on_delete=models.CASCADE, related_name="pvp_config"
    )
    additional_info = models.CharField(
        max_length=500, verbose_name="Additional info", blank=True
    )

    card_unit = models.CharField(
        max_length=128,
        help_text='Unit for card price (for example: $4/1 ${"win"}',
        null=True,
        blank=True,
    )
    points_unit = models.CharField(
        max_length=128,
        help_text='Unit for points in modal (for example: ${"DZ Level"} X > ${"DZ Level"} Y',
        null=True,
        blank=True,
    )
    initial_points_selected = models.PositiveIntegerField(
        help_text="Initial amount of points", default=10
    )
    initial_points = models.IntegerField(help_text="Points of user to start", default=0)
    min_points = models.PositiveIntegerField(
        help_text="Min amount of points", default=0
    )
    max_points = models.PositiveIntegerField(help_text="Max amount of points")

    first_mark_text = models.CharField(
        max_length=128, help_text="Text for first point", default="Guardian"
    )

    class Meta:
        verbose_name = "Pvp threshold config"
        verbose_name_plural = "Pvp thresholds config"

    def __str__(self):
        return f"{self.service.title} — pvp config"


class PvpThreshold(models.Model):
    config = models.ForeignKey(
        "services.ServiceConfigPvp",
        on_delete=models.CASCADE,
        related_name="threshold_configs",
    )

    step_price = models.DecimalField(help_text="Price", max_digits=5, decimal_places=2)
    step_value = models.PositiveSmallIntegerField(
        help_text="Value for step of range slider"
    )

    threshold_points = models.PositiveIntegerField(help_text="Points threshold")
    threshold_label = models.CharField(
        help_text="Value on range corresponding rank", max_length=64
    )

    class Meta:
        verbose_name = "Pvp threshold config"
        verbose_name_plural = "Pvp thresholds config"


class PromoCode(models.Model):
    class Meta:
        verbose_name = "Promo code"
        verbose_name_plural = "Promo codes"

    code = models.CharField(max_length=200, primary_key=True)
    service = models.ManyToManyField(
        "services.Service", related_name="promo_codes", related_query_name="promo_codes"
    )
    comment = models.TextField(blank=True, default="")
    usage_limit = models.IntegerField(default=10)
    first_buy_only = models.BooleanField(default=False)
    discount = models.IntegerField(
        default=1, validators=[MaxValueValidator(100), MinValueValidator(1)]
    )

    def calculate_discount_for_price(self, price: float) -> float:
        discount = price * (self.discount / 100)
        return float(price - discount)


class CategoryLayout(models.Model):
    type = models.CharField(primary_key=True, max_length=50)

    class Meta:
        verbose_name = "Category layout"
        verbose_name_plural = "Category layout"


class ServiceGroupTagORM(models.Model):
    value = models.CharField(max_length=58, primary_key=True)
    name = models.CharField(max_length=58)
    services = models.ManyToManyField(Service, through=Service.group_tags.through, blank=True)

    ordering = models.IntegerField(default=0, editable=True)

    class Meta:
        ordering = ["ordering"]
        db_table = 'service_group_tag'

        verbose_name = "Main Page Group Tag"
        verbose_name_plural = "Main Page Group tags"
