# coding: utf-8

from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class StandardSections(models.Model):
#  '''
#  стандартные разделы сайта для динамической генерации паттернов в urls
##  и 
#  - публикация (обычный html без форм)
#  - публикация с каментами (обычный html + форма для добавления каментов+ список каментов)
#  - список публикаций (Уник. заголовок (в нём ссылка на публикацию), дата, автор )
#  - список новостей (каждая новость открывается как публикация)
#  '''
  TYPE_CHOICES = (
    ('P', 'Публикация без каментов'),
    ('PC', 'Публикация с каментами'),
    ('LP', 'Список публикаций'),
    ('LN', 'Список новостей’',
    ('NULL', 'Нестандартный раздел'),
  )
  
  #YN_CHOICES = (
  #('Y', 'Да'), ('N', 'Нет'),
  #)
  
  #user_grp =  models.ForeignKey(Group, verbose_name='123', null=True, blank=True) 
  #parent_item = models.ForeignKey('self', verbose_name='Родительский пункт', null=True, blank=True) #иерархия для пунктов меню! используется для отображения 
  #type = models.CharField(max_length=4, choices=TYPE_CHOICES, verbose_name='Тип раздела') #список значений типов стандарных разделов 
  #name = models.CharField(max_length=50, verbose_name='Название пункта (для меню)', null=True, blank=True) #название раздела
  #description = models.CharField(max_length=240, null=True, blank=True, verbose_name='Подсказка') # текст подсказки для раздела
  #re_url = models.CharField(max_length=240, verbose_name='url') # рег. выражение  для урла
  #обработчик
  #is_menu_item = models.CharField(max_length=1, verbose_name='Да - пункт меню, Нет-нет') # является ли данная строка пунктом главного меню
  #order = models.IntegerField(verbose_name='Порядковый номер раздела', default='Y')# порядок отображения для пунктов меню, число
  