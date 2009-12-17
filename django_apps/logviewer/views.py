from django.conf.urls.defaults import *
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, Http404
from django.utils import simplejson
from models import Account, Message

import logging
import datetime
import simplejson

#If the time difference between two messages is greater than this, they are
#part of different conversations
CONVERSATION_LIMIT = 60*60

def account_list(request):
    account_list = Account.objects.filter(owned=True).order_by('protocol')
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
    
    conversations = []
    conversation = []
    last_message = None
    for message in messages:
        #A conversation ends if nothing is said for 60 minutes
        if last_message is not None and message.timestamp - last_message.timestamp > datetime.timedelta(0, CONVERSATION_LIMIT):
            conversations.append(conversation)
            conversation = []
        conversation.append(message)
        last_message = message
    conversations.reverse()
    return render_to_response("message_list.html", 
                              {"protocol":protocol, "account":user_account, "other_account":other_account, 
                               "conversations":conversations})

def get_conversation(message):
    account1 = message.sender
    account2 = message.receiver
    start_time = message.timestamp - datetime.timedelta(0, CONVERSATION_LIMIT)
    end_time = message.timestamp + datetime.timedelta(0, CONVERSATION_LIMIT)
    # First get any messages before this one in the conversation
    all_messages = Message.objects.filter(sender=account1, receiver=account2) | Message.objects.filter(sender=account2, receiver=account1)
    earlier = all_messages.filter(timestamp__gt=start_time).filter(timestamp__lt=message.timestamp).order_by('timestamp')
    after = all_messages.filter(timestamp__lt=end_time).filter(timestamp__gt=message.timestamp).order_by('timestamp')
    conversation = list(earlier) + [message] + list(after)
    return conversation

def search(request, protocol=None, uid=None, other_uid=None):
    search_terms = request.GET.get("search_terms", "")
    format = request.GET.get("format", "html")
    
    messages = Message.objects
    user_account = None
    other_account = None
    if uid is not None:
        user_account = get_object_or_404(Account, protocol=protocol, uid=uid)
        messages = messages.filter(sender=user_account) | messages.filter(receiver=user_account)
    if other_uid is not None:
        other_account = get_object_or_404(Account, protocol=protocol, uid=other_uid)
        messages = messages.filter(sender=other_account) | messages.filter(receiver=other_account)
    #TODO: Tokenize the search terms
    messages = messages.filter(text__contains=search_terms).order_by('timestamp')
    #TODO: Rank by date and search_term occurence
    
    conversations = [get_conversation(message) for message in messages]
    conversations.reverse()

    #Either render a template with the messages or return them in JSON form
    if format == "json":
        results = {"search":search_terms}
        json = simplejson.dumps(results)
        return HttpResponse(json, mimetype="application/json")
    elif format == "html":
        return render_to_response("includes/_conversations.html", 
                                  {"conversations":conversations,
                                   "account":user_account, 
                                   "other_account":other_account,
                                   "search_results":messages})
    else:
        raise Exception("Unknown format")
    
def get_or_create_account(protocol, uid, owner_account = None):
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
        print "Did not post"
        raise Http404("You must post to this URL")

    print request.POST
    print protocol
    print uid

    receiver_account = get_or_create_account(protocol, request.POST["receiver_account"], request.POST["owner_account"])
    sender_account = get_or_create_account(protocol, request.POST["sender_account"], request.POST["owner_account"])  
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