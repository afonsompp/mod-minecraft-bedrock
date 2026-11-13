"""Regenera o pack opcional de pose (packs/POSE_RP) a partir do player.entity.json oficial.

Quando o Minecraft atualizar, baixe o arquivo novo de
https://github.com/Mojang/bedrock-samples (resource_pack/entity/player.entity.json)
e rode:
  python3 tools/pose.py caminho/para/player.entity.json [versão mínima do jogo, ex: 1.26.0]
"""
import json
import sys
from pathlib import Path
from jsonc import load

POSE = Path(__file__).resolve().parent.parent / "packs" / "POSE_RP"


def main(vanilla, min_engine=None):
    d = load(vanilla)
    desc = d["minecraft:client_entity"]["description"]
    sc = desc["scripts"]
    sc.setdefault("pre_animation", []).append("variable.joao_mira = 1.0;")
    sc.setdefault("variables", {})["variable.joao_mira"] = "public"
    desc["animations"]["joao_mira_fuzil"] = "animation.joao.mira_fuzil"
    desc["animations"]["joao_mira_pistola"] = "animation.joao.mira_pistola"
    cond = "!variable.is_first_person && query.is_item_name_any('slot.weapon.mainhand', 0, {})"
    sc["animate"] += [
        {"joao_mira_fuzil": cond.format("'joao:ak47', 'joao:m4a4', 'joao:awp'")},
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

    if min_engine:
        p = POSE / "manifest.json"
        m = json.loads(p.read_text(encoding="utf-8"))
        m["header"]["min_engine_version"] = [int(x) for x in min_engine.split(".")]
        p.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("pose ok")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
