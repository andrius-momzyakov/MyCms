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
  code = models.CharField(max_length=20, verbose_name='Код раздела')
  name = models.CharField(max_length=50, verbose_name='Название пункта/ссылки', null=True, blank=True)
  description = models.CharField(max_length=240, null=True, blank=True, verbose_name='Описание')
  #re_url = models.CharField(max_length=240, verbose_name='url')
  is_menu_item = models.CharField(max_length=1, choices=YN_CHOICES, verbose_name='Да-пункт меню, Нет-ссылка')
  order = models.IntegerField(verbose_name='Порядковый номер', null=True, blank=True)
  is_active = models.CharField(max_length=1, choices=YN_CHOICES, verbose_name='Да-активный, Нет-выкл.')

  def __unicode__(self):
     return str(self.id) + '_' + self.code + '_' + self.name
	 
  def get_id(self):
    return int(self.id)
  
  class Meta:
    unique_together = (('code',), ('name', ),)
  
class BasePage(models.Model):
  '''
  базовый класс для всех типов страниц
  '''
  section = models.OneToOneField(StandardSection, verbose_name='Раздел сайта', unique=True)
  description = models.CharField(max_length=4000, verbose_name='Определение типа странички')
  title = models.CharField(max_length=500, verbose_name='Заголовок страницы', null=True, \
                          blank=True) # для использования в соотв. тэге или индексе
  pub_date = models.DateField(verbose_name='Дата публикации', default=datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')))
  close_date = models.DateField(verbose_name='Дата закрытия публикации', null=True, blank=True)
  template = models.ForeignKey('Template', verbose_name='Шаблон', null=True, blank=True)

  def __unicode__(self):
    return self.section.code + '_' + self.description[:50] # по умолчанию! опционально переопределяется для потомкоф
    
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

  def get_html(self, request=None): # вкручивает страницу в базовый шаблон, не переопределяется
    content = t.Template(self.template.body).render(t.Context({'content':self.html})) #self.html #self.get_content(self, request)
    return self.template.get_rendered_html(request, content)

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
  
  def get_html(self, request):
    #содержимое данной странички - список записей блогу
    blog_entry_list = BlogEntry.objects.filter(blog=self).order_by('-pub_date')
    # содержимое - список с пагинатором
    # "страница" пагинатора
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(blog_entry_list, 10)
    if not page_number:
        page_number = request.GET.get('page')
    try:
        blog_entries = paginator.page(page_number)
    except PageNotAnInteger:
        blog_entries = paginator.page(1)
    except EmptyPage:
        blog_entries = paginator.page(paginator.num_pages)
    content = t.Template(self.template.body).render(t.Context({'blog_entries':blog_entries}))
    return self.template.get_rendered_html(request, content)
  
class BlogEntry(StandardPage):
    '''
    Запись блога
    --is_open - Y - опубликована, N - не опубликована
    --is_active - Y - активная (в основном списке), N - архивная (список архивных записей) - ПОТОМ
    --
    '''
    #standard_page = models.OneToOneField(StandardPage, verbose_name='Родитель', related_name='blog_entry')
    blog = models.ForeignKey(BlogPage, verbose_name='Опубликовать в', null=True, blank=True)

    def __unicode__(self):
        return self.blog.section.code + '_' + self.blog_title + '_' + self.title
    
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
  
  def get_rendered_html(self, request, content):
	#контекст базового шаблона
    menu_items = StandardSection.objects.filter(is_menu_item='Y', is_active='Y').order_by('order')
    base_items = {'menu_items':menu_items, 'content':content, 'STATIC_URL':settings.STATIC_URL}
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
  
  
  
  

  
  
  
  
  
  
  