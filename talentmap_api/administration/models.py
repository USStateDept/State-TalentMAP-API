from django.db import models

class HomepageBanner(models.Model):
    '''
    The banner for the homepage
    '''
    text = models.CharField(max_length=50, null=False, help_text="The text for the banner")
    is_visible = models.BooleanField(default=False)

    class Meta:
        managed = True


class AboutPage(models.Model):
    '''
    About page content
    '''
    content = models.TextField(help_text="The content of the about page")

    class Meta:
        managed = True
