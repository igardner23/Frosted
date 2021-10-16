from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DecimalField, IntegerField
from simple_history.models import HistoricalRecords
from djmoney.models.fields import MoneyField



"""
Defines main Product model for each product. 


"""
class Product(models.Model):
    SKU=models.CharField(max_length=200) 
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=2000)
    composite_enabled=models.BooleanField()
    status_choices=(('IN_STOCK','Pending'),('Completed','Completed'))
    woo_id=models.CharField(max_length=100)
    

class Store(models.Model):
    def __str__(self):
        return self.store_name
    
    store_name=models.CharField(max_length=255, unique=True) 
    store_id=models.IntegerField() 



class Employee(models.Model):
    employee_id=models.CharField(max_length=255) 
    employee_key=models.CharField(max_length=255)
    employ_user=models.ForeignKey(User, on_delete=models.CASCADE)
    access_choices = [
     ('budtender', 'Bud Tender'), 
     ('manager','Manager'), 
     ('inventory','Inventory Management'), 
     ('admin','Administration')]
    app_access = models.CharField(max_length=100, choices=access_choices)
    pass 

class Customer(models.Model):
    name=models.CharField(max_length=100)
    woo_id_link=models.CharField(max_length=50)
    email=models.CharField(max_length=100)

class RewardPoints(models.Model):
    points=models.BigIntegerField()
    customer=models.ForeignKey(Customer, on_delete=models.CASCADE)
    history=HistoricalRecords



# Haha, yeah no shit. 
## The Product Variant model is very confusing

class ProductVariant(models.Model):
    def __str__(self):
        return self.variant_name
    variant_name=models.CharField(max_length=200, unique=True)
    variant_description=models.CharField(max_length=10000)
    price=MoneyField(decimal_places=2, max_digits=8)
    parent_product=models.ForeignKey(Product, on_delete=models.CASCADE)
    default_weight=models.FloatField()
    history=HistoricalRecords()
    woo_association = models.IntegerField() 
    def OverallStoreStock(self, store_id):
        batches=Batch.objects.filter(store=Store.objects.get(id=store_id), product=self)
        stock=0
        for batch in batches:
            stock+=batch.stock
        return stock
    pass




class Batch(models.Model):
    def __str__(self):
        return self.metrc_id
    metrc_id=models.CharField(max_length=200, unique=True)
    stock=models.PositiveIntegerField()
    weight=models.FloatField()
    product=models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    store=models.ForeignKey(Store, on_delete=models.CASCADE)
    history=HistoricalRecords()

class OrderType(models.Model):
    type_name=models.CharField(max_length=40)

class Order(models.Model):
    order_id=models.IntegerField() 
    order_status=models.CharField(max_length=100) 
    payment_method= models.CharField(max_length=100) 

    order_type=models.ForeignKey(OrderType, on_delete=models.CASCADE)
    history=HistoricalRecords()
    pass


class PointChange(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.BigIntegerField()
    points = models.BigIntegerField()
    reward_account=models.ForeignKey(RewardPoints, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    date = models.DateTimeField()
    processed = models.BooleanField()
    history=HistoricalRecords()


class LineItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    batch=models.ForeignKey(Batch, on_delete=models.CASCADE)
    fulfilled=models.BooleanField()


class TaxType(models.Model):
    type_name = models.CharField(max_length=200)


class Tax(models.Model):
    activate_on=models.ForeignKey(TaxType, on_delete=models.CASCADE)
    tax_name=models.CharField(max_length=50)
    tax_amount=models.DecimalField(decimal_places=2, max_digits=15)


class Register(models.Model):

    drawer_name=models.CharField(max_length=255)
    cash_drawer=models.DecimalField(decimal_places=2, max_digits=9)
    drawer_holder=models.ForeignKey(Employee, on_delete=models.CASCADE) 
    store=models.ForeignKey(Store, on_delete=models.CASCADE)
    history=HistoricalRecords()












