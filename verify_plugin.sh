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

exit $fail
