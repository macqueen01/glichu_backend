from rest_framework import serializers
from main.models import *
from django.contrib.auth import authenticate
from django.db import models



class MessageManager(models.Manager):

    def get_message_of_remix(self, remix_id):
        if self.filter(remix__id=remix_id).exists():
            return self.filter(remix__id=remix_id)
        return None
    
    def get_message_of_sender(self, sender_id):
        if self.filter(sender__id=sender_id).exists():
            return self.filter(sender__id=sender_id)
        return None
    
    def get_message_of_receiver(self, receiver_id):
        if self.filter(receiver__id=receiver_id).exists():
            return self.filter(receiver__id=receiver_id)
        return None
    
    def get_message_of_sender_and_receiver(self, sender_id, receiver_id):
        if self.filter(sender__id=sender_id, receiver__id=receiver_id).exists():
            return self.filter(sender__id=sender_id, receiver__id=receiver_id)
        return None
    
    def create(self, sender, receiver, content, remix):
        message = self.model(sender=sender, receiver=receiver, content=content, remix=remix)
        message.save()
        return message
    
    def get_unread_messages(self, receiver_id):
        if self.filter(receiver__id=receiver_id, is_read=0).exists():
            return self.filter(receiver__id=receiver_id, is_read=0)
        return None

    



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_messages')

    is_read = models.IntegerField(default=0)

    content = models.TextField(blank=True, null=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    remix = models.ForeignKey('Remix', on_delete=models.CASCADE, null=True)

    objects = MessageManager()

    def __str__(self):
        return "Message from " + self.sender.username + " to " + self.receiver.username + "in remix" + self.remix.title
    
    def get_sender(self):
        return self.sender
    
    def get_receiver(self):
        return self.receiver
    
    def get_content(self):
        return self.content
    
    def turn_to_read(self):
        self.is_read = 1
        self.save()
        return self
    
    def turn_to_unread(self):
        self.is_read = 0
        self.save()
        return self
    
    def get_remix(self):
        return self.remix
    

    
