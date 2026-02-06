from django import forms

class StoryForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'border p-2 w-full'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 3}))
    status = forms.ChoiceField(choices=[('published', 'Published'), ('draft', 'Draft')])