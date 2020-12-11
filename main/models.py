#-*- coding:utf8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime, date
from django.http import HttpResponse
import sys
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.db.models.signals import pre_save

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

from django.core.validators import RegexValidator
class Order(models.Model):
    school = models.ForeignKey('School')
    competition = models.ForeignKey('Competition')
    org_name = models.CharField("ФИО организатора", max_length=1024)
    org_phone = models.CharField("Телефон организатора", max_length=16, validators=[RegexValidator(regex=r'\+\d{11}', message=u'Введите телефон в формате +71112223344')])
    org_mail = models.EmailField("Адрес электронной почты организатора")
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
    send_sms_to_org = models.BooleanField("отправлять уведомления о статусе заявки на телефон организатора", default=True)
    send_mail_to_org = models.BooleanField("отправлять уведомления о статусе заявки на электронную почту организатора", default=True)
    send_mail_to_school = models.BooleanField("отправлять уведомления о статусе заявки на электронную почту школы", default=True)

    payer = models.CharField('Сведения об оплате(ФИО плательщика, сумма)',max_length=1024, blank=True)
    payment_date = models.DateField('Дата оплаты', blank=True)


    def __unicode__(self):
        return u'%s от школы %s' % (self.competition.name, self.school.name )

    def __init__(self, *args, **kwargs):
       super(Order, self).__init__(*args, **kwargs)
       self.old_status = self.status
       self.old_blank_status = self.blank_status

    def notify_about_status(self, message, template_name, is_old, sms_template=None):
        addresses = [self.competition.org_mail]
        now = date.today()
        if self.send_mail_to_org:
            addresses.append(self.org_mail)
        if self.send_mail_to_school:
            addresses.append(self.school.mail)
        if addresses:
            print >>sys.stderr, 'Message from %s to %s about order %s sending' % ('pm', addresses, self)
            try:
                subject, text, from_, to_ = (
                    message,
                    render_to_string(template_name, {
                        'order': self,
                        'now': now,
                        'order_parallels': OrderParallel.objects.filter(order=self),
                        'is_old': is_old
                    }),
                    'notifier@rm22.ru',
                    addresses
                )
                msg = EmailMessage(subject, text, from_, to_)
                msg.content_subtype='html'
                msg.send()
            except Exception, e:
                print >>sys.stderr, e
                raise

        print >>sys.stderr, 'email sent'
        if self.send_sms_to_org:
            try:
                print >>sys.stderr, 'sending sms to %s' % (self.org_phone)
                import requests
                if sms_template:
                    sms = render_to_string(sms_template, {
                        'order': self,
                        'now': now,
                        'order_parallels': OrderParallel.objects.filter(order=self),
                        'is_old': is_old
                    })
                else:
                    sms = message
                ans = requests.post(url='https://web.mirsms.ru/public/http',params={'gzip': 'none', 'user': '32796.1', 'pass': '73906317', 'action': 'post_sms', 'message': sms, 'target': self.org_phone}, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
                print >>sys.stderr, ans
                print >>sys.stderr, ans.text
            except Exception, e:
                print >>sys.stderr, e


    def save(self, *args, **kwargs):
        is_old = self.pk
        rv = super(Order, self).save(*args, **kwargs)
        if is_old:
            if self.old_status != self.status:
                self.status_updatetime = datetime.now()

                if self.status == 1:
                    message = self.competition.name
                    template_name = 'in_process_message.mail'
                    sms_template = 'in_process_message.sms'
                elif self.status == 2:
                    message = self.competition.name
                    template_name = 'order_ready_message.mail'
                    sms_template = 'order_ready_message.sms'
                else:
                    message = None

                if message:
                    self.notify_about_status(message, template_name, True, sms_template=sms_template)

            if self.old_blank_status != self.blank_status:
                self.blank_status_updatetime = datetime.now()
                if self.old_blank_status == 0 and self.blank_status == 1:
                    message = self.competition.name
                    self.notify_about_status(message, 'blanks_received.mail', True, 'blanks_received.sms')

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


def notify_participants(sender, instance, signal, *args, **kwargs):
    if sender is Competition:
        old_obj = Competition.objects.get(pk=instance.pk)
        print >>sys.stderr, 'old state:', old_obj.state
        print >>sys.stderr, 'new state:', instance.state
        if old_obj.state != instance.state and instance.state == 4:
            orders = Order.objects.filter(competition=instance)
            for order in orders:
                order.notify_about_status(instance.name, "results_ready.mail", False, "results_ready.sms")

pre_save.connect(notify_participants, sender=Competition)
# Create your models here.
