from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from services.utils import get_next_meals, get_products
from supernova.views import build_base_context
from services import models as m


def services_view(request):
    services = m.Service.objects.order_by('type').all()
    services_by_type = dict()
    for service in services:
        if service.type in services_by_type:
            services_by_type[service.type].append(service)
        else:
            services_by_type[service.type] = [service, ]

    context = build_base_context(request)
    context['pcode'] = "c_campus_services"
    context['title'] = "Serviços no campus"
    context['services_by_type'] = services_by_type
    context['sub_nav'] = [
        {'name': 'Serviços', 'url': reverse('services:services')}]
    return render(request, 'services/services.html', context)


def service_view(request, service_abbr):
    service = get_object_or_404(m.Service, abbreviation=service_abbr)
    context = build_base_context(request)
    context['pcode'] = "c_campus_service"
    context['title'] = f"Serviço {service.name}"
    context['service'] = service
    context['meal_occasions'] = get_next_meals(service)
    context['products'] = get_products(service)
    context['sub_nav'] = [
        {'name': 'Serviços', 'url': reverse('services:services')},
        {'name': service.name, 'url': reverse('services:service', args=[service_abbr])}]
    return render(request, 'services/service.html', context)
