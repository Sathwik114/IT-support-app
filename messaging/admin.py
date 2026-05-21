from django.contrib import admin
from .models import Conversation, Group, ConversationParticipant, Message, TypingIndicator, MessageReadReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation_type', 'created_at', 'updated_at']
    list_filter = ['conversation_type', 'created_at']
    search_fields = ['id']
    filter_horizontal = ['participants']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by']
    list_filter = ['created_by']
    search_fields = ['name', 'description']
    filter_horizontal = ['admins']


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'joined_at', 'is_muted']
    list_filter = ['joined_at', 'is_muted']
    search_fields = ['user__username', 'conversation__id']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'message_type', 'status', 'created_at']
    list_filter = ['message_type', 'status', 'created_at', 'is_deleted_for_everyone']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'is_typing', 'last_updated']
    list_filter = ['is_typing', 'last_updated']
    search_fields = ['user__username']


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__username', 'message__id']
