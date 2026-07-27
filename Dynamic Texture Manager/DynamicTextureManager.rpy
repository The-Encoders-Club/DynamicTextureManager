init -10 python:
    import json
    import os

    # Initialize the variable store
    store.mas_dtm_overrides = {
        "eyes_theme": None,
        "mouth_theme": None,
        "nose_theme": None,
        "body_theme": None,
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
            textures_dir = os.path.dirname(store.DTM_CONFIG_PATH)
            if not os.path.exists(textures_dir):
                os.makedirs(textures_dir)
            with open(store.DTM_CONFIG_PATH, "w") as f:
                json.dump(store.mas_dtm_overrides, f, indent=4)
        except Exception as e:
            renpy.log("DTM: Error saving config: " + str(e))

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
            store._mas_dtm_indexes = {
                "eyes": {},
                "mouth": {},
                "nose": {},
                "body": {},
                "chess": {},
                "pong": {},
                "nou": {}
            }
            
            category_paths = {
                "eyes": ("monika", "eyes"),
                "mouth": ("monika", "mouth"),
                "nose": ("monika", "nose"),
                "body": ("monika", "body"),
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
        except Exception as e:
            try:
                renpy.log("DTM Index Error: " + str(e))
            except Exception:
                pass

    # Mapping from standard MAS asset prefixes to their corresponding DTM categories
    category_prefixes = {
        "eyes": "mod_assets/monika/f/",
        "mouth": "mod_assets/monika/f/",
        "nose": "mod_assets/monika/f/",
        "body": "mod_assets/monika/b/",
        "chess": "mod_assets/games/chess/",
        "pong": "mod_assets/games/pong/",
        "nou": "mod_assets/games/nou/"
    }

    category_to_config_key = {
        "eyes": "eyes_theme",
        "mouth": "mouth_theme",
        "nose": "nose_theme",
        "body": "body_theme",
        "chess": "chess_theme",
        "pong": "pong_field",
        "nou": "nou_theme"
    }

    def get_custom_override(category, requested_path):
        try:
            # Get active theme from configuration
            overrides = getattr(store, "mas_dtm_overrides", {})
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
            
            if category in ("eyes", "mouth", "nose"):
                pfx_key = category + "-"
                if pfx_key in basename:
                    code = basename.partition(pfx_key)[2]
                    candidates.append(pfx_key + code)
                    candidates.append(code)
                    
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
        try:
            import renpy.loader
            if not isinstance(name, basestring):
                return renpy.loader._dtm_original_load(name, *args, **kwargs)
                
            norm_name = name.replace("\\", "/").lower()
            
            override = None
            
            # Determine category of requested resource
            category = None
            if norm_name.startswith("mod_assets/monika/f/"):
                if "eyes-" in norm_name:
                    category = "eyes"
                elif "mouth-" in norm_name:
                    category = "mouth"
                elif "nose-" in norm_name:
                    category = "nose"
            elif norm_name.startswith("mod_assets/monika/b/"):
                category = "body"
            elif norm_name.startswith("mod_assets/games/chess/"):
                category = "chess"
            elif norm_name.startswith("mod_assets/games/pong/"):
                category = "pong"
            elif norm_name.startswith("mod_assets/games/nou/"):
                category = "nou"
                
            if category:
                override = get_custom_override(category, norm_name)
                
            if override:
                return open(override, "rb")
        except Exception as e:
            try:
                renpy.log("DTM Hook Load Error: " + str(e))
            except Exception:
                pass
            
        import renpy.loader
        return renpy.loader._dtm_original_load(name, *args, **kwargs)

    def apply_loader_hook():
        """
        Safely applies the patch to Ren'Py's file loader.
        """
        try:
            import renpy.loader
            if not hasattr(renpy.loader, "_dtm_original_load"):
                renpy.loader._dtm_original_load = renpy.loader.load
            renpy.loader.load = custom_loader_load
        except Exception as e:
            try:
                renpy.log("DTM Hook Apply Error: " + str(e))
            except Exception:
                pass

    def force_update_mas_visuals():
        """
        Forces the engine to rebuild all dynamic displayables immediately.
        Essential for hot-swapping.
        """
        try:
            if hasattr(store.mas_sprites, "_gc"):
                for cid in (1, 2, 3, 4, 5): # CID_FACE, CID_ARMS, CID_BODY, CID_HAIR, CID_ACS
                    try:
                        store.mas_sprites._gc(cid).clear()
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            if hasattr(store.mas_sprites, "_clear_caches"):
                store.mas_sprites._clear_caches()
        except Exception:
            pass
        try:
            renpy.display.im.cache.clear()
        except Exception:
            pass
        renpy.exports.restart_interaction()

    # ==========================================
    # VISUAL CONTROL API - SETTERS & RESETTERS
    # ==========================================
    def set_eyes_textures(folder_path):
        store.mas_dtm_overrides["eyes_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_eyes_textures():
        store.mas_dtm_overrides["eyes_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_mouth_textures(folder_path):
        store.mas_dtm_overrides["mouth_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_mouth_textures():
        store.mas_dtm_overrides["mouth_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_nose_textures(folder_path):
        store.mas_dtm_overrides["nose_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_nose_textures():
        store.mas_dtm_overrides["nose_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_body_textures(folder_path):
        store.mas_dtm_overrides["body_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_body_textures():
        store.mas_dtm_overrides["body_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_pong_textures(folder_path):
        store.mas_dtm_overrides["pong_field"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_pong_textures():
        store.mas_dtm_overrides["pong_field"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_chess_textures(folder_path):
        store.mas_dtm_overrides["chess_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_chess_textures():
        store.mas_dtm_overrides["chess_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def set_nou_textures(folder_path):
        store.mas_dtm_overrides["nou_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals()

    def reset_nou_textures():
        store.mas_dtm_overrides["nou_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals()


init 1000 python:
    if hasattr(store, "dtm_core") and store.dtm_core:
        store.dtm_core.rebuild_all_indexes()
        store.dtm_core.apply_loader_hook()