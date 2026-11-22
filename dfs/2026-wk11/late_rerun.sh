set -e
cd ../engine && python3 run_week.py ../2026-wk11 --teams late --n 2 --target 180 --cands 400 --qbs "Bo Nix,Trevor Lawrence,Geno Smith,J.J. McCarthy,Fernando Mendoza,Justin Herbert" --tag late 2>&1 | grep -v Warn | tail -3
cd ../2026-wk11 && python3 late_deep.py 2>&1 | grep -v Warn
