from django import forms
from .models import Course


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
