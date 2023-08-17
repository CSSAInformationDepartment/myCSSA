from PublicSite import models


def LoadPagetoRegister(uri, title, template):
    query_set = models.PageRegister.objects.filter(uri=uri)
    if not query_set:
        newRegister = models.PageRegister(
            uri=uri,
            title=title,
            templates=template
        )
        newRegister.save()
        print("New Registered")
    else:
        print("Page Already Registered "+title)
