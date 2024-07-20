# Copyright (C) 2024 Shubham Agarwal, CISPA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("favicon.ico", views.favicon),
    path('images', views.images, name='images'),
    path('media', views.media, name='media'),
    path('scripts', views.scripts, name='scripts'),
    path('error', views.error, name='error'),

    path('protohook', views.prototype_hook_data, name='protohook'),
    path('poll', views.poll_data, name='poll'),
    path('sel', views.sel, name='sel')
]
