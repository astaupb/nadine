# -*- coding: utf-8 -*-
from django.urls import path,re_path


from comlink import views

app_name = 'comlink'
urlpatterns = [
    path('', views.home, name="home"),
    path('incoming/', views.Incoming.as_view(), name='incoming'),
    path('mail/<int:id>/', views.view_mail, name='mail'),
    re_path(r'inbox/(?P<address>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.inbox, name='inbox'),
]


# Copyright 2021 Office Nomads LLC (https://officenomads.com/) Licensed under the AGPL License, Version 3.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at https://www.gnu.org/licenses/agpl-3.0.html. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

