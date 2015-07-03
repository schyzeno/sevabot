#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A module that allows users to submit and retrieve trivia based on group name.
"""
import os
import sys
import random
import pymongo
from pymongo import MongoClient
import datetime

progname = 'trivia'

def get_next_trivia_sequence(chat_id):
    client = MongoClient()
    db = client.sevabot 
    sequence = db.counters.find_one({"collection":"trivia","chat_id":chat_id})['seq']
    nextSequence = sequence+1
    return nextSequence

def increment_trivia_sequence(chat_id)
    client = MongoClient()
    db = client.sevabot 
    sequence = db.counters.find_one({"collection":"trivia","chat_id":chat_id})['seq']
    nextSequence = sequence+1
    result = db.counters.update(
        {"collection": "trivia","chat_id":chat_id},
        {"$set": {"seq":(nextSequence)}}
    )
    return
    
def get_max_sequence(chat_id):
    client = MongoClient()
    db = client.sevabot 
    sequence = db.counters.find_one({"collection": "trivia","chat_id":chat_id})['seq']
    return sequence

def get_trivia(chat_id):
    """Retrieves trivia from mongoDB"""
    random.seed()
    client = MongoClient()
    db = client.sevabot 
    randomInteger = random.randint(1,get_max_sequence(chat_id))
    trivia_info = db.trivia.find_one({"chat_id": chat_id,"_id":{"$gte":randomInteger}})
    print('>'+trivia_info['info'])
    return

def trivia_already_exists(db,chat_id,info):
    return db.trivia.find({"chat_id": chat_id, "info": info}).count()==0
    
def chat_sequence_exists(db,chat_id):
    return db.counters.find({"collection":"trivia","chat_id": chat_id}).count()>0

def insert_chat_sequence(db,chat_id)
    db.counters.insert({"collection":"trivia","chat_id":chat_id,"sequence":1}))
    return 1
    
def add_trivia(chat_id,full_name,info):
    """Adds trivia to mongoDB"""
    client = MongoClient()
    db = client.sevabot 
    if(chat_sequence_exists(chat_id)):
        sequence = get_next_trivia_sequence(chat_id)
    else:
        sequence = insert_chat_sequence()
    increment_trivia_sequence(db,chat_id)
    result = db.trivia.insert_one(
        {
                "_id": sequence,
                "info": info,
                "chat_id": chat_id,
                "full_name": full_name,
                "date": datetime.datetime.utcnow()
        }
    )
    return

def main(args):
    """The program entry point."""
    client = MongoClient()
    db = client.sevabot 
    
    if len(args) <= 0:
        get_trivia(os.environ["SKYPE_CHATNAME"])
        return

    cmd = args[0]

    if cmd == 'help':
        print 'Usage:'
        print '       !trivia                  -- returns some trivia'
        print '       !trivia help             -- this dialouge'        
        print '       !trivia new [new_trivia] -- adds some new trivia'
        return
    elif cmd == 'new':
        new_trivia = ""
        if len(args) > 1:
            for i in range(1,len(args)):
                new_trivia = new_trivia+" "+args[i]
            if(trivia_already_exists(db,os.environ["SKYPE_CHATNAME"],new_trivia)):
                add_trivia(os.environ["SKYPE_CHATNAME"],os.environ["SKYPE_USERNAME"],new_trivia)
                print 'Thanks for the contribution '+ os.environ["SKYPE_FULLNAME"]
            else:
                print 'I already knew that, '+ os.environ["SKYPE_FULLNAME"]             
            return
        else:
            get_trivia(os.environ["SKYPE_CHATNAME"])
            return
    else:
        get_trivia(os.environ["SKYPE_CHATNAME"])
        return
    return

if __name__ == '__main__':
    main(sys.argv[1:])