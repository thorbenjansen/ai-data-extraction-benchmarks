from pathlib import Path
import sys,shutil,subprocess
here=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Usage: python reproduce.py /new/output/folder')
out=Path(sys.argv[1]).expanduser().resolve()
if out.exists():raise SystemExit('Choose a new output folder.')
shutil.copytree(here,out,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
subprocess.run([sys.executable,str(out/'reproducibility/validate_selection.py')],check=True)
if(out/'materials').is_dir():
 subprocess.run([sys.executable,str(out/'reproducibility/validate_article_materials.py')],check=True)
if(out/'data/progress_selection.json').exists():
    subprocess.run([sys.executable,str(out/'reproducibility/validate_progress.py')],check=True)
if(out/'data/point_details.json').exists():
    subprocess.run([sys.executable,str(out/'reproducibility/validate_interactive.py')],check=True)
print('Reproduced the source snapshot and its current presentation:',out)
