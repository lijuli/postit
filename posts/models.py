from textwrap import shorten

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'group title',
        max_length=200,
        help_text='enter the group title'
    )
    slug = models.SlugField(
        'group reference label',
        unique=True,
        help_text='enter the group reference label'
    )
    description = models.TextField(
        'group description',
        help_text='enter information about the group'
    )

    class Meta:
        app_label = 'posts'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('post text', help_text='enter your post here')
    pub_date = models.DateTimeField(
        'date published',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='author'
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='group',
        help_text='select a group'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        verbose_name = 'post'
        ordering = ('-pub_date',)

    def __str__(self):
        shorten_post_text = shorten(self.text, width=15, placeholder='...')
        return f'[{self.pub_date}] {self.author}: {shorten_post_text}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='post',
        help_text='add a comment'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='author'
    )
    text = models.TextField(
        'comment text',
        help_text='enter your comment here'
    )
    created = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        verbose_name = 'comment'
        ordering = ('-created',)

    def __str__(self):
        shorten_comment_text = shorten(self.text, width=10, placeholder='...')
        return f'[{self.created}] {self.author}: {shorten_comment_text}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='following'
    )

    class Meta:
        verbose_name = 'follow'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            )
        ]

    def __str__(self):
        return f'Follower: {self.user}, Following: {self.author}'
