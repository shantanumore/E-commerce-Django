from django.shortcuts import render,HttpResponse
from .models import Product,Contact,Order,OrderUpdate
from math import ceil 
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum
# Create your views here.

MERCHANT_KEY = '2cY%_e!kntp8N%nG'

def index(request):
    # products = Product.objects.all()
    # print(products)
    # n = len(products)
    # nSlides = n//4 + ceil((n/4)-(n//4))
    
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    #params = {'no_of_slides': nSlides , 'range': range(nSlides) , 'product' : products}
    
    # allProds = [[products, range(1,nSlides), nSlides],
    #             [products, range(1,nSlides), nSlides ]]

    params = {'allProds' : allProds}
               
    return render(request, 'E_com/index.html', params)

def searchMatch(query,item):

    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'E_com/search.html', params)
 

def about(request):
    return render(request, 'E_com/about.html')

def contact(request):
    if request.method == "POST":
      print(request) 
      name = request.POST.get('name','')
      email = request.POST.get('email','')
      phone = request.POST.get('phone','')
      contactdesc = request.POST.get('contactdesc','')
      contact = Contact(name=name , email=email, phone=phone , desc=contactdesc)
      contact.save()
      
    return render(request, 'E_com/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'E_com/tracker.html')



        
 


def productView(request, myid):
    #Fetch the product of that id 
    product = Product.objects.filter(id=myid)
    print(product)
    return render(request, 'E_com/productView.html',{'product':product[0]})

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        thank = True
        update = OrderUpdate(order_id = order.order_id , update_desc= "The order has placed")
        update.save()
        id = order.order_id
        #return render(request, 'E_com/checkout.html', {'thank':thank , 'id':id})
        # request paytm to transfer the amount to your account after payment by user
        param_dict = {
            'MID':'VLApve74747128778147',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000//pythonKit/handlerequest/',
        } 
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'E_com/paytm.html', {'param_dict': param_dict})

    
    return render(request, 'E_com/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here 
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verfiy = Checksum.verify_checksum(response_dict, MERCHANT_KEY ,checksum)
    if verfiy:
        if response_dict['RESPCODE']=='01':
            print('ORDER SUCCESSFUL')
        else:
            print("order unsuccessful because"+ response_dict['RESPMSG'])
    return render(request, 'E_com/paymentstatus.html', {'response': response_dict})