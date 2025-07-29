#!/usr/bin/env bash
set -e

# Wrapper for installing DeOldify on Codex environments.
# This delegates common Ubuntu setup to install.ubuntu.sh and
# then applies the proxy and certificate settings required by Codex.

SCRIPT_DIR="$(dirname "$0")"

# Run the generic installation first
"${SCRIPT_DIR}/install.ubuntu.sh"

# Apply Codex proxy certificate settings if provided (to circumvent Conda SSL issues)
if [ -n "${CODEX_PROXY_CERT}" ]; then
  ~/miniconda3/bin/conda config --set ssl_verify "${CODEX_PROXY_CERT}"
fi

# Uncomment to explicitly set proxy servers
# ~/miniconda3/bin/conda config --set proxy_servers.http "$http_proxy"
# ~/miniconda3/bin/conda config --set proxy_servers.https "$https_proxy"
