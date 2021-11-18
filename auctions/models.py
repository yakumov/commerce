from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class LotImage(models.Model):
    titleimage = models.CharField(max_length=64)
    lot_image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"{self.titleimage} ({self.id})" 


class LotCategory(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}" 


class Bid(models.Model):
    bid_user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    bid_price = models.IntegerField()
    bid_lot_id = models.IntegerField()

    def __str__(self):
        return f"{self.bid_user} ({self.bid_lot_id}) $ {self.bid_price}" 


class Lot(models.Model):
    lot_name = models.CharField(max_length=64)
    lot_price = models.IntegerField() 
    lot_description = models.CharField(max_length=256)
    lot_date = models.DateTimeField(auto_now=True)
    lot_status = models.BooleanField()
    lot_author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    #lot_author = models.CharField(max_length=64)
    #lot_category = models.CharField(max_length=64)
    lot_category = models.ForeignKey(LotCategory, on_delete=models.CASCADE, default=1)
    lot_viewimage = models.ForeignKey(LotImage, on_delete=models.CASCADE, related_name="imagelot", default=1)
    lot_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="lotbid", default=1)

    def __str__(self):
        return f"{self.id}: {self.lot_name} and {self.lot_price} and {self.lot_description} and {self.lot_date} and {self.lot_author} and {self.lot_status} and {self.lot_category} and {self.lot_viewimage} and {self.lot_bid}"

class Watchlist(models.Model):
    watch_user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    watch_lot_id = models.ForeignKey(Lot, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.watch_user} ({self.watch_lot_id})" 


class Comment(models.Model):
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    comment_text = models.TextField(null=True, blank=True)
    comment_date = models.DateTimeField(auto_now=True)
    comment_lot_id = models.IntegerField()

    def __str__(self):
        return f"{self.comment_user} [{self.comment_lot_id}] ({self.comment_date}):-> {self.comment_text}" 
