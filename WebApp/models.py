from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


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

    class Meta:
        permissions = [
            ('can_discount_watch', 'Может применять скидку на часы'),
        ]

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
    

class UserContent(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    content = models.TextField('Контент', blank=True)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='user_content/%Y/%m/%d/',
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Автор',
        related_name='user_contents'
    )
    is_published = models.BooleanField('Опубликовано', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            n = 1
            while UserContent.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пользовательский контент'
        verbose_name_plural = 'Пользовательский контент'
        ordering = ['-created_at']

class Comment(models.Model):
    watch = models.ForeignKey(
        Watch, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        verbose_name='Часы',
        null=True,
        blank=True
    )
    user_content = models.ForeignKey(
        UserContent,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользовательский контент',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_approved = models.BooleanField('Одобрено', default=True)

    def __str__(self):
        return f'Комментарий от {self.author} к {self.watch or self.user_content}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользователь'
    )
    watch = models.ForeignKey(
        Watch,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Часы',
        null=True,
        blank=True
    )
    user_content = models.ForeignKey(
        UserContent,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользовательский контент',
        null=True,
        blank=True
    )
    is_like = models.BooleanField('Лайк/Дизлайк', default=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = [
            ('user', 'watch'),
            ('user', 'user_content')
        ]

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)