# menu.rpy
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_dtm_change_textures",
            category=[_("appearance")],
            prompt=_("Change Textures"),
            pool=True,
            unlocked=True
        ),
        restartBlacklist=True,
        markSeen=True
    )

init python:
    def mas_dtm_get_texture_folders(sub_path):
        import os
        base_path = os.path.join(store.DTM_BASE_PARENT, "textures", sub_path)
        folders = []
        if os.path.exists(base_path):
            for d in os.listdir(base_path):
                full_dir = os.path.join(base_path, d)
                if os.path.isdir(full_dir):
                    has_png = False
                    for root, dirs, files in os.walk(full_dir):
                        for f in files:
                            if f.lower().endswith(".png"):
                                has_png = True
                                break
                        if has_png:
                            break
                    if has_png:
                        folders.append(d)
        return folders

screen mas_dtm_choice_menu(items):
    style_prefix "scrollable_menu"

    python:
        has_back = False
        back_item = None
        viewport_items = list(items)

        if len(items) > 0:
            last_item = items[-1]
            is_back = False
            if last_item.caption in ("Back", "Atrás", _("Back"), _("Atrás"), "Return"):
                is_back = True
            elif hasattr(last_item.action, "value") and last_item.action.value in ("return", "back", "dtm_pc_main", "dtm_pc_monika", "dtm_pc_games"):
                is_back = True
                
            if is_back:
                has_back = True
                back_item = last_item
                viewport_items = items[:-1]

        # Calculate exact height of the viewport content (approx 52px per item)
        vp_ymax = 480 if has_back else 550
        vp_height = min(len(viewport_items) * 52, vp_ymax)

    fixed:
        area (680, 40, 560, 640)

        vbox:
            xpos 0
            ypos 0
            xanchor 0
            yanchor 0

            viewport:
                id "mas_dtm_viewport"
                yfill False
                mousewheel True
                draggable True
                ymaximum vp_ymax
                ysize vp_height

                has vbox
                for i in viewport_items:
                    textbutton renpy.substitute(i.caption):
                        text_style "scrollable_menu_button_text"
                        xsize 560
                        action i.action

            if has_back:
                null height 15
                textbutton renpy.substitute(back_item.caption):
                    text_style "scrollable_menu_button_text"
                    xsize 560
                    action back_item.action

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("mas_dtm_viewport")
            unscrollable "hide"
            xalign -0.05
            ysize vp_height

label mas_dtm_change_textures:
    python:
        import os
        categories = [
            "monika/eyes",
            "monika/mouth",
            "monika/nose",
            "monika/body",
            "games/chess",
            "games/pong",
            "games/nou"
        ]
        for cat in categories:
            cat_dir = os.path.join(store.DTM_BASE_PARENT, "textures", cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

    jump dtm_pc_main

label dtm_pc_main:
    python:
        dtm_main_items = [
            (_("Monika"), "dtm_pc_monika"),
            (_("Games"), "dtm_pc_games"),
            (_("Back"), "return")
        ]
    $ result = renpy.display_menu(dtm_main_items, screen="mas_dtm_choice_menu")
    if result == "return":
        return
    else:
        jump expression result

label dtm_pc_monika:
    python:
        dtm_m_items = [
            (_("Eyes"), "dtm_pc_scan_eyes"),
            (_("Mouth"), "dtm_pc_scan_mouth"),
            (_("Nose"), "dtm_pc_scan_nose"),
            (_("Body"), "dtm_pc_scan_body"),
            (_("Back"), "dtm_pc_main")
        ]
    $ result = renpy.display_menu(dtm_m_items, screen="mas_dtm_choice_menu")
    jump expression result

label dtm_pc_games:
    python:
        dtm_g_items = [
            (_("Chess"), "dtm_pc_scan_chess"),
            (_("Pong"), "dtm_pc_scan_pong"),
            (_("NOU"), "dtm_pc_scan_nou"),
            (_("Back"), "dtm_pc_main")
        ]
    $ result = renpy.display_menu(dtm_g_items, screen="mas_dtm_choice_menu")
    jump expression result

label dtm_pc_scan_eyes:
    python:
        folders = mas_dtm_get_texture_folders("monika/eyes")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_monika
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_eyes_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_eyes
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                eyes_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "eyes", result)
                store.dtm_core.set_eyes_textures(eyes_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_eyes

label dtm_pc_scan_mouth:
    python:
        folders = mas_dtm_get_texture_folders("monika/mouth")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_monika
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_mouth_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_mouth
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                mouth_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "mouth", result)
                store.dtm_core.set_mouth_textures(mouth_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_mouth

label dtm_pc_scan_nose:
    python:
        folders = mas_dtm_get_texture_folders("monika/nose")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_monika
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_nose_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_nose
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                nose_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "nose", result)
                store.dtm_core.set_nose_textures(nose_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_nose

label dtm_pc_scan_body:
    python:
        folders = mas_dtm_get_texture_folders("monika/body")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_monika
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_body_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_body
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                body_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "body", result)
                store.dtm_core.set_body_textures(body_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_body

label dtm_pc_scan_chess:
    python:
        folders = mas_dtm_get_texture_folders("games/chess")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_games
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_chess_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_chess
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                chess_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "games", "chess", result)
                store.dtm_core.set_chess_textures(chess_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_chess

label dtm_pc_scan_pong:
    python:
        folders = mas_dtm_get_texture_folders("games/pong")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_games
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_pong_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_pong
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                pong_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "games", "pong", result)
                store.dtm_core.set_pong_textures(pong_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_pong

label dtm_pc_scan_nou:
    python:
        folders = mas_dtm_get_texture_folders("games/nou")
        items = [(f, f) for f in folders]
        items.append((_("Restore Original"), "restaurar"))
        items.append((_("Back"), "return"))
    $ result = renpy.display_menu(items, screen="mas_dtm_choice_menu")
    if result == "return":
        jump dtm_pc_games
    elif result == "restaurar":
        python:
            if hasattr(store, "dtm_core"):
                store.dtm_core.reset_nou_textures()
        $ renpy.notify(_("Textures restored"))
        jump dtm_pc_scan_nou
    else:
        python:
            if hasattr(store, "dtm_core"):
                import os
                nou_folder = os.path.join(store.DTM_BASE_PARENT, "textures", "games", "nou", result)
                store.dtm_core.set_nou_textures(nou_folder)
        $ renpy.notify(_("Texture changed successfully"))
        jump dtm_pc_scan_nou
