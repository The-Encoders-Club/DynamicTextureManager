# menu.rpy
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_dtm_change_textures",
            category=["appearance"],
            prompt=_("I want to change the textures"),
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

    def mas_dtm_get_dialogue_categories(pool=True):
        import store.evhand as evhand

        def mas_get_cat_label_safe(cat):
            if hasattr(store, "mas_get_cat_label"):
                return store.mas_get_cat_label(cat)
            return cat

        unlocked_events = store.Event.filterEvents(
            evhand.event_database,
            unlocked=True,
            pool=pool,
            aff=store.mas_curr_affection,
            flag_ban=store.EV_FLAG_HFM
        )
        main_cat_list = list()
        no_cat_list = list()
        for key in unlocked_events:
            if unlocked_events[key].category:
                evhand.addIfNew(unlocked_events[key].category, main_cat_list)
            else:
                no_cat_list.append(unlocked_events[key])
        
        main_cat_list.sort(key=lambda x: mas_get_cat_label_safe(x).lower())
        no_cat_list.sort(key=store.Event.getSortPrompt)
        
        dis_cat_list = [(mas_get_cat_label_safe(x).capitalize() + "...", x) for x in main_cat_list]
        no_cat_list = [(x.prompt, x.eventlabel) for x in no_cat_list]
        dis_cat_list.extend(no_cat_list)
        return dis_cat_list, main_cat_list

label mas_dtm_change_textures:
    python:
        import os
        categories = [
            "monika/eyes",
            "monika/eyebrows",
            "monika/mouth",
            "monika/nose",
            "monika/blush",
            "monika/tears",
            "monika/sweatdrop",
            "monika/arms",
            "monika/torso",
            "monika/body",
            "accessories/mug",
            "accessories/hotchoc_mug",
            "accessories/promisering",
            "accessories/quetzal",
            "accessories/roses",
            "accessories/thermos_mug",
            "room/calendar",
            "games/chess",
            "games/pong",
            "games/nou"
        ]
        for cat in categories:
            cat_dir = os.path.join(store.DTM_BASE_PARENT, "textures", cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

        # Initialize submod menu state
        dtm_current_view = "main"
        dtm_nav_stack = []
        dtm_exit = False
        dtm_action_to_run = None
        dtm_in_selector = False
        store.dtm_search_text = ""
        store.dtm_show_filter = False
        store.dtm_active_sub_category = "arms"
        dtm_initial_overrides = {}
        dtm_prev_items, dtm_prev_cats = mas_dtm_get_dialogue_categories(pool=True)

        # Hook main_adj.changed callback to save scroll position on scroll events
        store.dtm_original_changed = store.main_adj.changed
        store._dtm_last_scroll_value = 0
        def dtm_on_scroll(value):
            if value > 0:
                store._dtm_last_scroll_value = value
            if store.dtm_original_changed:
                store.dtm_original_changed(value)
        store.main_adj.changed = dtm_on_scroll

    # Move Monika to the left pane layout position
    show monika at t21

    while not dtm_exit:
        # Use precomputed categories to eliminate click lag
        $ prev_items = dtm_prev_items

        python:
            # Build items for right pane based on current view
            if dtm_current_view == "main":
                main_items = [
                    (_("Accessories"), "dtm_accessories"),
                    (_("Games"), "dtm_games"),
                    (_("Monika"), "dtm_monika"),
                    (_("Room"), "dtm_room")
                ]
            elif dtm_current_view == "dtm_monika":
                main_items = [
                    (_("Arms"), "dtm_scan_arms"),
                    (_("Blush"), "dtm_scan_blush"),
                    (_("Body"), "dtm_scan_body"),
                    (_("Eyebrows"), "dtm_scan_eyebrows"),
                    (_("Eyes"), "dtm_scan_eyes"),
                    (_("Mouth"), "dtm_scan_mouth"),
                    (_("Nose"), "dtm_scan_nose"),
                    (_("Sweat Drop"), "dtm_scan_sweatdrop"),
                    (_("Tears"), "dtm_scan_tears"),
                    (_("Torso"), "dtm_scan_torso")
                ]
            elif dtm_current_view == "dtm_accessories":
                main_items = [
                    (_("Coffee Mug"), "dtm_scan_mug"),
                    (_("Hot Chocolate Mug"), "dtm_scan_hotchoc_mug"),
                    (_("Promise Ring"), "dtm_scan_promisering"),
                    (_("Quetzal Plushie"), "dtm_scan_quetzal"),
                    (_("Roses"), "dtm_scan_roses"),
                    (_("Thermos Mug"), "dtm_scan_thermos_mug")
                ]
            elif dtm_current_view == "dtm_room":
                main_items = [
                    (_("Calendar"), "dtm_scan_calendar")
                ]
            elif dtm_current_view == "dtm_games":
                main_items = [
                    (_("Chess"), "dtm_scan_chess"),
                    (_("NOU"), "dtm_scan_nou"),
                    (_("Pong"), "dtm_scan_pong")
                ]
            elif dtm_current_view.startswith("dtm_scan_"):
                sub_path = dtm_current_view[9:]
                folder_map = {
                    "eyes": "monika/eyes",
                    "eyebrows": "monika/eyebrows",
                    "mouth": "monika/mouth",
                    "nose": "monika/nose",
                    "blush": "monika/blush",
                    "tears": "monika/tears",
                    "sweatdrop": "monika/sweatdrop",
                    "arms": "monika/arms",
                    "torso": "monika/torso",
                    "body": "monika/body",
                    "mug": "accessories/mug",
                    "hotchoc_mug": "accessories/hotchoc_mug",
                    "promisering": "accessories/promisering",
                    "quetzal": "accessories/quetzal",
                    "roses": "accessories/roses",
                    "thermos_mug": "accessories/thermos_mug",
                    "calendar": "room/calendar",
                    "chess": "games/chess",
                    "pong": "games/pong",
                    "nou": "games/nou"
                }
                folders = mas_dtm_get_texture_folders(folder_map.get(sub_path, sub_path))
                main_items = [(f, "apply:" + sub_path + ":" + f) for f in folders]
                main_items.append((_("Restore Original"), "restore:" + sub_path))
                
            elif dtm_current_view.startswith("category:"):
                cat_name = dtm_current_view[9:]
                import store.evhand as evhand
                unlocked_events = store.Event.filterEvents(
                    evhand.event_database,
                    category=(False, [cat_name]),
                    unlocked=True,
                    pool=True,
                    aff=store.mas_curr_affection,
                    flag_ban=store.EV_FLAG_HFM
                )
                sorted_events = sorted(unlocked_events.values(), key=store.Event.getSortPrompt)
                main_items = [(x.prompt, x.eventlabel) for x in sorted_events]

            # Add Back option only in DTM's own sub-views, not in left-panel category views
            if dtm_current_view != "main" and not dtm_current_view.startswith("category:"):
                main_items.append((_("Back"), "back"))

            # Register DTM-internal action values in namemap so renpy.has_label() returns True
            # for them, preventing the twopane screen from applying the bold "special_button" style.
            # Only registers strings that aren't already real Ren'Py labels.
            for _item_title, _action_val in main_items:
                if isinstance(_action_val, basestring) and not renpy.has_label(_action_val):
                    renpy.game.script.namemap[_action_val] = renpy.game.script.namemap["mas_dtm_change_textures"]

        # Select screen call based on whether we are in the sidebar selector view
        if dtm_in_selector:
            python:
                # Build list of categories for filter dropdown
                if dtm_current_view == "dtm_monika":
                    dtm_categories_list = [
                        (_("Arms"), "arms"),
                        (_("Blush"), "blush"),
                        (_("Body"), "body"),
                        (_("Eyebrows"), "eyebrows"),
                        (_("Eyes"), "eyes"),
                        (_("Mouth"), "mouth"),
                        (_("Nose"), "nose"),
                        (_("Sweat Drop"), "sweatdrop"),
                        (_("Tears"), "tears"),
                        (_("Torso"), "torso")
                    ]
                elif dtm_current_view == "dtm_accessories":
                    dtm_categories_list = [
                        (_("Coffee Mug"), "mug"),
                        (_("Hot Chocolate Mug"), "hotchoc_mug"),
                        (_("Promise Ring"), "promisering"),
                        (_("Quetzal Plushie"), "quetzal"),
                        (_("Roses"), "roses"),
                        (_("Thermos Mug"), "thermos_mug")
                    ]
                else: # dtm_room
                    dtm_categories_list = [
                        (_("Calendar"), "calendar")
                    ]
                
                # Fetch packs list for current active category
                folder_map = {
                    "eyes": ("monika", "eyes"),
                    "eyebrows": ("monika", "eyebrows"),
                    "mouth": ("monika", "mouth"),
                    "nose": ("monika", "nose"),
                    "blush": ("monika", "blush"),
                    "tears": ("monika", "tears"),
                    "sweatdrop": ("monika", "sweatdrop"),
                    "arms": ("monika", "arms"),
                    "torso": ("monika", "torso"),
                    "body": ("monika", "body"),
                    "mug": ("accessories", "mug"),
                    "hotchoc_mug": ("accessories", "hotchoc_mug"),
                    "promisering": ("accessories", "promisering"),
                    "quetzal": ("accessories", "quetzal"),
                    "roses": ("accessories", "roses"),
                    "thermos_mug": ("accessories", "thermos_mug"),
                    "calendar": ("room", "calendar")
                }
                p_sub = folder_map[store.dtm_active_sub_category]
                dtm_packs = mas_dtm_get_texture_folders(p_sub[0] + "/" + p_sub[1])
                
            call screen dtm_selector_sidebar(store.dtm_active_sub_category, dtm_packs, dtm_categories_list, folder_map) nopredict
        else:
            # Call the native MAS twopane screen directly. We pass 1 as cat_length to hide the native Go Back button on the left.
            call screen twopane_scrollable_menu(prev_items, main_items, store.evhand.LEFT_AREA, store.evhand.LEFT_XALIGN, store.evhand.RIGHT_AREA, store.evhand.RIGHT_XALIGN, 1) nopredict

        python:
            # Reset action state
            dtm_action_to_run = None
            
            if dtm_in_selector:
                set_func_map = {
                    "eyes": store.dtm_core.set_eyes_textures,
                    "eyebrows": store.dtm_core.set_eyebrows_textures,
                    "mouth": store.dtm_core.set_mouth_textures,
                    "nose": store.dtm_core.set_nose_textures,
                    "blush": store.dtm_core.set_blush_textures,
                    "tears": store.dtm_core.set_tears_textures,
                    "sweatdrop": store.dtm_core.set_sweatdrop_textures,
                    "arms": store.dtm_core.set_arms_textures,
                    "torso": store.dtm_core.set_torso_textures,
                    "body": store.dtm_core.set_body_textures,
                    "mug": store.dtm_core.set_mug_textures,
                    "hotchoc_mug": store.dtm_core.set_hotchoc_mug_textures,
                    "promisering": store.dtm_core.set_promisering_textures,
                    "quetzal": store.dtm_core.set_quetzal_textures,
                    "roses": store.dtm_core.set_roses_textures,
                    "thermos_mug": store.dtm_core.set_thermos_mug_textures,
                    "calendar": store.dtm_core.set_calendar_textures
                }
                reset_func_map = {
                    "eyes": store.dtm_core.reset_eyes_textures,
                    "eyebrows": store.dtm_core.reset_eyebrows_textures,
                    "mouth": store.dtm_core.reset_mouth_textures,
                    "nose": store.dtm_core.reset_nose_textures,
                    "blush": store.dtm_core.reset_blush_textures,
                    "tears": store.dtm_core.reset_tears_textures,
                    "sweatdrop": store.dtm_core.reset_sweatdrop_textures,
                    "arms": store.dtm_core.reset_arms_textures,
                    "torso": store.dtm_core.reset_torso_textures,
                    "body": store.dtm_core.reset_body_textures,
                    "mug": store.dtm_core.reset_mug_textures,
                    "hotchoc_mug": store.dtm_core.reset_hotchoc_mug_textures,
                    "promisering": store.dtm_core.reset_promisering_textures,
                    "quetzal": store.dtm_core.reset_quetzal_textures,
                    "roses": store.dtm_core.reset_roses_textures,
                    "thermos_mug": store.dtm_core.reset_thermos_mug_textures,
                    "calendar": store.dtm_core.reset_calendar_textures
                }
                if _return == "confirm":
                    # Exit selector to main menu
                    dtm_in_selector = False
                    dtm_current_view = "main"
                elif _return == "cancel":
                    # Exit selector to main menu (does not revert)
                    dtm_in_selector = False
                    dtm_current_view = "main"
                elif _return == "restore" or _return == "preview_restore":
                    # Reset current subcategory to default immediately
                    reset_func_map[store.dtm_active_sub_category]()
                elif isinstance(_return, basestring) and _return.startswith("preview:"):
                    # Apply and save pack selection immediately
                    pack_name = _return.split(":", 1)[1]
                    p_sub = folder_map[store.dtm_active_sub_category]
                    abs_folder = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], pack_name)
                    set_func_map[store.dtm_active_sub_category](abs_folder)
                elif _return == "dtm_change_category":
                    pass
            else:
                # Safe parsing of native screen return
                if _return is False or _return is None or _return == "nevermind":
                    dtm_exit = True
                    
                elif _return == "back":
                    if len(dtm_nav_stack) > 0:
                        dtm_current_view = dtm_nav_stack.pop()
                    else:
                        dtm_current_view = "main"
                    store._dtm_last_scroll_value = 0
                        
                elif _return in dtm_prev_cats:
                    # Clicked a category on the left panel: navigate into that category within DTM
                    dtm_nav_stack.append(dtm_current_view)
                    dtm_current_view = "category:" + _return[0] if isinstance(_return, list) else "category:" + _return
                    store._dtm_last_scroll_value = 0
                    
                elif isinstance(_return, basestring) and _return.startswith("apply:"):
                    parts = _return.split(":")
                    sub_path = parts[1]
                    folder_name = parts[2]
                    if hasattr(store, "dtm_core"):
                        import os
                        folder_map = {
                            "eyes": ("monika", "eyes"),
                            "eyebrows": ("monika", "eyebrows"),
                            "mouth": ("monika", "mouth"),
                            "nose": ("monika", "nose"),
                            "blush": ("monika", "blush"),
                            "tears": ("monika", "tears"),
                            "sweatdrop": ("monika", "sweatdrop"),
                            "arms": ("monika", "arms"),
                            "torso": ("monika", "torso"),
                            "body": ("monika", "body"),
                            "mug": ("accessories", "mug"),
                            "hotchoc_mug": ("accessories", "hotchoc_mug"),
                            "promisering": ("accessories", "promisering"),
                            "quetzal": ("accessories", "quetzal"),
                            "roses": ("accessories", "roses"),
                            "thermos_mug": ("accessories", "thermos_mug"),
                            "calendar": ("room", "calendar"),
                            "chess": ("games", "chess"),
                            "pong": ("games", "pong"),
                            "nou": ("games", "nou")
                        }
                        p_sub = folder_map[sub_path]
                        abs_folder = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], folder_name)
                        func_map = {
                            "eyes": store.dtm_core.set_eyes_textures,
                            "eyebrows": store.dtm_core.set_eyebrows_textures,
                            "mouth": store.dtm_core.set_mouth_textures,
                            "nose": store.dtm_core.set_nose_textures,
                            "blush": store.dtm_core.set_blush_textures,
                            "tears": store.dtm_core.set_tears_textures,
                            "sweatdrop": store.dtm_core.set_sweatdrop_textures,
                            "arms": store.dtm_core.set_arms_textures,
                            "torso": store.dtm_core.set_torso_textures,
                            "body": store.dtm_core.set_body_textures,
                            "mug": store.dtm_core.set_mug_textures,
                            "hotchoc_mug": store.dtm_core.set_hotchoc_mug_textures,
                            "promisering": store.dtm_core.set_promisering_textures,
                            "quetzal": store.dtm_core.set_quetzal_textures,
                            "roses": store.dtm_core.set_roses_textures,
                            "thermos_mug": store.dtm_core.set_thermos_mug_textures,
                            "calendar": store.dtm_core.set_calendar_textures,
                            "chess": store.dtm_core.set_chess_textures,
                            "pong": store.dtm_core.set_pong_textures,
                            "nou": store.dtm_core.set_nou_textures
                        }
                        func_map[sub_path](abs_folder)
                        renpy.notify(_("Texture changed successfully"))
                        
                elif isinstance(_return, basestring) and _return.startswith("restore:"):
                    sub_path = _return.split(":")[1]
                    if hasattr(store, "dtm_core"):
                        func_map = {
                            "eyes": store.dtm_core.reset_eyes_textures,
                            "eyebrows": store.dtm_core.reset_eyebrows_textures,
                            "mouth": store.dtm_core.reset_mouth_textures,
                            "nose": store.dtm_core.reset_nose_textures,
                            "blush": store.dtm_core.reset_blush_textures,
                            "tears": store.dtm_core.reset_tears_textures,
                            "sweatdrop": store.dtm_core.reset_sweatdrop_textures,
                            "arms": store.dtm_core.reset_arms_textures,
                            "torso": store.dtm_core.reset_torso_textures,
                            "body": store.dtm_core.reset_body_textures,
                            "mug": store.dtm_core.reset_mug_textures,
                            "hotchoc_mug": store.dtm_core.reset_hotchoc_mug_textures,
                            "promisering": store.dtm_core.reset_promisering_textures,
                            "quetzal": store.dtm_core.reset_quetzal_textures,
                            "roses": store.dtm_core.reset_roses_textures,
                            "thermos_mug": store.dtm_core.reset_thermos_mug_textures,
                            "calendar": store.dtm_core.reset_calendar_textures,
                            "chess": store.dtm_core.reset_chess_textures,
                            "pong": store.dtm_core.reset_pong_textures,
                            "nou": store.dtm_core.reset_nou_textures
                        }
                        func_map[sub_path]()
                        renpy.notify(_("Textures restored"))
                        
                elif isinstance(_return, basestring) and _return.startswith("dtm_"):
                    # DTM sub-view navigation
                    dtm_nav_stack.append(dtm_current_view)
                    dtm_current_view = _return
                    store._dtm_last_scroll_value = 0
                    
                    # If entering a sidebar category, set up the selector state
                    if dtm_current_view in ("dtm_monika", "dtm_accessories", "dtm_room"):
                        dtm_in_selector = True
                        store.dtm_search_text = ""
                        store.dtm_show_filter = False
                        if dtm_current_view == "dtm_monika":
                            store.dtm_active_sub_category = "arms"
                        elif dtm_current_view == "dtm_accessories":
                            store.dtm_active_sub_category = "mug"
                        elif dtm_current_view == "dtm_room":
                            store.dtm_active_sub_category = "calendar"
                            
                        # Save initial overrides for cancel/revert
                        dtm_initial_overrides = {k: v for k, v in store.mas_dtm_overrides.items()}
                    
                elif isinstance(_return, basestring) and (renpy.has_label(_return) or _return.startswith("event:")):
                    # Native dialogue selected from search or list: Exit DTM and run it
                    dtm_exit = True
                    dtm_action_to_run = _return.split(":")[1] if _return.startswith("event:") else _return

            # Restore the scroll position for the next iteration of the screen loop
            if not dtm_exit:
                store.main_adj.change(store._dtm_last_scroll_value)

        # Execute selected conversation event if applicable
        if dtm_action_to_run:
            $ store.mas_setEventPause(None)
            $ store.MASEventList.push(dtm_action_to_run, skipeval=True)
            $ dtm_exit = True

    python:
        if hasattr(store, "dtm_original_changed"):
            store.main_adj.changed = store.dtm_original_changed
            store.main_adj.change(0)
            del store.dtm_original_changed
        if hasattr(store, "_dtm_last_scroll_value"):
            del store._dtm_last_scroll_value

    # Reset Monika to standard centered position upon exit
    show monika at t11 with dissolve_monika
    
    if not dtm_action_to_run:
        $ renpy.pop_call()
        jump prompt_menu
    else:
        return

init python:
    def dtm_get_default_thumb():
        import os
        for f in ("mod_assets/thumbs/remove.png", "gui/window_icon.png"):
            if os.path.exists(os.path.join(config.gamedir, f)):
                return f
        return "gui/window_icon.png"

    def dtm_get_thumbnail(category, sub_category, pack):
        import os
        folder_map = {
            "eyes": ("monika", "eyes"),
            "eyebrows": ("monika", "eyebrows"),
            "mouth": ("monika", "mouth"),
            "nose": ("monika", "nose"),
            "blush": ("monika", "blush"),
            "tears": ("monika", "tears"),
            "sweatdrop": ("monika", "sweatdrop"),
            "arms": ("monika", "arms"),
            "torso": ("monika", "torso"),
            "body": ("monika", "body"),
            "mug": ("accessories", "mug"),
            "hotchoc_mug": ("accessories", "hotchoc_mug"),
            "promisering": ("accessories", "promisering"),
            "quetzal": ("accessories", "quetzal"),
            "roses": ("accessories", "roses"),
            "thermos_mug": ("accessories", "thermos_mug"),
            "calendar": ("room", "calendar")
        }
        
        default_thumb = dtm_get_default_thumb()
        p_sub = folder_map.get(sub_category)
        if not p_sub:
            return default_thumb
            
        pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], pack)
        for f in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg"):
            if os.path.exists(os.path.join(pack_dir, f)):
                return pack_dir.replace("\\", "/") + "/" + f
        return default_thumb

transform dtm_thumb_resize:
    size (180, 180)

screen dtm_selector_sidebar(sub_category, packs_list, categories_list, folder_map):
    zorder 50
    default hovered_item = None

    $ h_color = getattr(store.mas_ui, "light_button_text_hover_color", "#ffffff")
    $ i_color = getattr(store.mas_globals, "button_text_idle_color", "#000000")

    # Categorías / Filtro desplegable - Coordenadas y comportamiento exacto a zz_selector.rpy
    if store.dtm_show_filter:
        frame:
            area (750, 45, 300, 500)
            background None

            viewport id "filter_scroll":
                mousewheel True
                has vbox
                spacing 5
                for cat_label, cat_id in categories_list:
                    textbutton cat_label:
                        style "hkb_button"
                        xysize (280, 40)
                        xalign 0.5
                        hover_sound gui.hover_sound
                        activate_sound gui.activate_sound
                        selected (store.dtm_active_sub_category == cat_id)
                        action [
                            SetField(store, "dtm_active_sub_category", cat_id),
                            SetField(store, "dtm_show_filter", False),
                            Return("dtm_change_category")
                        ]
            vbar value YScrollValue("filter_scroll"):
                style "mas_selector_sidebar_vbar"
                unscrollable "hide"
                xoffset -15

    # Botón Filtro (Categoría) - Réplica exacta de area (960, 3, 50, 40)
    frame:
        area (960, 3, 50, 40)
        background None
        button:
            if store.dtm_show_filter:
                style "filter_dropdown_down"
            else:
                style "filter_dropdown_up"
            hover_sound gui.hover_sound
            activate_sound gui.activate_sound
            action ToggleField(store, "dtm_show_filter")

    # Buscador
    frame:
        xpos 1075
        ypos 5
        xsize 200
        ysize 40
        background Solid("#ffaa99aa")

        viewport:
            draggable False
            arrowkeys False
            mousewheel "horizontal"
            xsize 195
            ysize 38
            input:
                value VariableInputValue("dtm_search_text")
                style_prefix "input"
                length 50
                xalign 0.0
                layout "nobreak"
                first_indent (0 if not store.dtm_search_text else 10)

        if not store.dtm_search_text:
            text _("Search for..."):
                text_align 0.0
                layout "nobreak"
                color "#EEEEEEB2"
                first_indent 10
                line_leading 1
                outlines []

    # Lista de packs (Frame exclusivo para la lista)
    frame:
        area (1075, 50, 200, 480)
        background Frame(store.mas_ui.sel_sb_frame, left=6, top=6, tile=True)

        viewport id "sidebar_scroll":
            ysize 460
            mousewheel True
            arrowkeys True

            vbox:
                xsize 200
                spacing 10
                null height 1

                # Botón Original
                $ is_original_active = False
                python:
                    current_active = store.mas_dtm_overrides.get(store.dtm_core.category_to_config_key.get(store.dtm_active_sub_category))
                    if not current_active:
                        is_original_active = True
                        
                $ is_orig_hovered = (hovered_item == "___original___")
                $ is_orig_highlight = is_original_active or is_orig_hovered

                button:
                    style "empty"
                    xsize 180
                    yminimum 218
                    xalign 0.5
                    hover_sound gui.hover_sound
                    activate_sound gui.activate_sound
                    hovered SetScreenVariable("hovered_item", "___original___")
                    unhovered SetScreenVariable("hovered_item", None)
                    action Return("preview_restore")
                    vbox:
                        xsize 180
                        spacing 0
                        
                        frame:
                            xsize 180
                            yminimum 38
                            background Frame(
                                mas_getTimeFile(
                                    "mod_assets/frames/selector_top_frame_selected.png" 
                                    if is_orig_highlight else 
                                    "mod_assets/frames/selector_top_frame.png"
                                ),
                                left=4, top=4
                            )
                            padding (5, 5, 5, 5)
                            margin (0, 0)
                            text _("Original"):
                                xalign 0.0
                                yalign 0.5
                                font gui.default_font
                                size gui.text_size
                                bold False
                                outlines []
                                color (h_color if is_orig_highlight else i_color)
                                
                        frame:
                            xsize 180
                            ysize 180
                            background None
                            padding (0, 0)
                            margin (0, 0)
                            add dtm_get_default_thumb() at dtm_thumb_resize xalign 0.5 yalign 0.5
                            add mas_getTimeFile("mod_assets/frames/selector_overlay.png") xalign 0.5 yalign 0.5
                            if is_orig_hovered:
                                add Solid("#ffaa99aa") size (180, 180) xalign 0.5 yalign 0.5

                # Lista de packs filtrados
                for pack in packs_list:
                    if not store.dtm_search_text or store.dtm_search_text.lower() in pack.lower():
                        $ is_selected = False
                        python:
                            p_sub = folder_map[store.dtm_active_sub_category]
                            current_active = store.mas_dtm_overrides.get(store.dtm_core.category_to_config_key.get(store.dtm_active_sub_category))
                            if current_active:
                                import os
                                act_name = os.path.basename(current_active.rstrip("/" + chr(92))).lower()
                                if act_name == pack.lower():
                                    is_selected = True

                        $ is_pack_hovered = (hovered_item == pack)
                        $ is_highlight = is_selected or is_pack_hovered

                        button:
                            style "empty"
                            xsize 180
                            yminimum 218
                            xalign 0.5
                            hover_sound gui.hover_sound
                            activate_sound gui.activate_sound
                            hovered SetScreenVariable("hovered_item", pack)
                            unhovered SetScreenVariable("hovered_item", None)
                            action Return("preview:" + pack)
                            vbox:
                                xsize 180
                                spacing 0
                                
                                frame:
                                    xsize 180
                                    yminimum 38
                                    background Frame(
                                        mas_getTimeFile(
                                            "mod_assets/frames/selector_top_frame_selected.png" 
                                            if is_highlight else 
                                            "mod_assets/frames/selector_top_frame.png"
                                        ),
                                        left=4, top=4
                                    )
                                    padding (5, 5, 5, 5)
                                    margin (0, 0)
                                    text pack:
                                        xalign 0.0
                                        yalign 0.5
                                        font gui.default_font
                                        size gui.text_size
                                        bold False
                                        outlines []
                                        color (h_color if is_highlight else i_color)
                                        
                                frame:
                                    xsize 180
                                    ysize 180
                                    background None
                                    padding (0, 0)
                                    margin (0, 0)
                                    add dtm_get_thumbnail(store.dtm_active_sub_category, store.dtm_active_sub_category, pack) at dtm_thumb_resize xalign 0.5 yalign 0.5
                                    add mas_getTimeFile("mod_assets/frames/selector_overlay.png") xalign 0.5 yalign 0.5
                                    if is_pack_hovered:
                                        add Solid("#ffaa99aa") size (180, 180) xalign 0.5 yalign 0.5

                null height 1

        vbar value YScrollValue("sidebar_scroll"):
            style "mas_selector_sidebar_vbar"
            unscrollable "hide"
            xoffset -25

    # Botones de control inferiores - Fuera del frame rosa, alineados abajo
    vbox:
        xpos 1075
        ypos 540
        xsize 200
        spacing 5

        textbutton _("Confirm"):
            style "hkb_button"
            xalign 0.5
            hover_sound gui.hover_sound
            activate_sound gui.activate_sound
            action Return("confirm")

        textbutton _("Restore"):
            style "hkb_button"
            xalign 0.5
            hover_sound gui.hover_sound
            activate_sound gui.activate_sound
            action Return("restore")

        textbutton _("Cancel"):
            style "hkb_button"
            xalign 0.5
            hover_sound gui.hover_sound
            activate_sound gui.activate_sound
            action Return("cancel")
