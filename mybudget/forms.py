# -*- coding: utf-8 -*-
from django import forms
from django.utils import timezone
from .models import Baza_wydatkow, Typ_wydatku, Wydatek, Podtyp_wydatku
from functools import partial
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None, initial=None, help_text=None, *args, **kwargs):
        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label, initial=initial, help_text=help_text, *args, **kwargs)

class EnterForm(forms.ModelForm):
    alphanumeric = RegexValidator(r'^[0.-9.]*$', 'Wprowadz prawidłowa wartość')
    #typ = forms.ModelChoiceField(label='Typ wydatku (*)', queryset=Typ_wydatku.objects.all())
    cena = forms.CharField(label='Zaplacono', validators=[alphanumeric])
    komentarz = forms.CharField(label='Dodatkowy komentarz', required=False)
    class Meta:
        model = Wydatek
        fields = ('nazwa_wydatku','podtyp_wydatku','cena','komentarz')




class DetailForm(forms.ModelForm):
    empty_label = (('', '---------'),)
    type_list = Typ_wydatku.objects.values_list('nazwa_wydatku','nazwa_wydatku')
    # period_list = Baza_wydatkow.objects.values_list('okres', 'okres').distinct()
    
    typ = forms.CharField(label='Aktualny typ:', disabled = True)
    nowy_typ = EmptyChoiceField(label = 'Nowy typ wydatku', choices=type_list, required=False, empty_label=empty_label)
    
    cena = forms.CharField(label='Zaplacono: (*)')
    # okres = forms.CharField(label='Aktualny okres: ', disabled = True)
    # nowy_okres = EmptyChoiceField(label = 'Nowy okres', choices=period_list, required=False, empty_label=empty_label)
    komentarz = forms.CharField(label='Dodatkowy komentarz', required=False)
    class Meta:
        model = Baza_wydatkow
        fields = ('typ','nowy_typ','cena','komentarz')
'''
class DetailForm(forms.ModelForm):
    empty_label = (('', '---------'),)
    type_list = Typ_wydatku.objects.values_list('nazwa_wydatku','nazwa_wydatku')
    period_list = Baza_wydatkow.objects.values_list('okres', 'okres').distinct()
    
    typ = forms.CharField(label='Aktualny typ:', disabled = True)
    nowy_typ = EmptyChoiceField(label = 'Nowy typ wydatku', choices=type_list, required=False, empty_label=empty_label)
    
    cena = forms.CharField(label='Zaplacono: (*)')
    okres = forms.CharField(label='Aktualny okres: ', disabled = True)
    nowy_okres = EmptyChoiceField(label = 'Nowy okres', choices=period_list, required=False, empty_label=empty_label)
    komentarz = forms.CharField(label='Dodatkowy komentarz', required=False)
    class Meta:
        model = Wydatek
        fields = ('nazwa_wydatku','podtyp_wydatku','cena','okres','nowy_okres','komentarz')

'''

class UserForm(forms.ModelForm):
    username = forms.CharField(label = 'Username')
    email = forms.EmailField(label = 'Email')
    password = forms.CharField(widget=forms.PasswordInput, label = 'Password')
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class NewTypeForm(forms.Form):

    typ = forms.ModelChoiceField(label='Typ wydatku (*)', queryset=Typ_wydatku.objects.all())
    nowy_podtyp = forms.CharField(label='Nowy podtyp', required=True)
    class Meta:
        model = Podtyp_wydatku
        fields = ('nazwa_wydatku', 'podtyp_wydatku')





class RemoveTypeForm(forms.ModelForm):

    class Meta:
        model = Wydatek
        fields = ('nazwa_wydatku','podtyp_wydatku')


class DetailForm2(forms.ModelForm):
    empty_label = (('', '---------'),)   
    #type_list = Typ_wydatku.objects.values_list('nazwa_wydatku','nazwa_wydatku')
    #type_list = Typ_wydatku.objects.values_list('nazwa_wydatku','nazwa_wydatku')
    # period_list = Baza_wydatkow.objects.values_list('okres', 'okres').distinct()
    #nazwa_wydatku = forms.ChoiceField(label = 'Typ wydatku', required=False)

    #typ = forms.CharField(label='Aktualny typ:', disabled = True)
    #nowy_typ = EmptyChoiceField(label = 'Nowy typ wydatku', choices=type_list, required=False, empty_label=empty_label)
    
    cena = forms.CharField(label='Zaplacono: (*)')
    #okres = forms.CharField(label='Aktualny okres: ', disabled = True)
    # nowy_okres = EmptyChoiceField(label = 'Nowy okres', choices=period_list, required=False, empty_label=empty_label)
    komentarz = forms.CharField(label='Dodatkowy komentarz', required=False)
    class Meta:
        model = Wydatek
        fields = ('nazwa_wydatku','podtyp_wydatku','cena','komentarz')