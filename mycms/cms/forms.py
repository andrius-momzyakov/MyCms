#coding:utf-8

import django.forms as forms
import models as m
from recaptcha.field import ReCaptchaField
import mycms.settings as settings
from django.utils.translation import ugettext_lazy as _

class StaticFileUpload(forms.Form):
    """
    Simple form for loading static content files for sections
    """
    section = forms.ModelChoiceField(label=_('Section:'), queryset=m.StandardSection.objects.all(), required=False)
    file = forms.FileField(label=_('File:'))
    
