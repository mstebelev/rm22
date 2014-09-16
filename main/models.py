#-*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime, date
from django.http import HttpResponse
import sys
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string

class Parallel(models.Model):
    name = models.CharField(max_length=256)
    def __unicode__(self):
        return self.name

class Competition(models.Model):
    name = models.CharField(max_length=256)
    state = models.IntegerField('статус мероприятия',
        choices=(
            (0, 'в планировании'),
            (1, 'регистрация начата'),
            (2, 'регистрация завершена'),
            (3, 'проведено'),
            (4, 'объявлены результаты')
        )
    )
#    class_2 = models.BooleanField("Включить 2 класс", default=True)
#    class_3 = models.BooleanField("Включить 3 класс", default=True)
#    class_4 = models.BooleanField("Включить 4 класс", default=True)
#    class_5 = models.BooleanField("Включить 5 класс", default=True)
#    class_6 = models.BooleanField("Включить 6 класс", default=True)
#    class_7 = models.BooleanField("Включить 7 класс", default=True)
#    class_8 = models.BooleanField("Включить 8 класс", default=True)
#    class_9 = models.BooleanField("Включить 9 класс", default=True)
#    class_10 = models.BooleanField("Включить 10 класс", default=True)
#    class_11 = models.BooleanField("Включить 11 класс", default=True)
    registration_start_time = models.DateField('дата начала подачи заявок')
    registration_finish_time = models.DateField('дата окончания подачи заявок')
    event_time = models.DateField('дата проведения')
    org_mail = models.EmailField('почта организатора')
    cost = models.IntegerField('стоимость участия одного участника в рублях')
    imagelink = models.CharField( 'относительный путь к эмблеме',max_length=100, blank=True)
    available_for = models.ManyToManyField(Group)
    def __unicode__(self):
        return self.name

class CompetitionForParallel(models.Model):
    competition = models.ForeignKey(Competition)
    parallel = models.ForeignKey(Parallel)
    cost = models.IntegerField('стоимость')
    class Meta:
        unique_together = (('competition','parallel'),)
    def __unicode__(self):
        return u'%s для %s' % (self.competition, self.parallel)



class School(models.Model):
    user = models.OneToOneField(User)
    code = models.IntegerField()
    name = models.CharField('Название школы', max_length=1024)
    region = models.CharField('район', max_length=1024)
    settlement = models.CharField('населенный пункт', max_length=1024)
    postcode = models.IntegerField('почтовый индекс')
    postadress = models.CharField('почтовый адрес', max_length=1024)
    director_name = models.CharField('ФИО директора',max_length=1024)
    phone = models.CharField('телефон', max_length=16)
    mail = models.EmailField('e-mail школы')
    def __unicode__(self):
        return self.name

class Order(models.Model):
    school = models.ForeignKey('School')
    competition = models.ForeignKey('Competition')
    org_name = models.CharField("ФИО организатора", max_length=1024)
    org_phone = models.CharField("Телефон организатора", max_length=16)
    org_mail = models.EmailField("Адрес электронной почты")
#    count_2 = models.IntegerField("Количество участников 2 класса", blank=True,
#                                 default=0)
#    count_3 = models.IntegerField("Количество участников 3 класса", blank=True,
#                                 default=0)
#    count_4 = models.IntegerField("Количество участников 4 класса", blank=True,
#                                 default=0)
#    count_5 = models.IntegerField("Количество участников 5 класса", blank=True,
#                                 default=0)
#    count_6 = models.IntegerField("Количество участников 6 класса", blank=True,
#                                 default=0)
#    count_7 = models.IntegerField("Количество участников 7 класса", blank=True,
#                                 default=0)
#    count_8 = models.IntegerField("Количество участников 8 класса", blank=True,
#                                 default=0)
#    count_9 = models.IntegerField("Количество участников 9 класса", blank=True,
#                                 default=0)
#    count_10 = models.IntegerField("Количество участников 10 класса", blank=True,
#                                 default=0)
#    count_11 = models.IntegerField("Количество участников 11 класса", blank=True,
#                                 default=0)
    instr = models.IntegerField("Количество инструкций", blank=True)
    status = models.IntegerField("статус заявки",
        choices=(
            (0, 'отправлена'),
            (1, 'в обработке'),
            (2, 'готово'),
        ),
        default=0,
    )

    status_updatetime = models.DateTimeField('время изменения статуса заявки',
                                             editable=False,
                                             default=datetime.now)

    blank_status = models.IntegerField("статус бланков",
        choices=(
            (0, 'отсутствуют'),
            (1, 'получены'),
            (2, 'отправлены в центр'),
        ),
        default=0,
    )

    blank_status_updatetime = models.DateTimeField('время изменения статуса бланков',
                                             editable=False,
                                             default=datetime.now)

    create_time = models.DateTimeField('время подачи заявки',
                                             editable=False,
                                             default=datetime.now)

    delivery = models.IntegerField("способ доставки",
        choices = (
            (1, "почтой"),
            (2, "самовывоз"),
            (3, "доставка оргкомитетом (доступно, если количество участников не менее 250)")
        ),
        blank=True,
    )

    result_delivery = models.IntegerField("способ доставки результатов",
        choices = (
            (1, "почтой"),
            (2, "самовывоз"),
            (3, "выслать в комитет по образованию")
        ),
    )

    payer = models.CharField('Сведения об оплате(ФИО плательщика, сумма)',max_length=1024, blank=True)
    payment_date = models.DateField('Дата оплаты', blank=True)


    def __unicode__(self):
        return u'%s от школы %s' % (self.competition.name, self.school.name )

    def __init__(self, *args, **kwargs):
       super(Order, self).__init__(*args, **kwargs)
       self.old_status = self.status
       self.old_blank_status = self.blank_status

    def save(self, *args, **kwargs):
        is_old = self.pk
        rv = super(Order, self).save(*args, **kwargs)
        if is_old:
            if self.old_status != self.status:
                self.status_updatetime = datetime.now()

                if self.status == 1:
                    message = u'Заявка на конкурс %s получена оргкомитетом' % self.competition.name
                    template_name = 'in_process_message.mail'
                elif self.status == 2:
                    message = u'Статус заявки на конкурс %s изменен' % self.competition.name
                    template_name = 'order_ready_message.mail'
                else:
                    message = None

                if message:
                    now = date.today()
                    print >>sys.stderr, 'message from %s to %s about order %s sending' % ('pm', [self.org_mail, self.school.mail], self)
                    send_mail(message,
                              render_to_string(template_name, {'order': self, 'now': now}),
                          'notifier@rm22.ru',
                          [self.org_mail, self.school.mail])

            if self.old_blank_status != self.blank_status:
                self.blank_status_updatetime = datetime.now()
                if self.old_blank_status == 0 and self.blank_status == 1:
                    message = 'Бланки с ответами получены оргкомитетом'
                    send_mail(message,
                          render_to_string('blanks_received.mail', {'order': self}),
                          'notifier@rm22.ru',
                          [self.org_mail, self.school.mail])

        return rv




class OrderParallel(models.Model):
    order = models.ForeignKey(Order)
    parallel = models.ForeignKey(Parallel)
    count = models.IntegerField('count')
    class Meta:
        unique_together = (('parallel','order'),)

#class OrderEvent(models.Model):
#    order = models.ForeignKey('Order')
#    event_type = models.IntegerField('тип события',
#        choices=(
#            (0, 'Заявка создана'),
#            (1, ''),
#            (2, '')
#        )
#    )
#
class News(models.Model):
    header = models.TextField()
    text = models.TextField()
    post_time = models.DateTimeField(default=datetime.now, editable=False)


# Create your models here.
