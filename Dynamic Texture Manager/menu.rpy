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
        store.dtm_sidebar_adj = ui.adjustment()
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
                elif dtm_current_view == "dtm_games":
                    dtm_categories_list = [
                        (_("Chess"), "chess"),
                        (_("NOU"), "nou"),
                        (_("Pong"), "pong")
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
                    "calendar": ("room", "calendar"),
                    "chess": ("games", "chess"),
                    "nou": ("games", "nou"),
                    "pong": ("games", "pong")
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
                    "calendar": store.dtm_core.set_calendar_textures,
                    "chess": store.dtm_core.set_chess_textures,
                    "nou": store.dtm_core.set_nou_textures,
                    "pong": store.dtm_core.set_pong_textures
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
                    "calendar": store.dtm_core.reset_calendar_textures,
                    "chess": store.dtm_core.reset_chess_textures,
                    "nou": store.dtm_core.reset_nou_textures,
                    "pong": store.dtm_core.reset_pong_textures
                }
                if _return == "confirm":
                    # Exit selector to main menu
                    dtm_in_selector = False
                    dtm_current_view = "main"
                    dtm_nav_stack = []
                elif _return == "cancel":
                    # Revert to initial overrides when selector was opened
                    if hasattr(store.dtm_core, "restore_preview_textures"):
                        store.dtm_core.restore_preview_textures(dtm_initial_overrides)
                        store.mas_dtm_save_config()
                    dtm_in_selector = False
                    dtm_current_view = "main"
                    dtm_nav_stack = []
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
                    if dtm_current_view in ("dtm_monika", "dtm_accessories", "dtm_room", "dtm_games"):
                        dtm_in_selector = True
                        store.dtm_search_text = ""
                        store.dtm_show_filter = False
                        if hasattr(store, "dtm_sidebar_adj") and store.dtm_sidebar_adj:
                            store.dtm_sidebar_adj.change(0)
                        if dtm_current_view == "dtm_monika":
                            store.dtm_active_sub_category = "arms"
                        elif dtm_current_view == "dtm_accessories":
                            store.dtm_active_sub_category = "mug"
                        elif dtm_current_view == "dtm_room":
                            store.dtm_active_sub_category = "calendar"
                        elif dtm_current_view == "dtm_games":
                            store.dtm_active_sub_category = "chess"
                            
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
    store.dtm_sidebar_adj = ui.adjustment()

    def dtm_apply_preview(sub_category, pack_name):
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
            "nou": ("games", "nou"),
            "pong": ("games", "pong")
        }
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
            "calendar": store.dtm_core.set_calendar_textures,
            "chess": store.dtm_core.set_chess_textures,
            "nou": store.dtm_core.set_nou_textures,
            "pong": store.dtm_core.set_pong_textures
        }
        if sub_category in folder_map and sub_category in set_func_map:
            p_sub = folder_map[sub_category]
            abs_folder = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], pack_name)
            set_func_map[sub_category](abs_folder)
            renpy.restart_interaction()

    def dtm_restore_preview(sub_category):
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
            "calendar": store.dtm_core.reset_calendar_textures,
            "chess": store.dtm_core.reset_chess_textures,
            "nou": store.dtm_core.reset_nou_textures,
            "pong": store.dtm_core.reset_pong_textures
        }
        if sub_category in reset_func_map:
            reset_func_map[sub_category]()
            renpy.restart_interaction()

    DTM_ACCESSORY_CROP_MAP = {
        "mug": (280, 665, 180, 185),
        "hotchoc_mug": (280, 665, 180, 185),
        "thermos_mug": (275, 640, 190, 210),
        "roses": (192, 458, 185, 392),
        "quetzal": (875, 640, 210, 210)
    }

    DTM_DEFAULT_IMAGE_MAP = {
        "mug": "mod_assets/monika/a/mug/0.png",
        "hotchoc_mug": "mod_assets/monika/a/hotchoc_mug/0.png",
        "thermos_mug": "mod_assets/monika/a/thermos_mug/0.png",
        "roses": "mod_assets/monika/a/roses/0.png",
        "quetzal": "mod_assets/monika/a/quetzalplushie/0.png",
        "promisering": "mod_assets/monika/a/promisering/3-10.png",
        "calendar": "mod_assets/calendar/calendar_bg.png",
        "chess": "mod_assets/games/chess/chess_board.png",
        "pong": "mod_assets/games/pong/pong_field.png",
        "nou": "mod_assets/games/nou/cards/v1.png",
        "arms": "mod_assets/monika/b/arms-steepling-10.png",
        "torso": "mod_assets/monika/b/body-def-0.png",
        "body": "mod_assets/monika/b/body-def-head.png",
        "eyes": "mod_assets/monika/f/face-eyes-normal.png",
        "eyebrows": "mod_assets/monika/f/face-eyebrows-mid.png",
        "mouth": "mod_assets/monika/f/face-mouth-smile.png",
        "nose": "mod_assets/monika/f/face-nose-def.png",
        "blush": "mod_assets/monika/f/face-blush-lines.png",
        "tears": "mod_assets/monika/f/face-tears-streaming.png",
        "sweatdrop": "mod_assets/monika/f/face-sweatdrop-def.png"
    }

    def _find_file_in_dir(dirpath, preferred_names=(), keyword=None, ext=".png"):
        import os
        if not os.path.isdir(dirpath):
            return None
        files = os.listdir(dirpath)
        for pref in preferred_names:
            p_low = pref.lower()
            for f in files:
                if f.lower() == p_low:
                    return os.path.join(dirpath, f).replace("\\", "/")
        if keyword:
            k_low = keyword.lower()
            for f in files:
                f_low = f.lower()
                if k_low in f_low and f_low.endswith(ext):
                    return os.path.join(dirpath, f).replace("\\", "/")
        if ext:
            for f in files:
                if f.lower().endswith(ext):
                    return os.path.join(dirpath, f).replace("\\", "/")
        return None

    def dtm_get_monika_face_displayable(feature_path=None, exclude_feature=None):
        import os
        f_crop = (445, 115, 390, 390)
        f_size = (170, 170)
        args = []

        def _check_asset(*candidates):
            for c in candidates:
                if os.path.exists(os.path.join(config.gamedir, c)):
                    return c
            return None

        # 1. Hair back (canonical brown 0.png first)
        h_back = _check_asset("mod_assets/monika/h/def/0.png", "mod_assets/monika/h/hair-def-back.png")
        if h_back:
            args.extend([(0, 0), Transform(h_back + "?dtm_raw=1", crop=f_crop, size=f_size)])

        # 2. Body (neck & shoulders)
        body = _check_asset("mod_assets/monika/b/body-def-0.png")
        if body:
            args.extend([(0, 0), Transform(body + "?dtm_raw=1", crop=f_crop, size=f_size)])

        # 3. Head base
        if exclude_feature == "body" and feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])
        else:
            head = _check_asset("mod_assets/monika/b/body-def-head.png")
            if head:
                args.extend([(0, 0), Transform(head + "?dtm_raw=1", crop=f_crop, size=f_size)])

        # 4. Nose & Mouth (under front bangs)
        if exclude_feature != "nose":
            p_nose = _check_asset("mod_assets/monika/f/face-nose-def.png")
            if p_nose:
                args.extend([(0, 0), Transform(p_nose + "?dtm_raw=1", crop=f_crop, size=f_size)])
        elif feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])

        if exclude_feature != "mouth":
            p_mouth = _check_asset("mod_assets/monika/f/face-mouth-smile.png", "mod_assets/monika/f/face-mouth-small.png")
            if p_mouth:
                args.extend([(0, 0), Transform(p_mouth + "?dtm_raw=1", crop=f_crop, size=f_size)])
        elif feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])

        # 5. Hair front (canonical brown 10.png bangs)
        h_front = _check_asset("mod_assets/monika/h/def/10.png", "mod_assets/monika/h/hair-def-front.png")
        if h_front:
            args.extend([(0, 0), Transform(h_front + "?dtm_raw=1", crop=f_crop, size=f_size)])

        # 6. Eyes (drawn ON TOP of front hair bangs)
        if exclude_feature != "eyes":
            p_eyes = _check_asset("mod_assets/monika/f/face-eyes-normal.png")
            if p_eyes:
                args.extend([(0, 0), Transform(p_eyes + "?dtm_raw=1", crop=f_crop, size=f_size)])
        elif feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])

        # 7. Eyebrows (drawn ON TOP of front hair bangs)
        if exclude_feature != "eyebrows":
            p_brows = _check_asset("mod_assets/monika/f/face-eyebrows-mid.png")
            if p_brows:
                args.extend([(0, 0), Transform(p_brows + "?dtm_raw=1", crop=f_crop, size=f_size)])
        elif feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])

        # 8. Extra expressions: blush, tears, sweatdrop (ON TOP of everything)
        if exclude_feature not in ("nose", "mouth", "eyes", "eyebrows", "body") and feature_path:
            args.extend([(0, 0), Transform(feature_path, crop=f_crop, size=f_size)])

        if not args:
            return Transform("mod_assets/thumbs/remove.png", size=f_size)

        return LiveComposite((170, 170), *args)

    def dtm_get_default_thumb(sub_category=None):
        import os
        if sub_category and sub_category in DTM_DEFAULT_IMAGE_MAP:
            p = DTM_DEFAULT_IMAGE_MAP[sub_category]
            full_p = os.path.join(config.gamedir, p)
            if os.path.exists(full_p):
                return p
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
            "calendar": ("room", "calendar"),
            "chess": ("games", "chess"),
            "nou": ("games", "nou"),
            "pong": ("games", "pong")
        }

        default_thumb = dtm_get_default_thumb(sub_category)
        p_sub = folder_map.get(sub_category)
        if not p_sub or not pack:
            return default_thumb

        pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], pack)
        if os.path.isdir(pack_dir):
            try:
                # 1. Dedicated thumbnails (highest priority)
                for f in os.listdir(pack_dir):
                    f_lower = f.lower()
                    if f_lower in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg", "preview.png", "preview.jpg"):
                        return (os.path.join(pack_dir, f)).replace("\\", "/")
                # 2. Specific game candidates
                if sub_category == "chess":
                    candidate = os.path.join(pack_dir, "chess_board.png")
                    if os.path.exists(candidate):
                        return candidate.replace("\\", "/")
                elif sub_category == "pong":
                    candidate = os.path.join(pack_dir, "pong_field.png")
                    if os.path.exists(candidate):
                        return candidate.replace("\\", "/")
                elif sub_category == "nou":
                    for cand_name in ("v1.png", "a1.png", "r1.png", "c1.png"):
                        for cand in (
                            os.path.join(pack_dir, "cards", cand_name),
                            os.path.join(pack_dir, cand_name)
                        ):
                            if os.path.exists(cand):
                                return cand.replace("\\", "/")
                # 3. Calendar candidates
                elif sub_category == "calendar":
                    for c_name in ("calendar_bg.png", "calendar.png"):
                        cand = os.path.join(pack_dir, c_name)
                        if os.path.exists(cand):
                            return cand.replace("\\", "/")
                # 4. Accessory texture candidates
                elif sub_category in DTM_ACCESSORY_CROP_MAP:
                    for a_name in ("0.png", "2-10.png", "acs-quetzalplushie-0.png"):
                        cand = os.path.join(pack_dir, a_name)
                        if os.path.exists(cand):
                            return cand.replace("\\", "/")
                elif sub_category == "promisering":
                    for r_name in ("3-10.png", "2-10.png", "0.png"):
                        cand = os.path.join(pack_dir, r_name)
                        if os.path.exists(cand):
                            return cand.replace("\\", "/")
                # 5. Monika facial & body candidates
                elif sub_category == "eyes":
                    cand = _find_file_in_dir(pack_dir, ("face-eyes-normal.png", "face-eyes-def.png"), "eyes", ".png")
                    if cand: return cand
                elif sub_category == "eyebrows":
                    cand = _find_file_in_dir(pack_dir, ("face-eyebrows-mid.png", "face-eyebrows-def.png"), "eyebrows", ".png")
                    if cand: return cand
                elif sub_category == "mouth":
                    cand = _find_file_in_dir(pack_dir, ("face-mouth-smile.png", "face-mouth-def.png", "face-mouth-small.png"), "mouth", ".png")
                    if cand: return cand
                elif sub_category == "nose":
                    cand = _find_file_in_dir(pack_dir, ("face-nose-def.png",), "nose", ".png")
                    if cand: return cand
                elif sub_category == "blush":
                    cand = _find_file_in_dir(pack_dir, ("face-blush-lines.png", "face-blush-shade.png", "face-blush-full.png"), "blush", ".png")
                    if cand: return cand
                elif sub_category == "tears":
                    cand = _find_file_in_dir(pack_dir, ("face-tears-streaming.png", "face-tears-pooled.png", "face-tears-normal.png"), "tears", ".png")
                    if cand: return cand
                elif sub_category == "sweatdrop":
                    cand = _find_file_in_dir(pack_dir, ("face-sweatdrop-def.png", "face-sweat-def.png"), "sweat", ".png")
                    if cand: return cand
                elif sub_category == "arms":
                    cand = _find_file_in_dir(pack_dir, ("arms-steepling-10.png", "arms-rest-10.png", "arms-left-rest-10.png", "arms-crossed-10.png"), "arms", ".png")
                    if cand: return cand
                elif sub_category == "torso":
                    cand = _find_file_in_dir(pack_dir, ("body-def-0.png",), "torso", ".png")
                    if cand: return cand
                elif sub_category == "body":
                    cand = _find_file_in_dir(pack_dir, ("body-def-head.png", "body-def-0.png"), "body", ".png")
                    if cand: return cand
            except:
                pass
        return default_thumb

    def dtm_get_image_size(filepath):
        import struct
        import os
        if not filepath:
            return (180, 180)
        clean_path = filepath.split("?")[0] if "?" in filepath else filepath
        if not os.path.isabs(clean_path):
            full_path = os.path.join(config.gamedir, clean_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(store.DTM_BASE_PARENT, clean_path)
        else:
            full_path = clean_path

        if not os.path.exists(full_path):
            return (180, 180)

        try:
            with open(full_path, "rb") as f:
                head = f.read(32)
                if head.startswith(b"\x89PNG\r\n\x1a\n"):
                    w, h = struct.unpack(">II", head[16:24])
                    return (w, h)
                elif head.startswith((b"GIF87a", b"GIF89a")):
                    w, h = struct.unpack("<HH", head[6:10])
                    return (w, h)
                elif head.startswith(b"\xff\xd8"):
                    f.seek(2)
                    b = f.read(1)
                    while b and ord(b) != 0xda:
                        while ord(b) != 0xff:
                            b = f.read(1)
                        while ord(b) == 0xff:
                            b = f.read(1)
                        if 0xc0 <= ord(b) <= 0xc3:
                            f.read(3)
                            h, w = struct.unpack(">HH", f.read(4))
                            return (w, h)
                        else:
                            chunk_len = struct.unpack(">H", f.read(2))[0]
                            f.seek(chunk_len - 2, 1)
                        b = f.read(1)
        except Exception:
            pass

        try:
            return renpy.image_size(clean_path)
        except Exception:
            return (180, 180)

    def dtm_get_thumbnail_displayable(category, sub_category, pack):
        import os

        # 1. Monika facial parts: Composed Face
        monika_face_parts = ("eyes", "eyebrows", "mouth", "nose", "blush", "tears", "sweatdrop", "body")
        if sub_category in monika_face_parts:
            if pack:
                # Check dedicated thumbnail
                p_sub = ("monika", sub_category)
                pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], pack)
                if os.path.isdir(pack_dir):
                    for f in os.listdir(pack_dir):
                        if f.lower() in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg", "preview.png", "preview.jpg"):
                            thumb_path = os.path.join(pack_dir, f).replace("\\", "/")
                            w, h = dtm_get_image_size(thumb_path)
                            if w == h:
                                return Transform(thumb_path, size=(180, 180))
                            scale = min(170.0 / w, 170.0 / h)
                            return Transform(thumb_path, size=(int(round(w * scale)), int(round(h * scale))))

                cand = dtm_get_thumbnail(category, sub_category, pack)
                exclude = sub_category if sub_category in ("eyes", "eyebrows", "mouth", "nose", "body") else None
                feat_path = cand if cand and os.path.isabs(cand) else None
                return dtm_get_monika_face_displayable(feature_path=feat_path, exclude_feature=exclude)
            else:
                # Original button
                if sub_category == "blush":
                    return dtm_get_monika_face_displayable("mod_assets/monika/f/face-blush-lines.png?dtm_raw=1", exclude_feature=None)
                elif sub_category == "tears":
                    return dtm_get_monika_face_displayable("mod_assets/monika/f/face-tears-streaming.png?dtm_raw=1", exclude_feature=None)
                elif sub_category == "sweatdrop":
                    return dtm_get_monika_face_displayable("mod_assets/monika/f/face-sweatdrop-def.png?dtm_raw=1", exclude_feature=None)
                else:
                    return dtm_get_monika_face_displayable(None, exclude_feature=None)

        # 2. Monika Arms: Zoom to center
        if sub_category == "arms":
            arms_crop = (470, 420, 340, 340)
            if pack:
                pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "arms", pack)
                if os.path.isdir(pack_dir):
                    for f in os.listdir(pack_dir):
                        if f.lower() in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg", "preview.png", "preview.jpg"):
                            thumb_path = os.path.join(pack_dir, f).replace("\\", "/")
                            w, h = dtm_get_image_size(thumb_path)
                            scale = min(170.0 / w, 170.0 / h)
                            return Transform(thumb_path, size=(int(round(w * scale)), int(round(h * scale))))
                cand = dtm_get_thumbnail(category, sub_category, pack)
                if cand and os.path.isabs(cand):
                    return Transform(cand, crop=arms_crop, size=(170, 170))
            return Transform("mod_assets/monika/b/arms-steepling-10.png?dtm_raw=1", crop=arms_crop, size=(170, 170))

        # 3. Monika Torso: Zoom to upper torso
        if sub_category == "torso":
            torso_crop = (480, 440, 340, 340)
            if pack:
                pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", "monika", "torso", pack)
                if os.path.isdir(pack_dir):
                    for f in os.listdir(pack_dir):
                        if f.lower() in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg", "preview.png", "preview.jpg"):
                            thumb_path = os.path.join(pack_dir, f).replace("\\", "/")
                            w, h = dtm_get_image_size(thumb_path)
                            scale = min(170.0 / w, 170.0 / h)
                            return Transform(thumb_path, size=(int(round(w * scale)), int(round(h * scale))))
                cand = dtm_get_thumbnail(category, sub_category, pack)
                if cand and os.path.isabs(cand):
                    return Transform(cand, crop=torso_crop, size=(170, 170))
            return Transform("mod_assets/monika/b/body-def-0.png?dtm_raw=1", crop=torso_crop, size=(170, 170))

        # 4. Promise Ring: Pose 3 hand with ring zoom
        if sub_category == "promisering":
            ring_crop = (550, 380, 180, 180)
            if pack:
                pack_dir = os.path.join(store.DTM_BASE_PARENT, "textures", "accessories", "promisering", pack)
                if os.path.isdir(pack_dir):
                    for f in os.listdir(pack_dir):
                        if f.lower() in ("thumb.png", "thumbnail.png", "thumb.jpg", "thumbnail.jpg", "preview.png", "preview.jpg"):
                            thumb_path = os.path.join(pack_dir, f).replace(chr(92), "/")
                            w, h = dtm_get_image_size(thumb_path)
                            scale = min(170.0 / w, 170.0 / h)
                            return Transform(thumb_path, size=(int(round(w * scale)), int(round(h * scale))))
                cand = dtm_get_thumbnail(category, sub_category, pack)
                feat = cand if cand and os.path.isabs(cand) else "mod_assets/monika/a/promisering/3-10.png?dtm_raw=1"
            else:
                feat = "mod_assets/monika/a/promisering/3-10.png?dtm_raw=1"

            arms_img = "mod_assets/monika/b/arms-left-rest-10.png?dtm_raw=1"
            return LiveComposite(
                (170, 170),
                (0, 0), Transform(arms_img, crop=ring_crop, size=(170, 170)),
                (0, 0), Transform(feat, crop=ring_crop, size=(170, 170))
            )

        # 5. Accessories, Games, Room
        if not pack:
            thumb_path = dtm_get_default_thumb(sub_category)
        else:
            thumb_path = dtm_get_thumbnail(category, sub_category, pack)

        crop = None
        if sub_category in DTM_ACCESSORY_CROP_MAP:
            p_lower = thumb_path.replace("\\", "/").lower()
            if p_lower.endswith("/0.png") or p_lower.endswith("/2-10.png") or p_lower.endswith("quetzalplushie/0.png") or "monika/a/" in p_lower:
                crop = DTM_ACCESSORY_CROP_MAP[sub_category]

        if crop:
            w, h = crop[2], crop[3]
        else:
            w, h = dtm_get_image_size(thumb_path)

        if w <= 0 or h <= 0:
            return Transform(thumb_path, crop=crop, size=(180, 180)) if crop else Transform(thumb_path, size=(180, 180))

        if w == h:
            fit_size = (140, 140) if crop else (180, 180)
        else:
            max_dim = 170.0
            scale = min(max_dim / w, max_dim / h)
            fit_w = int(round(w * scale))
            fit_h = int(round(h * scale))
            fit_size = (fit_w, fit_h)

        if crop:
            return Transform(thumb_path, crop=crop, size=fit_size)
        else:
            return Transform(thumb_path, size=fit_size)

    def dtm_format_pack_name(name, max_len=15):
        if not name:
            return ""
        if len(name) > max_len:
            return name[:max_len - 3].rstrip(" -_") + "..."
        return name

transform dtm_thumb_resize:
    size (180, 180)

screen dtm_selector_sidebar(sub_category, packs_list, categories_list, folder_map):
    zorder 50
    default hovered_item = None

    $ h_color = getattr(store.mas_ui, "light_button_text_hover_color", "#ffffff")
    $ i_color = getattr(store.mas_globals, "button_text_idle_color", "#000000")
    $ is_night = store.mas_isNightNow() if hasattr(store, "mas_isNightNow") else False
    $ thumb_bg = "#262626e6" if is_night else "#e8e8e8cc"

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
                            Function(store.dtm_sidebar_adj.change, 0),
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
            yadjustment store.dtm_sidebar_adj
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
                    ysize 218
                    xalign 0.5
                    hover_sound gui.hover_sound
                    activate_sound gui.activate_sound
                    hovered SetScreenVariable("hovered_item", "___original___")
                    unhovered SetScreenVariable("hovered_item", None)
                    action Function(dtm_restore_preview, store.dtm_active_sub_category)
                    vbox:
                        xsize 180
                        spacing 0
                        
                        frame:
                            xsize 180
                            ysize 38
                            background Frame(
                                mas_getTimeFile(
                                    "mod_assets/frames/selector_top_frame_selected.png" 
                                    if is_orig_highlight else 
                                    "mod_assets/frames/selector_top_frame.png"
                                ),
                                left=4, top=4
                            )
                            padding (4, 2, 4, 2)
                            margin (0, 0)
                            text _("Original"):
                                xalign 0.5
                                yalign 0.5
                                text_align 0.5
                                font gui.default_font
                                size gui.text_size
                                layout "nobreak"
                                bold False
                                outlines []
                                color (h_color if is_orig_highlight else i_color)
                                
                        fixed:
                            xsize 180
                            ysize 180
                            add Solid(thumb_bg) size (180, 180)
                            add dtm_get_thumbnail_displayable(None, store.dtm_active_sub_category, None) xalign 0.5 yalign 0.5
                            add mas_getTimeFile("mod_assets/frames/selector_overlay.png") xalign 0.5 yalign 0.5
                            if is_orig_highlight:
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
                            ysize 218
                            xalign 0.5
                            hover_sound gui.hover_sound
                            activate_sound gui.activate_sound
                            hovered SetScreenVariable("hovered_item", pack)
                            unhovered SetScreenVariable("hovered_item", None)
                            action Function(dtm_apply_preview, store.dtm_active_sub_category, pack)
                            vbox:
                                xsize 180
                                spacing 0
                                
                                frame:
                                    xsize 180
                                    ysize 38
                                    background Frame(
                                        mas_getTimeFile(
                                            "mod_assets/frames/selector_top_frame_selected.png" 
                                            if is_highlight else 
                                            "mod_assets/frames/selector_top_frame.png"
                                        ),
                                        left=4, top=4
                                    )
                                    padding (4, 2, 4, 2)
                                    margin (0, 0)
                                    text dtm_format_pack_name(pack):
                                        xalign 0.5
                                        yalign 0.5
                                        text_align 0.5
                                        font gui.default_font
                                        size gui.text_size
                                        layout "nobreak"
                                        bold False
                                        outlines []
                                        color (h_color if is_highlight else i_color)
                                        
                                fixed:
                                    xsize 180
                                    ysize 180
                                    add Solid(thumb_bg) size (180, 180)
                                    add dtm_get_thumbnail_displayable(store.dtm_active_sub_category, store.dtm_active_sub_category, pack) xalign 0.5 yalign 0.5
                                    add mas_getTimeFile("mod_assets/frames/selector_overlay.png") xalign 0.5 yalign 0.5
                                    if is_highlight:
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
            action Function(dtm_restore_preview, store.dtm_active_sub_category)

        textbutton _("Cancel"):
            style "hkb_button"
            xalign 0.5
            hover_sound gui.hover_sound
            activate_sound gui.activate_sound
            action Return("cancel")
