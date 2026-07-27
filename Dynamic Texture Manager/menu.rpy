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

        # Initialize submod menu state
        dtm_current_view = "main"
        dtm_nav_stack = []
        dtm_exit = False
        dtm_action_to_run = None
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
                    (_("Monika"), "dtm_monika"),
                    (_("Games"), "dtm_games")
                ]
            elif dtm_current_view == "dtm_monika":
                main_items = [
                    (_("Eyes"), "dtm_scan_eyes"),
                    (_("Mouth"), "dtm_scan_mouth"),
                    (_("Nose"), "dtm_scan_nose"),
                    (_("Body"), "dtm_scan_body")
                ]
            elif dtm_current_view == "dtm_games":
                main_items = [
                    (_("Chess"), "dtm_scan_chess"),
                    (_("Pong"), "dtm_scan_pong"),
                    (_("NOU"), "dtm_scan_nou")
                ]
            elif dtm_current_view.startswith("dtm_scan_"):
                sub_path = dtm_current_view[9:]
                folder_map = {
                    "eyes": "monika/eyes",
                    "mouth": "monika/mouth",
                    "nose": "monika/nose",
                    "body": "monika/body",
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

        # Call the native MAS twopane screen directly. We pass 1 as cat_length to hide the native Go Back button on the left.
        call screen twopane_scrollable_menu(prev_items, main_items, store.evhand.LEFT_AREA, store.evhand.LEFT_XALIGN, store.evhand.RIGHT_AREA, store.evhand.RIGHT_XALIGN, 1) nopredict

        python:
            # Reset action state
            dtm_action_to_run = None
            
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
                        "mouth": ("monika", "mouth"),
                        "nose": ("monika", "nose"),
                        "body": ("monika", "body"),
                        "chess": ("games", "chess"),
                        "pong": ("games", "pong"),
                        "nou": ("games", "nou")
                    }
                    p_sub = folder_map[sub_path]
                    abs_folder = os.path.join(store.DTM_BASE_PARENT, "textures", p_sub[0], p_sub[1], folder_name)
                    func_map = {
                        "eyes": store.dtm_core.set_eyes_textures,
                        "mouth": store.dtm_core.set_mouth_textures,
                        "nose": store.dtm_core.set_nose_textures,
                        "body": store.dtm_core.set_body_textures,
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
                        "mouth": store.dtm_core.reset_mouth_textures,
                        "nose": store.dtm_core.reset_nose_textures,
                        "body": store.dtm_core.reset_body_textures,
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
