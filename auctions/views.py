from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def viewdetails(request, lot_id):
    current_lot = Lot.objects.get(pk=lot_id)
    print(f"lotid={lot_id}")

    if request.method == "POST" and "createbid" in request.POST and request.POST["bidprice"] != '':
        #print(f"request={request.POST}")
        lastbidprice = int(request.POST["bidprice"])
        userid = request.POST["userid"]
        biduser = User.objects.get(id=userid)
        print(f"bidprice={lastbidprice}")
        print(f"userid={userid}")
        print(f"biduser={biduser}")
        #oldprice = Lot.objects.get(pk=lot_id)
        oldprice = Lot.objects.values_list('lot_price', flat=True).get(pk=lot_id)
        print(f"oldprice={oldprice}")
        if lastbidprice <= oldprice:
            print("bid no")
            print(f"corentlot={current_lot}")
            return render(request, "auctions/viewdetails.html", {
                 "message": "The bid must be more then oldprice !",
                 "currentlot": current_lot,
                 "currentbids": Bid.objects.all().filter(bid_lot_id=lot_id).order_by('-id'),
                 "comments": Comment.objects.all().filter(comment_lot_id=lot_id).order_by('-id'),
                  "allbid": Bid.objects.all()
         })
        else:
            print("bid ok")
            #обновить таблицу лот значення бид и прайс
            newbid = Bid.objects.create(bid_user=biduser, bid_price=lastbidprice, bid_lot_id=lot_id)
            newbid.save()
            print(f"newbid={newbid}")
            current_lot.lot_price = lastbidprice
            current_lot.lot_bid = newbid
            current_lot.save()
            print(f"current_lotn={current_lot}")
            return HttpResponseRedirect(reverse("viewdetails", args=(current_lot.id,)))
    elif request.method == "POST" and "createcomment" in request.POST:
        print("lot comment")
        print(f"lotcomment={request.POST}")
        userid = request.POST["userid"]
        commentuser = User.objects.get(id=userid)
        commenttext = request.POST["commenttext"]
        commentdate = datetime.datetime.now()
        print(f"comuser={commentuser}, comtext={commenttext}, comdat={commentdate}")
        newcomment = Comment.objects.create(comment_user=commentuser, comment_text=commenttext, comment_date=commentdate, comment_lot_id=lot_id)
        newcomment.save()
        return HttpResponseRedirect(reverse("viewdetails", args=(current_lot.id,)))
    elif request.method == "POST" and "closedlot" in request.POST:
        print("lot closed")
        current_lot.lot_status = False
        current_lot.save()
        return HttpResponseRedirect(reverse("viewdetails", args=(current_lot.id,)))
    else:
        return render(request, "auctions/viewdetails.html", {
        "currentlot": current_lot,
        "currentbids": Bid.objects.all().filter(bid_lot_id=lot_id).order_by('-id'),
        "comments": Comment.objects.all().filter(comment_lot_id=lot_id).order_by('-id'),
         "allbid": Bid.objects.all()
    })