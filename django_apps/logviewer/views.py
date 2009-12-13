from django.conf.urls.defaults import *
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, Http404
from django.utils import simplejson
from models import Account, Message

import logging
import datetime

def account_list(request):
    account_list = Account.objects.filter(owned=True)
    return render_to_response("account_list.html", {"account_list":account_list})
    
def other_account_list(request, protocol, uid):
    user_account = get_object_or_404(Account, protocol=protocol, uid=uid)
    account_list = Account.objects.filter(protocol=protocol).exclude(uid=uid)
    return render_to_response("other_account_list.html", 
                              {"protocol":protocol, "uid":uid, "account_list":account_list})


def message_list(request, protocol, uid, other_uid):
    user_account = get_object_or_404(Account, protocol=protocol, uid=uid)
    other_account = get_object_or_404(Account, protocol=protocol, uid=other_uid)
    messages = Message.objects.filter(sender=user_account, receiver=other_account).order_by('timestamp')
    messages = messages | Message.objects.filter(sender=other_account, receiver=user_account).order_by('timestamp')
    return render_to_response("message_list.html", 
                              {"protocol":protocol, "account":user_account, "other_account":other_account, 
                               "messages":messages})
    
def get_account(protocol, uid, owner_account = None):
    user_accounts = Account.objects.filter(uid=uid).filter(protocol=protocol)
    if len(user_accounts) == 0:
        user_account = Account()
        if owner_account is not None:
            if owner_account == uid:
                user_account.owned = True
        user_account.protocol = protocol
        user_account.uid = uid
        user_account.save()
    else:
        user_account = user_accounts[0]
    return user_account
    
def message_add(request, protocol, uid):
    if request.method != "POST":
        raise Http404("You must post to this URL")

    print request.POST
    print protocol
    print uid

    receiver_account = get_account(protocol, request.POST["receiver_account"], request.POST["owner_account"])
    sender_account = get_account(protocol, request.POST["sender_account"], request.POST["owner_account"])  
    if sender_account.full_name == "":
        sender_account.full_name = request.POST["alias"]
        sender_account.save()
    
    timestamp = datetime.datetime.strptime(request.POST["timestamp"][:-6], "%Y-%m-%dT%H:%M:%S")    
    messages = Message.objects.filter(sender=sender_account).filter(receiver=receiver_account).filter(timestamp=timestamp)
    if len(messages) > 0:
        return HttpResponse(simplejson.dumps({"result":False,"reason":"Duplicate message"}), mimetype="application/json")
    message = Message()
    message.receiver = receiver_account
    message.sender = sender_account
    message.timestamp = timestamp
    message.text = request.POST["message_text"]
    message.client_type = request.POST["client_type"]
    message.host = request.POST["host"]
    message.save()

    data = simplejson.dumps({"result":True})
    return HttpResponse(data, mimetype="application/json")