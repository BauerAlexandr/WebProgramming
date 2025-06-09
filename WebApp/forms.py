from django import forms
from django.core.validators import MinLengthValidator
from .models import Category, Watch, UserContent, Comment

class AddWatchForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label="Название",
        validators=[MinLengthValidator(5, message="Название должно быть не короче 5 символов")]
    )
    slug = forms.SlugField(
        max_length=200,
        label="URL",
        validators=[MinLengthValidator(5, message="URL должен быть не короче 5 символов")]
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        required=False,
        label="Описание"
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Цена",
        min_value=0
    )
    is_published = forms.BooleanField(
        required=False,
        label="Опубликовано",
        initial=True
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория",
        empty_label="Категория не выбрана"
    )

    def clean_title(self):
        title = self.cleaned_data['title']
        ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789- "
        if not (set(title) <= set(ALLOWED_CHARS)):
            raise forms.ValidationError("Название должно содержать только русские символы, цифры, дефис и пробел.")
        return title

class AddWatchModelForm(forms.ModelForm):
    class Meta:
        model = Watch
        fields = ['title', 'slug', 'description', 'price','tags', 'is_published', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
            'image': forms.FileInput(),
        }
        labels = {
            'title': 'Название',
            'slug': 'URL',
            'description': 'Описание',
            'tags': 'Теги',
            'price': 'Цена',
            'is_published': 'Опубликовано',
            'category': 'Категория',
            'image': 'Фото',
        }

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория"
    )

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise forms.ValidationError('Длина названия превышает 50 символов')
        return title

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Файл")


class UserContentForm(forms.ModelForm):
    class Meta:
        model = UserContent
        fields = ['title', 'slug', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
            'image': forms.FileInput(),
        }
        labels = {
            'title': 'Название',
            'slug': 'URL',
            'content': 'Контент',
            'image': 'Изображение',
            'is_published': 'Опубликовано'
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise forms.ValidationError('Длина названия превышает 50 символов')
        return title

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 3, 'class': 'form-input'}),
        }
        labels = {
            'text': 'Ваш комментарий'
        }