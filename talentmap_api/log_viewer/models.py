from django.db import models


class LogEntry(models.Model):
    '''
    Represents a log file
    '''

    text = models.TextField(null=True)

    class Meta:
        managed = False
        ordering = ["text"]
