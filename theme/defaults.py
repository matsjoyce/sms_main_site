from mezzanine.conf import register_setting

register_setting(
    name="SITE_ICON",
    label="Site Icon",
    description="The icon shown next to the site title",
    editable=True,
    default="",
)

register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    description="Sequence of setting names available within templates.",
    editable=False,
    default=("SITE_ICON",),
    append=True,
)
