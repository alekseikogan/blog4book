from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        """QuerySet объектов, подлежащих включению в карту сайта."""

        return Post.published.all()
    
    def lastmod(self, obj):
        """Получает каждый возвращаемый методом items() объект 
        и возвращает время последнего изменения объекта."""

        return obj.updated
    