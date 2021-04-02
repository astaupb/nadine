from django.contrib import admin

from member.models import *


class MOTDAdmin(admin.ModelAdmin):
    list_display = ('start_ts', 'end_ts', 'message', 'delay_ms')
admin.site.register(MOTD, MOTDAdmin)


class HelpTextAdmin(admin.ModelAdmin):
    pass
admin.site.register(HelpText, HelpTextAdmin)


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('created', 'notify_user', 'target_user', 'sent_date')
admin.site.register(UserNotification, UserNotificationAdmin)


# Copyright 2021 Office Nomads LLC (https://officenomads.com/) Licensed under the AGPL License, Version 3.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at https://www.gnu.org/licenses/agpl-3.0.html. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
