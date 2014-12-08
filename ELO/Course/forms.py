#coding: utf-8

from django import forms
from ELO.BaseUnit import Id

import ELO.locale.index as lang

class LessonForm(forms.Form):
    lesson_id = forms.IntegerField(required=True)

    def clean_lesson_id(self):
        return Id(self.cleaned_data['lesson_id'])
