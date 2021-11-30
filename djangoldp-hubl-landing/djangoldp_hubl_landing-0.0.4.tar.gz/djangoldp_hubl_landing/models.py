
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from djangoldp.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader


class IntroProfile(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="prénom")
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name="métier")
    subtitle = models.CharField(max_length=50, blank=True, null=True, verbose_name="2ème ligne")
    picture = models.ImageField(blank=True, null=True, verbose_name="photo")

    def __str__(self):
        return self.name

class Network(Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="métier")
    picture = models.ImageField(blank=True, null=True, verbose_name="photo")

    def __str__(self):
        return self.name

class FAQ(Model):
    question = models.TextField(blank=True, null=True, verbose_name="Question")
    answer = models.TextField(blank=True, null=True, verbose_name="Réponse")
    
    def __str__(self):
        return self.question

class GeneralContact(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="nom")
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name="email")
    message = models.TextField(blank=True, null=True, verbose_name="message")

    class Meta:
        anonymous_perms = ['view', 'add']
    
    def __str__(self):
        return self.name

class JoinContact(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="nom")
    firstname = models.CharField(max_length=25, blank=True, null=True, verbose_name="prénom")
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name="email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="téléphone")
    city = models.CharField(max_length=25, blank=True, null=True, verbose_name="ville")

    class Meta:
        anonymous_perms = ['view', 'add']
    
    def __str__(self):
        return self.name

class ClientContact(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="nom")
    firstname = models.CharField(max_length=25, blank=True, null=True, verbose_name="prénom")
    role = models.CharField(max_length=25, blank=True, null=True, verbose_name="rôle")
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name="email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="téléphone")
    companyname =  models.CharField(max_length=25, blank=True, null=True, verbose_name="nom de l'entreprise")
    city = models.CharField(max_length=25, blank=True, null=True, verbose_name="ville")
    distancial = models.CharField(max_length=25, blank=True, null=True, verbose_name="travail à distance")
    price = models.CharField(max_length=25, blank=True, null=True, verbose_name="Budget ou TJM")
    startdate= models.DateField(blank=True, null=True, verbose_name="Date de démarrage")
    duration= models.CharField(max_length=50, blank=True, null=True, verbose_name="Durée de la mission")
    message = models.TextField(blank=True, null=True, verbose_name="Description de la mission")


    class Meta:
        anonymous_perms = ['view', 'add']
    
    def __str__(self):
        return self.name

@receiver(post_save, sender=GeneralContact)
def send_email_on_generalcontact(sender, instance, created, **kwargs):
    if created:
       messagegeneral = loader.render_to_string('contactgeneral_email.txt', {'contact': instance})
       messagegeneralresponse = loader.render_to_string('contactgeneralresponse_email.txt', {'contact': instance})
       recipient = getattr(settings, 'CONTACT_TO_EMAIL', 'contact@hubl.world')
       send_mail('HUBL : Une nouvelle demande de contact', messagegeneral, recipient, [recipient])
       send_mail('Votre message nous a bien été transmis', messagegeneralresponse, recipient, {instance.email})

@receiver(post_save, sender=JoinContact)
def send_email_on_joincontact(sender, instance, created, **kwargs):
    if created:
       messagejoin = loader.render_to_string('contactjoin_email.txt', {'contact': instance})
       messagejoinresponse = loader.render_to_string('contactjoinresponse_email.txt', {'contact': instance})
       recipient = getattr(settings, 'CONTACT_TO_EMAIL', 'contact@hubl.world')
       send_mail('Une nouvelle demande de rejoindre hubl', messagejoin, recipient, [recipient])
       send_mail('Ton message nous a bien été transmis', messagejoinresponse, recipient, {instance.email})

@receiver(post_save, sender=ClientContact)
def send_email_on_clientcontact(sender, instance, created, **kwargs):
    if created:
       messagefromclient = loader.render_to_string('contact_email_from_client.txt', {'contact': instance})
       messageclient = loader.render_to_string('client_email.txt', {'contact': instance})
       recipient = getattr(settings, 'CONTACT_TO_EMAIL', 'contact@hubl.world')
       send_mail("Un nouveau message d'un client", messagefromclient, recipient, [recipient])
       send_mail('Votre message nous a bien été transmis', messageclient, recipient, {instance.email})
 