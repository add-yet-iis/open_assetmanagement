from .models import Device, Product, ProductSupplier
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm, DeviceForm, ProductForm, SupplierForm, NetworkdiscoveryForm
from .filehandler import handle_uploaded_file, csv_to_device
from django.urls import reverse
from .tables import DeviceTable
from .filters import DeviceFilter
from django_tables2 import SingleTableView, RequestConfig
from django_tables2.export.export import TableExport
from django.contrib import messages
import csv
from .network_discovery_module import network_discovery


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
    RequestConfig(request, paginate={"per_page": 8}).configure(context['table'])
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, context['table'])
        return exporter.response("assets".format(export_format))
    context['filter'] = DeviceFilter()
    if request.method == 'POST':
        context['form'] == UploadFileForm(request.POST, request.FILES)
        if context['form'].is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        context['form'] = UploadFileForm()

    if request.method == 'POST':
        context['networkdiscovery_form'] == NetworkdiscoveryForm(request.POST, request.FILES)
        if context['networkdiscovery_form'].is_valid():
            csv_to_device(network_discovery(request.POST.get("ip_range")))
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        context['networkdiscovery_form'] = NetworkdiscoveryForm()
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


def network_scan(request):
    ip_range = str(request.POST.get("ip_range"))
    print(ip_range)
    csv_to_device(network_discovery(ip_range))
    return HttpResponseRedirect(reverse('inventory:index'))


def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


def delete_supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    supplier.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


def download_file(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="assets.csv"'},
    )
    writer = csv.writer(response)
    devices = Device.objects.all()
    writer.writerow(Device.keys(Device))
    for dev in devices:
        writer.writerow(dev.values())

    return response


def device(request, pk):
    device = Device.objects.get(pk=pk)
    context = {}
    context["pk"] = pk
    if request.method == "POST":
        context["form"] = DeviceForm(request.POST, instance=device)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = DeviceForm(instance=device)
    return render(request, 'inventory/device.html', context)


def product(request, pk):
    product = Product.objects.get(pk=pk)
    context = {}
    context["pk"] = pk
    if request.method == "POST":
        context["form"] = ProductForm(request.POST, instance=product)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = ProductForm(instance=product)
    return render(request, 'inventory/device.html', context)


def supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    context = {}
    context["pk"] = pk
    if request.method == "POST":
        context["form"] = SupplierForm(request.POST, instance=supplier)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SupplierForm(instance=supplier)
    return render(request, 'inventory/device.html', context)
