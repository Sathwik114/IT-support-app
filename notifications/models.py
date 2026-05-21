from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification model for user notifications."""
    
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('mention', 'Mention'),
        ('group_added', 'Added to Group'),
        ('group_removed', 'Removed from Group'),
        ('message_deleted', 'Message Deleted'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.ForeignKey('messaging.Message', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    conversation = models.ForeignKey('messaging.Conversation', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.get_default_title()
        if not self.body:
            self.body = self.get_default_body()
        super().save(*args, **kwargs)
    
    def get_default_title(self):
        """Generate default title based on notification type."""
        titles = {
            'new_message': 'New Message',
            'mention': 'You were mentioned',
            'group_added': 'Added to Group',
            'group_removed': 'Removed from Group',
            'message_deleted': 'Message Deleted',
        }
        return titles.get(self.notification_type, 'Notification')
    
    def get_default_body(self):
        """Generate default body based on notification type."""
        if self.message:
            sender = self.message.sender.get_full_name() or self.message.sender.username
            if self.notification_type == 'new_message':
                return f"{sender} sent you a message"
            elif self.notification_type == 'mention':
                return f"{sender} mentioned you"
        return ''
