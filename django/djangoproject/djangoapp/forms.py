from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Since Story isn't a Django model, we use a standard forms.Form
# forms.Form superclass allows for wrap the fetched data with tag/field type, styling, and other constraints
# attributes are required for input by default
class StoryForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full mb-4 px-3 py-2 border rounded'})
    )  # Styling
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full mb-4 px-3 py-2 border rounded', 'rows': 4})
    )
    # Start Text for the First Page
    start_text = forms.CharField(
        required=False,  # Optional because we might be in "Edit Mode"
        label="The Beginning (Start Page Text)",
        widget=forms.Textarea(attrs={
            'class': 'w-full mb-4 px-3 py-2 border rounded', 
            'rows': 4,
            'placeholder': 'It was a dark and stormy night...'
        })
    )


class PageForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        help_text="What happens on this page?"
    )
    is_ending = forms.BooleanField(
        required=False, 
        label="Is this an Ending?",
        help_text="If checked, the story ends here (no choices allowed)."
    )


class ChoiceForm(forms.Form):
    text = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'e.g. Open the door'}),
        label="Choice Text"
    )
    next_page_id = forms.ChoiceField(
        label="Leads to Page",
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )

    def __init__(self, page_options=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We populate the dropdown dynamically based on the story's pages
        if page_options:
            self.fields['next_page_id'].choices = page_options

    

class RegisterForm(UserCreationForm):
    # Role Selection Field
    ROLE_CHOICES = [
        ('Reader', 'Reader (Play Only)'),
        ('Author', 'Author (Create Stories)'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'flex gap-4'}),
        initial='Reader',
        help_text="Authors can create stories. Readers can only play."
    )

    class Meta:
        model = User
        fields = ['username', 'email'] # Password is handled by parent class

    def save(self, commit=True):
        # 1. Save the User instance
        user = super().save(commit=False)
        if commit:
            user.save()
        return user