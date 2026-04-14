find . -type f \( -name "*.py" -o -name "*.yml" -o -name "*.yaml" -o -name "*.html" -o -name "*.css" \) \
-not -path "./.venv/*" \
-not -path "./.git/*" \
-not -path "./__pycache__/*" \
-exec sh -c 'echo "===== $1 ====="; cat "$1"' _ {} \; > kod.txt