from .geometry import *
from .nlp_parser import parse_user_input

def _param_value(params, index, default):
    try:
        value = params[index]
    except Exception:
        return default
    return default if value is None else value

class BotGeometrie:
    """Bot pour interpréter les commandes et générer les figures géométriques"""
    
    def __init__(self):
      
        self.formes_2d = {
            "cercle": lambda p: Cercle(r=_param_value(p, 0, 2)),
            "carre": lambda p: Carre(a=_param_value(p, 0, 2)),
            "rectangle": lambda p: Rectangle(l=_param_value(p, 0, 4), w=_param_value(p, 1, 2)),
            "triangle": lambda p: TriangleEquilateral(a=_param_value(p, 0, 3)),
            "ellipse": lambda p: Ellipse(a=_param_value(p, 0, 3), b=_param_value(p, 1, 1.5)),
            "polygone": lambda p: Polygone(n=int(_param_value(p, 0, 6)), r=_param_value(p, 1, 2)),
            "losange": lambda p: Losange(D=_param_value(p, 0, 4), d=_param_value(p, 1, 2)),
            "secteur": lambda p: SecteurCirculaire(r=_param_value(p, 0, 3), angle_deg=_param_value(p, 1, 120))
        }
        
        self.formes_3d = {
            "cube": lambda p: Cube(a=_param_value(p, 0, 2)),
            "sphere": lambda p: Sphere(r=_param_value(p, 0, 2)),
            "cylindre": lambda p: Cylindre(r=_param_value(p, 0, 2), h=_param_value(p, 1, 4)),
            "cone": lambda p: Cone(r=_param_value(p, 0, 2), h=_param_value(p, 1, 4)),
            "pyramide": lambda p: PyramideCarree(a=_param_value(p, 0, 3), h=_param_value(p, 1, 4)),
            "tore": lambda p: Tore(R=_param_value(p, 0, 4), r=_param_value(p, 1, 1))
        }
    
    def traiter_commande(self, texte_commande):
        """
        Analyse le texte et retourne une LISTE d'objets géométriques.
        Retourne: (liste_formes, message_global)
        """
        try:
            intentions = parse_user_input(texte_commande)
            
            if not intentions:
                return [], "Je n'ai pas compris quelle forme dessiner."
            
            formes = []
            messages = []
            
 
            for data in intentions:
                if not isinstance(data, dict) or 'forme' not in data:
                    continue
                
                forme_nom = data.get('forme', '').lower()
                dims = data.get('dimensions', [])
                est_3d = data.get('type', '2D') == "3D"

                couleur = data.get('couleur', DEFCOLOR2D if not est_3d else DEFCOLOR3D) 
                
                catalogue = self.formes_3d if est_3d else self.formes_2d
                
                if forme_nom in catalogue:
                    try:
                        objet_geo = catalogue[forme_nom](dims)
                        objet_geo.color = couleur
                        formes.append(objet_geo)
                        messages.append(texte_commande)
                    except Exception as e:
                        messages.append(f"Erreur {forme_nom}: {str(e)}")
                else:
                    messages.append(f"Inconnu: {forme_nom}")
            
            if not formes:
                return [], "Aucune forme valide n'a pu être générée. " + " ".join(messages)
                
            return formes, messages[0]
            
        except Exception as e:
            return [], f"Erreur critique : {str(e)}"
    def Calcule(self, form_geom):
        if form_geom.type == '2D':
            s = form_geom.Perimetre()
            a = form_geom.Aire()
            return {
                'Aire' : round(a, 2),
                'Perimetre': round(s, 2)
            }
        else:
            result = {}
            v = form_geom.Volume()
            s = form_geom.Surface()
            
            name = type(form_geom).__name__
           
            if name in ['Cylindre', 'Cone', 'PyramideCarree']:
              
                v_name = 'Aire de base' if name == 'Cylindre' else 'Apotheme'
                result[v_name] = round(s[0], 2)
                result['Surface Laterale'] = round(s[1], 2)
                result['Surface Totale'] = round(s[2], 2)
            else:
                if name == 'Sphere':
                    d = form_geom.Diametre()
                    c = form_geom.Circonscription() 
                    result['Diametre'] = round(d, 2)
                    result['Circonscription'] = round(c, 2)
                
                if isinstance(s, (int, float)):
                    result['Surface'] = round(s, 2)
            
            result['Volume'] = round(v, 2)
            return result

    def _to_python(self, value):
        if hasattr(value, "tolist"):
            return value.tolist()
        if isinstance(value, (list, tuple)):
            return [self._to_python(v) for v in value]
        return value

    def generer_reponse(self, form_geo):
        """Génère une réponse pour UNE seule forme géométrique"""
        if not form_geo:
            return None, {}, {}, None
        try:
            formules = form_geo.formule()
            calculs = self.Calcule(form_geo)
            x, y, z = form_geo.calculeAXE()

            render = "line"
            if form_geo.type == '3D':
                if hasattr(x, 'ndim') and x.ndim > 1:
                    render = "surface"
                else:
                    render = "wireframe"

            axes = {
                "x": self._to_python(x),
                "y": self._to_python(y),
                "z": self._to_python(z),
            }
            return axes, formules, calculs, render
        except Exception as e:
            return None, {}, {}, None
