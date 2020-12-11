#-*- coding:utf8 -*-
from django.contrib import admin
from django.http import HttpResponse, Http404
from django.core import serializers
from models import School,Competition,Order,News, Parallel, CompetitionForParallel, OrderParallel
from django.core.urlresolvers import reverse
from django.template.defaultfilters import escape

def mark_as_in_progress(modeladmin, request, queryset):
    for order in queryset:
        order.status=1
        order.save()
    return get_orders_csv(modeladmin, request, queryset)
mark_as_in_progress.short_description = u'отправить в обработку и выгузить в CSV'
import sys
def get_orders_csv(modeladmin, request, queryset):
    competitions = set()
    for order in queryset:
        competitions.add(order.competition)
    if len(competitions) > 1:
        raise Http404(u'orders of multiple competitions chosen')
    competition = list(competitions)[0]
    data = serializers.serialize("python", queryset)
    fields = sorted(data[0]['fields'].keys())
    #print >>sys.stderr, data
    parallels = CompetitionForParallel.objects.filter(competition=competition)
    response = HttpResponse(mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=orders.csv'
    response.write(';'.join(fields))
    response.write(';')
    response.write(';'.join(unicode(op.parallel).encode('utf-8') for op in parallels))
    response.write('\n')
    for order,serial_order in zip(queryset, data):
        response.write(';'.join(getattr(order, 'get_' + field + '_display')().encode('utf-8') if hasattr(order, 'get_' + field + '_display') else unicode(serial_order['fields'][field]).encode('utf-8') for field in fields))
        order_parallels = dict((o.parallel, o) for o in OrderParallel.objects.filter(order=order))
        response.write(';')
        response.write(';'.join(str(order_parallels[p.parallel].count) if p.parallel in order_parallels else '0' for p in parallels))
        response.write('\n')
    #serializers.serialize("csv", queryset, fields=('org_name', 'sum_all'), stream=response)
    return response
get_orders_csv.short_description = u'выгузить в CSV'

def mark_as_ready(modeladmin, request, queryset):
    for order in queryset:
        order.status=2
        order.save()
mark_as_ready.short_description = u'поставить статус "готово"'

def mark_as_blanks_ready(modeladmin, request, queryset):
    queryset.update(blank_status=1)
mark_as_blanks_ready.short_description = u'поставить статус "бланки получены"'

def mark_as_blanks_sent(modeladmin, request, queryset):
    queryset.update(blank_status=2)
mark_as_blanks_sent.short_description = u'поставить статус "бланки отправлены в центр. оргкомитет"'

class OrderParallelInline(admin.TabularInline):
    model = OrderParallel


class OrderAdmin(admin.ModelAdmin):
    change_form_template = 'change_order_admin.html'
    raw_id_fields = ('school',)
    def change_view(self, request, object_id, extra_context=None):
        properties = Order.objects.get(id=object_id).school.id
        extra_context = extra_context or {}
        extra_context['school_id'] = properties
        return super(OrderAdmin, self).change_view(request, object_id,
                                                   extra_context)

    list_display=('school', 'school_code', 'total_participants', 'competition','status','blank_status','status_updatetime',
                  'blank_status_updatetime', 'create_time')
    list_filter=('status','blank_status', 'competition', 'delivery', 'result_delivery')
    search_fields = ['school__code', 'school__name']
    #fields = (('school_edit', 'org_name', 'org_phone', 'org_mail',) +
    #          tuple('count_%d' % x for x in xrange(2,12)) + 
    #          ('blank_status', 'status', 'delivery', 'result_delivery', 'payer',
    #          'payment_date'))
    actions = [mark_as_in_progress, mark_as_ready, mark_as_blanks_ready,
               mark_as_blanks_sent, get_orders_csv]
    inlines = [OrderParallelInline]

    readonly_fields = ('total_participants',)

    def school_edit(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse("admin:main_school_change", args=(obj.school.id,)) ,
                                        escape(obj.school))
    school_edit.allow_tags = True
    school_edit.short_description = u'редактирование школы'

    def school_code(self, obj):
        return obj.school.code
    school_code.short_description = u'код школы'
    school_code.allow_tags = True
    school_code.admin_order_field = 'school__code'

    def total_participants(self, obj):
        return sum(op.count for op in OrderParallel.objects.filter(order=obj))
    total_participants.short_description = u'Количество участников'
    total_participants.allow_tags = True


def download(modeladmin, request, queryset):
    response = HttpResponse(mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=schools.csv'
    serializers.serialize("csv", queryset, stream=response)
    return response
download.short_description = u'Выгрузить выбранные школы в CSV'


class SchoolAdmin(admin.ModelAdmin):
    list_display=('name', 'code', 'region')
    search_fields = ['code', 'name', 'region']
    actions = [download]
    change_form_template = 'change_school_admin.html'

    def change_view(self, request, object_id, extra_context=None):
        school_code = School.objects.get(id=object_id).code
        extra_context = extra_context or {}
        extra_context['school_code'] = school_code
        return super(SchoolAdmin, self).change_view(request, object_id,
                                                   extra_context)

class CompetitionForParallelInline(admin.TabularInline):
    model = CompetitionForParallel


class CompetitionAdmin(admin.ModelAdmin):
    list_display=('id', 'name')
    inlines = [CompetitionForParallelInline]

admin.site.register(School, SchoolAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(News)
admin.site.register(Parallel)
