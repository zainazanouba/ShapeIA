import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.bot_logic import BotGeometrie
from src.function_plotter import plot_function

app = FastAPI(title='ShapeIA API', version='0.1.0')

origins_env = os.getenv('CORS_ORIGINS', 'http://localhost:5173')
origins = [origin.strip() for origin in origins_env.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

bot = BotGeometrie()

class CommandRequest(BaseModel):
    text: str
    mode: Optional[str] = "shapes"

class ShapePayload(BaseModel):
    name: str
    type: str
    color: str
    formulas: Dict[str, str]
    calculations: Dict[str, float]
    render: Optional[str]
    axes: Optional[Dict[str, Any]]

class CommandResponse(BaseModel):
    message: str
    shapes: List[ShapePayload]

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/api/command', response_model=CommandResponse)
def command(req: CommandRequest):
    mode = (req.mode or "shapes").lower()

    if mode in {"functions", "function", "plot"}:
        try:
            result = plot_function(req.text)
        except Exception as e:
            return {"message": f"Erreur fonction: {str(e)}", "shapes": []}

        domain = result.get("domain") or {}
        sig = result.get("signature", "f(x)")
        expr = result.get("expr", "")
        dim = result.get("dimension", 2)

        if dim == 1:
            dom_x = domain.get("x")
            dom_txt = f"x in [{dom_x[0]}, {dom_x[1]}]" if dom_x else ""
        else:
            dom_x = domain.get("x")
            dom_y = domain.get("y")
            if dom_x and dom_y and dom_x == dom_y:
                dom_txt = f"x,y in [{dom_x[0]}, {dom_x[1]}]"
            elif dom_x and dom_y:
                dom_txt = f"x in [{dom_x[0]}, {dom_x[1]}], y in [{dom_y[0]}, {dom_y[1]}]"
            else:
                dom_txt = ""

        message = f"Fonction: {sig} = {expr}"
        if dom_txt:
            message = f"{message} | {dom_txt}"

        shapes = [{
            'name': 'Function',
            'type': '2D' if dim == 1 else '3D',
            'color': '#16a34a',
            'formulas': result.get('formulas') or {},
            'calculations': result.get('calculations') or {},
            'render': result.get('render'),
            'axes': result.get('axes')
        }]
        return {'message': message, 'shapes': shapes}

    formes, message = bot.traiter_commande(req.text)
    shapes = []

    for forme in formes:
        axes, formulas, calculations, render = bot.generer_reponse(forme)

        shapes.append({
            'name': type(forme).__name__,
            'type': forme.type,
            'color': forme.color,
            'formulas': formulas or {},
            'calculations': calculations or {},
            'render': render,
            'axes': axes
        })

    return {'message': message, 'shapes': shapes}
