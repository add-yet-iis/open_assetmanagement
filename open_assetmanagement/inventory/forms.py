import magic
from django import forms
from .models import Device, Product, ProductSupplier
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = []


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = []


class SupplierForm(forms.ModelForm):
    class Meta:
        model = ProductSupplier
        exclude = []


class NetworkdiscoveryForm(forms.Form):
    ip_range = forms.CharField()


class UploadFileForm(forms.Form):
    #title = forms.CharField(max_length=50)
    file = forms.FileField()
    #FILE_TYPES = [
    #    ('XLSX', 'Excel'),
    #    ('CSV', 'CSV'),
    #    ('XML', 'XML'),
    #]
    #file_type = forms.ChoiceField(
    #    choices=FILE_TYPES,
    #)

    def clean_title(self):
        data = self.cleaned_data['title']
        if "bad" in data:
            raise ValidationError(_('Invalid name'))

        # Remember to always return the cleaned data.
        return data

    def clean_file(self):
        d_type = self.cleaned_data.get('file_type')
        file = self.cleaned_data.get("file", False)
        filetype = magic.from_buffer(file.read())
        if not "text" in filetype and not "Microsoft Excel" in filetype:
            raise ValidationError("Filetype ist wrong, you tried uploading: '" + filetype + "' but shoud have uploaded: CSV or XLSX")
        return file
