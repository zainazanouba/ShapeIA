from fuzzywuzzy import process
import re

SHAPE_SYNONYMS = {
    "cercle": ["rond", "disque", "daira", "circle"], 
    "carre": ["square", "box", "carré", "mrba3"], 
    "rectangle": ["rect", "mustatil"], 
    "triangle": ["tri", "motalat"], 
    "ellipse": ["oval", "baydawi"],
    "polygone": ["moudalla3", "polygon", "hexagone", "pentagone"],
    "losange": ["diamond"],
    "secteur": ["camembert", "sector"],
    
    "cube": ["box3d", "muka3ab", "sandou9"], 
    "sphere": ["sphère", "ball", "balle", "kora", "ballon"],
    "cylindre": ["tube", "ja3ba", "oustowana"], 
    "pyramide": ["pyramid", "haram"],
    "cone": ["cône", "tarbouch", "makhrout", "chapeau"],
    "tore": ["donut", "ka3ka", "torus"]
}

COLOR_SYNONYMS = {
    "red": ["rouge", "rouges", "hmer"], 
    "blue": ["bleu", "bleue", "bleus", "zre9"], 
    "green": ["vert", "verte", "verts", "khder"], 
    "gold": ["jaune", "yellow", "sfer"],
    "black": ["noir", "noire", "k7el"], 
    "white": ["blanc", "blanche", "byad"],
    "orange": ["orange", "limouni"], 
    "purple": ["violet", "violette"]
}

STOP_WORDS = {
    "and","or","with","want","a","i","the","draw","make","create","string",
    "de","du","des","avec","un","une","le","la","les","pour","please","stp",
    "dessine","dessiner","trace","tracer","fais","faire","cree","creer",
    "et","ou"
}

TRANSLATION = {}
KNOWN_WORDS = []

for k, v in SHAPE_SYNONYMS.items():
    TRANSLATION[k] = k
    KNOWN_WORDS.append(k)
    for sub in v:
        TRANSLATION[sub] = k 
        KNOWN_WORDS.append(sub)

for k, v in COLOR_SYNONYMS.items():
    TRANSLATION[k] = k
    KNOWN_WORDS.append(k)
    for sub in v:
        TRANSLATION[sub] = k
        KNOWN_WORDS.append(sub)


SHAPES_3D = ["cube", "sphere", "cylindre", "pyramide", "cone", "tore"]

CONNECTORS = {
    "de", "du", "des", "d", "of", "avec", "with", "a", "an", "the", "le", "la", "les", "pour", "et", "ou"
}

COLOR_LABELS = {"color", "couleur", "colore", "colo"}

BIG_WORDS = {"grand", "grande", "big", "large", "major"}
SMALL_WORDS = {"petit", "petite", "small", "minor"}

DIMENSION_KEYWORDS = {
    "rayon": "r",
    "radius": "r",
    "rad": "r",
    "diametre": "diam",
    "diamètre": "diam",
    "diameter": "diam",
    "diam": "diam",
    "hauteur": "h",
    "height": "h",
    "haut": "h",
    "h": "h",
    "largeur": "w",
    "width": "w",
    "w": "w",
    "longueur": "l",
    "length": "l",
    "long": "l",
    "l": "l",
    "cote": "a",
    "côté": "a",
    "side": "a",
    "edge": "a",
    "arete": "a",
    "arête": "a",
    "a": "a",
    "cotes": "n",
    "côtes": "n",
    "cotés": "n",
    "sides": "n",
    "vertices": "n",
    "vertex": "n",
    "n": "n",
    "diagonale": "diag",
    "diagonal": "diag",
    "diag": "diag",
    "axe": "axe",
    "axes": "axe",
    "angle": "angle",
    "theta": "angle",
    "degre": "angle",
    "degres": "angle",
    "degree": "angle",
    "deg": "angle",
    "base": "base",
    "taille": "size",
    "size": "size",
    "dimension": "size",
    "dimensions": "size"
}

for k, v in DIMENSION_KEYWORDS.items():
    TRANSLATION[k] = v
    KNOWN_WORDS.append(k)

SHAPE_DIMENSION_ORDER = {
    "cercle": ["r"],
    "carre": ["a"],
    "rectangle": ["l", "w"],
    "triangle": ["a"],
    "ellipse": ["a", "b"],
    "polygone": ["n", "r"],
    "losange": ["D", "d"],
    "secteur": ["r", "angle"],
    "cube": ["a"],
    "sphere": ["r"],
    "cylindre": ["r", "h"],
    "cone": ["r", "h"],
    "pyramide": ["a", "h"],
    "tore": ["R", "r"]
}

def is_number(token):
    return re.fullmatch(r"[-+]?(?:\d+\.\d+|\d+)", token) is not None

def is_hex_color(token):
    return re.fullmatch(r"#(?:[0-9a-f]{6}|[0-9a-f]{3})", token) is not None

def normalize_text(text):
    text = text.lower().strip()
    text = text.replace("×", "x")
    text = re.sub(r"(\d),(\d)", r"\1.\2", text)
    text = re.sub(r"(\d+(?:\.\d+)?)[x](\d+(?:\.\d+)?)", r"\1 \2", text)
    text = re.sub(r"[,:;()\[\]{}]", " ", text)
    text = text.replace("=", " ")
    return text

def tokenize(text):
    text = normalize_text(text)
    return re.findall(r"#(?:[0-9a-f]{6}|[0-9a-f]{3})|\d+(?:\.\d+)?|[a-zA-ZÀ-ÿ0-9]+", text)

def find_next_index(tokens, start, predicate, max_lookahead=4):
    limit = min(len(tokens), start + max_lookahead)
    for j in range(start, limit):
        if tokens[j] in CONNECTORS:
            continue
        if predicate(tokens[j]):
            return j
    return None

def map_label_to_shape(key, shape_type, order):
    if not order:
        return None, None
    if key in order:
        return key, None
    if key == "diam":
        if "r" in order:
            return "r", lambda v: v / 2
        if shape_type == "tore" and "R" in order:
            return "R", lambda v: v / 2
    if key == "h" and "w" in order and shape_type in {"rectangle", "ellipse"}:
        return "w", None
    if key == "w" and "h" in order:
        return "h", None
    if key == "w" and "a" in order and shape_type == "ellipse":
        return "a", None
    if key == "h" and "b" in order and shape_type == "ellipse":
        return "b", None
    if key == "l" and "h" in order:
        return "h", None
    if key == "base":
        if "r" in order:
            return "r", None
        if "a" in order:
            return "a", None
    if key == "size":
        return order[0], None
    if key == "r" and shape_type == "tore" and "R" in order and "r" in order:
        return "R", None
    if len(order) == 1:
        return order[0], None
    return None, None

def parse_user_input(text):
    words = tokenize(text or "")
    clean_words = []
    
    for w in words:
        if w in STOP_WORDS:
           continue

        if w in TRANSLATION:
            clean_words.append(TRANSLATION[w])
        elif is_number(w) or is_hex_color(w):
            clean_words.append(w)
        elif w in DIMENSION_KEYWORDS or w in COLOR_LABELS or w in CONNECTORS:
            clean_words.append(w)
        elif len(w) > 4:
            match, score = process.extractOne(w, KNOWN_WORDS)
            if score >= 90:
                clean_words.append(TRANSLATION[match])
            else:
                clean_words.append(w)
        else:
            clean_words.append(w)

    shapes_found = []
    colors_found = []
    numbers_found = []
    numbers_by_index = {}
    labels_found = []

    target_shapes = list(SHAPE_SYNONYMS.keys())
    target_colors = list(COLOR_SYNONYMS.keys())

    for i, word in enumerate(clean_words):
        if is_number(word):
            entry = {"val": float(word), "index": i, "used": False}
            numbers_found.append(entry)
            numbers_by_index[i] = entry
        if word in target_shapes:
            shapes_found.append({"type": word, "index": i})

    color_indices = set()

    for i, word in enumerate(clean_words):
        if is_hex_color(word):
            colors_found.append({"val": word, "index": i, "used": False, "explicit": False})
            color_indices.add(i)

    for i, word in enumerate(clean_words):
        if word in COLOR_LABELS:
            next_idx = find_next_index(
                clean_words,
                i + 1,
                lambda t: not is_number(t)
            )
            if next_idx is None:
                continue
            candidate = clean_words[next_idx]
            if candidate in target_shapes or candidate in DIMENSION_KEYWORDS:
                continue
            if next_idx not in color_indices:
                colors_found.append({
                    "val": candidate,
                    "index": next_idx,
                    "used": False,
                    "explicit": True,
                    "label_index": i
                })
                color_indices.add(next_idx)

    for i, word in enumerate(clean_words):
        if i in color_indices:
            continue
        if word in target_colors:
            colors_found.append({"val": word, "index": i, "used": False, "explicit": False})

    for i, word in enumerate(clean_words):
        if word in DIMENSION_KEYWORDS:
            key = DIMENSION_KEYWORDS[word]
            prev = clean_words[i - 1] if i > 0 else ""

            if key == "r" and prev in BIG_WORDS:
                key = "R"
            elif key == "r" and prev in SMALL_WORDS:
                key = "r"

            if key == "diag":
                key = "d" if prev in SMALL_WORDS else "D"

            if key == "axe":
                if prev in SMALL_WORDS:
                    key = "b"
                else:
                    key = "a"

            num_idx = find_next_index(clean_words, i + 1, is_number)
            if num_idx is not None:
                labels_found.append({
                    "key": key,
                    "val": float(clean_words[num_idx]),
                    "index": i,
                    "num_index": num_idx,
                    "used": False
                })

    for col in colors_found:
        if not col.get("explicit"):
            continue
        anchor = col.get("label_index", col["index"])
        prev_shapes = [s for s in shapes_found if s["index"] <= anchor]
        if prev_shapes:
            col["target_shape"] = prev_shapes[-1]["index"]
        else:
            next_shapes = [s for s in shapes_found if s["index"] > anchor]
            if next_shapes:
                col["target_shape"] = next_shapes[0]["index"]

    detected_objects = []

    for shape in shapes_found:
        idx_shape = shape["index"]
        order = SHAPE_DIMENSION_ORDER.get(shape["type"], [])
        obj = {
            "forme": shape["type"],
            "couleur": "#c1e328", 
            "dimensions": [None] * len(order),
            "type": "3D" if shape["type"] in SHAPES_3D else "2D"
        }


        explicit_color = None
        for col in colors_found:
            if col.get("explicit") and not col["used"] and col.get("target_shape") == idx_shape:
                explicit_color = col
                break

        if explicit_color:
            obj["couleur"] = explicit_color["val"]
            explicit_color["used"] = True
        else:
            best_color = None
            min_dist = 100
            for col in colors_found:
                if not col["used"]:
                    dist = abs(col["index"] - idx_shape)
                    if dist < 6 and dist < min_dist:
                        min_dist = dist
                        best_color = col

            if best_color:
                obj["couleur"] = best_color["val"]
                best_color["used"] = True 

        label_candidates = []
        for lab in labels_found:
            if lab["used"]:
                continue
            dist = abs(lab["index"] - idx_shape)
            if len(shapes_found) == 1 or dist < 6:
                label_candidates.append((dist, lab))

        label_candidates.sort(key=lambda x: x[0])

        for _, lab in label_candidates:
            mapped_key, converter = map_label_to_shape(lab["key"], shape["type"], order)
            if not mapped_key:
                continue
            if mapped_key not in order:
                continue
            target_idx = order.index(mapped_key)

            if obj["dimensions"][target_idx] is not None:
                continue

            value = converter(lab["val"]) if converter else lab["val"]

            if shape["type"] == "tore" and mapped_key == "R":
                idx_R = order.index("R")
                idx_r = order.index("r")
                if obj["dimensions"][idx_R] is None and obj["dimensions"][idx_r] is None:
                    obj["dimensions"][idx_R] = value
                else:
                    obj["dimensions"][idx_r] = value
            else:
                obj["dimensions"][target_idx] = value

            lab["used"] = True
            num_entry = numbers_by_index.get(lab["num_index"])
            if num_entry:
                num_entry["used"] = True

        missing = [i for i, v in enumerate(obj["dimensions"]) if v is None]
        if missing:
            nearby_nums = []
            for num in numbers_found:
                if not num["used"]:
                    dist = abs(num["index"] - idx_shape)
                    if len(shapes_found) == 1 or dist < 6:
                        nearby_nums.append(num)

            nearby_nums.sort(key=lambda x: abs(x["index"] - idx_shape))

            for idx in missing:
                if not nearby_nums:
                    break
                n = nearby_nums.pop(0)
                obj["dimensions"][idx] = n["val"]
                n["used"] = True

        detected_objects.append(obj)
    return detected_objects
