from django.db import models
from django.utils.text import slugify

class WatchManager(models.Manager):
    def available(self):
        return self.filter(is_published='PB')
        
    def by_category(self, category_id):
        return self.filter(category_id=category_id)
    
    def price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)

class Tag(models.Model):
    name = models.CharField('Название', max_length=100, db_index=True)
    slug = models.SlugField('URL', max_length=255, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            n = 1
            while Tag.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

class TechSpec(models.Model):
    mechanism = models.CharField('Механизм', max_length=100, blank=True)
    water_resistance = models.CharField('Водозащита', max_length=50, blank=True)
    case_material = models.CharField('Материал корпуса', max_length=100, blank=True)

    def __str__(self):
        return f"Характеристики: {self.mechanism}"

    class Meta:
        verbose_name = 'Технические характеристики'
        verbose_name_plural = 'Технические характеристики'

class Watch(models.Model):
    class WatchStatus(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория', null=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='watches', verbose_name='Теги')
    tech_spec = models.OneToOneField('TechSpec', on_delete=models.SET_NULL, null=True, blank=True, related_name='watch', verbose_name='Технические характеристики')
    is_published = models.CharField(
        'Статус',
        max_length=2,
        choices=WatchStatus.choices,
        default=WatchStatus.DRAFT
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='photos/%Y/%m/%d/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    objects = WatchManager()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            n = 1
            while Watch.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{n}"
                n += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Часы'
        verbose_name_plural = 'Часы'
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            n = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{n}"
                n += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']