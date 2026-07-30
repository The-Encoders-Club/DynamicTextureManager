init -10 python:
    import json
    import os

    store.mas_dtm_overrides = {
        "eyes_theme": None,
        "eyebrows_theme": None,
        "mouth_theme": None,
        "nose_theme": None,
        "blush_theme": None,
        "tears_theme": None,
        "sweatdrop_theme": None,
        "arms_theme": None,
        "torso_theme": None,
        "body_theme": None,
        "mug_theme": None,
        "hotchoc_theme": None,
        "promisering_theme": None,
        "quetzal_theme": None,
        "roses_theme": None,
        "thermos_theme": None,
        "calendar_theme": None,
        "chess_theme": None,
        "pong_field": None,
        "nou_theme": None
    }

    # Purge any old overrides from persistent to clean saves
    for k in list(dir(persistent)):
        if k.startswith("_mas_dtm") or k.startswith("mas_dtm"):
            try:
                delattr(persistent, k)
            except Exception:
                pass

    # PC compatible path configuration
    store.DTM_BASE_PARENT = renpy.config.basedir

    store.DTM_CONFIG_PATH = os.path.join(store.DTM_BASE_PARENT, "textures", "config.json")

    def mas_dtm_load_config():
        try:
            if os.path.isfile(store.DTM_CONFIG_PATH):
                with open(store.DTM_CONFIG_PATH, "r") as f:
                    data = json.load(f)
                changed = False
                for k, v in data.items():
                    if k in store.mas_dtm_overrides:
                        if v is not None:
                            # Resolve path relative to DTM_BASE_PARENT if it is relative
                            abs_v = v if os.path.isabs(v) else os.path.join(store.DTM_BASE_PARENT, v)
                            if not os.path.exists(abs_v):
                                v = None
                                changed = True
                        store.mas_dtm_overrides[k] = v
                if changed:
                    mas_dtm_save_config()
        except Exception:
            pass

    def mas_dtm_save_config():
        try:
            data_copy = dict(store.mas_dtm_overrides)
            config_path = store.DTM_CONFIG_PATH
            
            def save_worker():
                try:
                    textures_dir = os.path.dirname(config_path)
                    if not os.path.exists(textures_dir):
                        os.makedirs(textures_dir)
                    with open(config_path, "w") as f:
                        json.dump(data_copy, f, indent=4)
                except Exception:
                    pass
            
            try:
                import threading
                t = threading.Thread(target=save_worker)
                t.daemon = True
                t.start()
            except Exception:
                save_worker()
        except Exception as e:
            try:
                print("DTM: Error saving config: " + str(e))
            except Exception:
                pass

    mas_dtm_load_config()

init 999 python in dtm_core:
    import store
    import os
    import renpy

    # Python compatibility helper for built-in types across Python 2 and 3
    try:
        import __builtin__ as builtins
    except ImportError:
        import builtins
    basestring = getattr(builtins, "basestring", str)

    if not hasattr(store, "_mas_dtm_surface_cache"):
        store._mas_dtm_surface_cache = {}

    def get_cached_surface(file_path):
        """
        Retrieves a cached Pygame surface for the given absolute path,
        or loads and decodes it if not already cached.
        Only stores in cache if requested from the main rendering thread to avoid prediction RAM bloat.
        """
        try:
            file_path_clean = file_path.replace("\\", "/")
            if file_path_clean in store._mas_dtm_surface_cache:
                return store._mas_dtm_surface_cache[file_path_clean]
                
            import renpy.display.pgrender as pgrender
            with open(file_path_clean, "rb") as f:
                surf = pgrender.load_image(f, file_path_clean)
                
            import threading
            if threading.currentThread().name == "MainThread":
                store._mas_dtm_surface_cache[file_path_clean] = surf
            return surf
        except Exception as e:
            dtm_log("get_cached_surface error for '{0}': {1}".format(file_path, e))
            return None

    def clear_surface_cache_for_category(category):
        """
        Evicts all cached surfaces in our custom surface cache for the given category
        to free up memory and prevent Out of Memory crashes.
        """
        try:
            marker = "/{0}/".format(category)
            keys_to_remove = [k for k in store._mas_dtm_surface_cache.keys() if marker in k.lower()]
            for k in keys_to_remove:
                store._mas_dtm_surface_cache.pop(k, None)
            dtm_log("clear_surface_cache_for_category: Cleared {0} surfaces for category '{1}'".format(len(keys_to_remove), category))
        except Exception as e:
            dtm_log("clear_surface_cache_for_category error: " + str(e))

    def dtm_log(message):
        pass

    def _make_portable_path(folder_path):
        """
        Converts an absolute path to relative for portable saving
        in the config.json file.
        """
        if folder_path is None:
            return None
        if os.path.isabs(folder_path):
            try:
                return os.path.relpath(folder_path, store.DTM_BASE_PARENT).replace("\\", "/")
            except Exception:
                pass
        return folder_path

    # Global dictionary for active theme file indexes
    if not hasattr(store, "_mas_dtm_indexes"):
        store._mas_dtm_indexes = {}

    def rebuild_all_indexes():
        """
        Scans the textures/ folder at startup and generates indexes for all themes.
        """
        try:
            dtm_log("Rebuilding all texture indexes...")
            store._mas_dtm_indexes = {
                "eyes": {},
                "eyebrows": {},
                "mouth": {},
                "nose": {},
                "blush": {},
                "tears": {},
                "sweatdrop": {},
                "arms": {},
                "torso": {},
                "body": {},
                "mug": {},
                "hotchoc_mug": {},
                "promisering": {},
                "quetzal": {},
                "roses": {},
                "thermos_mug": {},
                "calendar": {},
                "chess": {},
                "pong": {},
                "nou": {}
            }
            
            category_paths = {
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
            
            textures_root = os.path.join(store.DTM_BASE_PARENT, "textures")
            if os.path.isdir(textures_root):
                for cat, sub_paths in category_paths.items():
                    cat_dir = os.path.join(textures_root, sub_paths[0], sub_paths[1])
                    if os.path.isdir(cat_dir):
                        for theme_folder in os.listdir(cat_dir):
                            theme_path = os.path.join(cat_dir, theme_folder)
                            if os.path.isdir(theme_path):
                                theme_idx = {}
                                for root, dirs, files in os.walk(theme_path):
                                    for f in files:
                                        if f.lower().endswith((".png", ".ogg", ".wav")):
                                            abs_path = os.path.join(root, f)
                                            abs_path_clean = abs_path.replace("\\", "/")
                                            
                                            rel_in_theme = os.path.relpath(abs_path, theme_path).replace("\\", "/").lower()
                                            theme_idx[rel_in_theme] = abs_path_clean
                                            theme_idx[f.lower()] = abs_path_clean
                                            
                                store._mas_dtm_indexes[cat][theme_folder.lower()] = theme_idx
                                dtm_log("Indexed theme '{0}' in category '{1}' with {2} assets".format(theme_folder, cat, len(theme_idx)))
        except Exception as e:
            dtm_log("DTM Index Error: " + str(e))

    # Mapping from standard MAS asset prefixes to their corresponding DTM categories
    category_prefixes = {
        "eyes": "mod_assets/monika/f/",
        "eyebrows": "mod_assets/monika/f/",
        "mouth": "mod_assets/monika/f/",
        "nose": "mod_assets/monika/f/",
        "blush": "mod_assets/monika/f/",
        "tears": "mod_assets/monika/f/",
        "sweatdrop": "mod_assets/monika/f/",
        "arms": "mod_assets/monika/b/",
        "torso": "mod_assets/monika/b/",
        "body": "mod_assets/monika/b/",
        "mug": "mod_assets/monika/a/mug/",
        "hotchoc_mug": "mod_assets/monika/a/hotchoc_mug/",
        "promisering": "mod_assets/monika/a/promisering/",
        "quetzal": "mod_assets/monika/a/",
        "roses": "mod_assets/monika/a/roses/",
        "thermos_mug": "mod_assets/monika/a/thermos_mug/",
        "calendar": "mod_assets/calendar/",
        "chess": "mod_assets/games/chess/",
        "pong": "mod_assets/games/pong/",
        "nou": "mod_assets/games/nou/"
    }

    category_to_config_key = {
        "eyes": "eyes_theme",
        "eyebrows": "eyebrows_theme",
        "mouth": "mouth_theme",
        "nose": "nose_theme",
        "blush": "blush_theme",
        "tears": "tears_theme",
        "sweatdrop": "sweatdrop_theme",
        "arms": "arms_theme",
        "torso": "torso_theme",
        "body": "body_theme",
        "mug": "mug_theme",
        "hotchoc_mug": "hotchoc_theme",
        "promisering": "promisering_theme",
        "quetzal": "quetzal_theme",
        "roses": "roses_theme",
        "thermos_mug": "thermos_theme",
        "calendar": "calendar_theme",
        "chess": "chess_theme",
        "pong": "pong_field",
        "nou": "nou_theme"
    }

    def get_category_for_path(norm_name):
        if norm_name.startswith("mod_assets/monika/f/"):
            if "eyes-" in norm_name:
                return "eyes"
            elif "eyebrows-" in norm_name:
                return "eyebrows"
            elif "mouth-" in norm_name:
                return "mouth"
            elif "nose-" in norm_name:
                return "nose"
            elif "blush-" in norm_name:
                return "blush"
            elif "tears-" in norm_name:
                return "tears"
            elif "sweatdrop-" in norm_name:
                return "sweatdrop"
        elif norm_name.startswith("mod_assets/monika/b/"):
            if "arms-" in norm_name:
                return "arms"
            elif "body-" in norm_name:
                return "torso"
            else:
                return "body"
        elif norm_name.startswith("mod_assets/monika/a/"):
            if "mug/" in norm_name:
                return "mug"
            elif "hotchoc_mug/" in norm_name:
                return "hotchoc_mug"
            elif "promisering/" in norm_name:
                return "promisering"
            elif "quetzalplushie/" in norm_name or "quetzalplushie_mid/" in norm_name:
                return "quetzal"
            elif "roses/" in norm_name:
                return "roses"
            elif "thermos_mug/" in norm_name:
                return "thermos_mug"
        elif norm_name.startswith("mod_assets/calendar/"):
            return "calendar"
        elif norm_name.startswith("mod_assets/games/chess/"):
            return "chess"
        elif norm_name.startswith("mod_assets/games/pong/"):
            return "pong"
        elif norm_name.startswith("mod_assets/games/nou/"):
            return "nou"
        return None

    def get_custom_override(category, requested_path):
        try:
            # Get active theme from configuration
            overrides = getattr(store, "mas_dtm_overrides", {})
            
            # Fallback check for arms/torso to body
            if category in ("arms", "torso") and not overrides.get(category_to_config_key.get(category)):
                if overrides.get("body_theme"):
                    category = "body"
                    
            config_key = category_to_config_key.get(category)
            theme_path = overrides.get(config_key)
            if not theme_path:
                return None
                
            # Extract active theme folder name
            theme_name = os.path.basename(theme_path.rstrip("/\\")).lower()
            
            # Get pre-loaded index for this theme
            all_cat_themes = getattr(store, "_mas_dtm_indexes", {}).get(category, {})
            idx = all_cat_themes.get(theme_name)
            if not idx:
                return None
                
            prefix = category_prefixes.get(category)
            rel_part = ""
            if prefix and requested_path.startswith(prefix):
                rel_part = requested_path[len(prefix):].lower()
                
            # 1. Ultra-fast direct lookup (covers 95% of cases)
            if rel_part and rel_part in idx:
                return idx[rel_part]
                
            basename = os.path.basename(requested_path).lower()
            if basename in idx:
                return idx[basename]
                
            # 2. Generate candidate list (only if direct lookup fails)
            candidates = []
            if rel_part:
                candidates.append(rel_part)
            candidates.append(basename)
            
            if category in ("eyes", "eyebrows", "mouth", "nose", "blush", "tears", "sweatdrop"):
                pfx_key = category + "-"
                if pfx_key in basename:
                    code = basename.partition(pfx_key)[2]
                    candidates.append(pfx_key + code)
                    candidates.append(code)
                    candidates.append("face-" + pfx_key + code)
                    candidates.append("face-leaning-def-" + pfx_key + code)
                    
            elif category == "arms":
                if "arms-" in basename:
                    candidates.append(basename.partition("arms-")[2])
            elif category == "torso":
                if "body-" in basename:
                    candidates.append(basename.partition("body-")[2])
            elif category == "body":
                if "body-" in basename:
                    candidates.append(basename.partition("body-")[2])
                elif "arms-" in basename:
                    candidates.append(basename.partition("arms-")[2])
                    
            # Candidates with support for fallbacks (-n, -s, -h)
            final_candidates = []
            for cand in candidates:
                final_candidates.append(cand)
                if cand.endswith("-n.png") or cand.endswith("-s.png") or cand.endswith("-h.png"):
                    final_candidates.append(cand[:-6] + ".png")
                    
            # Search for the first matching candidate in our index
            for cand in final_candidates:
                if cand in idx:
                    return idx[cand]
        except Exception:
            pass
                    
        return None

    def custom_loader_load(name, *args, **kwargs):
        theme_suffix = "?dtm_theme="
        try:
            import renpy.loader
            if not isinstance(name, basestring):
                return renpy.loader._dtm_original_load(name, *args, **kwargs)
                
            if theme_suffix in name:
                parts = name.split(theme_suffix)
                real_name = parts[0]
                theme_name = parts[1]
            else:
                real_name = name
                theme_name = "none"
                
            norm_name = real_name.replace("\\", "/").lower()
            
            override = None
            category = get_category_for_path(norm_name)
                
            if category:
                override = get_custom_override(category, norm_name)
                
            if override:
                dtm_log("Loader redirect: '{0}' -> '{1}' (Active theme: {2})".format(name, override, theme_name))
                return open(override, "rb")
        except Exception as e:
            dtm_log("Loader hook load exception for '{0}': {1}".format(name, e))
            
        import renpy.loader
        real_name = name.split(theme_suffix)[0] if theme_suffix in name else name
        return renpy.loader._dtm_original_load(real_name, *args, **kwargs)

    def apply_loader_hook():
        """
        Safely applies the patch to Ren'Py's file loader and image classes.
        """
        # Hook for renpy.loader.load
        try:
            import renpy.loader
            if not hasattr(renpy.loader, "_dtm_original_load"):
                renpy.loader._dtm_original_load = renpy.loader.load
            renpy.loader.load = custom_loader_load
            dtm_log("File loader hook applied.")
        except Exception as e:
            dtm_log("File loader hook exception: " + str(e))

        # Helper to get the active theme suffix for DTM categories
        def get_suffix_for_file(filename):
            if not isinstance(filename, basestring):
                return None
            norm_name = filename.replace("\\", "/").lower()
            category = get_category_for_path(norm_name)
                
            if category:
                overrides = getattr(store, "mas_dtm_overrides", {})
                if category in ("arms", "torso") and not overrides.get(category_to_config_key.get(category)):
                    if overrides.get("body_theme"):
                        category = "body"
                        
                config_key = category_to_config_key.get(category)
                theme_path = overrides.get(config_key)
                if theme_path:
                    theme_name = os.path.basename(theme_path.rstrip("/\\")).lower()
                    return theme_name
            return None

        # Hook for renpy.display.im.Image
        try:
            import renpy.display.im
            if not hasattr(renpy.display.im.Image, "_dtm_original_init"):
                renpy.display.im.Image._dtm_original_init = renpy.display.im.Image.__init__
                
            def custom_im_image_init(self, filename, *args, **kwargs):
                theme_name = get_suffix_for_file(filename)
                if theme_name:
                    if "?dtm_theme=" not in filename:
                        filename = filename + "?dtm_theme=" + theme_name
                        dtm_log("im.Image instantiated with suffix: '{0}'".format(filename))
                renpy.display.im.Image._dtm_original_init(self, filename, *args, **kwargs)
                
            renpy.display.im.Image.__init__ = custom_im_image_init
            dtm_log("im.Image constructor hook applied.")
        except Exception as e:
            dtm_log("im.Image hook exception: " + str(e))

        # Hook for renpy.display.im.Composite
        try:
            import renpy.display.im
            if not hasattr(renpy.display.im.Composite, "_dtm_original_init"):
                renpy.display.im.Composite._dtm_original_init = renpy.display.im.Composite.__init__
                
            def custom_im_composite_init(self, size, *args, **properties):
                new_args = []
                modified = False
                for arg in args:
                    if isinstance(arg, basestring):
                        theme_name = get_suffix_for_file(arg)
                        if theme_name:
                            if "?dtm_theme=" not in arg:
                                arg = arg + "?dtm_theme=" + theme_name
                                modified = True
                    new_args.append(arg)
                if modified:
                    dtm_log("im.Composite initialized with suffixed children: {0}".format(new_args))
                renpy.display.im.Composite._dtm_original_init(self, size, *new_args, **properties)
                
            renpy.display.im.Composite.__init__ = custom_im_composite_init
            dtm_log("im.Composite constructor hook applied.")
        except Exception as e:
            dtm_log("im.Composite hook exception: " + str(e))

        # Hook for renpy.display.image.Image (Displayable Image)
        try:
            import renpy.display.image
            if not hasattr(renpy.display.image.Image, "_dtm_original_init"):
                renpy.display.image.Image._dtm_original_init = renpy.display.image.Image.__init__
                
            def custom_displayable_image_init(self, filename, *args, **kwargs):
                theme_name = get_suffix_for_file(filename)
                if theme_name:
                    if "?dtm_theme=" not in filename:
                        filename = filename + "?dtm_theme=" + theme_name
                        dtm_log("Displayable Image instantiated with suffix: '{0}'".format(filename))
                renpy.display.image.Image._dtm_original_init(self, filename, *args, **kwargs)
                
            renpy.display.image.Image.__init__ = custom_displayable_image_init
            dtm_log("renpy.display.image.Image constructor hook applied.")
        except Exception as e:
            dtm_log("renpy.display.image.Image hook exception: " + str(e))

        # Hook for renpy.display.im.Image.load to return pre-decoded surfaces directly
        try:
            import renpy.display.im as im
            if not hasattr(im.Image, "_dtm_original_load"):
                im.Image._dtm_original_load = im.Image.load
                
            def custom_im_image_load(self):
                name = self.filename
                theme_suffix = "?dtm_theme="
                real_name = name.split(theme_suffix)[0] if theme_suffix in name else name
                norm_name = real_name.replace("\\", "/").lower()
                
                category = get_category_for_path(norm_name)
                    
                if category:
                    override = get_custom_override(category, norm_name)
                    if override:
                        surf = get_cached_surface(override)
                        if surf is not None:
                            return surf
                return im.Image._dtm_original_load(self)
                
            im.Image.load = custom_im_image_load
            dtm_log("renpy.display.im.Image.load hook applied.")
        except Exception as e:
            dtm_log("renpy.display.im.Image.load hook exception: " + str(e))

    def predict_active_custom_assets():
        """
        Starts predicting only the currently active custom face assets
        to pre-populate Ren'Py's image cache safely and prevent out-of-memory.
        """
        try:
            dtm_log("predict_active_custom_assets: Starting background prediction for active themes.")
            count = 0
            overrides = getattr(store, "mas_dtm_overrides", {})
            for cat in ("eyes", "eyebrows", "mouth", "nose", "blush", "tears", "sweatdrop"):
                config_key = category_to_config_key.get(cat)
                if not config_key:
                    continue
                theme_path = overrides.get(config_key)
                if not theme_path:
                    continue
                theme_name = os.path.basename(theme_path.rstrip("/\\")).lower()
                all_cat_themes = getattr(store, "_mas_dtm_indexes", {}).get(cat, {})
                idx = all_cat_themes.get(theme_name)
                if not idx:
                    continue
                prefix = category_prefixes.get(cat)
                if not prefix:
                    continue
                unique_abs_paths = list(set(idx.values()))
                if not unique_abs_paths:
                    continue
                theme_dir = os.path.dirname(unique_abs_paths[0])
                for abs_path in unique_abs_paths:
                    rel_path = os.path.relpath(abs_path, theme_dir).replace("\\", "/").lower()
                    v_path = prefix + rel_path + "?dtm_theme=" + theme_name
                    try:
                        renpy.exports.start_predict(v_path)
                        count += 1
                    except Exception as pe:
                        dtm_log("predict_active_custom_assets: Error predicting '{0}': {1}".format(v_path, pe))
            dtm_log("predict_active_custom_assets: Successfully queued {0} active assets for prediction.".format(count))
        except Exception as e:
            dtm_log("predict_active_custom_assets error: " + str(e))

    def force_update_mas_visuals(category=None):
        """
        Forces the engine to rebuild all dynamic displayables immediately.
        Essential for hot-swapping.
        """
        dtm_log("force_update_mas_visuals: Requesting visual refresh for category: {0}".format(category))
        try:
            if hasattr(store.mas_sprites, "_gc"):
                # CID_FACE = 1, CID_ARMS = 2, CID_BODY = 3, CID_HAIR = 4, CID_ACS = 5
                cids = []
                if category in ("eyes", "eyebrows", "mouth", "nose", "blush", "tears", "sweatdrop"):
                    cids = [1] # CID_FACE
                elif category in ("arms", "torso", "body"):
                    cids = [2, 3] # CID_ARMS, CID_BODY
                elif category in ("mug", "hotchoc_mug", "promisering", "quetzal", "roses", "thermos_mug"):
                    cids = [5] # CID_ACS
                else:
                    cids = [1, 2, 3, 4, 5]
                
                dtm_log("force_update_mas_visuals: Clearing MAS CACHE_TABLE CIDs {0}.".format(cids))
                for cid in cids:
                    try:
                        store.mas_sprites._gc(cid).clear()
                    except Exception as e:
                        dtm_log("force_update_mas_visuals: Error clearing _gc({0}): {1}".format(cid, e))
        except Exception as e:
            dtm_log("force_update_mas_visuals: Error: " + str(e))
        try:
            if category is None and hasattr(store.mas_sprites, "_clear_caches"):
                dtm_log("force_update_mas_visuals: Calling store.mas_sprites._clear_caches().")
                store.mas_sprites._clear_caches()
        except Exception as e:
            dtm_log("force_update_mas_visuals: Error clear_caches: " + str(e))
            
        dtm_log("force_update_mas_visuals: Restarting interaction.")
        renpy.exports.restart_interaction()

    # ==========================================
    # VISUAL CONTROL API - SETTERS & RESETTERS
    # ==========================================
    def set_eyes_textures(folder_path):
        dtm_log("set_eyes_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("eyes")
        store.mas_dtm_overrides["eyes_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("eyes")

    def reset_eyes_textures():
        dtm_log("reset_eyes_textures called")
        clear_surface_cache_for_category("eyes")
        store.mas_dtm_overrides["eyes_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("eyes")

    def set_eyebrows_textures(folder_path):
        dtm_log("set_eyebrows_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("eyebrows")
        store.mas_dtm_overrides["eyebrows_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("eyebrows")

    def reset_eyebrows_textures():
        dtm_log("reset_eyebrows_textures called")
        clear_surface_cache_for_category("eyebrows")
        store.mas_dtm_overrides["eyebrows_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("eyebrows")

    def set_mouth_textures(folder_path):
        dtm_log("set_mouth_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("mouth")
        store.mas_dtm_overrides["mouth_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("mouth")

    def reset_mouth_textures():
        dtm_log("reset_mouth_textures called")
        clear_surface_cache_for_category("mouth")
        store.mas_dtm_overrides["mouth_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("mouth")

    def set_nose_textures(folder_path):
        dtm_log("set_nose_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("nose")
        store.mas_dtm_overrides["nose_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("nose")

    def reset_nose_textures():
        dtm_log("reset_nose_textures called")
        clear_surface_cache_for_category("nose")
        store.mas_dtm_overrides["nose_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("nose")

    def set_blush_textures(folder_path):
        dtm_log("set_blush_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("blush")
        store.mas_dtm_overrides["blush_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("blush")

    def reset_blush_textures():
        dtm_log("reset_blush_textures called")
        clear_surface_cache_for_category("blush")
        store.mas_dtm_overrides["blush_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("blush")

    def set_tears_textures(folder_path):
        dtm_log("set_tears_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("tears")
        store.mas_dtm_overrides["tears_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("tears")

    def reset_tears_textures():
        dtm_log("reset_tears_textures called")
        clear_surface_cache_for_category("tears")
        store.mas_dtm_overrides["tears_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("tears")

    def set_sweatdrop_textures(folder_path):
        dtm_log("set_sweatdrop_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("sweatdrop")
        store.mas_dtm_overrides["sweatdrop_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("sweatdrop")

    def reset_sweatdrop_textures():
        dtm_log("reset_sweatdrop_textures called")
        clear_surface_cache_for_category("sweatdrop")
        store.mas_dtm_overrides["sweatdrop_theme"] = None
        store.mas_dtm_save_config()
        predict_active_custom_assets()
        force_update_mas_visuals("sweatdrop")

    def set_arms_textures(folder_path):
        dtm_log("set_arms_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("arms")
        store.mas_dtm_overrides["arms_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("arms")

    def reset_arms_textures():
        dtm_log("reset_arms_textures called")
        clear_surface_cache_for_category("arms")
        store.mas_dtm_overrides["arms_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("arms")

    def set_torso_textures(folder_path):
        dtm_log("set_torso_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("torso")
        store.mas_dtm_overrides["torso_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("torso")

    def reset_torso_textures():
        dtm_log("reset_torso_textures called")
        clear_surface_cache_for_category("torso")
        store.mas_dtm_overrides["torso_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("torso")

    def set_body_textures(folder_path):
        dtm_log("set_body_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("body")
        store.mas_dtm_overrides["body_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("body")

    def reset_body_textures():
        dtm_log("reset_body_textures called")
        clear_surface_cache_for_category("body")
        store.mas_dtm_overrides["body_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("body")

    def set_mug_textures(folder_path):
        dtm_log("set_mug_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("mug")
        store.mas_dtm_overrides["mug_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("mug")

    def reset_mug_textures():
        dtm_log("reset_mug_textures called")
        clear_surface_cache_for_category("mug")
        store.mas_dtm_overrides["mug_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("mug")

    def set_hotchoc_mug_textures(folder_path):
        dtm_log("set_hotchoc_mug_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("hotchoc_mug")
        store.mas_dtm_overrides["hotchoc_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("hotchoc_mug")

    def reset_hotchoc_mug_textures():
        dtm_log("reset_hotchoc_mug_textures called")
        clear_surface_cache_for_category("hotchoc_mug")
        store.mas_dtm_overrides["hotchoc_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("hotchoc_mug")

    def set_promisering_textures(folder_path):
        dtm_log("set_promisering_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("promisering")
        store.mas_dtm_overrides["promisering_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("promisering")

    def reset_promisering_textures():
        dtm_log("reset_promisering_textures called")
        clear_surface_cache_for_category("promisering")
        store.mas_dtm_overrides["promisering_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("promisering")

    def set_quetzal_textures(folder_path):
        dtm_log("set_quetzal_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("quetzal")
        store.mas_dtm_overrides["quetzal_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("quetzal")

    def reset_quetzal_textures():
        dtm_log("reset_quetzal_textures called")
        clear_surface_cache_for_category("quetzal")
        store.mas_dtm_overrides["quetzal_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("quetzal")

    def set_roses_textures(folder_path):
        dtm_log("set_roses_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("roses")
        store.mas_dtm_overrides["roses_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("roses")

    def reset_roses_textures():
        dtm_log("reset_roses_textures called")
        clear_surface_cache_for_category("roses")
        store.mas_dtm_overrides["roses_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("roses")

    def set_thermos_mug_textures(folder_path):
        dtm_log("set_thermos_mug_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("thermos_mug")
        store.mas_dtm_overrides["thermos_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("thermos_mug")

    def reset_thermos_mug_textures():
        dtm_log("reset_thermos_mug_textures called")
        clear_surface_cache_for_category("thermos_mug")
        store.mas_dtm_overrides["thermos_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("thermos_mug")

    def set_calendar_textures(folder_path):
        dtm_log("set_calendar_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("calendar")
        store.mas_dtm_overrides["calendar_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("calendar")

    def reset_calendar_textures():
        dtm_log("reset_calendar_textures called")
        clear_surface_cache_for_category("calendar")
        store.mas_dtm_overrides["calendar_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("calendar")

    def set_pong_textures(folder_path):
        dtm_log("set_pong_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("pong")
        store.mas_dtm_overrides["pong_field"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("pong")

    def reset_pong_textures():
        dtm_log("reset_pong_textures called")
        clear_surface_cache_for_category("pong")
        store.mas_dtm_overrides["pong_field"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("pong")

    def set_chess_textures(folder_path):
        dtm_log("set_chess_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("chess")
        store.mas_dtm_overrides["chess_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("chess")

    def reset_chess_textures():
        dtm_log("reset_chess_textures called")
        clear_surface_cache_for_category("chess")
        store.mas_dtm_overrides["chess_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("chess")

    def set_nou_textures(folder_path):
        dtm_log("set_nou_textures: folder_path = {0}".format(folder_path))
        clear_surface_cache_for_category("nou")
        store.mas_dtm_overrides["nou_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("nou")

    def reset_nou_textures():
        dtm_log("reset_nou_textures called")
        clear_surface_cache_for_category("nou")
        store.mas_dtm_overrides["nou_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("nou")


init 1000 python:
    if hasattr(store, "dtm_core") and store.dtm_core:
        store.dtm_core.rebuild_all_indexes()
        store.dtm_core.apply_loader_hook()
        
        # Register prediction callbacks to run after game init is complete
        config.start_callbacks.append(store.dtm_core.predict_active_custom_assets)
        config.after_load_callbacks.append(store.dtm_core.predict_active_custom_assets)