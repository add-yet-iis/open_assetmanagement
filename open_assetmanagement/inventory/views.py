from .models import Device, Product, ProductSupplier, Software
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm, DeviceForm, ProductForm, SupplierForm, NetworkdiscoveryForm, CreateUserForm, \
    SoftwareForm, S7discoveryForm
from .filehandler import handle_uploaded_file, csv_to_device
from django.urls import reverse
from .tables import DeviceTable, ProductTable
from .filters import DeviceFilter
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import csv
from .network_discovery_module import network_discovery, s7_discovery


@login_required(login_url='inventory:login')
def dashboard(request):
    devices = Device.objects.all()
    products = Product.objects.all()
    suppliers = ProductSupplier.objects.all()
    softwares = Software.objects.all()
    product_table = ProductTable(products)
    RequestConfig(request, paginate={"per_page": 8}).configure(product_table)
    form = UploadFileForm()
    context = {
        'devices': devices,
        'products': products,
        'suppliers': suppliers,
        'softwares': softwares,
        'total_devices': devices.count(),
        'total_products': products.count(),
        'total_suppliers': suppliers.count(),
        'total_software': softwares.count(),
        'product_table': product_table,
        'form': form,
    }
    return render(request, "inventory/dashboard.html", context)


def register_page(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('inventory:login')

        context = {'form': form}
        return render(request, 'inventory/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('inventory:login')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('inventory:dashboard')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'inventory/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('inventory:login')


@login_required(login_url='inventory:login')
def index(request):
    context = {}
    devices = Device.objects.all()
    context['filter'] = DeviceFilter(request.GET, queryset=devices)
    export_format = request.GET.get("_export", None)
    context['table'] = DeviceTable(context['filter'].qs)
    RequestConfig(request, paginate={"per_page": 10}).configure(context['table'])
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, context['table'])
        return exporter.response("assets".format(export_format))
    context['networkdiscovery_form'] = NetworkdiscoveryForm()
    context['s7discovery_form'] = S7discoveryForm()
    return render(request, "inventory/index.html", context)


@login_required(login_url='inventory:login')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST.get("delimiter"))
            return HttpResponseRedirect(reverse('inventory:dashboard'))
    else:
        form = UploadFileForm()
    return render(request, 'inventory/upload.html', {'form': form})


@login_required(login_url='inventory:login')
def network_scan(request):
    csv_to_device(network_discovery(str(request.POST.get("ip_range")), int(request.POST.get("type")), int(request.POST.get("timeout"))))
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
def s7_scan(request):
    csv_to_device(s7_discovery(str(request.POST.get("ip_range"))))
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
def download_file(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="assets.csv"'},
    )
    writer = csv.writer(response)
    devices = Device.objects.all().values('id', 'device_name', 'product_id__product_supplier_id__name',
                                          'product_id__model', 'product_id__version', 'product_id__type',
                                          'product_id__endOfSupport', 'automatic_import', 'communication_capability',
                                          'criticality', 'csv_import', 'group', 'interdependencies', 'ip_address',
                                          'location', 'mac_address', 'network', 'os', 'product_id', 'redundancy',
                                          'role', 'serial_number', 'software', 'configuration_file')
    writer.writerow(devices.first().keys())
    for dev in devices:
        writer.writerow(dev.values())

    return response


@login_required(login_url='inventory:login')
def device(request, pk):
    device = Device.objects.get(pk=pk)
    softwares = device.software_set.all()
    context = {"pk": pk, "device": device, "softwares": softwares}
    return render(request, 'inventory/device.html', context)


@login_required(login_url='inventory:login')
def change_device(request, pk):
    device = Device.objects.get(pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')
    form = DeviceForm(instance=device)
    context = {"form": form}
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def create_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')
    form = DeviceForm()
    context = {"form": form}
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return HttpResponseRedirect(reverse('inventory:dashboard'))


@login_required(login_url='inventory:login')
def product(request, pk):
    product = Product.objects.get(pk=pk)
    devices = Device.objects.all().filter(product_id=pk)
    context = {"pk": pk, "product": product, "devices": devices}
    return render(request, 'inventory/product.html', context)


@login_required(login_url='inventory:login')
def change_product(request, pk):
    product = Product.objects.get(pk=pk)
    context = {"product": product}
    if request.method == "POST":
        context["form"] = ProductForm(request.POST, instance=product)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')
    context["form"] = ProductForm(instance=product)

    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def create_product(request):
    context = {}
    if request.method == "POST":
        context["form"] = ProductForm(request.POST)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')
    context["form"] = ProductForm()

    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    return HttpResponseRedirect(reverse('inventory:dashboard'))


@login_required(login_url='inventory:login')
def supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    context = {
        "pk": pk,
        "supplier": supplier,
        "products": Product.objects.all().filter(product_supplier_id=pk),
        "softwares": Software.objects.all().filter(product_supplier_id=pk)
    }
    return render(request, 'inventory/supplier.html', context)


@login_required(login_url='inventory:login')
def change_supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    context = {}
    context["pk"] = pk
    context["supplier"] = supplier
    context["products"] = Product.objects.all().filter(product_supplier_id=pk)
    if request.method == "POST":
        context["form"] = SupplierForm(request.POST, instance=supplier)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SupplierForm(instance=supplier)
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def create_supplier(request):
    context = {}
    if request.method == "POST":
        context["form"] = SupplierForm(request.POST)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SupplierForm()
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def delete_supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    supplier.delete()
    return HttpResponseRedirect(reverse('inventory:dashboard'))


@login_required(login_url='inventory:login')
def software(request, pk):
    software = Software.objects.get(pk=pk)
    devices = software.devices.all()
    context = {
        "pk": pk,
        "software": software,
        "devices": devices,
    }
    return render(request, 'inventory/software.html', context)


@login_required(login_url='inventory:login')
def change_software(request, pk):
    software = Software.objects.get(pk=pk)
    context = {}
    context["pk"] = pk
    context["software"] = software

    if request.method == "POST":
        context["form"] = SoftwareForm(request.POST, instance=software)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SoftwareForm(instance=software)
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def create_software(request):
    context = {}
    if request.method == "POST":
        context["form"] = SoftwareForm(request.POST)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:dashboard'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SoftwareForm()
    return render(request, 'inventory/form.html', context)


@login_required(login_url='inventory:login')
def delete_software(request, pk):
    software = Software.objects.get(pk=pk)
    software.delete()
    return HttpResponseRedirect(reverse('inventory:dashboard'))

