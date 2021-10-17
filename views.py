from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view ## Might still need this to an extent.
from restapi.serializers import UserSerializer, GroupSerializer, RewardPointsSerializer, CustomerSerializer, ProductSerializer, ProductVariantSerializer, BatchSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from rest_framework.parsers import JSONParser
from restapi.models import Product, Employee, Register, ProductVariant, Store, Batch, Customer, RewardPoints
from restapi.serializers import ProductSerializer, RegisterSerializer, StoreSerializer
from woocommerce import API
import qrcode
import json
from fuzzywuzzy import fuzz
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


## This is fine and all but....
@csrf_exempt
def webhook_endpoint(request):
    print(request)
    return HttpResponse(status=200)


## Remove this and replace with SetupAPI from reporting/home/ubuntu/Reporting/backend (?)
## Also move the API Key to locally stored variable, duh.


wcapi = API(
    url="http://harrison.frostedleaf.co/",
    consumer_key="",## Do this properly
    consumer_secret="",## Same
    version="wc/v1",
    timeout=15)

def BatchPipeline(metrc, stock, weight, product_id, store_id, user_info):
    requests.post('http://127.0.0.1:8000/batch', headers={'Authorization':'Token '+user_info['token']}, data={
    "metrc_id": metrc,
    "stock": stock,
    "weight": weight,
    "product": ProductVariants.objects.get(id=product_id),
    "store": Store.objects.get(id=store_id)
}
)

@csrf_exempt
def skucheck(request, sku):
    try:
        product=Product.objects.get(SKU=sku)   
    except Product.DoesNotExist:
        APIchek=wcapi.get('products', params={'sku':sku}).json()
        if len(APIchek)==0:
            return HttpResponse(status=404)
        product=Product.objects.create(SKU=APIchek[0]['sku'], name=APIchek[0]['name'], price=float(APIchek[0]['price']))
        ##
    if request.method == 'GET':
        serializer=ProductSerializer(product)
        return JsonResponse(serializer.data) 



"""
The below function is interesting, but wouldn't this just be largely handled client side?
I'm honestly not sure. 
"""
@csrf_exempt
def product_search(request, name):
    product_list = [prod for prod in Product.objects.all() if fuzz.partial_ratio(prod.name, name) > 0.9]
    return JsonResponse(product_list) 

SecretKey='PFRkc9uBqK8XWY1GoOlG6PP+WvyRb7Pg9L8A+hO0' 
## OKay, so after tonight, I can keep rolling with this shit, I just have a little bit more to figure out, God that fucking inflatable matt thing is going to be a lifesaver. Hopping over to target

## So, for product creation (Linked from the inventory system primarily.) we want to create a post data request with all the information for not only product data, but also batch and productvariant data, part of that will be turned around.

## Maybe this isn't the best place to put this, but this is the function that is creating the product inside product_creation view.
## Oh no tiny change in the schema means I have to rewrite this every time, I wish I had a better fundamental understanding of the REST API package, maybe I should look into that further rather then just kicking everything I can possibly conceive of into functions returned by views.
## Truthfully, I am not even sure this is hooked up to anything. But it's nice to know it's here anyways.
@csrf_exempt ## Alrogjt. 
def CreateProduct(product_data, variant_data, metrc_id, stock, store_id):
    if product_data['existing'] == False:
        product_object=Product.objects.create(SKU=product_data['sku'], name=product_data['name'], description=product_data['description'], composite_enabled=product_data['composite_enabled']) ## figure out how we're creating Product id's
    elif product_data['existing'] == True:
        product_object=Product.objects.get(id=product_data['id'])
    else:
        print('error parsing data') ## Write in better exception handling
        return 'poop' ## and maybe more informative responses to errors.
    if variant_data['existing'] == False: ## Cosnider changing this to a list and looping through multiple variants for quicker inventory input.
        variant_object=ProductVariant.objects.create(variant_name=variant_data['name'], variant_description=variant_data['description'], price=Decimal(variant_data['price']), parent_product=product_object)
        ## Include uninqueness validator for everything especially batch
    elif variant_data['existing'] == True:
        variant_object=ProductVariant.objects.get(id=variant_data['id'])
    else:
        print('bad') ## Cool that's good and informative
        return 'poop' ## Yep, this is professional programming at it's peak right here.
    batch_object=Batch.objects.create(
        metrc_id=metrc_id,
        stock=stock,
        product=variant_object,
        store=Store.objects.get(id=store_id)
        )
    product_object.save()
    variant_object.save()
    batch_object.save()
    return batch_object.id

## Oh wow I remember that actually that's.... Are we creating batches? Should I return a dialog box when there is an existing batch asking if they'd prefer to just reprint or modify the existing version prior to confirmation? Yes, of course I should, that's a good idea. 
@csrf_exempt
def ExistingCheck(request): ## This is wrong, and I don't know how to explain that this is wrong, but it's still the route I'm going.
    if request.method =='GET':
        print(request) ## Okay, what is going on with this clusterfuck over here? first of all, product creation is functioning(ish) so let's separate it out so it doesn't get swallowed up.
##Seriously reconsider how you're doing this, I mean, this will function for now, but this is definitely a target area that I'm going to want to recall and figure out.
@csrf_exempt
def product_creation(request): ## THis is a temporary view for the endpoint test_products (See urls.py)
    if request.method == 'POST':
        print(request.POST.dict())
        TestInput=request.POST.dict()
        if TestInput['product-existing'] == 'True': ## Okay, so do I have multiples of these? How many product creation endpoints do I even have? Ohhhh nevermind I see, this accesses the product creation function I was referring to up there, wow I'm glad I did this, even if it is functionally useless at the moment.
            product_data={
                'existing':True,
                'id':int(TestInput['product-id'])
                }
        elif TestInput['product-existing'] == 'False':
            product_data={'existing':False,
            'sku':TestInput['product-sku'],
            'name':TestInput['product-name'],
            'description':TestInput['product-description'],
            'composite_enabled':True
            }
        if TestInput['variant-existing'] == 'True':
            variant_data = {
                'existing':True,
                'id':int(TestInput['variant-id']),
            }
        elif TestInput['variant-existing'] == 'False':
            variant_data={
                'existing':False,
                'name':TestInput['variant-name'],
                'description':TestInput['variant-description'],
                'price':float(TestInput['variant-price'])
            }
        Answer=CreateProduct(product_data=product_data, variant_data=variant_data, metrc_id=TestInput['batch-metrcid'], stock=int(TestInput['batch-stock']), store_id=int(TestInput['batch-store']))
        return JsonResponse({'Here take this.':Answer})
        pass
        
## OKay, so in order to correct this, I have to do so many things, it's rather frustrating, but okay, so wanna translate this into a serializer, I literally wrote it all out, but in the future it's going to be a good idea to take all this and do it the right way, which long term I'd imagine would actually be simpler.

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

## ugfh
class ProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class= ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class StoreViewSet(viewsets.ModelViewSet):
    queryset=Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

class CustomerViewSet(viewsets.ModelViewSet):
    queryset=Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]


class RewardPointsViewSet(viewsets.ModelViewSet):
    queryset=RewardPoints.objects.all()
    serializer_class = RewardPointsSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset=ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]

class BatchViewset(viewsets.ModelViewSet):
    queryset=Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows register to be viewed or edited.
    """
    ## Do we need any additional processors? I'm perplexed as to how I'm going 
    queryset=Register.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated] ## Need to reconsider and redefine, no shit. ## But actually this is super useful, the way this is set out, it's finally starting to click.


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username':user.username,
            'app_access':Employee.objects.get(employ_user=user).app_access
        })

##### Don't think I need this function anymore, as QR codes will be handled and transitioned into metrc_ids or batch ids, either way it's chill and I don't need any direct QR code handling from the API.
## Simple request, returns QR code for product labels, ugh I need to get out of tremote desktop lag is killing me
##def ReturnProductQR(request):
##Finish this out later, what's important right now is getting the register running and testing.
