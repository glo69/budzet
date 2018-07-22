# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from .forms import EnterForm, DetailForm2, UserForm, NewTypeForm, RemoveTypeForm
from models import Baza_wydatkow, Typ_wydatku, Podtyp_wydatku
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from django.contrib.auth import logout, login
from django.db.models import Sum, Q
from datetime import date
from subprocess import call
from django.contrib.auth.models import User
import csv
import operator
import os

# Create your views here.
### FUNKCJE WEWNETRZNE

def check_date(start_date, end_date):
    if start_date == "" or end_date == "" or start_date == None or end_date == None:
        return HttpResponse('''Podano nieprawidlowe dane <button onclick="window.location.href = '/period_list'">OK</button>''')
    data = str(start_date) +' - '+str(end_date)
    end_date = end_date + " 23:59:59"
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    if start_date > end_date:
        temp = end_date
        end_date = start_date
        start_date = temp
    return start_date, end_date

def chart_data_generator(dane1):
    suma = 0
    dane = {}
    tablica3 = []
    tablica2 = []
    tablica = []
    for key, value in dane1.iteritems():
        try:
            temp = float(value)
        except TypeError or ValueError:
            temp = 0.0
        dane1[key] = temp
        suma = suma + temp
        if temp > 0.0:
            tablica3.append ((key, temp))
            dane[key]=temp
        tablica3 = sorted(tablica3, key=operator.itemgetter(1), reverse=True)
        tablica2 = [(i[1]) for i in tablica3]
        tablica  = [(i[0]) for i in tablica3]
    chart_data = { 'categories' : tablica , 'cat': tablica2}
    return chart_data, suma, dane

def dane_calkowite(name):
    try:
        dane = Baza_wydatkow.objects.filter(autor=name)
        przychod_calkowity = dane.filter(dochod = True).aggregate(Sum('cena')).values()[0]
        wydatek_calkowity = dane.filter(dochod = False).aggregate(Sum('cena')).values()[0]
        oszczednosci_calkowite = dane.filter(oszczednosci = True).aggregate(Sum('cena')).values()[0]
    except Baza_wydatkow.DoesNotExist:   
        przychod_calkowity = 0
        wydatek_calkowity = 0
        oszczednosci_calkowite = 0
    if przychod_calkowity is None:
        przychod_calkowity = 0
    if wydatek_calkowity is None:
        wydatek_calkowity = 0 
    if oszczednosci_calkowite is None:
        oszczednosci_calkowite = 0      
    return przychod_calkowity, wydatek_calkowity, oszczednosci_calkowite

def przychod_wydatek_30dni(name):
    try:
        dane = Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__lte=datetime.datetime.today(), data_utworzenia__gt=datetime.datetime.today()-datetime.timedelta(days=30))
        wydatek_dni = dane.filter(dochod = False).aggregate(Sum('cena')).values()[0]
        przychod_dni = dane.filter(dochod = True).aggregate(Sum('cena')).values()[0]
    except Baza_wydatkow.DoesNotExist:   
        przychod_dni = 0
        wydate_dni = 0
    if przychod_dni is None or przychod_dni == " " :
        przychod_dni = 0
    if wydatek_dni is None or wydatek_dni == " ":
        wydatek_dni = 0  
    return przychod_dni, wydatek_dni

def csv_file(request):
    # Create the HttpResponse object with the appropriate CSV header.
    username = None
    if request.user.is_authenticated():
        output = []
        posts ={}
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=raport_budzet.csv'
        writer = csv.writer(response, csv.QUOTE_MINIMAL)
        posts=Baza_wydatkow.objects.filter(autor=request.user).order_by('-id')
        writer.writerow(['Data','Typ', 'Podtyp','Wartosc','Komentarz'])
        for post in posts:
            if post.dochod == False:
                cena = (post.cena * -1)
            else:
                cena = post.cena
            data_wpisu = (post.data_utworzenia.strftime("%Y-%m-%d %H:%M"))    
            temp = (data_wpisu +','+ str(post.typ.nazwa_wydatku) + ',' + str(post.podtyp.podtyp_wydatku) + ',' +str(cena) + ',' + ',' + (post.komentarz.encode('utf-8')))    
            print temp
            output.append (temp)
            writer.writerow (output)
            del output [:]

        return response
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')


def export_typy(request):
    # Create the HttpResponse object with the appropriate CSV header.
    username = None
    if request.user.is_authenticated():
        output = []
        posts ={}
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=typy.csv'
        writer = csv.writer(response, csv.QUOTE_MINIMAL)
        typy = Typ_wydatku.objects.all()
        for typ in typy:
            pod_typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ)
            for pod_typ in pod_typy:
                temp = (str(typ.nazwa_wydatku) + ',' + str(pod_typ.podtyp_wydatku) + ',' + str(typ.dochod) + ',' + str(typ.oszczednosci))
                print temp
                writer.writerow ([temp])
        return response
    else:
        return HttpResponse('''Prosze sie zalogo wac!! <button onclick="window.location.href = '/login'">OK</button>''')


def import_typy(request):
    path = os.getcwd()
    odczyt_typ = ''
    path = path + '/typy.csv'
    file = open(path, "r")
    for line in file:
        tekst = line.replace('"','').replace('\n', '')
        wynik = tekst.split(',')
        odczyt_podtyp = str(wynik[1])
        odczyt_dochod = str_to_bool(wynik[2])
        odczyt_oszczednosci = str_to_bool(wynik[3])
        if odczyt_typ != wynik[0]:
            wpis1 = Typ_wydatku(nazwa_wydatku = str(wynik[0]), dochod = odczyt_dochod, oszczednosci = odczyt_oszczednosci)
            wpis1.save()
            odczyt_typ = str(wynik[0])
            wpis1 = Typ_wydatku.objects.get(nazwa_wydatku = str(wynik[0]))
            wpis = Podtyp_wydatku(nazwa_wydatku = wpis1, podtyp_wydatku = str(wynik[1]))
            wpis.save()
        else:
            wpis1 = Typ_wydatku.objects.get(nazwa_wydatku = str(wynik[0]))
            wpis = Podtyp_wydatku(nazwa_wydatku = wpis1, podtyp_wydatku = str(wynik[1]))
            wpis.save()
    return HttpResponse('''Prawidlowo pobrano dane <button onclick="window.location.href = '/new'">OK</button>''')

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was

#wylogowanie
def logout_page(request):
    logout(request)
    return HttpResponseRedirect("/login")

#nowy wydatek
def post_new(request):
    username = None
    if request.user.is_authenticated():
        name = request.user
        wynik = {}
        form = EnterForm()
        przychod, wydatek_calosc, oszczednosci = dane_calkowite(name)
        przychod_dni, wydatek_dni = przychod_wydatek_30dni(name)
        wynik["przychod_calkowity"] = przychod
        wynik["wydatek_calkowity"] = wydatek_calosc
        wynik["oszczednosci"] = oszczednosci
        wydatki = wydatek_calosc - oszczednosci
        wynik["wydatki"] = wydatki  
        wynik["przychod_30dni"] = przychod_dni
        wynik["wydatek_30dni"] = wydatek_dni 
        if przychod >0 and oszczednosci >0:
            wynik["procent_oszczednosci"] = round((float(oszczednosci) * 100 / float(wydatek_calosc)),2)
        if wydatek_calosc > 0 and przychod >0:
            wynik["procent_wydatek"] = round((float(wydatki) * 100 / float(wydatek_calosc)),2)            
        try:
            post = Baza_wydatkow.objects.filter(autor=name).last()
        except:
            post = {}
        wynik["wolne_srodki"] = przychod - wydatek_calosc
        if request.method == "POST":
            form = EnterForm(request.POST)
            if form.is_valid():
                wartosc = request.POST.get('kolejny_wpis')
                dzis = datetime.datetime.now()
                typy_dochod = Typ_wydatku.objects.filter(dochod = True)
                typy_oszczednosci = Typ_wydatku.objects.filter(oszczednosci = True)
                typ = form.cleaned_data["nazwa_wydatku"]
                dochod = False
                oszczednosci = False
                if typ in typy_dochod:
                    dochod = True
                if typ in typy_oszczednosci:
                    oszczednosci = True
                wpis = Baza_wydatkow(autor = request.user, typ = form.cleaned_data["nazwa_wydatku"], 
                    cena = form.cleaned_data["cena"], komentarz = form.cleaned_data["komentarz"], 
                    rok = dzis.strftime("%Y"), tydzien = dzis.strftime("%W"), 
                    miesiac = dzis.strftime("%m"), dochod = dochod, oszczednosci = oszczednosci,
                    podtyp = form.cleaned_data["podtyp_wydatku"] )    
                wpis.save()
                if wartosc == 'on':
                    return HttpResponseRedirect("/history/aktualny")
                else:
                    return HttpResponseRedirect("/new")
            else:
                return render(request, 'nowy_wydatek.html', {'form': form,'post':post, 'wynik':wynik})
        else:
            return render(request, 'nowy_wydatek.html', {'form': form,'post':post, 'wynik':wynik})
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')

#wybor historii
def period_list(request):
    if request.user.is_authenticated():
        wynik = {}
        name = request.user
        przychod, wydatek_calosc, oszczednosci = dane_calkowite(name)
        if przychod ==0 and wydatek_calosc ==0 and oszczednosci ==0:
            return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
        wynik["przychod_calkowity"] = przychod
        wynik["oszczednosci_calkowite"] = oszczednosci
        wynik["wydatek_calkowity"] = wydatek_calosc
        wynik["wolne_srodki"] = wynik["przychod_calkowity"] - wynik["wydatek_calkowity"]
        wynik["wydatek_calkowity"]  = wynik["wydatek_calkowity"] - wynik["oszczednosci_calkowite"]
        return render(request, 'historia.html', {'wynik':wynik})
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')

def actual_period_data(request):
    username = None
    if request.user.is_authenticated():
        name = request.user
        dane = {}
        dane1 = {}
        wynik = {}
        suma = 0
        typy = Typ_wydatku.objects.filter(dochod = False)
        posts =Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__lte=datetime.datetime.today(), data_utworzenia__gt=datetime.datetime.today()-datetime.timedelta(days=30)).order_by('-id')
        for typ in typy:
            pod_typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ)
            dane [typ.nazwa_wydatku] = posts.filter(typ= typ.id).aggregate(Sum('cena')).values()[0]
            for pod_typ in pod_typy:
                nazwa = (typ.nazwa_wydatku) +'-' + (pod_typ.podtyp_wydatku)
                dane1 [nazwa] = posts.filter(podtyp = pod_typ.id).aggregate(Sum('cena')).values()[0]
        dane_wykres_szczegoly, suma, dane1 = chart_data_generator(dane1)
        dane_wykres, suma, dane = chart_data_generator(dane)
        przychod, wydatek_calosc, oszczednosci = dane_calkowite(name)
        przychod_dni, wydatek_dni = przychod_wydatek_30dni(name)
        wynik["przychod_calkowity"] = przychod
        wynik["wydatek_calkowity"] = wydatek_calosc
        wynik["wolne_srodki"] = wynik["przychod_calkowity"] - wynik["wydatek_calkowity"]
        wynik["przychod"] = wynik["przychod_calkowity"]
        wynik["suma"] = int (suma)
        if (przychod>0) and (suma > 0):
            wynik["procent"] = str(round((float(suma) * 100 / float(przychod)),1)) + '%'
        else:
            wynik["procent"] = 'Brak dochodu'
        try:
            najstarszy = posts.last()
            najnowszy = posts.first()
            wynik["najnowszy"] = najnowszy.id
            wynik["najstarszy"] = najstarszy.id
        except:
            return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
        return render(request, 'lista_wydatkow_tabela.html', {'posts': posts, 'dane': dane, 'wynik':wynik, 'dane_wykres':dane_wykres, 'dane_wykres_szczegoly':dane_wykres_szczegoly })
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')

def all_data(request):
    username = None
    if request.user.is_authenticated():
        name = request.user
        dane = {}
        dane1 = {}
        wynik = {}
        suma = 0
        typy = Typ_wydatku.objects.filter(dochod = False)
        posts =Baza_wydatkow.objects.filter(autor=name).order_by('-id')
        for typ in typy:
            pod_typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ)
            dane [typ.nazwa_wydatku] = posts.filter(typ= typ.id).aggregate(Sum('cena')).values()[0]
            for pod_typ in pod_typy:
                nazwa = (typ.nazwa_wydatku) +'-' + (pod_typ.podtyp_wydatku)
                dane1 [nazwa] = posts.filter(podtyp = pod_typ.id).aggregate(Sum('cena')).values()[0]
        dane_wykres_szczegoly, suma, dane1 = chart_data_generator(dane1)
        dane_wykres, suma, dane = chart_data_generator(dane)
        przychod, wydatek_calosc, oszczednosci = dane_calkowite(name)
        przychod_dni, wydatek_dni = przychod_wydatek_30dni(name)
        wynik["przychod_calkowity"] = przychod
        wynik["wydatek_calkowity"] = wydatek_calosc
        wynik["wolne_srodki"] = wynik["przychod_calkowity"] - wynik["wydatek_calkowity"]
        wynik["przychod"] = wynik["przychod_calkowity"]
        wynik["suma"] = int (suma)
        if (przychod>0) and (suma > 0):
            wynik["procent"] = str(round((float(suma) * 100 / float(przychod)),1)) + '%'
        else:
            wynik["procent"] = 'Brak dochodu'
        try:
            najstarszy = posts.last()
            najnowszy = posts.first()
            wynik["najnowszy"] = najnowszy.id
            wynik["najstarszy"] = najstarszy.id
        except:
            return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
        return render(request, 'lista_wydatkow_tabela.html', {'posts': posts, 'dane': dane, 'wynik':wynik, 'dane_wykres':dane_wykres, 'dane_wykres_szczegoly':dane_wykres_szczegoly })
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')



def range_date(request):
    username = None
    if request.user.is_authenticated():
        name = request.user
        dane = {}
        dane1 = {}
        wynik = {}
        input_start_date = request.POST.get('start_date')
        input_end_date = request.POST.get('end_date')
        wynik["Okres"] = str(input_start_date) +" - "+ str(input_end_date)
        start_date, end_date = check_date(input_start_date, input_end_date)
        try:
            posts = Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__range=(start_date, end_date))
            najstarszy = posts.order_by('-id').last()
            najnowszy = posts.order_by('-id').first()
        except:
            return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
        wynik["najnowszy"] = najnowszy.id
        wynik["najstarszy"] = najstarszy.id
        przychod =posts.filter(dochod = True).aggregate(Sum('cena')).values()[0]
        typy = Typ_wydatku.objects.filter(dochod = False)
        for typ in typy:
            dane [typ.nazwa_wydatku] = (posts.filter(typ= typ.id).aggregate(Sum('cena')).values()[0])
            pod_typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ)
            for opis in pod_typy:
                nazwa = str(typ.nazwa_wydatku) +'-' + str(opis.podtyp_wydatku)
                # dane1 [nazwa] = (Baza_wydatkow.objects.filter(autor=name).filter(typ = typ.id).filter(podtyp = opis.id).filter(data_utworzenia__range=(start_date, end_date)).aggregate(Sum('cena')).values()[0])
                dane1 [nazwa] = (posts.filter(podtyp = opis.id).aggregate(Sum('cena')).values()[0])
        dane_wykres_szczegoly, suma, dane1 = chart_data_generator(dane1)
        dane_wykres, suma, dane = chart_data_generator(dane)
        if przychod is None: 
            przychod = 0.0
        wynik["suma"] = suma
        wynik["przychod"] = przychod
        wynik["historia"]= 'True'
        return render(request, 'lista_wydatkow.html', {'posts': posts, 'dane': dane, 'wynik':wynik, 'dane_wykres':dane_wykres, 'dane_wykres_szczegoly':dane_wykres_szczegoly })
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')

def details(request, ids):
    username = None
    if request.user.is_authenticated():
        post = {}
        name= request.user
        post = Baza_wydatkow.objects.get(id = ids, autor = name)
        form = DetailForm2(request.POST or None, instance = post)
        detail = post
        if form.is_valid():
            typy_dochod = Typ_wydatku.objects.filter(dochod = True)
            typ = form.cleaned_data['nazwa_wydatku'].nazwa_wydatku
            wybrany_typ = Typ_wydatku.objects.get(nazwa_wydatku = typ)
            post.typ = wybrany_typ
            podtyp = form.cleaned_data["podtyp_wydatku"].podtyp_wydatku
            wybrany_podtyp = Podtyp_wydatku.objects.get(nazwa_wydatku = podtyp)
            post.podtyp = wybrany_podtyp
            komentarz = form.cleaned_data["komentarz"]
            cena = form.cleaned_data["cena"]
            if post.komentarz != komentarz:
                post.komentarz = komentarz
            if post.cena != cena:
                post.cena = cena          
            dochod = False
            if typ in typy_dochod:
                dochod = True
            post.dochod = dochod
            post.save()
            return HttpResponseRedirect("/new")
        else:
            return render(request, 'details.html', {'form': form, 'post': post})
    else:
        return HttpResponseRedirect("/login")

def remove(request, ids):
    Baza_wydatkow.objects.filter(id = ids).delete()
    return HttpResponse('''Wpis usunieto <button onclick="window.location.href = '/period_list'">OK</button>''')

def compare_dates(request):
    username = None
    if request.user.is_authenticated():
        name = request.user
        dane = {}
        dane1 = {}
        wynik = {}
        tablica = []
        tablica2 = []
        tablica3 = []
        input_start_date = request.POST.get('start_date')
        input_end_date = request.POST.get('end_date')
        input_start_date1 = request.POST.get('start_date1')
        input_end_date1 = request.POST.get('end_date1')
        data = str(input_start_date) +' - '+str(input_end_date)
        data1 = str(input_start_date1) +' - '+str(input_end_date1)
        start_date, end_date = check_date(input_start_date, input_end_date)
        start_date1, end_date1 = check_date(input_start_date1, input_end_date1)
        typy = Typ_wydatku.objects.filter(dochod = False)
        posts = Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__range=(start_date, end_date))
        posts1 = Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__range=(start_date1, end_date1))
        suma = 0
        for opis in typy:
            try:
                dane [opis.nazwa_wydatku] = posts.filter(typ = opis.id).aggregate(Sum('cena')).values()[0]
                dane1 [opis.nazwa_wydatku] = posts1.filter(typ = opis.id).aggregate(Sum('cena')).values()[0]
            except:
                return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
        for key, value in dane.iteritems():
            if value is None: 
                value = 0
                dane[key] = value
            temp = float(value)
            suma = suma + temp
            tablica2.append(temp)
            tablica.append (key)
        wynik["suma"] = suma
        suma = 0
        for key, value in dane1.iteritems():
            if value is None: 
                value = 0
                dane1[key] = value
            temp = float(value)
            suma = suma + temp
            tablica3.append(temp)
        wynik["suma1"] = suma
        dane_wykres = { 'categories' : tablica , 'cat': tablica2, 'cat2': tablica3}
        wynik["Okres"] = data +' do ' + data1
        wynik["data"] = data
        wynik["data1"]= data1
        return render(request, 'lista_wydatkow_historia_porownanie.html', {'dane': dane, 'dane1': dane1, 'wynik':wynik, 'dane_wykres':dane_wykres })
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')


def type_chart(request, typ, min_id, max_id):    
    username = None
    if request.user.is_authenticated():
        name = request.user
        dane = {}
        typ_obiekt = Typ_wydatku.objects.get(nazwa_wydatku = typ)
        print typ_obiekt
        typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ_obiekt)
        for opis in typy:
            dane [opis.podtyp_wydatku] = (Baza_wydatkow.objects.filter(autor=name).filter(podtyp = opis.id).filter(id__range=(max_id,min_id)).aggregate(Sum('cena')).values()[0])
        dane_wykres, suma, dane = chart_data_generator(dane)
        return render(request, 'detail_chart.html', {'dane_wykres':dane_wykres, 'typ':typ })
    else:
        return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')


def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            return HttpResponse('''Uzytkownik utworzony - zaloguj sie <button onclick="window.location.href = '/login'">OK</button>''')
    else:
        form = UserForm()
    return render(request, 'adduser.html', {'form': form})

def new_type(request):
    username = None
    if request.user.is_authenticated():
        wpis = Typ_wydatku(nazwa_wydatku='test', dochod = True, oszczednosci = False)
        wpis.save()
        if request.method == "POST":
            form = NewTypeForm(request.POST)
            if form.is_valid():
                typ = form.cleaned_data['typ']
                print typ
                nowy_podtyp = form.cleaned_data['nowy_podtyp']
                print nowy_podtyp
                wpis = Podtyp_wydatku(autor = request.user, nazwa_wydatku = typ, podtyp_wydatku = nowy_podtyp)
                wpis.save()
                return HttpResponse('ok!!')        
        else:
            form = NewTypeForm()
        return render(request, 'new_type.html', {'form': form})
    else:
        return HttpResponseRedirect("/login")


############################################333
# funkcje testowe nie uzywane

def details_ok(request, ids):
    username = None
    if request.user.is_authenticated():
        detail = {}
        username = request.user.username
        instance = Baza_wydatkow.objects.get(id = ids, autor = request.user)
        form = DetailForm(request.POST or None, instance = instance)
        detail = instance
        if form.is_valid():
            form = form.save(commit=False)
            typ = instance.typ
            okres = instance.okres
            nowy_typ = str(request.POST.get('nowy_typ'))
            nowy_okres = str(request.POST.get('nowy_okres'))
            if nowy_typ !='':
                form.typ = nowy_typ
            else:
                form.typ = typ

            if nowy_okres !='':
                form.okres = nowy_okres
            else:
                form.okres = okres
            form.save()
            return HttpResponseRedirect("/history/aktualny/")
        else:
            return render(request, 'details.html', {'form': form, 'detail': detail})
    else:
        return HttpResponseRedirect("/login")



def temp_data(request):
    #content = []
    my_file =  open('/mnt/usb_1/Programy/wyniki_co.txt', 'r') 
    #with my_file:
    #    odczyt = my_file.readlines()
    #    content.append(odczyt)
    #print content
    #response = HttpResponse(content)
    response = HttpResponse(my_file.read())
    response['Content-Disposition'] = 'inline;filename=some_file.txt'
    return response




    #requesty testowe

# aktualny, lista_krotka, none, okres
# def post_actual_period2(request):
#     username = None
#     if request.user.is_authenticated():
#         name = request.user
#         dane = {}
#         dane1 = {}
#         wynik = {}
#         suma = 0
#         typy = Typ_wydatku.objects.filter(dochod = False)
#         dane_z_bazy = Baza_wydatkow.objects.filter(autor=name).filter(data_utworzenia__lte=datetime.datetime.today(), data_utworzenia__gt=datetime.datetime.today()-datetime.timedelta(days=30))
#         for typ in typy:
#             pod_typy = Podtyp_wydatku.objects.filter(nazwa_wydatku__nazwa_wydatku__exact = typ)
#             dane [typ.nazwa_wydatku] = (dane_z_bazy.filter(typ= typ.id).aggregate(Sum('cena')).values()[0])
#             for pod_typ in pod_typy:
#                 nazwa = (typ.nazwa_wydatku) +'-' + (pod_typ.podtyp_wydatku)
#                 dane1 [nazwa] = (dane_z_bazy.filter(podtyp = pod_typ.id).aggregate(Sum('cena')).values()[0])
#         dane_wykres_szczegoly, suma, dane1 = chart_data_generator(dane1)
#         dane_wykres, suma, dane = chart_data_generator(dane)
#         przychod, wydatek_calosc, oszczednosci = dane_calkowite(name)
#         przychod_dni = przychod_30dni(name)
#         wydatek_dni = wydatek_30dni(name)
#         wynik["przychod_calkowity"] = przychod
#         wynik["wydatek_calkowity"] = wydatek_calosc
#         wynik["wolne_srodki"] = wynik["przychod_calkowity"] - wynik["wydatek_calkowity"]
#         wynik["przychod"] = wynik["przychod_calkowity"]
#         wynik["suma"] = int (suma)
#         if (przychod>0) and (suma > 0):
#             wynik["procent"] = str(round((float(suma) * 100 / float(przychod)),1)) + '%'
#         else:
#             wynik["procent"] = 'Brak dochodu'
#         wynik["historia"] = 'True'
#         try:
#             posts=dane_z_bazy.order_by('-id')
#             najstarszy = posts.last()
#             najnowszy = posts.first()
#             wynik["najnowszy"] = najnowszy.id
#             wynik["najstarszy"] = najstarszy.id
#         except:
#             return HttpResponse('''Brak danych do wyswietlenia <button onclick="window.location.href = '/new'">OK</button>''')
#             #return render(request, 'lista_wydatkow_tabela.html', {'posts': posts, 'dane': dane, 'wynik':wynik, 'dane_wykres':dane_wykres, 'dane_wykres_szczegoly':dane_wykres_szczegoly })
#         return render(request, 'lista_wydatkow.html', {'dane': dane, 'wynik':wynik, 'dane_wykres':dane_wykres, 'dane_wykres_szczegoly':dane_wykres_szczegoly })
#     else:
#         return HttpResponse('''Prosze sie zalogowac!! <button onclick="window.location.href = '/login'">OK</button>''')




def test(request):
    wartosc = request.POST.get('your_name')
    wartosc2 = request.POST.get('your_name2')
    wynik = wartosc + wartosc2
    return HttpResponse(wynik)

def set_date(request):
    return HttpRedirect("/name")

def range_date_function (start_date, end_date):
    #start_date = request.POST.get('start_date')
    #end_date = request.POST.get('end_date')
    #if start_date == "" or end_date == "":
    #    return HttpResponse('''Podano nieprawidlowe dane <button onclick="window.location.href = '/period_list'">OK</button>''')

    end_date = end_date + " 23:59:59"
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    if start_date > end_date:
        temp = end_date
        end_date = start_date
        start_date = temp

    posts = Baza_wydatkow.objects.filter(autor=request.user).filter(data_utworzenia__range=(start_date, end_date))
    dane = {}
    wynik = {}
    tablica = []
    tablica2 = []
    suma = 0
    typy = Typ_wydatku.objects.all()
    for opis in typy:
        dane [opis.wydatku] = str(Baza_wydatkow.objects.filter(autor=request.user).filter(data_utworzenia__range=(start_date, end_date)).filter(typ = opis.nazwa_wydatku).aggregate(Sum('cena')).values()[0])
    for key, value in dane.iteritems():
        if value is None: # == 'None':
            value = 0
        temp = float(value)
        suma = suma + tem
        tablica2.append(temp)
        tablica.append (key)
    dane_wykres = { 'categories' : tablica , 'cat': tablica2}
    wynik["Okres"] = str(start_date) +" - "+ str(end_date)
    dane["suma"] = suma
    return tablica, tablica2, wynik, dane


def remove_type(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        if request.method == "POST":
            form = RemoveTypeForm(request.POST)
            if form.is_valid():
                #typ = form.cleaned_data['typ']
                #print typ
                #nowy_podtyp = form.cleaned_data['nowy_podtyp']
                #print nowy_podtyp
                
                return HttpResponse('ok!!')
        else:
            form = RemoveTypeForm()
        
        return render(request, 'remove_type.html', {'form': form})

    else:
        return HttpResponseRedirect("/login")




def charts(request):
    dane = {}
    dane2 = {}
    tablica = []
    tablica2 = []
    typy = Typ_wydatku.objects.all()
    for opis in typy:
        dane2 [opis.wydatku] = str(Baza_wydatkow.objects.filter(okres= aktualny_okres()).filter(typ = opis.nazwa_wydatku).aggregate(Sum('cena')).values()[0])
    for key, value in dane2.iteritems():
        if value is None: #== 'None':
            value = 0
        temp = float(value)
        tablica2.append(temp)
        tablica.append (key)
    dane = { 'categories' : tablica , 'cat': tablica2}
    return render(request, 'charts.html', dane)



# def aktualny_okres():
#     wynik = 'aktualny'
#     return wynik

# def ilosc_dni():
#     days = 30
#     return days

# def numer_dnia(name):  
#     dzis = datetime.datetime.now(timezone.utc)
#     aktualny ='aktualny'
#     try:
#         posts = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).exclude (okres = aktualny).filter(autor=name).latest('data_utworzenia')
#         ostatni= posts.data_utworzenia
#     except Baza_wydatkow.DoesNotExist:
#         try:
#             posts = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).filter(autor=name).earliest('data_utworzenia')    
#             ostatni= posts.data_utworzenia
#         except Baza_wydatkow.DoesNotExist:
#             ostatni  = dzis
#     #ostatni= posts.data_utworzenia
#     print dzis
#     print ostatni
#     numer = dzis - ostatni
#     numer = int(numer.days)
#     print numer
#     if numer == 0:
#         numer = 1
#     return numer

# def poczatek_aktualnego_okresu():
#     aktualny ='aktualny'
#     try:
#         posts = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).exclude (okres = aktualny).latest('data_utworzenia')
#         ostatni= posts.data_utworzenia
#         if ostatni is None: 
#             ostatni = 'brak aktualnych wpisow'
#     except Baza_wydatkow.DoesNotExist:
#         ostatni = 'brak aktualnych wpisow'
    # return ostatni

# def check_period(period):
#     posts_end = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).exclude (okres = period).latest('data_utworzenia')
#     end = posts_end.data_utworzenia
#     posts_start = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).exclude (okres = period).earliest('data_utworzenia')
#     start = posts_start.data_utworzenia 
#     return (start, end)

# def nazwa_nowego_okresu():
#     dzis = datetime.datetime.now(timezone.utc)
#     rok = int (dzis.strftime("%Y"))
#     print rok
#     miesiac = dzis.strftime("%m")
#     aktualny ='aktualny'
#     posts = Baza_wydatkow.objects.filter(data_utworzenia__lte=timezone.now()).exclude (okres = 'aktualny').latest('data_utworzenia')
#     if bool(posts) == False:
#         nazwa_okresu = miesiac + rok
#     else:
#         nazwa_okresu = posts.okres  
#         dlugosc_nazwa = len (nazwa_okresu) 
#         dlugosc_miesiac = dlugosc_nazwa - 4
#         nazwa_okresu_miesiac = int (nazwa_okresu [:dlugosc_miesiac])
#         nazwa_okresu_rok = int(nazwa_okresu [dlugosc_miesiac:dlugosc_nazwa])
#         if rok == nazwa_okresu_rok:
#             nazwa_okresu_miesiac = nazwa_okresu_miesiac + 1
#             if nazwa_okresu_miesiac>9:
#                 nazwa_okresu = str(nazwa_okresu_miesiac) + str(rok)
#             else:
#                 nazwa_okresu = '0' + str(nazwa_okresu_miesiac) + str(rok)
#         else:
#             nazwa_okresu = '01' + str(rok)
#     return nazwa_okresu

###REQUESTY

# def end_period(request):
#     username = None
#     if request.user.is_authenticated():
#         nowy_okres = nazwa_nowego_okresu()
#         posts = Baza_wydatkow.objects.filter(autor=request.user).filter(okres='aktualny')
#         i = 0
#         for post in posts:
#             post.okres = nowy_okres
#             post.save()
#             i = i + 1  
#         if i > 0:
#             return HttpResponse ('Zamknieto okres aktualny. Zostal zapisany pod nazwa: ' + nowy_okres + '''</br>
#                 <button onclick="window.location.href = '/new'">OK</button>''')
#         else:
#             return HttpResponse('''Brak wpisow w okresie aktualnym do zamkniecia </br>
#                 <button onclick="window.location.href = '/new'">OK</button>''')
            
# def end_period_first_step(request):
#     username = None
#     if request.user.is_authenticated():
#         nowy_okres = nazwa_nowego_okresu()
#         posts = Baza_wydatkow.objects.filter(autor=request.user).filter(okres='aktualny')
#         i = 0
#         for post in posts:
#             post.okres = nowy_okres
#             post.save()
#             i = i + 1  
#         if i > 0:
#             return HttpResponse ('Zamknieto okres aktualny. Zostal zapisany pod nazwa: ' + nowy_okres + '''</br>
#                 <button onclick="window.location.href = '/new'">OK</button>''')
#         else:
#             return HttpResponse('''Brak wpisow w okresie aktualnym do zamkniecia </br>
#                 <button onclick="window.location.href = '/new'">OK</button>''')

# def minidlna_refresh(request):
#     w = call(["minidlnad", "-R"])
#     return HttpResponse('Baza danych MiniDLNA zaaktualizowana! Dodano {} nowych wpisow'.format(w))

# def question(request):
#     username = None
#     if request.user.is_authenticated():
#         name = request.user
#         wynik = {}
#         suma =(Baza_wydatkow.objects.filter(okres= 'aktualny').filter(dochod = False).filter(autor=name).aggregate(Sum('cena')).values()[0])
#         przychod =(Baza_wydatkow.objects.filter(okres= 'aktualny').filter(autor=name).filter(dochod = True).aggregate(Sum('cena')).values()[0])
#         oszczednosci = Baza_wydatkow.objects.filter(okres= 'aktualny').filter(autor=name).filter(oszczednosci = True).aggregate(Sum('cena')).values()[0]
#         if suma is None:
#             wynik["suma"] = 0
#             suma = 0
#         else:
#             wynik["suma"] = (suma)

#         if przychod is None:
#             wynik["przychod"] = 0
#             przychod = 0
#         else:
#             wynik["przychod"] = (przychod)

#         if oszczednosci is None:
#             wynik["oszczednosci"] = 0
#             oszczednosci = 0
#         else:
#             wynik["oszczednosci"] = (oszczednosci)
#         wynik["wydatki"] = wynik["suma"] - wynik["oszczednosci"]
#         wynik["przychod_calkowity"] = przychod_calkowity(name)
#         wynik["wydatek_calkowity"] = wydatek_calkowity(name)
#         wynik["wolne_srodki"] = wynik["przychod_calkowity"] - wynik["wydatek_calkowity"]
#     return render(request, 'question.html',{'wynik': wynik})
