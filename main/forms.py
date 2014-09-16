#-*- coding:utf8 -*-
from django.forms import ModelForm
from models import Order,School, CompetitionForParallel, OrderParallel, Parallel
from django.core.exceptions import ValidationError
from operator import and_
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import TextInput
from widgets import CalendarWidget
import django.forms as forms
import sys
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude= ('school', 'competition', 'status', 'blank_status')
        widgets = {
            'payment_date': CalendarWidget(),
        }

    def __init__(self, *args, **kws):
        super(OrderForm, self).__init__(*args, **kws)
        instance = getattr(self, 'instance', None)
        parallels_for_competition = CompetitionForParallel.objects.filter(competition=instance.competition)
        for p in parallels_for_competition:
            try:
                order_parallel = OrderParallel.objects.get(order=instance,
                                                   parallel=p.parallel)
                initial = order_parallel.count
            except OrderParallel.DoesNotExist:
                initial = 0
            print >>sys.stderr, 'count for p', p.parallel.pk, initial
            self.fields['count_parallel_%d' % p.parallel.pk] = forms.IntegerField(label=u'Количество участников %sа' % p.parallel.name, initial=initial, required=instance.status == 0 if instance else True)
            if instance and instance.status > 0:
                self.fields['count_parallel_%d' % p.parallel.pk].widget.attrs['disabled'] = True
#        for x in xrange(2,12):
#            if not getattr(instance.competition, 'class_%d' % x):
#                del self.fields['count_%d' % x]
#            else:
#                if not self.instance.pk:
#                    self.initial['count_%d' % x] = None
        if instance and instance.status > 0:
            self.fields['instr'].widget.attrs['disabled'] = True
            self.fields['delivery'].widget.attrs['disabled'] = True

    def save(self, *args, **kws):
        kws['commit'] = False
        instance = super(OrderForm, self).save(*args, **kws)
        is_old = instance.pk
        instance.save()

        for parallel_for_competition in CompetitionForParallel.objects.filter(competition=instance.competition):
            count = self.cleaned_data.get('count_parallel_%d' %
                                          parallel_for_competition.parallel.pk, 0)
            if count is not None:
                try:
                    parallel_order = OrderParallel.objects.get(
                        parallel=parallel_for_competition.parallel,
                        order=instance)
                    parallel_order.count = count
                    parallel_order.save()
                except OrderParallel.DoesNotExist:
                    parallel_order = OrderParallel.objects.create(
                        parallel=parallel_for_competition.parallel,
                        order=instance,
                        count=count)

        subject, text, from_, to_ = (
                  u'Заявка на конкурс %s' % instance.competition.name,
                  render_to_string('order_create_message.mail', {
                      'order': instance,
                      'order_parallels': OrderParallel.objects.filter(order=instance),
                      'is_old': is_old,
                  }),
                  'notifier@rm22.ru',
                  [instance.org_mail, instance.school.mail, instance.competition.org_mail])
        print >>sys.stderr, 'message from %s to %s about order %s sending' % (from_, to_, instance)
        msg = EmailMessage(subject, text, from_, to_)
        msg.content_subtype='html'
        msg.send()

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        if (
            cleaned_data['delivery'] == 3
            and sum(cleaned_data.get('count_parallel_%d' % x.parallel.pk, 0)
                           for x in CompetitionForParallel.objects.filter(competition=self.instance.competition)
                           ) < 250
            ):
            raise ValidationError(u'количество участников должно быть не менее 250, если выбрана доставка оргкомитетом')
        return cleaned_data



#    def clean(self):
#        instance = getattr(self, 'instance', None)
#        for field in ['instr', 'delivery'] + ['count_%d' % x for x in
#                                            xrange(2,12)]:
#            #if not instance or instance.status == 0:
#            if instance and instance.status != 0:
#                self.cleaned_data[field] = getattr(self.instance, field)
#            else:
#                raise Va
#        return self.cleaned_data

import re
def get_cleaner(field):
    def func(self):
        instance = getattr(self, 'instance', None)
        if not instance or instance.status == 0:
            cleaned_data = self.cleaned_data
            if field not in self.cleaned_data or self.cleaned_data[field] is None or self.cleaned_data[field] == '':
                raise ValidationError(u'Обязательное поле')
            else:
                return cleaned_data[field]
        rv = getattr(self.instance, field)
        self.data[field] = rv
        return rv
    return func

for field in ['instr', 'delivery']: # + ['count_parallel_%d' % x.pk for x in Parallel.objects.all()]:
    setattr(OrderForm, 'clean_%s' % field, get_cleaner(field))






class SchoolForm(ModelForm):
    class Meta:
        model = School
        exclude= ('user', 'code')
