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

    if store.DTM_BASE_PARENT not in renpy.config.searchpath:
        renpy.config.searchpath.append(store.DTM_BASE_PARENT)

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
        except Exception:
            pass

    mas_dtm_load_config()

init 999 python in dtm_core:
    import store
    import os
    import shutil

    # Python compatibility helper
    try:
        basestring
    except NameError:
        basestring = str

    def _get_rel_path(abs_path):
        """
        Convierte una ruta absoluta a relativa basada en el directorio del juego (PC),
        utilizando formato POSIX para compatibilidad con el VFS de Ren'Py.
        """
        try:
            rel = os.path.relpath(abs_path, store.DTM_BASE_PARENT)
            return rel.replace("\\", "/")
        except Exception:
            return abs_path

    def _make_portable_path(folder_path):
        """
        Convierte una ruta absoluta a relativa para guardarla de forma portable
        en el archivo config.json.
        """
        if folder_path is None:
            return None
        if os.path.isabs(folder_path):
            try:
                return os.path.relpath(folder_path, store.DTM_BASE_PARENT).replace("\\", "/")
            except Exception:
                pass
        return folder_path

    if not hasattr(store, "_mas_dtm_originals"):
        store._mas_dtm_originals = {
            "eye_map": store.mas_sprite_decoder.EYE_MAP.copy()
        }

    def force_update_mas_visuals():
        """
        Fuerza al motor a reconstruir inmediatamente todos los displayables dinámicos.
        Esencial para el intercambio en caliente (Hot-Swap).
        """
        renpy.restart_interaction()

    # ==========================================
    # VISUAL CONTROL API - FACE
    # ==========================================
    def set_eyes_textures(folder_path):
        store.mas_dtm_overrides["eyes_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_sprite_overrides()
        force_update_mas_visuals()

    def reset_eyes_textures():
        store.mas_dtm_overrides["eyes_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "_mas_dtm_original_rk_face"):
            store.mas_sprites._rk_face = store._mas_dtm_original_rk_face
        apply_sprite_overrides()
        force_update_mas_visuals()

    def set_mouth_textures(folder_path):
        store.mas_dtm_overrides["mouth_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_sprite_overrides()
        force_update_mas_visuals()

    def reset_mouth_textures():
        store.mas_dtm_overrides["mouth_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "_mas_dtm_original_rk_face"):
            store.mas_sprites._rk_face = store._mas_dtm_original_rk_face
        apply_sprite_overrides()
        force_update_mas_visuals()

    def set_nose_textures(folder_path):
        store.mas_dtm_overrides["nose_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_sprite_overrides()
        force_update_mas_visuals()

    def reset_nose_textures():
        store.mas_dtm_overrides["nose_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "_mas_dtm_original_rk_face"):
            store.mas_sprites._rk_face = store._mas_dtm_original_rk_face
        apply_sprite_overrides()
        force_update_mas_visuals()

    # ==========================================
    # VISUAL CONTROL API - BODY
    # ==========================================
    def set_body_textures(folder_path):
        store.mas_dtm_overrides["body_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_body_overrides()
        force_update_mas_visuals()

    def reset_body_textures():
        store.mas_dtm_overrides["body_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "_mas_dtm_original__rk_base_body_nh"):
            store.mas_sprites._rk_base_body_nh = store._mas_dtm_original__rk_base_body_nh
        if hasattr(store, "_mas_dtm_original__rk_base_body_lean_nh"):
            store.mas_sprites._rk_base_body_lean_nh = store._mas_dtm_original__rk_base_body_lean_nh
        if hasattr(store, "_mas_dtm_original__rk_body_nh"):
            store.mas_sprites._rk_body_nh = store._mas_dtm_original__rk_body_nh
        if hasattr(store, "_mas_dtm_original__rk_body_lean_nh"):
            store.mas_sprites._rk_body_lean_nh = store._mas_dtm_original__rk_body_lean_nh
        if hasattr(store, "_mas_dtm_original__add_arms_rk"):
            store.mas_sprites._add_arms_rk = store._mas_dtm_original__add_arms_rk
        if hasattr(store, "_mas_dtm_original__rk_head"):
            store.mas_sprites._rk_head = store._mas_dtm_original__rk_head
        apply_body_overrides()
        force_update_mas_visuals()

    # ==========================================
    # VISUAL CONTROL API - GAMES
    # ==========================================
    def set_pong_textures(folder_path):
        store.mas_dtm_overrides["pong_field"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_pong_overrides()
        force_update_mas_visuals()

    def reset_pong_textures():
        store.mas_dtm_overrides["pong_field"] = None
        store.mas_dtm_save_config()
        renpy.display.image.images[("bg", "pong", "field")] = store.Image("mod_assets/games/pong/pong_field.png")
        if hasattr(store, "_mas_dtm_original_pong_init") and hasattr(store, "PongDisplayable"):
            store.PongDisplayable.__init__ = store._mas_dtm_original_pong_init
        if hasattr(store, "_mas_dtm_pong_surfaces"):
            del store._mas_dtm_pong_surfaces
        renpy.display.im.cache.clear()
        force_update_mas_visuals()

    def set_chess_textures(folder_path):
        store.mas_dtm_overrides["chess_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_chess_overrides()

    def reset_chess_textures():
        store.mas_dtm_overrides["chess_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "MASPiece"):
            if hasattr(store, "_mas_dtm_original_chess_map"):
                store.MASPiece.IMG_MAP.clear()
                store.MASPiece.IMG_MAP.update(store._mas_dtm_original_chess_map)
        if hasattr(store, "_mas_dtm_original_chess_board"):
            store.MASChessDisplayableBase.BOARD_IMAGE = store._mas_dtm_original_chess_board
        if hasattr(store, "_mas_dtm_original_chess_indicator_player"):
            store.MASChessDisplayableBase.MOVE_INDICATOR_PLAYER = store._mas_dtm_original_chess_indicator_player
        if hasattr(store, "_mas_dtm_original_chess_indicator_monika"):
            store.MASChessDisplayableBase.MOVE_INDICATOR_MONIKA = store._mas_dtm_original_chess_indicator_monika
        if hasattr(store, "_mas_dtm_original_chess_hl_green"):
            store.MASChessDisplayableBase.PIECE_HIGHLIGHT_GREEN_IMAGE = store._mas_dtm_original_chess_hl_green
        if hasattr(store, "_mas_dtm_original_chess_hl_red"):
            store.MASChessDisplayableBase.PIECE_HIGHLIGHT_RED_IMAGE = store._mas_dtm_original_chess_hl_red
        if hasattr(store, "_mas_dtm_original_chess_hl_yellow"):
            store.MASChessDisplayableBase.PIECE_HIGHLIGHT_YELLOW_IMAGE = store._mas_dtm_original_chess_hl_yellow
        if hasattr(store, "_mas_dtm_original_chess_hl_magenta"):
            store.MASChessDisplayableBase.PIECE_HIGHLIGHT_MAGENTA_IMAGE = store._mas_dtm_original_chess_hl_magenta
        renpy.display.im.cache.clear()
        force_update_mas_visuals()

    def set_nou_textures(folder_path):
        store.mas_dtm_overrides["nou_theme"] = _make_portable_path(folder_path)
        store.mas_dtm_save_config()
        apply_nou_overrides()

    def reset_nou_textures():
        store.mas_dtm_overrides["nou_theme"] = None
        store.mas_dtm_save_config()
        if hasattr(store, "_mas_dtm_original_filter_switch"):
            store.MASFilterSwitch = store._mas_dtm_original_filter_switch
        if hasattr(store, "mas_nou") and hasattr(store.mas_nou.NOU, "_load_sfx"):
            store.mas_nou.NOU._load_sfx()
        if hasattr(store, "mas_cardgames") and hasattr(store.mas_cardgames, "_m1_zz_cardgames__scanDeskSprites"):
            store.mas_cardgames.DESK_SPRITES_MAP.clear()
            store.mas_cardgames._m1_zz_cardgames__scanDeskSprites()
        if hasattr(store, "_mas_dtm_original_nou_init") and hasattr(store, "mas_nou"):
            store.mas_nou.NOU.__init__ = store._mas_dtm_original_nou_init
        if hasattr(store, "_mas_dtm_original_load_card_asset") and hasattr(store, "mas_nou"):
            store.mas_nou.NOU._m1_zz_cardgames__load_card_asset = store._mas_dtm_original_load_card_asset
        renpy.display.im.cache.clear()
        force_update_mas_visuals()

    # ==========================================
    # INJECTION LOGIC - BODY
    # ==========================================
    def apply_body_overrides():
        body_folder_raw = store.mas_dtm_overrides.get("body_theme", None)
        body_folder = None
        if body_folder_raw:
            body_folder = body_folder_raw if os.path.isabs(body_folder_raw) else os.path.join(store.DTM_BASE_PARENT, body_folder_raw)

        import os
        mod_art_path = getattr(store.mas_sprites, "MOD_ART_PATH", "mod_assets/monika/").replace("\\", "/")
        body_folder_valid = bool(body_folder and os.path.isdir(body_folder))

        if not body_folder_valid:
            if hasattr(store, "_mas_dtm_original__rk_base_body_nh"):
                store.mas_sprites._rk_base_body_nh = store._mas_dtm_original__rk_base_body_nh
            if hasattr(store, "_mas_dtm_original__rk_base_body_lean_nh"):
                store.mas_sprites._rk_base_body_lean_nh = store._mas_dtm_original__rk_base_body_lean_nh
            if hasattr(store, "_mas_dtm_original__rk_body_nh"):
                store.mas_sprites._rk_body_nh = store._mas_dtm_original__rk_body_nh
            if hasattr(store, "_mas_dtm_original__rk_body_lean_nh"):
                store.mas_sprites._rk_body_lean_nh = store._mas_dtm_original__rk_body_lean_nh
            if hasattr(store, "_mas_dtm_original__add_arms_rk"):
                store.mas_sprites._add_arms_rk = store._mas_dtm_original__add_arms_rk
            if hasattr(store, "_mas_dtm_original__rk_head"):
                store.mas_sprites._rk_head = store._mas_dtm_original__rk_head

            try:
                if hasattr(store.mas_sprites, "_gc"):
                    store.mas_sprites._gc(store.mas_sprites.CID_BODY).clear()
                    store.mas_sprites._gc(store.mas_sprites.CID_HEAD).clear()
                    store.mas_sprites._gc(store.mas_sprites.CID_ARMS).clear()
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
            return

        body_index = {}
        for root, dirs, files in os.walk(body_folder):
            for f in files:
                if f.lower().endswith(".png"):
                    abs_path = os.path.join(root, f)
                    rel_path_in_theme = os.path.relpath(abs_path, body_folder).replace("\\", "/")
                    rel_path_clean = _get_rel_path(abs_path)
                    body_index[rel_path_in_theme] = rel_path_clean
                    body_index[f] = rel_path_clean
                    
                    if "-def-" in rel_path_in_theme:
                        body_index[rel_path_in_theme.replace("-def-", "-")] = rel_path_clean
                    if "-def-" in f:
                        body_index[f.replace("-def-", "-")] = rel_path_clean

        def _get_body_override(img_str):
            if not body_folder:
                return None

            normalized = img_str.replace("\\", "/")
            if not normalized.startswith(mod_art_path):
                return None

            rel_path = normalized[len(mod_art_path):].lstrip("/\\")
            if not rel_path.startswith("b/"):
                return None

            res = body_index.get(rel_path)
            if res: return res

            flat_name = os.path.basename(rel_path)
            res = body_index.get(flat_name)
            if res: return res

            if "-def-" in rel_path:
                rel_path_alt = rel_path.replace("-def-", "-")
                res = body_index.get(rel_path_alt)
                if res: return res
                
                flat_name_alt = os.path.basename(rel_path_alt)
                res = body_index.get(flat_name_alt)
                if res: return res

            res = body_index.get(normalized)
            if res: return res

            game_key = "game/" + normalized
            res = body_index.get(game_key)
            if res: return res

            return None

        def _patch_body_method(method_name, wrapper):
            if not hasattr(store.mas_sprites, method_name):
                return
            original = getattr(store.mas_sprites, method_name)
            store_attr = "_mas_dtm_original_" + method_name
            if not hasattr(store, store_attr):
                setattr(store, store_attr, original)
            setattr(store.mas_sprites, method_name, wrapper)

        def custom_rk_base_body_nh(rk_list, flt, bcode):
            img_str = "".join((store.mas_sprites.B_MAIN, store.mas_sprites.BASE_BODY_STR, bcode, store.mas_sprites.FILE_EXT))
            override = _get_body_override(img_str)
            if override:
                img_key = (flt, img_str)
                if img_key in store.mas_sprites._gc(store.mas_sprites.CID_BODY):
                    rk_list.append((img_key, store.mas_sprites.CID_BODY, None, None))
                    return
                rk_list.append((img_key, store.mas_sprites.CID_BODY, store.Image(override), None))
            else:
                store._mas_dtm_original__rk_base_body_nh(rk_list, flt, bcode)

        def custom_rk_base_body_lean_nh(rk_list, lean, flt, bcode):
            img_str = "".join((store.mas_sprites.B_MAIN, store.mas_sprites.PREFIX_BODY_LEAN, lean, store.mas_sprites.ART_DLM, bcode, store.mas_sprites.FILE_EXT))
            override = _get_body_override(img_str)
            if override:
                img_key = (flt, img_str)
                if img_key in store.mas_sprites._gc(store.mas_sprites.CID_BODY):
                    rk_list.append((img_key, store.mas_sprites.CID_BODY, None, None))
                    return
                rk_list.append((img_key, store.mas_sprites.CID_BODY, store.Image(override), None))
            else:
                store._mas_dtm_original__rk_base_body_lean_nh(rk_list, lean, flt, bcode)

        def custom_rk_head(rk_list, flt, lean):
            if lean:
                img_str = "".join((
                    store.mas_sprites.B_MAIN,
                    store.mas_sprites.PREFIX_BODY_LEAN,
                    lean,
                    store.mas_sprites.ART_DLM,
                    store.mas_sprites.HEAD,
                    store.mas_sprites.FILE_EXT,
                ))
            else:
                img_str = "".join((
                    store.mas_sprites.B_MAIN,
                    store.mas_sprites.BASE_BODY_STR,
                    store.mas_sprites.HEAD,
                    store.mas_sprites.FILE_EXT
                ))

            override = _get_body_override(img_str)
            if override:
                img_key = (flt, img_str)
                if img_key in store.mas_sprites._gc(store.mas_sprites.CID_BODY):
                    rk_list.append((img_key, store.mas_sprites.CID_BODY, None, None))
                    return
                rk_list.append((img_key, store.mas_sprites.CID_BODY, store.Image(override), None))
            else:
                store._mas_dtm_original__rk_head(rk_list, flt, lean)

        def custom_rk_body_nh(rk_list, clothing, flt, bcode):
            img_list = (
                store.mas_sprites.C_MAIN,
                clothing.img_sit,
                "/",
                store.mas_sprites.NEW_BODY_STR,
                store.mas_sprites.ART_DLM,
                bcode,
                store.mas_sprites.FILE_EXT,
            )
            img_str = "".join(img_list)
            override = _get_body_override(img_str)
            if override:
                img_key = (flt, img_str)
                if img_key in store.mas_sprites._gc(store.mas_sprites.CID_BODY):
                    rk_list.append((img_key, store.mas_sprites.CID_BODY, None, None))
                    return
                body_image = store.Image(override)
                rk_list.append((
                    img_key,
                    store.mas_sprites.CID_BODY,
                    body_image,
                    store.mas_sprites._bhli(img_list, clothing.gethlc(bcode, None, flt)),
                ))
            else:
                store._mas_dtm_original__rk_body_nh(rk_list, clothing, flt, bcode)

        def custom_rk_body_lean_nh(rk_list, clothing, lean, flt, bcode):
            img_list = (
                store.mas_sprites.C_MAIN,
                clothing.img_sit,
                "/",
                store.mas_sprites.PREFIX_BODY_LEAN,
                lean,
                store.mas_sprites.ART_DLM,
                bcode,
                store.mas_sprites.FILE_EXT,
            )
            img_str = "".join(img_list)
            override = _get_body_override(img_str)
            if override:
                img_key = (flt, img_str)
                cache_body = store.mas_sprites._gc(store.mas_sprites.CID_BODY)
                if img_key in cache_body:
                    rk_list.append((img_key, store.mas_sprites.CID_BODY, None, None))
                    return
                body_image = store.Image(override)
                rk_list.append((
                    img_key,
                    store.mas_sprites.CID_BODY,
                    body_image,
                    store.mas_sprites._bhli(img_list, clothing.gethlc(bcode, lean, flt)),
                ))
            else:
                store._mas_dtm_original__rk_body_lean_nh(rk_list, clothing, lean, flt, bcode)

        def custom_add_arms_rk(rk_list, arms, pfx, flt, bcode, clothing_t, leanpose):
            if not hasattr(store, "_mas_dtm_original__add_arms_rk"):
                return
            
            old_len = len(rk_list)
            store._mas_dtm_original__add_arms_rk(rk_list, arms, pfx, flt, bcode, clothing_t, leanpose)
            
            if len(rk_list) == old_len or rk_list[-1][2] is None or not body_folder_valid:
                return
            
            arm_data = []
            if arms:
                for arm in arms:
                    tag_list = arm.get(bcode)
                    if len(tag_list) > 0:
                        arm_data.append((arm, tag_list))
            
            if not arm_data:
                return
            
            pfx_str = "".join(pfx)
            if len(arm_data) < 2:
                arm, tag_list = arm_data[0]
                img_str = "".join((pfx_str, "".join(tag_list), store.mas_sprites.FILE_EXT))
                override = _get_body_override(img_str)
                if override:
                    last_rk = list(rk_list[-1])
                    last_rk[2] = store.Image(override)
                    rk_list[-1] = tuple(last_rk)
            else:
                arm_comp_args = [store.mas_sprites.LOC_WH]
                any_override = False
                for arm, tag_list in arm_data:
                    img_str = "".join((pfx_str, "".join(tag_list), store.mas_sprites.FILE_EXT))
                    override = _get_body_override(img_str)
                    arm_comp_args.append((0, 0))
                    if override:
                        arm_comp_args.append(override)
                        any_override = True
                    else:
                        arm_comp_args.append(img_str)
                
                if any_override:
                    new_composite = renpy.display.im.Composite(*arm_comp_args)
                    last_rk = list(rk_list[-1])
                    last_rk[2] = new_composite
                    rk_list[-1] = tuple(last_rk)

        _patch_body_method("_rk_base_body_nh", custom_rk_base_body_nh)
        _patch_body_method("_rk_base_body_lean_nh", custom_rk_base_body_lean_nh)
        _patch_body_method("_rk_body_nh", custom_rk_body_nh)
        _patch_body_method("_rk_body_lean_nh", custom_rk_body_lean_nh)
        _patch_body_method("_add_arms_rk", custom_add_arms_rk)
        _patch_body_method("_rk_head", custom_rk_head)

        try:
            if hasattr(store.mas_sprites, "_gc"):
                store.mas_sprites._gc(store.mas_sprites.CID_BODY).clear()
                store.mas_sprites._gc(store.mas_sprites.CID_HEAD).clear()
                store.mas_sprites._gc(store.mas_sprites.CID_ARMS).clear()
            if hasattr(store.mas_sprites, "_clear_caches"):
                store.mas_sprites._clear_caches()
            renpy.display.im.cache.clear()
        except Exception:
            pass

    # ==========================================
    # INJECTION LOGIC - FACE
    # ==========================================
    def apply_sprite_overrides():
        if not hasattr(store, "_mas_dtm_original_rk_face"):
            store._mas_dtm_original_rk_face = store.mas_sprites._rk_face

        if hasattr(store.mas_sprites, "_gc"):
            try:
                store.mas_sprites._gc(store.mas_sprites.CID_BODY).clear()
                store.mas_sprites._gc(store.mas_sprites.CID_HEAD).clear()
                store.mas_sprites._gc(store.mas_sprites.CID_ARMS).clear()
            except Exception:
                pass
        if hasattr(store.mas_sprites, "_clear_caches"):
            try:
                store.mas_sprites._clear_caches()
            except Exception:
                pass
        try:
            renpy.display.im.cache.clear()
        except Exception:
            pass

        eyes_folder_raw = store.mas_dtm_overrides.get("eyes_theme")
        eyes_folder = None
        if eyes_folder_raw:
            eyes_folder = eyes_folder_raw if os.path.isabs(eyes_folder_raw) else os.path.join(store.DTM_BASE_PARENT, eyes_folder_raw)

        mouth_folder_raw = store.mas_dtm_overrides.get("mouth_theme")
        mouth_folder = None
        if mouth_folder_raw:
            mouth_folder = mouth_folder_raw if os.path.isabs(mouth_folder_raw) else os.path.join(store.DTM_BASE_PARENT, mouth_folder_raw)

        nose_folder_raw = store.mas_dtm_overrides.get("nose_theme")
        nose_folder = None
        if nose_folder_raw:
            nose_folder = nose_folder_raw if os.path.isabs(nose_folder_raw) else os.path.join(store.DTM_BASE_PARENT, nose_folder_raw)

        if not (eyes_folder or mouth_folder or nose_folder):
            if hasattr(store, "_mas_dtm_original_rk_face"):
                store.mas_sprites._rk_face = store._mas_dtm_original_rk_face
            return

        face_index = {"eyes": {}, "mouth": {}, "nose": {}}
        import os
        for key, folder in [("eyes", eyes_folder), ("mouth", mouth_folder), ("nose", nose_folder)]:
            if folder and os.path.isdir(folder):
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        if f.lower().endswith(".png"):
                            abs_path = os.path.join(root, f)
                            rel_path_in_theme = os.path.relpath(abs_path, folder).replace("\\", "/")
                            face_index[key][rel_path_in_theme.lower()] = _get_rel_path(abs_path)
                            face_index[key][f.lower()] = _get_rel_path(abs_path)

        def _find_custom_file(key, code, prefix):
            mapped_name = code
            if key == "eyes" and hasattr(store.mas_sprite_decoder, "EYE_MAP"):
                mapped_name = store.mas_sprite_decoder.EYE_MAP.get(code, code)
            elif key == "mouth" and hasattr(store.mas_sprite_decoder, "MOUTH_MAP"):
                mapped_name = store.mas_sprite_decoder.MOUTH_MAP.get(code, code)

            candidates = [
                ("face-" + prefix + mapped_name + ".png").lower(),
                (prefix + mapped_name + ".png").lower(),
                (mapped_name + ".png").lower(),
                ("face-" + prefix + code + ".png").lower(),
                (prefix + code + ".png").lower(),
                (code + ".png").lower()
            ]

            idx = face_index.get(key, {})
            for cand in candidates:
                if cand in idx:
                    return idx[cand]
            return None

        def custom_rk_face(rk_list, eyes, eyebrows, nose, mouth, flt, fpfx, lean, sweat, tears, emote):
            if not (eyes_folder or mouth_folder or nose_folder):
                store._mas_dtm_original_rk_face(rk_list, eyes, eyebrows, nose, mouth, flt, fpfx, lean, sweat, tears, emote)
                return

            original_len = len(rk_list)
            store._mas_dtm_original_rk_face(rk_list, eyes, eyebrows, nose, mouth, flt, fpfx, lean, sweat, tears, emote)

            if len(rk_list) == original_len or rk_list[-1][2] is None:
                return

            try:
                eye_path = "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_EYES, eyes, store.mas_sprites.FILE_EXT))
                mouth_path = "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_MOUTH, mouth, store.mas_sprites.FILE_EXT))
                nose_path = "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_NOSE, nose, store.mas_sprites.FILE_EXT))

                any_custom = False

                if eyes_folder:
                    found = _find_custom_file("eyes", eyes, fpfx + store.mas_sprites.PREFIX_EYES)
                    if found:
                        eye_path = found
                        any_custom = True

                if mouth_folder:
                    found = _find_custom_file("mouth", mouth, fpfx + store.mas_sprites.PREFIX_MOUTH)
                    if found:
                        mouth_path = found
                        any_custom = True

                if nose_folder:
                    found = _find_custom_file("nose", nose, fpfx + store.mas_sprites.PREFIX_NOSE)
                    if found:
                        nose_path = found
                        any_custom = True

                if not any_custom:
                    return

                img_str_list = [
                    (0, 0), eye_path,
                    (0, 0), "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_EYEB, eyebrows, store.mas_sprites.FILE_EXT)),
                    (0, 0), nose_path,
                    (0, 0), mouth_path
                ]

                if sweat: img_str_list.extend(((0,0), "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_SWEAT, sweat, store.mas_sprites.FILE_EXT))))
                if tears: img_str_list.extend(((0,0), "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_TEARS, tears, store.mas_sprites.FILE_EXT))))
                if emote: img_str_list.extend(((0,0), "".join((store.mas_sprites.F_T_MAIN, fpfx, store.mas_sprites.PREFIX_EMOTE, emote, store.mas_sprites.FILE_EXT))))

                new_composite = renpy.display.im.Composite((1280, 850), *img_str_list)

                last_rk = list(rk_list[-1])
                for _ci in range(len(last_rk) - 1, -1, -1):
                    if isinstance(last_rk[_ci], renpy.display.im.Composite):
                        last_rk[_ci] = new_composite
                        break
                rk_list[-1] = tuple(last_rk)

            except Exception:
                pass

        store.mas_sprites._rk_face = custom_rk_face

    # ==========================================
    # INJECTION LOGIC - GAMES (PONG)
    # ==========================================
    def apply_pong_overrides():
        pong_folder_raw = store.mas_dtm_overrides.get("pong_field", None)
        pong_folder = None
        if pong_folder_raw:
            pong_folder = pong_folder_raw if os.path.isabs(pong_folder_raw) else os.path.join(store.DTM_BASE_PARENT, pong_folder_raw)

        if not pong_folder or not os.path.isdir(pong_folder):
            return

        copied = {}
        for fname in ("pong_field.png", "pong.png", "pong_ball.png"):
            src = os.path.join(pong_folder, fname)
            if os.path.isfile(src):
                copied[fname] = _get_rel_path(src)

        store._mas_dtm_pong_surfaces = copied
        renpy.display.im.cache.clear()

        if "pong_field.png" in copied:
            renpy.display.image.images[("bg", "pong", "field")] = store.Image(copied["pong_field.png"])

        if hasattr(store, "PongDisplayable"):
            if not hasattr(store, "_mas_dtm_original_pong_init"):
                store._mas_dtm_original_pong_init = store.PongDisplayable.__init__

            def custom_pong_init(self, *args, **kwargs):
                store._mas_dtm_original_pong_init(self, *args, **kwargs)
                cached = getattr(store, "_mas_dtm_pong_surfaces", {})
                if "pong.png" in cached:
                    self.paddle = renpy.display.im.Image(cached["pong.png"])
                if "pong_ball.png" in cached:
                    self.ball = renpy.display.im.Image(cached["pong_ball.png"])

            store.PongDisplayable.__init__ = custom_pong_init

    # ==========================================
    # INJECTION LOGIC - GAMES (CHESS)
    # ==========================================
    def apply_chess_overrides(sync=True):
        chess_folder = store.mas_dtm_overrides.get("chess_theme", None)
        if not chess_folder:
            return

        _finish_apply_chess_overrides(startup=sync)

    def _finish_apply_chess_overrides(startup=False):
        chess_folder_raw = store.mas_dtm_overrides.get("chess_theme", None)
        chess_folder = None
        if chess_folder_raw:
            chess_folder = chess_folder_raw if os.path.isabs(chess_folder_raw) else os.path.join(store.DTM_BASE_PARENT, chess_folder_raw)

        if not chess_folder or not os.path.isdir(chess_folder):
            return

        if not hasattr(store, "MASPiece"):
            return

        if not hasattr(store, "_mas_dtm_original_chess_map"):
            store._mas_dtm_original_chess_map = store.MASPiece.IMG_MAP.copy()
        if not hasattr(store, "_mas_dtm_original_chess_board"):
            store._mas_dtm_original_chess_board = store.MASChessDisplayableBase.BOARD_IMAGE
        if not hasattr(store, "_mas_dtm_original_chess_indicator_player"):
            store._mas_dtm_original_chess_indicator_player = store.MASChessDisplayableBase.MOVE_INDICATOR_PLAYER
        if not hasattr(store, "_mas_dtm_original_chess_indicator_monika"):
            store._mas_dtm_original_chess_indicator_monika = store.MASChessDisplayableBase.MOVE_INDICATOR_MONIKA
        if not hasattr(store, "_mas_dtm_original_chess_hl_green"):
            store._mas_dtm_original_chess_hl_green = store.MASChessDisplayableBase.PIECE_HIGHLIGHT_GREEN_IMAGE
        if not hasattr(store, "_mas_dtm_original_chess_hl_red"):
            store._mas_dtm_original_chess_hl_red = store.MASChessDisplayableBase.PIECE_HIGHLIGHT_RED_IMAGE
        if not hasattr(store, "_mas_dtm_original_chess_hl_yellow"):
            store._mas_dtm_original_chess_hl_yellow = store.MASChessDisplayableBase.PIECE_HIGHLIGHT_YELLOW_IMAGE
        if not hasattr(store, "_mas_dtm_original_chess_hl_magenta"):
            store._mas_dtm_original_chess_hl_magenta = store.MASChessDisplayableBase.PIECE_HIGHLIGHT_MAGENTA_IMAGE

        board_path = os.path.join(chess_folder, "chess_board.png")
        if os.path.isfile(board_path):
            store.MASChessDisplayableBase.BOARD_IMAGE = renpy.display.im.Image(_get_rel_path(board_path))

        ind_player_path = os.path.join(chess_folder, "move_indicator_player.png")
        if os.path.isfile(ind_player_path):
            store.MASChessDisplayableBase.MOVE_INDICATOR_PLAYER = renpy.display.im.Image(_get_rel_path(ind_player_path))

        ind_monika_path = os.path.join(chess_folder, "move_indicator_monika.png")
        if os.path.isfile(ind_monika_path):
            store.MASChessDisplayableBase.MOVE_INDICATOR_MONIKA = renpy.display.im.Image(_get_rel_path(ind_monika_path))

        _chess_hl_map = {
            "piece_highlight_green.png": "PIECE_HIGHLIGHT_GREEN_IMAGE",
            "piece_highlight_red.png": "PIECE_HIGHLIGHT_RED_IMAGE",
            "piece_highlight_yellow.png": "PIECE_HIGHLIGHT_YELLOW_IMAGE",
            "piece_highlight_magenta.png": "PIECE_HIGHLIGHT_MAGENTA_IMAGE",
        }
        for fname, attr in _chess_hl_map.items():
            fpath = os.path.join(chess_folder, fname)
            if os.path.isfile(fpath):
                setattr(store.MASChessDisplayableBase, attr, renpy.display.im.Image(_get_rel_path(fpath)))

        pieces_dir = os.path.join(chess_folder, "pieces")
        if os.path.isdir(pieces_dir):
            for fname in os.listdir(pieces_dir):
                if not fname.lower().endswith(".png"):
                    continue
                key = fname[:-4]
                piece_file_path = os.path.join(pieces_dir, fname)
                rel_piece_path = _get_rel_path(piece_file_path)
                for img_map_key in store.MASPiece.IMG_MAP:
                    if img_map_key.lower() == key.lower():
                        store.MASPiece.IMG_MAP[img_map_key] = renpy.display.im.Image(rel_piece_path)

        renpy.display.im.cache.clear()
        if not startup:
            force_update_mas_visuals()

    # ==========================================
    # INJECTION LOGIC - GAMES (NOU)
    # ==========================================
    def apply_nou_overrides(sync=True):
        nou_folder = store.mas_dtm_overrides.get("nou_theme", None)
        if not nou_folder:
            return
        _finish_apply_nou_overrides(startup=sync)

    def _finish_apply_nou_overrides(startup=False):
        nou_folder_raw = store.mas_dtm_overrides.get("nou_theme", None)
        nou_folder = None
        if nou_folder_raw:
            nou_folder = nou_folder_raw if os.path.isabs(nou_folder_raw) else os.path.join(store.DTM_BASE_PARENT, nou_folder_raw)

        if not nou_folder or not os.path.isdir(nou_folder):
            return

        # Build NOU index in memory
        nou_index = {}
        for sub in ["cards", "desks", "sfx"]:
            sub_dir = os.path.join(nou_folder, sub)
            if os.path.isdir(sub_dir):
                for root, dirs, files in os.walk(sub_dir):
                    for f in files:
                        if f.lower().endswith(".png") or f.lower().endswith(".ogg") or f.lower().endswith(".wav"):
                            abs_path = os.path.join(root, f)
                            rel_path_in_sub = os.path.relpath(abs_path, nou_folder).replace("\\", "/")
                            rel_clean = _get_rel_path(abs_path)
                            nou_index[rel_path_in_sub.lower()] = rel_clean
                            nou_index[f.lower()] = rel_clean

        note_path = os.path.join(nou_folder, "note.png")
        store._mas_dtm_nou_note = _get_rel_path(note_path) if os.path.isfile(note_path) else None
        pen_path = os.path.join(nou_folder, "pen.png")
        store._mas_dtm_nou_pen = _get_rel_path(pen_path) if os.path.isfile(pen_path) else None
        
        store._mas_dtm_nou_index = nou_index

        if not hasattr(store, "_mas_dtm_original_nou_init") and hasattr(store, "mas_nou"):
            store._mas_dtm_original_nou_init = store.mas_nou.NOU.__init__
        
        def custom_nou_init(self, *args, **kwargs):
            store._mas_dtm_original_nou_init(self, *args, **kwargs)
            idx = getattr(store, "_mas_dtm_nou_index", {})
            back_key = "cards/back.png"
            if back_key in idx:
                back_img = store.MASFilterSwitch(idx[back_key])
                self.table.back = back_img
                for card_obj in self.table.cards.values():
                    card_obj.back = back_img
        
        if hasattr(store, "mas_nou"):
            store.mas_nou.NOU.__init__ = custom_nou_init
        
        if hasattr(store, "mas_nou") and not hasattr(store, "_mas_dtm_original_load_card_asset"):
            store._mas_dtm_original_load_card_asset = store.mas_nou.NOU._m1_zz_cardgames__load_card_asset
        
        def custom_load_card_asset(self, card):
            store._mas_dtm_original_load_card_asset(self, card)
            card_png = self._m1_zz_cardgames__get_card_filename(card)
            card_key = "cards/" + card_png.lower() + ".png"
            idx = getattr(store, "_mas_dtm_nou_index", {})
            
            if card_key in idx:
                self.table.card(card, idx[card_key])
                self.table.set_faceup(card, False)
        
        if hasattr(store, "mas_nou"):
            store.mas_nou.NOU._m1_zz_cardgames__load_card_asset = custom_load_card_asset
        
        if not hasattr(store, "_mas_dtm_original_filter_switch"):
            store._mas_dtm_original_filter_switch = store.MASFilterSwitch
        
        def custom_filter_switch(img):
            if isinstance(img, basestring):
                if img == "mod_assets/games/nou/note.png" and getattr(store, "_mas_dtm_nou_note", None):
                    img = store._mas_dtm_nou_note
                elif img == "mod_assets/games/nou/pen.png" and getattr(store, "_mas_dtm_nou_pen", None):
                    img = store._mas_dtm_nou_pen
            return store._mas_dtm_original_filter_switch(img)
        
        store.MASFilterSwitch = custom_filter_switch
        
        if hasattr(store, "mas_cardgames") and hasattr(store, "mas_background"):
            store.mas_cardgames.DESK_SPRITES_MAP.clear()
            idx = getattr(store, "_mas_dtm_nou_index", {})
            fb_key = "desks/" + store.mas_background.MBG_DEF.lower() + ".png"
            fb_val = idx.get(fb_key)
            for bg_id in store.mas_background.BACKGROUND_MAP:
                if bg_id not in store.mas_cardgames.DESK_SPRITES_MAP:
                    bg_key = "desks/" + bg_id.lower() + ".png"
                    filename_rel = idx.get(bg_key, fb_val)
                    if filename_rel:
                        store.mas_cardgames.DESK_SPRITES_MAP[bg_id] = store.MASFilterSwitch(filename_rel)
        
        if hasattr(store, "mas_nou"):
            sfx_dir = os.path.join(nou_folder, "sfx")
            if os.path.isdir(sfx_dir):
                name_to_sfx_list_map = {
                    "shuffle": store.mas_nou.NOU.SFX_SHUFFLE,
                    "move": store.mas_nou.NOU.SFX_MOVE,
                    "slide": store.mas_nou.NOU.SFX_DRAW,
                    "place": store.mas_nou.NOU.SFX_PLAY,
                    "shove": store.mas_nou.NOU.SFX_PLAY
                }
                found_types = set()
                idx = getattr(store, "_mas_dtm_nou_index", {})
                for f in os.listdir(sfx_dir):
                    if f.endswith(store.mas_nou.NOU.SFX_EXT):
                        found_types.add(f.partition("_")[0])
                
                for t in found_types:
                    lst = name_to_sfx_list_map.get(t)
                    if lst is not None:
                        del lst[:]
                
                for f in os.listdir(sfx_dir):
                    if f.endswith(store.mas_nou.NOU.SFX_EXT):
                        lst = name_to_sfx_list_map.get(f.partition("_")[0])
                        if lst is not None:
                            f_key = "sfx/" + f.lower()
                            val = idx.get(f_key)
                            if val:
                                lst.append(val)
        
        renpy.display.im.cache.clear()
        if not startup:
            force_update_mas_visuals()


init 1000 python:
    if hasattr(store, "dtm_core") and store.dtm_core:
        store.dtm_core.apply_sprite_overrides()
        store.dtm_core.apply_body_overrides()
        if hasattr(store, "MASChessDisplayableBase"):
            store.dtm_core.apply_chess_overrides(sync=True)
        store.dtm_core.apply_pong_overrides()
        store.dtm_core.apply_nou_overrides(sync=True)