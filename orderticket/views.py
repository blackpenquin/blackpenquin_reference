from unicodedata import name
import os,sys
import traceback
from unittest import result
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.shortcuts import render,redirect
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from itertools import permutations
from datetime import date,datetime
import datetime as dt
from django.contrib.auth.models import User
from .forms import CustomerForm
import random,string
from django import forms
from .models import Customer, order
from django.db.models import Count
from .filters import OrderFilter
from django.shortcuts import get_object_or_404,HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from datetime import timedelta 
from django.contrib.auth.models import User

import csv
from django.http import HttpResponse

def file_load_view(request,username):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order No.', 'Races','Detail','Total','Ordered on'])

    students = order.objects.filter(customer=Customer.objects.get(name=username)).values_list('ordertag', 'race','orderdetail','total','orderdate')

    # Note: we convert the students query set to a values_list as the writerow expects a list/tuple       
    # students = students.values_list('studName__VMSAcc', 'mark')

    for student in students:
        writer.writerow(student)

    return response

def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('/')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'login.html', context)

def logout(request):
	
	auth_logout(request)
	messages.info(request, 'Logged out successfully')
	return redirect('login')

def pastorders(request):

    section = int(request.POST['section'])
    orderdate = datetime.strptime(request.POST['orderdate'], '%Y-%m-%d') 
    nextday = orderdate + timedelta(days=1) 
    result = order.objects.filter(customer=Customer.objects.get(id=int(section)),orderdate__range=(orderdate,nextday))
    Tvalue = 0

    for item in result:
        Tvalue= Tvalue + int(item.total)
    totalOrders = len(result)

    context = {
        'totalOrders':totalOrders,
        'Tvalue':Tvalue,
            }

    return render(request, 'pastorders.html',context=context)

def customerpastorders(request):
    section = int(request.POST['section'])
    orderdate = datetime.strptime(request.POST['orderdate'], '%Y-%m-%d') 
    nextday = orderdate + timedelta(days=1) 
    result = order.objects.filter(customer=Customer.objects.get(id=int(section)),orderdate__range=(orderdate,nextday))
    Tvalue = 0

    for item in result:
        Tvalue= Tvalue + int(item.total)
    totalOrders = len(result)

    context = {
        'totalOrders':totalOrders,
        'Tvalue':Tvalue,
            }

    return render(request, 'pastorders.html',context=context)

def change_password(request,username):

    cust = Customer.objects.get(user=User.objects.get(username=username))
    custid = cust.id

    if request.method == 'POST':
        newpassword = request.POST['newpassword']
        user = User.objects.get(username=username)
        user.set_password(newpassword)
        user.save()
        cust = Customer.objects.get(user=User.objects.get(username=username))
        cust.loginkey = newpassword
        cust.save()
        messages.success(request, 'New password was successfully updated!')
        return render(request, 'changePassword.html', {'custid':custid})
    else:
        return render(request, 'changePassword.html', {'custid':custid})

def orderCalculation(request):
    try:

        # Getting input datas from user
        d1 = request.POST['input1']
        d2 = request.POST['input2']
        raceList = {1:'Magnum',2:'Kuda',3:'Todo',4:'Singapore',5:'Sarawale',6:'Sabah',7:'Sandakan',8:'Grand'}
        # sample = "123#4\n*123#4\n**123#4"
        sampleList = d2.splitlines()
        result = 0
        output = ""
        raceValue = 1
        racekeys = ['m','k','t','s','w','b','d','g']
        racedict = {1:'M',2:'K',3:'T',4:'S',5:'W',6:'B',7:'D',8:'G'}

        def singleStar(item):
            item =item.replace("*","")
            firstsplit = item.split("#")[0] 
            secondsplit = list(firstsplit)
            comb = permutations(secondsplit, len(secondsplit))
            comb = len(set(list(comb)))
            result2  = "Box(" + item.split("#")[0] +") - "+item.split("#")[1]+"B" 
            output2= comb * int(item.split("#")[1])
            return output2,result2

        def dualStar(item):
            item =item.replace("*","")
            output3 = int(item.split("#")[1])
            result3 = "iB(" + item.split("#")[0] +") - "+item.split("#")[1]+"B" 
            return output3,result3
            
        for i in range(len(sampleList)):
            initialSplit = sampleList[i].split('#')
            if len(initialSplit) > 1:
                if "**" in sampleList[i]:
                    dualresult,sioutput = dualStar(sampleList[i])
                    result = result + (raceValue*int(dualresult)) 
                    output = output + sioutput + '\n'

                elif "*" in sampleList[i]:
                    singleresult,duoutput = singleStar(sampleList[i])
                    result = result + (raceValue*int(singleresult))  
                    output = output + duoutput + '\n'

                else:
                    if raceValue:
                        result = result + (raceValue*int(initialSplit[1]))
                        output = output + (initialSplit[0] +" - " +initialSplit[1]+"B") + "\n"
                    else:
                        result = result + int(initialSplit[1])
            else:
                racelist = list(sampleList[i])
                raceValue = len(racelist)
                if raceValue == 1:
                    if racelist[0].isdigit():
                        output = output + racedict[int(racelist[0])] + "\n"
                    else:
                        output = output + sampleList[i] + "\n"
                else:
                    if any(ext.lower() in racekeys for ext in racelist):
                        output = output + sampleList[i] + "\n"
                    else:
                        racestring = ''
                        for item in racelist:
                            racestring = racestring + racedict[int(item)]
                        output = output + racestring + "\n"
                    

        d1items = "".join(dict.fromkeys(d1.split('*')[0]))
        raceName = []
        for number in d1items:
            raceName.append(raceList[int(number)])

        dbraceName = ",".join(raceName)
        todaysdate = date.today()
        now = dt.datetime.now()
        #H:M:S
        ordertime = now.strftime("%H:%M:%S")
        current_user = request.user
        orderCount = order.objects.filter(customer__name=current_user.username).order_by('-id')
        if len(orderCount) > 0:
            orderCount = len(orderCount) + 1
        else:
            orderCount = 1

        if 'admin' in current_user.username or 'blackpenquin' in current_user.username:

            messages.info(request, 'Admin cannot place orders!')
        else:
            b=Customer.objects.get(name=current_user.username)

            e = order(race=dbraceName,ordertag=int(orderCount),orderdetail=output,total=result,customer =b)
            e.save()
        sharemessage = str(current_user.username)+ "\n" +"#" + str(orderCount) +"\n"+ str(todaysdate)+" "+ str(ordertime)+ "\n" +str(dbraceName)+"\n" + output +"\n"+ "T- " + str(result)

        context = {
                'todaysdate':todaysdate,
                'ordertime':ordertime,
                'orderCount':orderCount,
                'output':output,
                'finalresult':result,
                'raceName':raceName,
                'dbraceName':dbraceName,
                'sharemessage':sharemessage
                }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        messages.error(request, 'Please check your input.')
        return render(request,'inputerror.html')

    return render(request,'orderresult.html',context=context)

@login_required(login_url='login')
def home(request):
    today = datetime.today()
    latestInstruction = []

    return render(request,'ordersubmission.html',{'latestInstruction':latestInstruction})

def deleteOrder(request, id):
    odr = order.objects.get(id=id)
    odr.delete()
    # messages.warning(request, "You have deleted the Customer profile")
    return HttpResponseRedirect(reverse('home'))

def check_admin(user):
   return user.is_superuser
   
def dashboard(request):

    Totalorders = order.objects.all().count()
    customers = Customer.objects.all()

    # from django.db.models import Count

    newcustomer = Customer.objects.annotate(num_subscription=Count('order')).filter(num_subscription=0)

    existingCustomer = Customer.objects.annotate(num_subscription=Count('order')).filter(num_subscription__gt=0)
    total_customers = customers.count()

    # latestInstruction = Instruction.objects.order_by('-livedate')

    context = {'customers':customers,
                'total_customers':total_customers,
               'newcustomer':newcustomer,'existingCustomer':existingCustomer,'Totalorders':Totalorders}

    return render(request, 'dashboard.html',context=context)

@user_passes_test(check_admin)
@login_required(login_url='login')
def newCustomerAdmin(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():

            # user creation
            name = request.POST['name']
            try:
                User.objects.get(username__iexact=name)
                # raise forms.ValidationError("Username already present.Please change username")
                messages.info(request, 'Username already present.Please change username')


            except User.DoesNotExist:
                full_name = str(name).lower()
                if len(full_name) > 1:
                    first_letter = full_name[0][0]
                    three_letters_surname = full_name[-1][:3].rjust(3, 'x')
                    number = '{:04d}'.format(random.randrange (1,999))
                    username = '{}{}{}'.format(first_letter, three_letters_surname, number)
                            # password creation
                length = 8
                chars = string.ascii_letters + string.digits + '@#*'

                rnd = random.SystemRandom()
                pwd = ''.join(rnd.choice(chars) for i in range(length))

                user = User.objects.create_user(username=name,password=pwd)

                newuser = User.objects.get(username=name)
                profile = form.save(commit=False)
                profile.user = newuser
                profile.loginkey = pwd
                profile.save()
                form = CustomerForm()

                messages.info(request, 'Details recorded Successfully!')
                return redirect('dashboard')

        else:
            messages.error(request, "Error")
    else:
        form = CustomerForm()

    return render(request, 'newuser.html', {'form': form})

@login_required(login_url='login')
def customer(request, pk_test):
    customer = Customer.objects.get(user=User.objects.get(username=pk_test))
    subscriptions = customer.order_set.all().order_by('-orderdate')
    subscription_count = subscriptions.count()

    myFilter = OrderFilter(request.GET, queryset=subscriptions)
    subscriptions = myFilter.qs 

    context = {'customer':customer, 'subscriptions':subscriptions, 'subscription_count':subscription_count,
    'myFilter':myFilter}

    return render(request, 'customer.html',context)

@login_required(login_url='login')
def customerOrder(request, pk_test):
    try:
        customer = Customer.objects.get(name=pk_test)
        subscriptions = customer.order_set.all().order_by('-orderdate')
        subscription_count = subscriptions.count()

        myFilter = OrderFilter(request.GET, queryset=subscriptions)
        subscriptions = myFilter.qs 

        context = {'customer':customer, 'subscriptions':subscriptions, 'subscription_count':subscription_count,
        'myFilter':myFilter}
        return render(request, 'customerOrderdetail.html',context)
    except:
        context = {'noorders':"No Orders Found"}
        return render(request, 'Noorders.html',context)

@user_passes_test(check_admin)
@login_required(login_url='login')
def deleteCustomer(request, id):
    cust = Customer.objects.get(id=id)
    username = cust.user.username
    cust.delete()
    u = User.objects.get(username = username)
    u.delete()
    # messages.warning(request, "You have deleted the Customer profile")
    return HttpResponseRedirect(reverse('dashboard'))

def orderResult(request):
    return render(request,'orderresult.html')
