from celery.task import Task
from celery.registry import tasks
from bs4 import BeautifulStoneSoup
from tendenci.apps.wp_importer.utils import get_media, get_posts, get_pages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from tendenci.apps.site_settings.utils import get_setting

class WPImportTask(Task):

    def run(self, file_name, user, **kwargs):
        """
        Parse the given xml file using BeautifulSoup. Save all Article, Redirect and Page objects.
        """
        f = open(file_name, 'r')
        xml = f.read()
        f.close()

        soup = BeautifulStoneSoup(xml)
        items = soup.find_all('item')

        for item in items:
            post_type = item.find('wp:post_type').string
            post_status = item.find('wp:status').string

            if post_type == 'attachment':
                get_media(item, user)
                # Note! This script assumes all the attachments come before
                # posts and pages in the xml. If this ends up changing,
                # do two loops, one with attachments and the second with posts and pages.
            elif post_type == 'post' and post_status == 'publish':
                get_posts(item, user)
            elif post_type == 'page' and post_status == 'publish':
                get_pages(item, user)

        if user.email:
            context = {
                'SITE_GLOBAL_SITEDISPLAYNAME': get_setting('site', 'global', 'sitedisplayname'),
                'SITE_GLOBAL_SITEURL': get_setting('site', 'global', 'siteurl'),
            }
            subject = ''.join(render_to_string(template_name=('notification/wp_import/short.txt'), context=context).splitlines())
            body = render_to_string(template_name=('notification/wp_import/full.html'), context=context)

            #send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.content_subtype = 'html'
            email.send(fail_silently=True)

tasks.register(WPImportTask)
