#!/usr/bin/env bash
# Struktur-Check der Plugin-Manifeste. Kein Test-Framework im Kit — bewusst ein Script.
set -euo pipefail
cd "$(dirname "$0")"
fail=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: erwartet '$3', ist '$2'"; fail=1; fi }

check "marketplace name"      "$(jq -r '.name' .claude-plugin/marketplace.json)"                       "bob-kit"
check "marketplace plugin"    "$(jq -r '.plugins[0].name' .claude-plugin/marketplace.json)"            "bob"
check "marketplace source"    "$(jq -r '.plugins[0].source' .claude-plugin/marketplace.json)"          "./plugins/bob"
check "plugin name"           "$(jq -r '.name' plugins/bob/.claude-plugin/plugin.json)"                "bob"
check "token sensitive"       "$(jq -r '.userConfig.bob_token.sensitive' plugins/bob/.claude-plugin/plugin.json)" "true"
check "token required"        "$(jq -r '.userConfig.bob_token.required' plugins/bob/.claude-plugin/plugin.json)"  "true"
check "adzuna id NOT sensitive" "$(jq -r '.userConfig.adzuna_app_id.sensitive' plugins/bob/.claude-plugin/plugin.json)" "null"
check "adzuna key NOT sensitive" "$(jq -r '.userConfig.adzuna_app_key.sensitive' plugins/bob/.claude-plugin/plugin.json)" "null"
check "jooble NOT sensitive"  "$(jq -r '.userConfig.jooble_key.sensitive' plugins/bob/.claude-plugin/plugin.json)" "null"
check "mcp type"              "$(jq -r '.mcpServers.bob.type' plugins/bob/.mcp.json)"                  "http"
check "mcp url"               "$(jq -r '.mcpServers.bob.url' plugins/bob/.mcp.json)"                   "https://job-scanner.thinkshark.de/mcp"
check "mcp auth header"       "$(jq -r '.mcpServers.bob.headers.Authorization' plugins/bob/.mcp.json)" "Bearer \${user_config.bob_token}"
check "plugin.json kein mcpServers" "$(jq -r 'has("mcpServers")' plugins/bob/.claude-plugin/plugin.json)" "false"

check "bob-score existiert"   "$([ -f plugins/bob/skills/bob-score/SKILL.md ] && echo yes || echo no)" "yes"
check "bob-scan existiert"    "$([ -f plugins/bob/skills/bob-scan/SKILL.md ] && echo yes || echo no)"  "yes"
check ".claude/skills weg"    "$([ -d .claude/skills ] && echo yes || echo no)"                        "no"
check "bob-scan nutzt user_config" "$(grep -c 'user_config.adzuna_app_id' plugins/bob/skills/bob-scan/SKILL.md)" "2"
check "kein bob-keys.json"    "$(grep -rc 'bob-keys.json' plugins/ | grep -vc ':0$' || true)"          "0"
check "kein bob-setup-Verweis" "$(grep -rl 'bob-setup' plugins/ | wc -l)"                              "0"
check "kein claude mcp add"   "$(grep -rl 'claude mcp add' plugins/ | wc -l)"                          "0"

check "LICENSE existiert"     "$([ -f LICENSE ] && echo yes || echo no)"                               "yes"
check "README ohne Zip"       "$(grep -ic 'zip' README.md || true)"                                    "0"
check "README ohne bob-setup" "$(grep -c 'bob-setup' README.md || true)"                               "0"
check "README nennt marketplace add" "$(grep -c 'plugin marketplace add DJTJ9/bob-member-kit' README.md)" "1"
check "README nennt install"  "$(grep -c 'plugin install bob@bob-kit' README.md)"                      "1"
check "README verweist /mitmachen" "$(grep -c 'job-scanner.thinkshark.de/mitmachen' README.md)"        "1"

exit $fail
