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
  TYPE_CHOICES = (
  ('P', 'Обычный HTML'),
  )
  
  user_grp =  models.ForeignKey(Group, verbose_name='Группа пользователей', null=True, blank=True)
  parent_item = models.ForeignKey('self', verbose_name='Родительский пункт меню', null=True, blank=True)
  type = models.CharField(max_length=4, choices=TYPE_CHOICES, verbose_name='Тип шаблона')
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
  
class StandardPage(models.Model):
  '''
  Стандартная страница html
  представляет собой редакцию страницы
  '''
  section = models.OneToOneField(StandardSection, verbose_name='Раздел сайта')
  html = models.TextField(verbose_name='Код HTML')
  is_current = models.CharField(max_length=1, verbose_name='Y-текущая редакция, N-архивная')
  open_date = models.DateField()
  close_date = models.DateField(null=True, blank=True)
  template = models.ForeignKey('Template', null=True, blank=True)
  
  def get_html(self, request=None):
    # контекст данной странички
    #context = t.Context({'content':self.html})
    
	#содержимое данной странички
    content = self.html
    
	#контекст базового шаблона
    menu_items = StandardSection.objects.filter(is_menu_item='Y', is_active='Y').order_by('order')
    base_items = {'menu_items':menu_items, 'content':t.Template(self.template.body).render(t.Context({'content':self.html})), 'STATIC_URL':settings.STATIC_URL}
    context_instance = None
    if request:
        context = {}
        context.update(csrf(request))
        context_instance = RequestContext(request, context)	   
        context_instance.update(base_items)
    else:
        # если тек страница имеет контекст, то добавляем его в base_context типа: base_items.update(content_items)
        # контекст базового шаблона, включающий всё
        base_context = t.Context(base_items)
    if self.template.base:
        if context_instance:
            return t.Template(self.template.base.body).render(context_instance)
        else:
            return t.Template(self.template.base.body).render(base_context)
    return content
    
  def __unicode__(self):
    return self.section.code
	
  class Meta:
    unique_together = (('section'),)
    
class UserProfile(models.Model):
  user = models.OneToOneField(User, verbose_name='Аккаунт')
  last_visited_url=models.CharField(max_length=240, null=True, blank=True, verbose_name='Последний открытый URL')
  default_tz = models.CharField(max_length=100, choices=TZ, verbose_name='Часовой пояс', default='Europe/Moscow') 
  
  def __unicode__(self):
    return user.username + '_profile'
  
class Template(models.Model):
  '''
  Шаблон html
  '''
  code = models.CharField(max_length=20, verbose_name='Код шаблона', unique=True)
  description = models.TextField(verbose_name='Комментарий', null=True, blank=True)
  body = models.TextField(verbose_name='Код шаблона', null=True, blank=True)
  base = models.ForeignKey('self', null=True, blank=True, verbose_name='Базовый шаблон')
  
  def __unicode__(self):
    return self.code + '_' + self.description 
  
  
  
  

  
  
  
  
  
  
  