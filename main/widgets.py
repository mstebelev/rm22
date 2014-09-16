# -*- coding: utf-8 -*-
import settings
from django import forms
class CalendarWidget(forms.widgets.DateInput):
    class Media:
        js = ('/static/admin/jsi18n/',
                settings.ADMIN_MEDIA_PREFIX + 'js/core.js',
                settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
               settings.ADMIN_MEDIA_PREFIX + "js/admin/DateTimeShortcuts.js"
        )
        css = {
            'all': (
                 #settings.ADMIN_MEDIA_PREFIX + 'css/forms.css',
                 #settings.ADMIN_MEDIA_PREFIX + 'css/base.css',
                 settings.ADMIN_MEDIA_PREFIX + 'css/widgets.css',)
        }
    def __init__(self, attrs={}):
        super(CalendarWidget, self).__init__(
            attrs={'class': 'vDateField', 'size': '10'})
#    def render(self, name, value, attrs=None):
 #       return super(CalendarWidget, self).render(name, value.strftime('%d.%m.%Y'), attrs)
