from django import forms

# Since Story isn't a Django model, we use a standard forms.Form
# forms.Form superclass allows for wrap the fetched data with tag/field type, styling, and other constraints
class StoryForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full mb-4 px-3 py-2 border rounded'})
    )  # Styling
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full mb-4 px-3 py-2 border rounded', 'rows': 4})
    )
    status = forms.ChoiceField(
        choices=[('published', 'Published'), ('draft', 'Draft')]
    )