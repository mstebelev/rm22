#-*- coding:utf8 -*-
# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from models import News, Competition, School, Order
from forms import OrderForm, SchoolForm, CompetitionForParallel, OrderParallel
from django.template import RequestContext
from datetime import datetime
from operator import attrgetter
from django.http import Http404
from settings import RESULTS_PATH
import os.path
from django.http import HttpResponse
from glob import glob

def main_page(request):
    latest_news = sorted(News.objects.all(), key=attrgetter('post_time'), reverse=True)[:10]
    all_competitions = ', '.join(['"%s"' % c.name for c in Competition.objects.all()])
    school = None
    if request.user.is_authenticated():
        school = School.objects.get(user=request.user)
    return render_to_response('index.html',{
            'news_list': latest_news,
            'all_competitions': all_competitions,
            'school': school,
    })

def get_results(request, compete_id):
    response = HttpResponse(mimetype="application/pdf")
    school = get_object_or_404(School, user=request.user)
    competition = get_object_or_404(Competition, pk=compete_id)
    res_files = glob(os.path.join(RESULTS_PATH, str(compete_id), '%08d.*' % school.code))
    if not res_files:
        raise Http404('no results')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(res_files[0])
    try:
        with open(res_files[0]) as res_file:
            response.write(res_file.read())
    except IOError, e:
        raise Http404('no results')
    return response

def logout_view(request):
    logout(request)
    return redirect(main_page)

@login_required
def view_order(request, compete_id=1):
    if compete_id is None:
        compete_id = 1
    school = get_object_or_404(School, user=request.user)
    competition = get_object_or_404(Competition, pk=compete_id)
    groups = set(request.user.groups.all())
    available_competitions = [c for c in Competition.objects.all()
                              if any(g in groups for g in c.available_for.all())]

    parallels_for_competition = CompetitionForParallel.objects.filter(competition=competition)
    parallels_for_competition_dict = dict((pc.parallel, pc) for pc in parallels_for_competition)
    if competition not in available_competitions:
        raise Http404('this competition is unavalilable for you')
    if competition.state == 4:
        return render_to_response('cabinet_order.html', {
            'school': school,
            'competitions':  available_competitions,
            'selected_competition': competition,
            'form': None,
            'message': '',
            'parallels': parallels_for_competition,
        }, context_instance=RequestContext(request))
    else:
        message = ''
        messagestatus = 1
        is_new = True
        order_status = 'не подана'
        blank_status = ''
        try:
            current_order = Order.objects.get(school=school, competition=competition)
            order_status = current_order.get_status_display()
            if competition.state == 3:
                blank_status = current_order.get_blank_status_display()
            is_new = False
        except Order.DoesNotExist:
            current_order = Order()
            current_order.create_time = datetime.now()
            current_order.competition = competition
            current_order.school = school

        if request.method == 'POST':
            form = OrderForm(dict(request.POST.items()), instance=current_order)
            if form.is_valid():
                message = ('Заявка поступила на рассмотрение'
                           if is_new else
                           'Заявка изменена')
                form.save()
            else:
                message='Неправильно указаны поля'
                messagestatus = 0
                if is_new:
                    current_order = None
            #form = OrderForm(instance=current_order)
            #form.errors = src_form.errors
        else:
            form = OrderForm(instance=current_order)
            if is_new:
               current_order = None
        total = 0
        total_cost = 0
        if current_order:
            order_parallels = OrderParallel.objects.filter(order=current_order)
            total = sum(op.count for op in order_parallels)
            total_cost = sum(op.count * parallels_for_competition_dict[op.parallel].cost for op in order_parallels if op.parallel in parallels_for_competition_dict)

        return render_to_response('cabinet_order.html', {
            'total': total,
            'parallels': parallels_for_competition,
            'total_cost': total_cost,
            'competitions':  available_competitions,
            'selected_competition': competition,
            'form': form,
            'message': message,
            'messagestatus': messagestatus,
            'order': current_order,
            'school': school,
        }, context_instance=RequestContext(request))

@login_required
def view_school(request, message=''):
    school = get_object_or_404(School, user=request.user)
    messagestatus=1
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            message = 'Информация изменена'
        else:
            message='Указаны неправильные данные'
            messagestatus=0
    else:
        form = SchoolForm(instance=school)
    groups = set(request.user.groups.all())
    available_competitions = [c for c in Competition.objects.all()
                              if any(g in groups for g in c.available_for.all())]
    return render_to_response('cabinet_school.html', {
        'competitions':  available_competitions,
        'school': school,
        'form': form,
        'message': message,
        'messagestatus': messagestatus,
        'school': school,
    }, context_instance=RequestContext(request))

