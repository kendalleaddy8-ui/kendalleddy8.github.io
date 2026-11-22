set -e
cd ../engine && python3 run_week.py ../2026-wk11 --n 3 --target 230 --cands 600 --shared 3 --qbs "Patrick Mahomes,Dak Prescott,Cam Ward,Josh Allen,Caleb Williams,Bo Nix,Trevor Lawrence,Jared Goff,Geno Smith,Justin Herbert" --tag run 2>&1 | grep -v Warn | head -3
cd ../2026-wk11 && python3 improve_prep.py 2>&1 | grep -v Warn
python3 improve.py 2>&1 | grep -v Warn
