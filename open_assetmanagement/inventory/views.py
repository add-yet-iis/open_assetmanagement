from .models import Device, Product, ProductSupplier
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm, DeviceForm, ProductForm, SupplierForm, NetworkdiscoveryForm, CreateUserForm
from .filehandler import handle_uploaded_file, csv_to_device
from django.urls import reverse
from .tables import DeviceTable, ProductTable
from .filters import DeviceFilter
from django_tables2 import SingleTableView, RequestConfig
from django_tables2.export.export import TableExport
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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


@login_required(login_url='inventory:login')
def dashboard(request):
    devices = Device.objects.all()
    products = Product.objects.all()
    suppliers = ProductSupplier.objects.all()
    product_table = ProductTable(products)
    RequestConfig(request, paginate={"per_page": 8}).configure(product_table)
    context = {
        'devices': devices,
        'products': products,
        'suppliers': suppliers,
        'total_devices': devices.count(),
        'total_products': products.count(),
        'total_suppliers': suppliers.count(),
        'product_table': product_table,
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
            password =request.POST.get('password')

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
    RequestConfig(request, paginate={"per_page": 8}).configure(context['table'])
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, context['table'])
        return exporter.response("assets".format(export_format))

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


@login_required(login_url='inventory:login')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST.get("delimiter"))
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        form = UploadFileForm()
    return render(request, 'inventory/upload.html', {'form': form})


@login_required(login_url='inventory:login')
def network_scan(request):
    ip_range = str(request.POST.get("ip_range"))
    print(ip_range)
    csv_to_device(network_discovery(ip_range))
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
def delete_supplier(request, pk):
    supplier = ProductSupplier.objects.get(pk=pk)
    supplier.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    return HttpResponseRedirect(reverse('inventory:index'))


@login_required(login_url='inventory:login')
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


@login_required(login_url='inventory:login')
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


@login_required(login_url='inventory:login')
def product(request, pk):
    product = Product.objects.get(pk=pk)
    #devices = Device.objects.get(product_id=product)
    devices = Device.objects.all().filter(product_id=pk)
    context = {}
    context["pk"] = pk
    context["product"] = product
    context["devices"] = devices
    if request.method == "POST":
        context["form"] = ProductForm(request.POST, instance=product)
        if context["form"].is_valid():
            context["form"].save()
            messages.success(request, 'Changes successful!')
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = ProductForm(instance=product)
    return render(request, 'inventory/product.html', context)


@login_required(login_url='inventory:login')
def supplier(request, pk):
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
            return HttpResponseRedirect(reverse('inventory:index'))
        else:
            messages.error(request, 'Error saving form')

    context["form"] = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier.html', context)
