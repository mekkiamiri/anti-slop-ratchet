#!/usr/bin/env bash
# Capteur (sensor) de l'agent : relance les règles anti-slop quand l'agent touche du Java.
#
# Branché dans .claude/settings.json sur deux événements Claude Code :
#   - PostToolUse (Edit|Write) : après chaque fichier .java modifié ; exit 2 => Claude lit stderr.
#   - Stop : avant que l'agent rende la main ; exit 2 => Claude doit continuer et corriger.
# Format vérifié sur https://code.claude.com/docs/en/hooks (16/11/2026).
#
# ArchUnit lit les classes compilées : la commande vérifie tout le module, mais elle ne se déclenche
# que si un fichier Java a changé. Variable optionnelle : ARCH_GATE_MVN_ARGS (ex. -Djava.version=17).
set -uo pipefail

input="$(cat)"
field() { python3 -c 'import json,sys; d=json.load(sys.stdin); v=d
for k in sys.argv[1].split("."): v=v.get(k, "") if isinstance(v, dict) else ""
print(v)' "$1" <<<"$input"; }

event="$(field hook_event_name)"
project="${CLAUDE_PROJECT_DIR:-$(field cwd)}"
cd "$project" || exit 0

case "$event" in
  PostToolUse)
    file="$(field tool_input.file_path)"
    [[ "$file" == *.java ]] || exit 0
    ;;
  Stop)
    # Évite la boucle infinie : si un hook Stop a déjà relancé l'agent, on le laisse s'arrêter.
    [[ "$(field stop_hook_active)" == "True" ]] && exit 0
    # Rien à vérifier si aucun fichier Java n'a changé depuis le dernier commit.
    git status --porcelain -- '*.java' | grep -q . || exit 0
    ;;
  *) exit 0 ;;
esac

# shellcheck disable=SC2086
out="$(mvn -q -B test -Dtest='*ArchTest' -Dsurefire.failIfNoSpecifiedTests=false ${ARCH_GATE_MVN_ARGS:-} 2>&1)"
status=$?
if [[ $status -ne 0 ]]; then
  {
    echo "Règles anti-slop en échec (mvn test -Dtest='*ArchTest'). Corrige le code, pas la règle :"
    grep -E "^(Architecture Violation|Rule '|Method <|Field <|Constructor <|Class <|io\.github|\[ERROR\] .*(cannot find|error:))" <<<"$out" | head -40
    echo "Si une règle te semble fausse, dis-le à l'humain au lieu de la contourner."
  } >&2
  exit 2
fi
exit 0
