from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Bid, LotCategory, User, Lot, LotImage, Watchlist
from .forms import LotImageForm
import datetime

def index(request):
    #print(f"{Lot.objects.all()}")
    if request.method == "POST" and request.POST['category'] != "1":
        category = request.POST['category']
        #print(f"request={request.POST}")
        #print(f"catr={category}")
        return render(request, "auctions/index.html", {
        "lots": Lot.objects.all().filter(lot_category=category).filter(lot_status=True).order_by('-id'),
        "lotimages": LotImage.objects.all(),
        "userinf": User.objects.all(),
        "categorylot": LotCategory.objects.all()
        })
    else:
       # print(f"shalom")
        return render(request, "auctions/index.html", {
        "lots": Lot.objects.all().filter(lot_status=True).order_by('-id'),
        "lotimages": LotImage.objects.all(),
        "userinf": User.objects.all(),
        "categorylot": LotCategory.objects.all()
    })


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


def createlot(request):
    #print(f"{Lot.objects.all()}")
    if request.method == "POST":
        print(f"requestcrlot={request.POST}")
        form = LotImageForm(request.POST, request.FILES)
        lot_name = request.POST["lotname"]
        lot_price = request.POST["lotprice"]
        lot_description = request.POST["lotdescription"]
        lot_categoryid = request.POST["category"]
        lot_category = LotCategory.objects.get(id=lot_categoryid)
        lot_authorid = request.POST["userid"]
        lot_author = User.objects.get(id=lot_authorid)
        lot_status = True
        lot_date = datetime.datetime.now()
        lot_viewimage = form.instance
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            print(f"imagobj={img_obj}")
            lot = Lot.objects.create(lot_name=lot_name, lot_price=lot_price, lot_description=lot_description, lot_date=lot_date, lot_status=lot_status, lot_author=lot_author, lot_category=lot_category, lot_viewimage=lot_viewimage)
            lot.save()
            current_lot = Lot.objects.get(pk=lot.id)
            print(f"lotid={current_lot}")
            return render(request, 'auctions/viewdetails.html', {
                "currentlot": current_lot,
                'form': form,
                'img_obj': img_obj,
                "categorylot": LotCategory.objects.all()
                })
    else:
        form = LotImageForm()
    return render(request, 'auctions/createlot.html', {
        'form': form,
        "categorylot": LotCategory.objects.all()
        })


def watchlist(request, user_id):
    print("watchlist work")
    print(f"requestaaa={request.POST}")
    #print(f"{Lot.objects.all()}")
    if request.method == "POST" and "delwatchlist" in request.POST:
         print("watchlist work if0")
         print(f"requestbbb={request.POST}")
         userid = request.POST['userid']
         watchuser = User.objects.get(id=userid)
         delwatchlist = request.POST['delwatchlist']
         watchlist = Watchlist.objects.get(pk=delwatchlist)
         print(f"delwatclist={delwatchlist}")
         print(f"watchlistid={watchlist}")
         watchlist.delete()
         #currentid = request.POST['currentid']
         #watchlotid = Lot.objects.get(id=currentid)
         return render(request, "auctions/watchlist.html", {
         "lotimages": LotImage.objects.all(),
         "userinf": User.objects.all(),
         "categorylot": LotCategory.objects.all(),
         "watchlists": Watchlist.objects.all().filter(watch_user=watchuser).exclude(id=1)
         })
    elif request.method == "POST" and "addwatchlist" in request.POST:
         print("watchlist work if1")
         userid = request.POST['userid']
         watchuser = User.objects.get(id=userid)
         currentid = request.POST['currentid']
         watchlotid = Lot.objects.get(id=currentid)
         print(f"userid={userid}")
         print(f"currentid={currentid}")
         watchlist = Watchlist.objects.create(watch_user=watchuser, watch_lot_id=watchlotid)
         watchlist.save()
         return render(request, "auctions/watchlist.html", {
         "lotimages": LotImage.objects.all(),
         "userinf": User.objects.all(),
         "categorylot": LotCategory.objects.all(),
         "watchlists": Watchlist.objects.all().filter(watch_user=watchuser).exclude(id=1)
         })
    elif request.method == "POST" and request.POST['category'] != "1":
        print("watchlist work if2")
        category = request.POST['category']
        print(f"requestwatch={request.POST}")
        userid = request.POST['userid']
        watchuser = User.objects.get(id=userid)
        #print(f"catr={category}")
        #print(f"watchlistcat={Watchlist.objects.all().filter(watch_lot_id__lot_category=category)}")
        print(f"watchlistcat={Watchlist.objects.values_list('watch_lot_id__lot_category', flat=True).get(pk=1)}")
        return render(request, "auctions/watchlist.html", {
        "lots": Lot.objects.all().filter(lot_category=category),
        "lotimages": LotImage.objects.all(),
        "userinf": User.objects.all(),
        "categorylot": LotCategory.objects.all(),
        "watchlists": Watchlist.objects.all().filter(watch_user=watchuser).filter(watch_lot_id__lot_category=category).exclude(id=1)
        })
    else:
       # print(f"shalom")
        print("watchlist work if3")
        userid = user_id
        watchuser = User.objects.get(id=userid)
        return render(request, "auctions/watchlist.html", {
        "lots": Lot.objects.all(),
        "lotimages": LotImage.objects.all(),
        "userinf": User.objects.all(),
        "categorylot": LotCategory.objects.all(),
        "watchlists": Watchlist.objects.all().filter(watch_user=watchuser).exclude(id=1)
    })