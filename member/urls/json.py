from django.urls import path

from member.views import json

app_name = 'member'
urlpatterns = [
    path('user_search/', json.user_search, name='user_search'),
    path('user_tags/', json.user_tags, name='user_tags'),
    path('org_tags/', json.org_tags, name='org_tags'),
    path('org_search/', json.org_search, name='org_search'),
]

# Copyright 2021 Office Nomads LLC (https://officenomads.com/) Licensed under the AGPL License, Version 3.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at https://www.gnu.org/licenses/agpl-3.0.html. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

