# DynamicTextureManager.rpy
init 999 python in dtm_core:
    import store
    import os
    import shutil

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
    # API DE CONTROL VISUAL - ROSTRO
    # ==========================================
    def set_eyes_textures(folder_path):
        store.mas_dtm_overrides["eyes_theme"] = folder_path
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
        store.mas_dtm_overrides["mouth_theme"] = folder_path
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
        store.mas_dtm_overrides["nose_theme"] = folder_path
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
    # API DE CONTROL VISUAL - CUERPO
    # ==========================================
    def set_body_textures(folder_path):
        store.mas_dtm_overrides["body_theme"] = folder_path
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
    # LÓGICA DE INYECCIÓN - CUERPO
    # ==========================================
    def apply_body_overrides():
        body_folder = store.mas_dtm_overrides.get("body_theme", None)
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
    # LÓGICA DE INYECCIÓN - ROSTRO (UNIFICADA)
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

        eyes_folder = store.mas_dtm_overrides.get("eyes_theme")
        mouth_folder = store.mas_dtm_overrides.get("mouth_theme")
        nose_folder = store.mas_dtm_overrides.get("nose_theme")

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