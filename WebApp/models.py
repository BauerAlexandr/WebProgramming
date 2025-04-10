from django.db import models
from django.utils.text import slugify



# Пользовательский менеджер модели
class WatchManager(models.Manager):
    def available(self):
        return self.filter(is_published='PB')
        
    def by_category(self, category_id):
        return self.filter(category_id=category_id)
    
    def price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)

# Модель часов
class Watch(models.Model):
    class WatchStatus(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория', null=True)
    is_published = models.CharField(
        'Статус',
        max_length=2,
        choices=WatchStatus.choices,
        default=WatchStatus.DRAFT
    )
    image = models.CharField('Изображение', max_length=200, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    # Подключаем пользовательский менеджер
    objects = WatchManager()
    
    def get_status_display(self):
        """Возвращает человекочитаемое представление статуса"""
        for status in WatchStatus:
            if self.status == status.name:
                return status.value
        return "Не указан"
    
    def save(self, *args, **kwargs):
        # Автоматическое создание слага из названия, если слаг не указан
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            
            # Проверяем уникальность слага
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

# Модель категории часов
class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            
            # Проверяем уникальность слага
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
