import os
import ast
from pathlib import Path


# =========================
# STAGES (contenido educativo)
# =========================
STAGES = {
    1: {
        "title": "Output",
        "goal": 'Dejar de devolver "TODO".',
        "hint": "Modifica run_agent() para retornar texto real.",
    },
    2: {
        "title": "Connect LLM",
        "goal": "Crear una función generate_response(prompt).",
        "hint": "No hace falta LLM real, solo simular la función.",
    },
    3: {
        "title": "Tools Connection",
        "goal": "Importar echo_tool desde tools.py.",
        "hint": "from tools import echo_tool",
    },
    4: {
        "title": "Tool Execution",
        "goal": "Usar echo_tool dentro del agente.",
        "hint": "echo_tool(prompt)",
    },
    5: {
        "title": "Thinking Loop",
        "goal": "Agregar lógica (if / loop).",
        "hint": "if, for o while",
    },
    6: {
        "title": "Read/Write Agent",
        "goal": "Leer input y generar output coherente.",
        "hint": "usar prompt correctamente",
    },
}


# =========================
# UTILIDADES
# =========================
def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_file(path: str) -> str:
    try:
        return (_project_root() / path).read_text(encoding="utf-8")
    except:
        return ""


def _parse(source: str):
    try:
        return ast.parse(source)
    except:
        return ast.Module(body=[], type_ignores=[])


def _find_function(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


# =========================
# STAGE DETECTION
# =========================
def get_current_stage():
    env = os.getenv("CRAFTER_STAGE")
    if env:
        try:
            return int(env)
        except:
            pass
    return 1


def _is_stage_implemented(stage):
    agent_src = _read_file("app/agent.py")
    main_src = _read_file("app/main.py")

    agent_tree = _parse(agent_src)
    main_tree = _parse(main_src)

    # Stage 1
    if stage == 1:
        fn = _find_function(agent_tree, "run_agent")
        if not fn:
            return False, "run_agent no existe"
        returns = [
            n
            for n in ast.walk(fn)
            if isinstance(n, ast.Return)
            and isinstance(n.value, ast.Constant)
            and n.value.value == "TODO"
        ]
        return len(returns) == 0, "run_agent no devuelve TODO"

    # Stage 2
    if stage == 2:
        return (
            _find_function(agent_tree, "generate_response") is not None,
            "existe generate_response()",
        )

    # Stage 3
    if stage == 3:
        for node in agent_tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == "tools":
                for alias in node.names:
                    if alias.name == "echo_tool":
                        return True, "echo_tool importada"
        return False, "echo_tool no importada"

    # Stage 4
    if stage == 4:
        for node in ast.walk(agent_tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "echo_tool":
                    return True, "echo_tool usada"
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "echo_tool"
                ):
                    return True, "tools.echo_tool usada"
        return False, "echo_tool no usada"

    # Stage 5
    if stage == 5:
        for node in ast.walk(agent_tree):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                return True, "hay lógica"
        return False, "no hay lógica"

    # Stage 6
    if stage == 6:
        uses_input = "input(" in main_src or "sys.argv" in main_src
        uses_prompt = "prompt" in agent_src
        return uses_input and uses_prompt, "usa input y prompt"

    return False, "stage desconocido"


# =========================
# RENDER (UX)
# =========================
def render(stage, prompt):
    info = STAGES.get(stage, STAGES[1])
    implemented, evidence = _is_stage_implemented(stage)

    status = "implementado ✅" if implemented else "no implementado ❌"

    # progreso
    progress = sum(_is_stage_implemented(i)[0] for i in range(1, 7))

    return f"""
========================================
 CRAFTER AGENT
========================================

Stage: {stage} - {info['title']}
Progress: {progress}/6

Input:
> {prompt}

Estado:
{status}

Evidencia:
{evidence}

Hint:
{info['hint']}

Objetivo:
{info['goal']}

Next Step:
→ Implementa este stage
→ Ejecuta: ./run.sh
→ Luego: crafter test
"""


# =========================
# AGENTE
# =========================
def run_agent(prompt: str):
    stage = get_current_stage()
    return render(stage, prompt)
