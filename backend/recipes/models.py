from django.contrib.auth import get_user_model
from django.core.validators import (MaxLengthValidator, MaxValueValidator,
                                    MinValueValidator, RegexValidator,)
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        validators=[MaxLengthValidator(1000)],
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        related_name='tag_recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1,
                              'Минимальное время приготовления 1 мин'
                              ),
            MaxValueValidator(600,
                              'Слишком долго. Давай рецепт побыстрее.'
                              ),
        ],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        db_index=True,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        help_text=(
            'Введите код цвета в шестнадцетиричном формате (#ABCDEF)'),
        max_length=7,
        unique=True,
        validators=(
            RegexValidator(
                regex='^#[a-fA-F0-9]{6}$', code='wrong_hex_code',
                message='Неправильный формат цвета'),
        )
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингридиента"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )

    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингридиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент по рецепту'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(1),
                    MaxValueValidator(1000),)
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipeingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe.name}: {self.ingredient} – {self.amount}'


class RecipeTag(models.Model):
    """Модель тега в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
        verbose_name='Тег рецепта',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    constraints = [
        models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_tag'
        )
    ]

    def __str__(self):
        return self.recipe.name


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранные',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранные',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} имеет "{self.recipe}" в Избранном'


class ShoppingCart(models.Model):
    """Модель cписка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок',
    )
    constraints = [
        models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_shopping_cart'
        )
    ]

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} имеет {self.recipe} в Списке покупок'
