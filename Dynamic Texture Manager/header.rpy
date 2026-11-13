init -990 python:
    store.mas_submod_utils.Submod(
        author="The Encoders Club",
        name="Dynamic Texture Manager",
        description=_("Advanced system for managing and applying custom dynamic textures within the game without overwriting the base files."),
        version="2.0.2"
    )

# Updates through the Submod Updater Plugin. It is optional: without it the submod works the same
# NOTE: the tag of each release on GitHub has to be the version above (e.g. v2.0.2, the v is ignored)
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Dynamic Texture Manager",
            user_name="The-Encoders-Club",
            repository_name="DynamicTextureManager",
            tag_formatter=lambda tag: tag.lstrip("vV")
        )
