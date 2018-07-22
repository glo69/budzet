from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey

# Create your models here.


class Typ_wydatku(models.Model):
    nazwa_wydatku = models.CharField(max_length= 128, unique= True)
    dochod = models.BooleanField(default = False)
    oszczednosci = models.BooleanField(default = False)
    def __unicode__(self):
        return unicode(self.nazwa_wydatku)

class Podtyp_wydatku(models.Model):
    nazwa_wydatku = models.ForeignKey(Typ_wydatku)
    podtyp_wydatku = models.CharField(max_length = 45)
    def __unicode__(self):
        return unicode(self.podtyp_wydatku)

class Wydatek(models.Model):
    nazwa_wydatku = models.ForeignKey(Typ_wydatku)
    podtyp_wydatku = ChainedForeignKey(Podtyp_wydatku, chained_field="nazwa_wydatku", chained_model_field="nazwa_wydatku", show_all=False, auto_choose=True)


class Baza_wydatkow(models.Model):
    autor = models.ForeignKey('auth.User')
    rok = models.IntegerField()
    miesiac = models.IntegerField()
    tydzien = models.IntegerField()
    typ = models.ForeignKey(Typ_wydatku)
    podtyp = models.ForeignKey(Podtyp_wydatku)
    cena = models.DecimalField(max_digits = 9, decimal_places = 2)
    komentarz = models.CharField(max_length = 256)
    data_utworzenia = models.DateTimeField(default=timezone.now)
    dochod = models.BooleanField(default = False)
    oszczednosci = models.BooleanField(default = False)
    #konto = models.models.CharField(max_length = 48)
    def __unicode__(self):
        return unicode(self.typ)

# class Konto(models.Model):
#     autor = models.ForeignKey('auth.User')
#     nazwa_konta = models.CharField(max_length = 45)
#     typ_konta = models.CharField(max_length = 45)
#     wartosc_wydatkow = models.DecimalField(max_digits = 9, decimal_places = 2)
#     wartosc_przychodow = models.DecimalField(max_digits = 9, decimal_places = 2)
#     def __unicode__(self):
#         return unicode(self.nazwa_konta)
