#!/usr/bin/env bash
# Download llama.cpp's server into bin/ and a small model into models/.
#
#   scripts/get_llama_server.sh                  prebuilt binary (about a minute)
#   scripts/get_llama_server.sh --from-source    compile it yourself (5-10 minutes on 2 cores)
#
# Linux only (Codespaces is Linux). Safe to run again; finished parts are skipped.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p bin models

MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_FILE="models/qwen2.5-0.5b-instruct-q4_k_m.gguf"

case "$(uname -m)" in
  x86_64) ARCH=x64 ;;
  aarch64 | arm64) ARCH=arm64 ;;
  *) echo "unsupported CPU: $(uname -m)" >&2; exit 1 ;;
esac

if [[ -x bin/llama-server ]]; then
  echo "bin/llama-server already there"
elif [[ "${1:-}" == "--from-source" ]]; then
  [[ -d bin/llama.cpp-src ]] || git clone --depth 1 https://github.com/ggml-org/llama.cpp bin/llama.cpp-src
  cmake -S bin/llama.cpp-src -B bin/llama.cpp-src/build -DCMAKE_BUILD_TYPE=Release
  cmake --build bin/llama.cpp-src/build -j "$(nproc)" --target llama-server
  ln -sf llama.cpp-src/build/bin/llama-server bin/llama-server
else
  TAG=$(curl -fsSL https://api.github.com/repos/ggml-org/llama.cpp/releases/latest \
    | python3 -c 'import json, sys; print(json.load(sys.stdin)["tag_name"])')
  echo "downloading llama.cpp $TAG for $ARCH"
  curl -fL --progress-bar -o bin/llama.tar.gz \
    "https://github.com/ggml-org/llama.cpp/releases/download/$TAG/llama-$TAG-bin-ubuntu-$ARCH.tar.gz"
  tar -xzf bin/llama.tar.gz -C bin
  rm bin/llama.tar.gz
  ln -sf "llama-$TAG/llama-server" bin/llama-server
fi
bin/llama-server --version

if [[ -f "$MODEL_FILE" ]]; then
  echo "$MODEL_FILE already there"
else
  echo "downloading model (about 400 MB)"
  curl -fL --progress-bar -o "$MODEL_FILE.part" "$MODEL_URL"
  mv "$MODEL_FILE.part" "$MODEL_FILE"
fi
ls -lh "$MODEL_FILE"

echo
echo "Start the server with:"
echo "  bin/llama-server -m $MODEL_FILE --port 8080 -np 4 -c 8192"
