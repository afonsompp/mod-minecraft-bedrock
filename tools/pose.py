"""Põe a pose de mira de 3ª pessoa no RP, a partir do player.entity.json oficial do jogo.

Quando o Minecraft atualizar, baixe o arquivo novo de
https://github.com/Mojang/bedrock-samples (resource_pack/entity/player.entity.json)
e rode:
  python3 tools/pose.py caminho/para/player.entity.json

Sem argumento, ele reaproveita o player.entity.json que já está no RP como base. É idempotente:
tira o que uma geração anterior pôs antes de pôr de novo. É assim que o `build.py --gerar` o chama, para
a lista de armas da pose de 3ª pessoa não ficar atrasada (na v1.6.3 a AWP não tinha entrado nela).
"""
import json
import sys
from pathlib import Path
from jsonc import load

# Até a v1.6.3 isso era um pack separado (POSE_RP), para poder desligar só a pose. Na v1.6.4 virou parte
# do RP: eram dois resource packs para ativar no mundo, e o João só queria um. O arquivo substitui o
# player.entity.json do jogo, então o min_engine_version do RP segue em 1.21.90 de propósito: num jogo
# anterior ao format_version deste arquivo (1.26.0) o jogo o ignora e cai na pose vanilla, enquanto um
# min_engine 1.26 deixaria o add-on INTEIRO incompatível e as armas sumiriam.
POSE = Path(__file__).resolve().parent.parent / "packs" / "RP"


def main(vanilla=None):
    d = load(vanilla or POSE / "entity/player.entity.json")
    desc = d["minecraft:client_entity"]["description"]
    sc = desc["scripts"]
    # limpa o que uma geração anterior pôs, para poder rodar sobre o arquivo já gerado
    sc["pre_animation"] = [l for l in sc.get("pre_animation", []) if "joao_mira" not in l]
    sc["animate"] = [a for a in sc["animate"]
                     if not (isinstance(a, dict) and any(k.startswith("joao_") for k in a))]
    for k in [k for k in desc["animations"] if k.startswith("joao_")]:
        del desc["animations"][k]
    sc.setdefault("pre_animation", []).append("variable.joao_mira = 1.0;")
    sc.setdefault("variables", {})["variable.joao_mira"] = "public"
    desc["animations"]["joao_mira_fuzil"] = "animation.joao.mira_fuzil"
    desc["animations"]["joao_mira_pistola"] = "animation.joao.mira_pistola"
    cond = "!variable.is_first_person && query.is_item_name_any('slot.weapon.mainhand', 0, {})"
    sc["animate"] += [
        {"joao_mira_fuzil": cond.format("'joao:ak47', 'joao:m4a4', 'joao:awp', 'joao:besta'")},
        {"joao_mira_pistola": cond.format("'joao:glock'")},
    ]
    (POSE / "entity").mkdir(parents=True, exist_ok=True)
    (POSE / "entity/player.entity.json").write_text(json.dumps(d, indent=2))

    def braco(y_esq):
        return {"loop": True, "bones": {
            "rightarm": {"rotation": ["query.target_x_rotation - 90.0 - this", "query.target_y_rotation - 5.73 - this", "-this"]},
            "leftarm": {"rotation": ["query.target_x_rotation - 90.0 - this", f"query.target_y_rotation + {y_esq} - this", "-this"]}}}
    an = {"format_version": "1.10.0", "animations": {
        "animation.joao.mira_fuzil": braco(40.0),
        "animation.joao.mira_pistola": braco(28.65)}}
    (POSE / "animations").mkdir(parents=True, exist_ok=True)
    (POSE / "animations/joao_mira.animation.json").write_text(json.dumps(an, indent=2))

    print("pose ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
