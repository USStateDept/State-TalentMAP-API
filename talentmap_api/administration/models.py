from django.db import models


class HomepageBanner(models.Model):
    '''
    The banner for the homepage
    '''
    text = models.TextField(null=False, help_text="The text for the banner")
    is_visible = models.BooleanField(default=False)
    print('-------------------------------------------------------------------')
    print('in HomepageBanner models. text:', text)
    print('in HomepageBanner models. is_visible:', is_visible)
    print('-------------------------------------------------------------------')

    class Meta:
        managed = True


class AboutPage(models.Model):
    '''
    About page content
    '''
    content = models.TextField(help_text="The content of the about page")
    print('-------------------------------------------------------------------')
    print('in AboutPage models. models:', models)
    print('in AboutPage models. models.Model:', models.Model)
    print('in AboutPage models. content:', content)
    print('-------------------------------------------------------------------')

    class Meta:
        managed = True


class FeatureFlags(models.Model):
    '''
    Feature Flags content
    '''
    print('-------------------------------------------------------------------')
    print('in featureflags models. models:', models)
    print('in featureflags models. models.Model:', models.Model)
    content = models.TextField(help_text="The content of the Feature Flags config file")
    print('in featureflags models. content:', content)
    print('-------------------------------------------------------------------')

    class Meta:
        managed = True
