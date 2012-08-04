#coding:utf-8

from django.contrib.syndication.views import Feed
from cms.models import BlogEntry

class LatestBlogEntriesFeed(Feed):
    title = "Новые посты"
    link = "/content/BLOG/"
    description = "Новые посты"
    def items(self):
      return BlogEntry.objects.filter(close_date__isnull=True).order_by('-pub_date')[:5]
    def item_title(self, item):
      return item.title
    def item_description(self, item):
      return item.get_rss_content(200)
