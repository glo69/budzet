from django.contrib import admin
from models import Baza_wydatkow, Typ_wydatku, Podtyp_wydatku
# Register your models here.


class Baza_wydatkow_admin(admin.ModelAdmin):
	list_display = ('autor','rok','miesiac','tydzien','typ','cena','komentarz','data_utworzenia')

class Typ_wydatku_admin(admin.ModelAdmin):
	list_display = ('id','nazwa_wydatku')	
	
admin.site.register(Baza_wydatkow, Baza_wydatkow_admin)
admin.site.register(Typ_wydatku, Typ_wydatku_admin)
admin.site.register(Podtyp_wydatku)

