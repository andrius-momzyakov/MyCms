# coding:utf-8

import django.utils.timezone
from django.utils import timezone
import datetime
from django.utils.timezone import utc
import pytz
from django.db import models
from django.contrib.auth.models import User, Group
import django.template as t
from django.core.context_processors import csrf
from django.template import RequestContext
from django.forms import ModelForm, Textarea, HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect

import mycms.settings as settings

YN_CHOICES = (
('Y', 'Да'), ('N', 'Нет'),
)

TZ = tuple([tuple([tz, tz]) for tz in pytz.common_timezones])

class StandardSection(models.Model):
  '''
  Раздел сайта
  '''
  
  user_grp =  models.ForeignKey(Group, verbose_name='Группа пользователей', null=True, blank=True)
  parent_item = models.ForeignKey('self', verbose_name='Родительский пункт меню', null=True, blank=True)
  code = models.CharField(max_length=100, verbose_name='Код раздела')
  name = models.CharField(max_length=100, verbose_name='Название пункта/ссылки', null=True, blank=True)
  description = models.CharField(max_length=240, null=True, blank=True, verbose_name='Описание')
  #re_url = models.CharField(max_length=240, verbose_name='url')
  is_menu_item = models.CharField(max_length=1, choices=YN_CHOICES, verbose_name='Да-пункт меню, Нет-ссылка')
  order = models.IntegerField(verbose_name='Порядковый номер', null=True, blank=True)
  is_active = models.CharField(max_length=1, choices=YN_CHOICES, verbose_name='Да-активный, Нет-выкл.')
  
  def get_params(self):
    try:
        page = BasePage.objects.filter(section=self, close_date__isnull=True).latest()
        return page.get_params
    except:
        return ''
    
  def __unicode__(self):
     return str(self.id) + '_' + self.code + '_' + self.name
	 
  def get_id(self):
    return int(self.id)
  
  class Meta:
    unique_together = (('code',), ('name', ),)
  
class BasePage(models.Model):
  '''
  базовый класс для всех типов страниц
  
  написать про Exception Type:	TypeError
  Exception Value:	
  get_content() takes exactly 2 arguments (3 given)
  '''
  section = models.ForeignKey(StandardSection, verbose_name='Раздел сайта')
  #description = models.CharField(max_length=4000, verbose_name='Определение типа странички')
  title = models.CharField(max_length=500, verbose_name='Заголовок страницы', null=True, \
                          blank=True) # для использования в соотв. тэге или индексе
  pub_date = models.DateTimeField(verbose_name='Дата публикации', default=datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')))
  close_date = models.DateTimeField(verbose_name='Дата закрытия публикации', null=True, blank=True)
  template = models.ForeignKey('Template', verbose_name='Шаблон', null=True, blank=True)
  #mob_template = models.ForeignKey('Template', verbose_name='Шаблон для моб. устройств', null=True, blank=True, related_name='mob_template')
  get_params = models.CharField(max_length=500, verbose_name='GET-параметры', null=True, blank=True)

  #def get_content(self, request): #, *args, **kwargs):
  def get_content(self, request, *args, **kwargs):
    return None
  
  def get_html(self, request=None, *args, **kwargs): # вкручивает страницу в базовый шаблон, не переопределяется
    content = self.get_content(request) #t.Template(self.template.body).render(t.Context({'content':self.html})) #self.html #self.get_content(self, request)
    if request.method=='POST':
        return HttpResponseRedirect('/content/' + self.section.code + '/' + self.get_params)
    return HttpResponse(self.template.get_rendered_html(request, content))

  def __unicode__(self):
    return self.section.code + '_' + self.title # по умолчанию! опционально переопределяется для потомкоф
    
#  def save():
    # сделать проверку, что одному Base соответствует ровно один child ровно одного класса!!!
#    pass
    
  class Meta:
    get_latest_by = 'pub_date'
  
class StandardPage(BasePage):
  '''
  Стандартная страница html
  представляет собой редакцию страницы
  '''
  html = models.TextField(verbose_name='Код HTML')
  #base_page = models.OneToOneField(BasePage, verbose_name='Родитель', related_name='standard_page')

  def get_content(self, request, *args, **kwargs):
    return t.Template(self.template.body).render(t.Context({'content':self.html}))

class BlogPage(BasePage):
  '''
  Страничка Блога для Босса:
  1. Список записей (BlogEntry):
    - Заголовок
    - Дата публикации
    - Кол-во каментов (одобренных боссом к показу)
    
  2. Форма каментов Обычная, для незарег. пользователей
  
  3. Камент при добавлении невидим, видим только после соотв. отметки босса
    
  4. Добавление: BlogEntry доб-ся и изменяется через админку
  '''
  #base_page = models.OneToOneField(BasePage, verbose_name='Родитель', related_name='blog_page')
  
  def get_content(self, request, *args, **kwargs):
    #содержимое данной странички - список записей блогу
    blog_entry_list = BlogEntry.objects.filter(blog=self).order_by('-pub_date')
    # содержимое - список с пагинатором
    # "страница" пагинатора
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(blog_entry_list, 10)
    #if request.method=='GET':
    #    return HttpResponse('GET!')
    #return HttpResponse('нету!')
    if request.GET.get('page'):
      page_number = request.GET.get('page')
    else:
      page_number = 1
    try:
        blog_entries = paginator.page(page_number)
    except PageNotAnInteger:
        blog_entries = paginator.page(1)
    except EmptyPage:
        blog_entries = paginator.page(paginator.num_pages)
    return t.Template(self.template.body).render(t.Context({'blog_entries':blog_entries}))
 
class BlogEntry(StandardPage):
    '''
    Запись блога
    --is_open - Y - опубликована, N - не опубликована
    --is_active - Y - активная (в основном списке), N - архивная (список архивных записей) - ПОТОМ
    --
    '''
    #standard_page = models.OneToOneField(StandardPage, verbose_name='Родитель', related_name='blog_entry')
    blog = models.ForeignKey(BlogPage, verbose_name='Опубликовать в', null=True, blank=True)
    comment_allowed = models.CharField(max_length=1, verbose_name='Разрешить комментарии', choices=YN_CHOICES)

    def get_content(self, request, *args, **kwargs):
        show_form = False
        if request.method=='POST':
            comment_form = BlogCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.blog_entry = self
                comment.save()
                #отправляем почту
                #from django.core import mail
                #mail.mail_admins(u'Комментарий на ' + comment.blog_entry.section.code, \
                #                u'Отправил: ' + comment.name + ' ' + str(comment.creation_time) + '\n' \
                #                u'Текст комментария: ' + comment.text + ' ' + u'Связь: ' + comment.email)
                from django.core.mail import send_mail
                send_mail(u'Комментарий на ' + comment.blog_entry.section.code, 
                                    u'Отправил: ' + comment.name + ' ' + str(comment.creation_time) + '\n' +  u'Текст комментария: ' + comment.text + ' ' + u'Связь: ' + comment.email,
                                   settings.ADMINS[0][1], [settings.ADMINS[0][1]], fail_silently=False)
                show_form = False
                #return redirect('/content/' + self.section.code + '/?show_form=no')
        else:
            if request.GET.get('show_form')=='yes':
                show_form = True
            else:
                show_form = False
        if show_form:
            comment_form = BlogCommentForm()
        else:
            comment_link = '/content/' + self.section.code + '/?show_form=yes'
        try:
            comments = BlogEntryComment.objects.filter(blog_entry=self).order_by('creation_time')
        except:
            comments = tuple([])
        context = {}
        context.update(csrf(request))
        context_instance = RequestContext(request, context)	   
        if show_form:
            context_instance.update({'content':self.html, 'title':self.title, 
                                                    'comments':comments, 
                                                    'comment_form':comment_form,
                                                    'blog_entry':self})
        else:
            context_instance.update({'content':self.html, 'title':self.title, 
                                                    'comments':comments, 'comment_link':comment_link, #'comment_form':comment_form,
                                                    'blog_entry':self})
        return t.Template(self.template.body).render(t.Context(context_instance))
    
    def __unicode__(self):
        if self.blog:
            return self.blog.section.code + '_' + self.title
        return self.title
        
    def get_count(self):
        return BlogEntryComment.objects.filter(blog_entry=self).count()
   
class BlogEntryComment(models.Model):
  '''
  Комментарии к записям блога
  и к др. комментариям
  '''
  blog_entry = models.ForeignKey(BlogEntry, verbose_name='К записи')
  creation_time = models.DateTimeField(verbose_name='Дата создания:', default=datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')))
  name = models.CharField(max_length=100, verbose_name='Ваше имя:')
  email = models.CharField(max_length=100, verbose_name='Ваш e-mail:', null=True, blank=True)
  #comment = models.ForeignKey('self', verbose_name='Ответ на', null=True, blank=True)
  text = models.CharField(max_length=4000, verbose_name='Комментарий:')

from recaptcha.field import ReCaptchaField

class BlogCommentForm(ModelForm):
    captcha = ReCaptchaField(error_messages = {  
          'required': u'Это поле должно быть заполнено',            
          'invalid' : u'Указанное значение было неверно'  
          },label='Введите код с картинки:')
    class Meta:
        model = BlogEntryComment
        fields = ('name', 'email', 'text')
        widgets = {
                   'text': Textarea(),
                  }

class UserProfile(models.Model):
  user = models.OneToOneField(User, verbose_name='Аккаунт')
  last_visited_url=models.CharField(max_length=240, null=True, blank=True, verbose_name='Последний открытый URL')
  default_tz = models.CharField(max_length=100, choices=TZ, verbose_name='Часовой пояс', default='Europe/Moscow') 
  
  def __unicode__(self):
    return self.user.username + '_profile'
  
class Template(models.Model):
  '''
  Шаблон html
  '''
  code = models.CharField(max_length=20, verbose_name='Код шаблона', unique=True)
  description = models.TextField(verbose_name='Комментарий', null=True, blank=True)
  body = models.TextField(verbose_name='Код шаблона', null=True, blank=True)
  base = models.ForeignKey('self', null=True, blank=True, verbose_name='Базовый шаблон')
  
  def get_rendered_html(self, request, content, get_params=None):
	#контекст базового шаблона
    menu_items = StandardSection.objects.filter(is_menu_item='Y', is_active='Y').order_by('order')
    base_items = {'menu_items':menu_items, 'content':content, 'STATIC_URL':settings.STATIC_URL, 'curr_date':datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))}
    context_instance = None
    if request:
        context = {}
        context.update(csrf(request))
        context_instance = RequestContext(request, context)	   
        context_instance.update(base_items)
    else:
        base_context = t.Context(base_items)
    if self.base:
        if context_instance:
            return t.Template(self.base.body).render(context_instance)
        else:
            return t.Template(self.template.base.body).render(base_context)
    return content

  def __unicode__(self):
    return self.code + '_' + self.description 
    
class RequestLog(models.Model):
    path = models.CharField(max_length=2000, null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    referer = models.CharField(max_length=2000, null=True, blank=True)
    user = models.CharField(max_length=100, null=True, blank=True)
    ip = models.CharField(max_length=100, null=True, blank=True)
    
    def __init__(self, *args, **kwargs):
        request = args[0]
        super(RequestLog, self).__init__(*args, **kwargs)
        self.path = request.get_full_path()
        self.method = request.method
        self.referer = request.META['HTTP_REFERER']
        try:
            self.user = request.META['REMOTE_USER']
        except:
            try:
                self.user = request.META['USERNAME']
            except:
                None
        self.ip = request.META['REMOTE_ADDR']
     
    def __unicode__(self):
        return self.path
        
  
#class StaticFile(models.Model):
#    section = models.ForeignKey(StandardSection, verbose_name='К разделу:')
#    file = models.FileField(upload_to='static_files')
  
  

  
  
  
  
  
  
  