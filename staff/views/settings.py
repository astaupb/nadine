from datetime import date, datetime
from slugify import slugify

from django.utils import timezone
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.sites.models import Site
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime, now
from django.core.files.storage import FileSystemStorage

from nadine.models.membership import MembershipPackage, SubscriptionDefault
from nadine.models.core import Documents
from nadine.models.profile import FileUpload
from nadine.utils import network
from nadine.forms import HelpTextForm, MOTDForm, DocUploadForm, PackageForm
from nadine.settings import MOTD_TIMEOUT
from member.models import HelpText, MOTD


def times_timeszones(date):
    with_time = date + ' 00:00'
    time_dt = datetime.strptime(with_time, "%Y-%m-%d %H:%M")
    final = timezone.make_aware(time_dt, timezone.get_current_timezone())
    return final


@staff_member_required
def index(request):
    ip = network.get_addr(request)
    context = {'settings': settings, 'ip': ip, 'request': request}
    return render(request, 'staff/settings/index.html', context)


@staff_member_required
def membership_packages(request):
    packages = SubscriptionDefault.objects.all().order_by('package')
    PackageFormset = formset_factory(PackageForm)
    if request.method == 'POST':
        name = request.POST.get('name')
        enabled_bx = request.POST.get('enabled')
        if enabled_bx == 'on':
            enabled = True
        else:
            enabled = False
        mem_pkg = MembershipPackage(name=name, enabled=enabled)
        mem_pkg.save()
        print('id is %s ') % mem_pkg.id
        try:
            with transaction.atomic():
                package_formset = PackageFormset(request.POST)
                if package_formset.is_valid():
                    for p in package_formset:
                        p.package = mem_pkg.id
                        if p.is_valid():
                            p.save()
                            return HttpResponseRedirect(reverse('staff:tasks:todo'))
                        # else:
                        #     messages.error(request, 'There was an error saving the membeship package')
                else:
                    print package_formset.errors
        except IntegrityError as e:
            print('There was an ERROR: %s' % e.message)
            messages.error(request, 'There was an error creating the new membership package')
    else:
        print('boop')
        package_formset = PackageFormset()
    context = {'packages':packages,
               'package_formset': package_formset,
               }
    return render(request, 'staff/settings/membership_packages.html', context)


@staff_member_required
def helptexts(request):
    helps = HelpText.objects.all()
    if helps:
        latest = HelpText.objects.filter().order_by('-order')[0]
        latest_order = latest.order + 1
    else:
        latest = None
        latest_order = 0
    selected = None
    message = None
    selected_help = request.GET.get('selected_help', None)
    if selected_help:
        selected = HelpText.objects.get(title=selected_help)

    if request.method == "POST":
        to_update = request.POST.get('id', None)
        if to_update:
            updated = HelpText.objects.get(id=to_update)
            updated.title = request.POST['title']
            slug = request.POST['slug']
            updated.slug = slugify(slug)
            updated.template = request.POST['template']
            updated.save()

            return HttpResponseRedirect(reverse('staff:tasks:todo'))

        else:
            helptext_form = HelpTextForm(request.POST)
            slug = slugify(request.POST['slug'])
            title = request.POST['title']
            template = request.POST['template']
            order = request.POST['order']
            helptext_form = HelpText(title=title, template=template, slug=slug, order=order)
            helptext_form.save()

            return HttpResponseRedirect(reverse('staff:tasks:todo'))
    else:
        helptext_form = HelpTextForm()

    context = {'latest_order': latest_order, 'helps': helps, 'helptext_form': helptext_form, 'selected': selected, 'message': message}
    return render(request, 'staff/settings/helptexts.html', context)


@staff_member_required
def motd(request):
    prev_motd = MOTD.objects.filter().order_by('-end_ts')
    selected = None
    message = None
    delay = settings.MOTD_TIMEOUT
    selected_motd = request.GET.get('selected_motd', None)
    if selected_motd:
        selected = MOTD.objects.get(id=selected_motd)

    if request.method == 'POST':
        to_update = request.POST.get('id', None)
        start_ts = times_timeszones(request.POST.get('start_ts'))
        end_ts = times_timeszones(request.POST.get('end_ts'))

        if to_update:
            updated = MOTD.objects.get(id=to_update)
            updated.message = request.POST['message']
            updated.save()
            return HttpResponseRedirect(reverse('staff:tasks:todo'))
        else:
            motd_form = MOTDForm(request.POST)

            if MOTD.objects.filter(start_ts__lte=start_ts, end_ts__gte=end_ts):
                message = 'A Message of the Day exists for this time period'

            else:
                motd_form.start_ts = start_ts
                motd_form.end_ts = end_ts
                motd_form.message = request.POST['message']
                if motd_form.is_valid():
                    motd_form.save()
                    return HttpResponseRedirect(reverse('staff:tasks:todo'))
    else:
        motd_form = MOTDForm()
    context = {'prev_motd': prev_motd,
               'motd_form': motd_form,
               'delay': delay,
               'selected': selected,
               'message': message}
    return render(request, 'staff/settings/motd.html', context)

@staff_member_required
def document_upload(request):
    doc_form = DocUploadForm()
    # To be used to preview uploaded docs
    # docs = FileUpload.objects.values_list('document_type', flat=True).distinct().exclude(document_type='None')
    docs = Documents.objects.values_list('name', flat=True).distinct().exclude(name='None')

    if request.method == 'POST':
        if 'doc_type' in request.POST:
            user = request.user
            today = localtime(now()).date()
            doc_type = request.POST.get('doc_type')
            pdf_args = {'doc_type': doc_type}
            return render(request, 'staff/settings/doc_preview.html', pdf_args)
        else:
            doc_form = DocUploadForm(request.POST, request.FILES)
            name = slugify(request.POST.get('name'))
            doc = request.POST.get('document')
            if doc_form.is_valid():
                doc_form.save()
                return HttpResponseRedirect(reverse('staff:tasks:todo'))
            else:
                print doc_form.errors
                messages.error(request, 'There was an error uploading your document')
    context = {
        'doc_form': doc_form,
        'docs': docs,
    }
    return render(request, 'staff/settings/doc_upload.html', context)


# Copyright 2017 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
