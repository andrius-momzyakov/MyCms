#coding:utf-8

import django.forms as forms
import models as m
from recaptcha.field import ReCaptchaField
import mycms.settings as settings

class StaticFileUpload(forms.Form):
    """
    Простая форма для загрузки файлов статического контента (картинки, жаба-скрипты и проч.)
    """
    section = forms.ModelChoiceField(label=u'Раздел', queryset=m.StandardSection.objects.all(), required=False)
    file = forms.FileField(label=u'Выбрать файл:')
    
