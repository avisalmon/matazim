from django import forms

from .models import Part, Item

class DateInput(forms.DateInput):
    input_type = 'date'

class PartCreateForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['title', 'image', 'link', 'location', 'sub_location', 'mode',
                  'price', 'contact', 'many', 'critical']

    create_items = forms.IntegerField()

    def save(self, commit=True):
        part = super(PartCreateForm, self).save(commit=False)
        if commit:
            part.save()
        item_num = self.cleaned_data["create_items"]
        for i in range(item_num):
            Item.objects.create(part=part, location='')
        return part


class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['location', 'return_date']

        widgets = {
            'return_date': DateInput(),
            }
