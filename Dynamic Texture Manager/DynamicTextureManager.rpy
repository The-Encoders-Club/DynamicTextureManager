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
        "hair_theme": None,
        "face_theme": None,
        "body_theme": None,
        "torso_theme": None,
        "mug_theme": None,
        "hotchoc_theme": None,
        "promisering_theme": None,
        "quetzal_theme": None,
        "roses_theme": None,
        "thermos_theme": None,
        "calendar_theme": None,
        "chess_theme": None,
        "pong_field": None,
        "pong_theme": None,
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
        except Exception:
            pass

    mas_dtm_load_config()

init 999 python in dtm_core:
    import store
    import os
    import renpy

    try:
        import __builtin__ as builtins
    except ImportError:
        import builtins
    basestring = getattr(builtins, "basestring", str)

    def dtm_log(message):
        pass

    def _make_portable_path(folder_path):
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
        try:
            store._mas_dtm_indexes = {
                "eyes": {},
                "eyebrows": {},
                "mouth": {},
                "nose": {},
                "blush": {},
                "tears": {},
                "sweatdrop": {},
                "arms": {},
                "hair": {},
                "face": {},
                "body": {},
                "torso": {},
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
                "hair": ("monika", "hair"),
                "face": ("monika", "face"),
                "body": ("monika", "body"),
                "torso": ("monika", "body"),
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
                                        if f.lower().endswith((".png", ".ogg", ".wav", ".mp3", ".jpg", ".jpeg")):
                                            abs_path = os.path.join(root, f)
                                            abs_path_clean = abs_path.replace("\\", "/")
                                            rel_in_theme = os.path.relpath(abs_path, theme_path).replace("\\", "/").lower()
                                            theme_idx[rel_in_theme] = abs_path_clean
                                            theme_idx[f.lower()] = abs_path_clean
                                store._mas_dtm_indexes[cat][theme_folder.lower()] = theme_idx
        except Exception:
            pass

    category_prefixes = {
        "eyes": "mod_assets/monika/f/",
        "eyebrows": "mod_assets/monika/f/",
        "mouth": "mod_assets/monika/f/",
        "nose": "mod_assets/monika/f/",
        "blush": "mod_assets/monika/f/",
        "tears": "mod_assets/monika/f/",
        "sweatdrop": "mod_assets/monika/f/",
        "arms": "mod_assets/monika/b/",
        "hair": "mod_assets/monika/h/",
        "face": "mod_assets/monika/b/",
        "body": "mod_assets/monika/b/",
        "torso": "mod_assets/monika/b/",
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
        "hair": "hair_theme",
        "face": "face_theme",
        "body": "body_theme",
        "torso": "body_theme",
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
        if not norm_name:
            return None
        norm_name = norm_name.replace("\\", "/").lower()
        if "mod_assets/" in norm_name:
            norm_name = norm_name[norm_name.index("mod_assets/"):]

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
        elif norm_name.startswith("mod_assets/monika/h/"):
            return "hair"
        elif norm_name.startswith("mod_assets/monika/b/"):
            if "arms-" in norm_name:
                return "arms"
            elif "head" in norm_name:
                return "face"
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
            if not requested_path:
                return None
            requested_path = requested_path.replace("\\", "/").lower()
            if "mod_assets/" in requested_path:
                requested_path = requested_path[requested_path.index("mod_assets/"):]

            overrides = getattr(store, "mas_dtm_overrides", {})
            if category == "torso" and not overrides.get("body_theme"):
                if overrides.get("torso_theme"):
                    category = "torso"
                else:
                    category = "body"

            config_key = category_to_config_key.get(category)
            theme_path = overrides.get(config_key)
            if not theme_path and category == "body":
                theme_path = overrides.get("torso_theme")
            if not theme_path and category == "pong":
                theme_path = overrides.get("pong_theme")
            if not theme_path:
                return None

            theme_name = os.path.basename(theme_path.rstrip("/\\")).lower()
            all_cat_themes = getattr(store, "_mas_dtm_indexes", {}).get(category, {})
            idx = all_cat_themes.get(theme_name)
            if not idx and category == "body":
                all_cat_themes = getattr(store, "_mas_dtm_indexes", {}).get("torso", {})
                idx = all_cat_themes.get(theme_name)

            if not idx and theme_path:
                abs_theme = theme_path if os.path.isabs(theme_path) else os.path.join(store.DTM_BASE_PARENT, theme_path)
                if os.path.isdir(abs_theme):
                    idx = {}
                    for root, dirs, files in os.walk(abs_theme):
                        for f in files:
                            if f.lower().endswith((".png", ".ogg", ".wav", ".mp3", ".jpg", ".jpeg")):
                                abs_f = os.path.join(root, f).replace("\\", "/")
                                rel_f = os.path.relpath(abs_f, abs_theme).replace("\\", "/").lower()
                                idx[rel_f] = abs_f
                                idx[f.lower()] = abs_f
                    if hasattr(store, "_mas_dtm_indexes"):
                        if category not in store._mas_dtm_indexes:
                            store._mas_dtm_indexes[category] = {}
                        store._mas_dtm_indexes[category][theme_name] = idx

            if not idx:
                return None

            prefix = category_prefixes.get(category)
            rel_part = ""
            if prefix and requested_path.startswith(prefix):
                rel_part = requested_path[len(prefix):].lower()

            if rel_part and rel_part in idx:
                return idx[rel_part]

            basename = os.path.basename(requested_path).lower()
            if basename in idx:
                return idx[basename]

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

            elif category == "hair":
                if "hair-def-back" in basename or basename == "0.png":
                    candidates.extend(["0.png", "hair-def-back.png", "def/0.png", "def-back.png", "hair-def-def-back.png"])
                elif "hair-def-front" in basename or basename == "10.png":
                    candidates.extend(["10.png", "hair-def-front.png", "def/10.png", "def-front.png", "hair-def-def-front.png"])
                elif "def-0" in basename or "def-back" in basename:
                    candidates.extend(["def-0.png", "hair-leaning-def-def-back.png", "hair-leaning-def-back.png", "0.png"])
                elif "def-10" in basename or "def-front" in basename:
                    candidates.extend(["def-10.png", "hair-leaning-def-def-front.png", "hair-leaning-def-front.png", "10.png"])
                else:
                    candidates.append(basename)

            elif category == "arms":
                if "arms-" in basename:
                    candidates.append(basename.partition("arms-")[2])
            elif category == "face":
                if "head" in basename:
                    candidates.extend(["body-def-head.png", "head.png", "face-def-head.png", "face.png"])
            elif category in ("body", "torso"):
                if "body-" in basename:
                    candidates.append(basename.partition("body-")[2])
                candidates.extend(["body-def-0.png", "body-def-1.png"])
            elif category == "pong":
                if basename in ("pong.png", "paddle.png"):
                    candidates.extend(["pong.png", "pong - copy.png", "paddle.png"])
                elif basename in ("pong_ball.png", "ball.png"):
                    candidates.extend(["pong_ball.png", "ball.png"])
                elif basename in ("pong_field.png", "field.png", "bg.png"):
                    candidates.extend(["pong_field.png", "field.png", "bg.png"])
            elif category == "chess":
                if basename in ("chess_board.png", "board.png"):
                    candidates.extend(["chess_board.png", "board.png"])
            elif category == "quetzal":
                if "mid" in basename or "mid" in requested_path:
                    candidates.extend(["acs-quetzalplushie_mid-0.png", "quetzalplushie_mid-0.png", "mid-0.png", "mid.png", "0.png", "acs-quetzalplushie-0.png"])
                else:
                    candidates.extend(["acs-quetzalplushie-0.png", "0.png", "quetzalplushie-0.png", "quetzal.png"])
            elif category == "mug":
                candidates.extend(["acs-mug-0.png", "0.png", "mug-0.png", "mug.png"])
            elif category == "hotchoc_mug":
                candidates.extend(["acs-hotchoc_mug-0.png", "acs-hotchoc-0.png", "0.png", "hotchoc_mug-0.png", "hotchoc-0.png", "hotchoc.png"])
            elif category == "thermos_mug":
                candidates.extend(["acs-thermos_mug-0.png", "acs-thermos-0.png", "0.png", "thermos_mug-0.png", "thermos-0.png", "thermos.png"])
            elif category == "roses":
                candidates.extend(["acs-roses-0.png", "0.png", "roses-0.png", "roses.png"])
            elif category == "promisering":
                code = basename.replace(".png", "")
                candidates.extend([basename, code + ".png"])
                for ik in idx.keys():
                    if ik.endswith("-" + basename) or ik.endswith("-" + code + ".png") or ik.endswith("/" + basename):
                        candidates.append(ik)

            final_candidates = []
            for cand in candidates:
                final_candidates.append(cand)
                if cand.endswith("-n.png") or cand.endswith("-s.png") or cand.endswith("-h.png"):
                    final_candidates.append(cand[:-6] + ".png")

            for cand in final_candidates:
                if cand in idx:
                    return idx[cand]
        except Exception:
            pass

        return None

    def custom_loader_load(name, *args, **kwargs):
        try:
            if not isinstance(name, basestring):
                return renpy.loader._dtm_original_load(name, *args, **kwargs)

            # Bypass DTM override if ?dtm_raw is requested
            if "?dtm_raw" in name:
                clean_name = name.split("?")[0]
                return renpy.loader._dtm_original_load(clean_name, *args, **kwargs)

            real_name = name.split("?dtm_theme=")[0] if "?dtm_theme=" in name else name
            norm_name = real_name.replace("\\", "/").lower()
            clean_norm_name = norm_name[norm_name.index("mod_assets/"):] if "mod_assets/" in norm_name else norm_name

            category = get_category_for_path(clean_norm_name)
            if category:
                override = get_custom_override(category, clean_norm_name)
                if override and os.path.isfile(override):
                    return open(override, "rb")
        except Exception:
            pass

        return renpy.loader._dtm_original_load(name, *args, **kwargs)

    def apply_loader_hook():
        try:
            import renpy.loader
            if not hasattr(renpy.loader, "_dtm_original_load"):
                renpy.loader._dtm_original_load = renpy.loader.load
            renpy.loader.load = custom_loader_load
        except Exception:
            pass

    def force_update_mas_visuals(category=None, *args, **kwargs):
        try:
            if category is None and args:
                category = args[0]
            # 1. Clear MAS composite sprite caches for affected categories
            if hasattr(store, "mas_sprites"):
                cids = []
                if category in ("eyes", "eyebrows", "mouth", "nose", "blush", "tears", "sweatdrop", "face"):
                    cids = [1]
                elif category in ("arms", "torso", "body"):
                    cids = [2, 3]
                elif category == "hair":
                    cids = [0, 4]
                elif category in ("mug", "hotchoc_mug", "promisering", "quetzal", "roses", "thermos_mug"):
                    cids = [5]
                else:
                    cids = [0, 1, 2, 3, 4, 5]

                if hasattr(store.mas_sprites, "_gc"):
                    for cid in cids:
                        try:
                            store.mas_sprites._gc(cid).clear()
                        except Exception:
                            pass

                if hasattr(store.mas_sprites, "_clear_caches"):
                    try:
                        store.mas_sprites._clear_caches()
                    except Exception:
                        pass
                if hasattr(store.mas_sprites, "CACHE_TABLE"):
                    try:
                        for cid, cache in store.mas_sprites.CACHE_TABLE.items():
                            cache.clear()
                    except Exception:
                        pass
                if hasattr(store.mas_sprites, "MFM_CACHE"):
                    try:
                        store.mas_sprites.MFM_CACHE.clear()
                    except Exception:
                        pass

            # 2. Clear Ren'Py image surface cache to immediately free RAM
            try:
                import renpy.display.im as im
                if hasattr(im, "cache") and hasattr(im.cache, "clear"):
                    im.cache.clear()
            except Exception:
                pass

            # 3. Garbage collect unreferenced memory
            try:
                import gc
                gc.collect()
            except Exception:
                pass

            try:
                renpy.exports.free_memory()
            except Exception:
                pass

            # 4. Redraw screen
            renpy.exports.restart_interaction()
        except Exception:
            pass

    # ==========================================
    # VISUAL CONTROL API - SETTERS & RESETTERS
    # ==========================================
    def set_eyes_textures(folder_path):
        store.mas_dtm_overrides["eyes_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("eyes")

    def reset_eyes_textures():
        store.mas_dtm_overrides["eyes_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("eyes")

    def set_eyebrows_textures(folder_path):
        store.mas_dtm_overrides["eyebrows_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("eyebrows")

    def reset_eyebrows_textures():
        store.mas_dtm_overrides["eyebrows_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("eyebrows")

    def set_mouth_textures(folder_path):
        store.mas_dtm_overrides["mouth_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("mouth")

    def reset_mouth_textures():
        store.mas_dtm_overrides["mouth_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("mouth")

    def set_nose_textures(folder_path):
        store.mas_dtm_overrides["nose_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("nose")

    def reset_nose_textures():
        store.mas_dtm_overrides["nose_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("nose")

    def set_blush_textures(folder_path):
        store.mas_dtm_overrides["blush_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("blush")

    def reset_blush_textures():
        store.mas_dtm_overrides["blush_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("blush")

    def set_tears_textures(folder_path):
        store.mas_dtm_overrides["tears_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("tears")

    def reset_tears_textures():
        store.mas_dtm_overrides["tears_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("tears")

    def set_sweatdrop_textures(folder_path):
        store.mas_dtm_overrides["sweatdrop_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("sweatdrop")

    def reset_sweatdrop_textures():
        store.mas_dtm_overrides["sweatdrop_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("sweatdrop")

    def set_arms_textures(folder_path):
        store.mas_dtm_overrides["arms_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("arms")

    def reset_arms_textures():
        store.mas_dtm_overrides["arms_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("arms")

    def set_hair_textures(folder_path):
        store.mas_dtm_overrides["hair_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("hair")

    def reset_hair_textures():
        store.mas_dtm_overrides["hair_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("hair")

    def set_face_textures(folder_path):
        store.mas_dtm_overrides["face_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("face")

    def reset_face_textures():
        store.mas_dtm_overrides["face_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("face")

    def set_body_textures(folder_path):
        store.mas_dtm_overrides["body_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("body")

    def reset_body_textures():
        store.mas_dtm_overrides["body_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("body")

    def set_torso_textures(folder_path):
        set_body_textures(folder_path)

    def reset_torso_textures():
        reset_body_textures()

    def set_mug_textures(folder_path):
        store.mas_dtm_overrides["mug_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("mug")

    def reset_mug_textures():
        store.mas_dtm_overrides["mug_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("mug")

    def set_hotchoc_mug_textures(folder_path):
        store.mas_dtm_overrides["hotchoc_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("hotchoc_mug")

    def reset_hotchoc_mug_textures():
        store.mas_dtm_overrides["hotchoc_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("hotchoc_mug")

    def set_promisering_textures(folder_path):
        store.mas_dtm_overrides["promisering_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("promisering")

    def reset_promisering_textures():
        store.mas_dtm_overrides["promisering_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("promisering")

    def set_quetzal_textures(folder_path):
        store.mas_dtm_overrides["quetzal_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("quetzal")

    def reset_quetzal_textures():
        store.mas_dtm_overrides["quetzal_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("quetzal")

    def set_roses_textures(folder_path):
        store.mas_dtm_overrides["roses_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("roses")

    def reset_roses_textures():
        store.mas_dtm_overrides["roses_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("roses")

    def set_thermos_mug_textures(folder_path):
        store.mas_dtm_overrides["thermos_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("thermos_mug")

    def reset_thermos_mug_textures():
        store.mas_dtm_overrides["thermos_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("thermos_mug")

    def set_calendar_textures(folder_path):
        store.mas_dtm_overrides["calendar_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("calendar")

    def reset_calendar_textures():
        store.mas_dtm_overrides["calendar_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("calendar")

    def set_pong_textures(folder_path):
        p = _make_portable_path(folder_path)
        store.mas_dtm_overrides["pong_field"] = p
        store.mas_dtm_overrides["pong_theme"] = p
        store.mas_dtm_save_config()
        force_update_mas_visuals("pong")

    def reset_pong_textures():
        store.mas_dtm_overrides["pong_field"] = None
        store.mas_dtm_overrides["pong_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("pong")

    def set_chess_textures(folder_path):
        store.mas_dtm_overrides["chess_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("chess")

    def reset_chess_textures():
        store.mas_dtm_overrides["chess_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("chess")

    def set_nou_textures(folder_path):
        store.mas_dtm_overrides["nou_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        force_update_mas_visuals("nou")

    def reset_nou_textures():
        store.mas_dtm_overrides["nou_theme"] = None
        store.mas_dtm_save_config()
        force_update_mas_visuals("nou")

    def apply_preview_texture(category, folder_path):
        config_key = category_to_config_key.get(category)
        if config_key:
            store.mas_dtm_overrides[config_key] = _make_portable_path(folder_path) if folder_path else None
            force_update_mas_visuals(category)

    def restore_preview_textures(initial_overrides):
        if not initial_overrides:
            return
        changed = False
        for config_key, path in initial_overrides.items():
            if store.mas_dtm_overrides.get(config_key) != path:
                store.mas_dtm_overrides[config_key] = path
                changed = True
        if changed:
            force_update_mas_visuals(None)

init 1000 python:
    if hasattr(store, "dtm_core") and store.dtm_core:
        store.dtm_core.rebuild_all_indexes()
        store.dtm_core.apply_loader_hook()
