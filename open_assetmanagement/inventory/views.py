from django.views import generic
from django.utils import timezone
from .models import Device, Product
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm, DeviceForm, ProductForm
from .filehandler import handle_uploaded_file
from django.urls import reverse
from .tables import DeviceTable
from .filters import DeviceFilter
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
from django.contrib import messages


class IndexView(SingleTableView):
    template_name = 'inventory/index.html'
    context_object_name = 'devices'
    model = Device
    table_class = DeviceTable

    def get_queryset(self):
        #    """Return the last five published questions."""
        #    return Device.objects.filter(
        #        group='1'
        #    ).order_by('-device_name')[:5]
        return Device.objects.all()


def index(request):
    context = {}
    context['table'] = DeviceTable(Device.objects.all())
    RequestConfig(request).configure(context['table'])
    if request.method == 'POST':
        context['form'] == UploadFileForm(request.POST, request.FILES)
        if context['form'].is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        context['form'] = UploadFileForm()
    return render(request, "inventory/index.html", context)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        form = UploadFileForm()
    return render(request, 'inventory/upload.html', {'form': form})


def device(request, pk):
    device = Device.objects.get(pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    form = DeviceForm(instance=device)
    return render(request, 'inventory/device.html', {'form': form})


def product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    form = ProductForm(instance=device)
    return render(request, 'inventory/device.html', {'form': form})


def productsupplier(request):
    device = Device.objects.get(pk=1)
    form = DeviceForm(instance=device)

    return render(request, 'inventory/device.html', {'form': form})

# Create your views here.
