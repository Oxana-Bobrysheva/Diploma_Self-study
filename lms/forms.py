from django import forms
from .models import Course, Testing


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "price", "preview"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название курса"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Описание курса",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Цена"}
            ),
            "preview": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Название курса",
            "description": "Описание",
            "price": "Цена (руб)",
            "preview": "Изображение курса",
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

class TestingForm(forms.ModelForm):
    # Add custom fields that match your template
    test_title = forms.CharField(label="Название теста")
    test_description = forms.CharField(label="Описание", widget=forms.Textarea, required=False)

    class Meta:
        model = Testing
        fields = ["title", "description", "time_limit", "passing_score"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Map initial data if needed
        if 'data' in kwargs:
            data = kwargs['data'].copy()
            if 'test_title' in data:
                data['title'] = data['test_title']
            if 'test_description' in data:
                data['description'] = data['test_description']
            kwargs['data'] = data
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Map custom fields to model fields before saving
        self.instance.title = self.cleaned_data.get('test_title', '')
        self.instance.description = self.cleaned_data.get('test_description', '')
        return super().save(commit)
