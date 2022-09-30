from django.views import generic
from django.utils import timezone
from .models import Device
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .filehandler import handle_uploaded_file
from django.urls import reverse

class IndexView(generic.ListView):
    template_name = 'inventory/index.html'
    context_object_name = 'devices'

    def get_queryset(self):
    #    """Return the last five published questions."""
    #    return Device.objects.filter(
    #        group='1'
    #    ).order_by('-device_name')[:5]
        return Device.objects.all()


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('inventory:index'))
    else:
        form = UploadFileForm()
    return render(request, 'inventory/upload.html', {'form': form})

# Create your views here.
