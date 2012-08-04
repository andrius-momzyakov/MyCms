from django.contrib import admin
from cms.models import StandardSection, StandardPage, UserProfile, Template, BlogPage, \
                        BlogEntry, BasePage, BlogEntryComment, RequestLog, BlogEntryTopic,\
			SiteMessage

admin.site.register(StandardSection)
admin.site.register(StandardPage)
admin.site.register(UserProfile)
admin.site.register(Template)
admin.site.register(BlogPage)
admin.site.register(BlogEntry)
admin.site.register(BasePage)
admin.site.register(BlogEntryComment)
admin.site.register(RequestLog)
admin.site.register(BlogEntryTopic)
admin.site.register(SiteMessage)


