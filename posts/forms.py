from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        verbose_name = 'new post'
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'This is plain text area.',
            'group': 'Group to which this post belongs to.'
        }


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        verbose_name = 'new comment'
        fields = ('text',)

        help_texts = {
            'text': 'This is comment text area.',
            'group': 'Group to which this post belongs to.'
        }
