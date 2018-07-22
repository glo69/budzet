
# -*- coding: utf-8 -*-
"""budget URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from mybudget import views
from django.contrib.auth.views import logout, login
from django.conf.urls.static import static



urlpatterns = [
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', login, name='login'),
    url(r'^login/$', login, name='login'),
    url(r'^new/$', views.post_new, name='post_new'),
    # url(r'^minidlna/$', views.minidlna_refresh),
    url(r'^compare_dates/$', views.compare_dates, name='compare_dates'),
    url(r'^range_date/$', views.range_date, name='range_date'),
    url(r'^logout/$', logout, {'template_name': 'lista_wydatkow.html', 'next_page': '/login'}, name='log-out'),
    url(r'^period_list/$', views.period_list, name='period_list'),
    # url(r'^history/(?P<wybrany_okres>\w+)/$', views.post_actual_period2, name='post_actual_period2'),
    url(r'^history/', views.actual_period_data, name='actual_period_data'),
    url(r'^history_all/', views.all_data, name='all_data'),
    url(r'^history_data/$', views.actual_period_data, name='actual_period_data'),
    # url(r'^question/$', views.question, name='question'),
    # url(r'^end_period/$', views.end_period, name='end_period'),
    url(r'^details/(?P<ids>\w+)/$', views.details, name='details'),
    url(r'^remove/(?P<ids>\w+)/$', views.remove, name='remove'),
    url(r'^adduser/$', views.add_user, name='add_user'),
    url(r'^csv_file/$', views.csv_file, name='csv_file'),
    url(r'^export_typy/$', views.export_typy, name='export_typy'),
    url(r'^import_typy/$', views.import_typy, name='import_typy'),
    url(r'^new_type/$', views.new_type, name='new_type'),
    url(r'^temp_data/$', views.temp_data, name='temp_data'),
  
    url(r'^chart/(?P<typ>[\w\ ]+)/(?P<min_id>[\w-]+)/(?P<max_id>\w+)/$', views.type_chart, name='type_chart'),
    #url(r'^remove_type/$', views.remove_type, name='remove_type'), 

 
]
