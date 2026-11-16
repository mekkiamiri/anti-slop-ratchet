#!/usr/bin/env bash
# Capteur (sensor) de l'agent : relance les règles anti-slop quand l'agent touche du Java.
#
# Branché dans .claude/settings.json sur deux événements Claude Code :
#   - PostToolUse (Edit|Write) : après un fichier .java modifié ; exit 2 => Claude lit stderr.
#   - Stop : avant que l'agent rende la main ; exit 2 => Claude doit continuer et corriger.
# Format vérifié sur https://code.claude.com/docs/en/hooks (16/11/2026).
#
# ArchUnit lit les classes compilées : la commande vérifie tout le module. Pour ne pas relancer Maven
# à chaque étape d'un refactor sur plusieurs fichiers, on ne relance que si les fichiers Java ont changé
# depuis le dernier passage réussi (empreinte de `git diff`).
#
# Variables optionnelles :
#   ARCH_GATE_MVN_ARGS      arguments Maven en plus (ex. -Djava.version=17)
#   ARCH_GATE_ON_STOP_ONLY  si 1, ne vérifie qu'au Stop (rien après chaque fichier)
set -uo pipefail

# Sans les outils, on ne bloque pas l'agent avec une fausse consigne : on le dit et on laisse passer.
for tool in python3 mvn git; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "gate anti-slop ignoré : $tool absent" >&2
    exit 0
  fi
done

input="$(cat)"
field() { python3 -c 'import json,sys; d=json.load(sys.stdin); v=d
for k in sys.argv[1].split("."): v=v.get(k, "") if isinstance(v, dict) else ""
print(v)' "$1" <<<"$input"; }

event="$(field hook_event_name)"
project="${CLAUDE_PROJECT_DIR:-$(field cwd)}"
cd "$project" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || { echo "gate anti-slop ignoré : pas un dépôt git" >&2; exit 0; }

case "$event" in
  PostToolUse)
    [[ "${ARCH_GATE_ON_STOP_ONLY:-0}" == "1" ]] && exit 0
    file="$(field tool_input.file_path)"
    [[ "$file" == *.java ]] || exit 0
    ;;
  Stop)
    # Pas de sortie anticipée sur stop_hook_active : on revérifie à chaque fois, pour que l'agent
    # ne puisse pas rendre la main avec une violation. Claude Code plafonne lui-même les relances
    # (8 relances consécutives d'après la doc), donc pas de boucle infinie.
    ;;
  *) exit 0 ;;
esac

# Empreinte des fichiers Java modifiés ou nouveaux. Identique au dernier passage réussi : rien à faire.
fingerprint="$( { git diff HEAD -- '*.java' 2>/dev/null
                 git ls-files --others --exclude-standard -- '*.java' | while IFS= read -r f; do echo "$f"; cat "$f"; done
               } | git hash-object --stdin )"
marker="$(git rev-parse --git-dir)/archunit-gate.ok"
[[ -f "$marker" && "$(cat "$marker")" == "$fingerprint" ]] && exit 0

# shellcheck disable=SC2086
out="$(mvn -q -B test -Dtest='*ArchTest' -Dsurefire.failIfNoSpecifiedTests=false ${ARCH_GATE_MVN_ARGS:-} 2>&1)"
status=$?

if [[ $status -eq 0 ]]; then
  echo "$fingerprint" > "$marker"
  exit 0
fi
rm -f "$marker"

if grep -q "Architecture Violation" <<<"$out"; then
  {
    echo "Règles anti-slop en échec (mvn test -Dtest='*ArchTest'). Corrige le code, pas la règle :"
    grep -E "^(Architecture Violation|Rule '|Method <|Field <|Constructor <|Class <)" <<<"$out" \
      | awk '!seen[$0]++' | head -40
    echo "Si une règle te semble fausse, dis-le à l'humain au lieu de la contourner."
  } >&2
else
  {
    echo "Build cassé, pas une règle anti-slop (compilation, dépendance ou autre test). Sortie Maven :"
    awk '!seen[$0]++' <<<"$out" | grep -v -E "^[[:space:]]+at |Re-run Maven|full stack trace|Help 1|^\[ERROR\] *$|^\[ERROR\] -> " | head -40
  } >&2
fi
exit 2
