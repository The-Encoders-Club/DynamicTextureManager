# dtm_header.rpy
init -990 python:
    store.mas_submod_utils.Submod(
        author="The Encoders Club",
        name="Dynamic Texture Manager",
        description="Sistema avanzado para gestionar y aplicar texturas dinámicas personalizadas en el cuerpo y rostro sin sobrescribir los archivos base.",
        version="1.0.0"
    )

init -10 python:
    import json
    import os

    # Inicializar el almacén de variables
    store.mas_dtm_overrides = {
        "eyes_theme": None,
        "mouth_theme": None,
        "nose_theme": None,
        "body_theme": None
    }


    # Configuración de rutas compatibles con PC
    store.DTM_BASE_PARENT = renpy.config.basedir

    if store.DTM_BASE_PARENT not in renpy.config.searchpath:
        renpy.config.searchpath.append(store.DTM_BASE_PARENT)

    store.DTM_CONFIG_PATH = os.path.join(store.DTM_BASE_PARENT, "Submods", "DynamicTextureManager", "dtm_config.json")

    def mas_dtm_load_config():
        try:
            if os.path.isfile(store.DTM_CONFIG_PATH):
                with open(store.DTM_CONFIG_PATH, "r") as f:
                    data = json.load(f)
                changed = False
                for k, v in data.items():
                    if k in store.mas_dtm_overrides:
                        if v is not None and not os.path.exists(v):
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