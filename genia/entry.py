import site
import subprocess
import os


def local_streamlit():
    subprocess.run(["python", "-m", "streamlit", "run", "genia/main.py"])


def streamlit():
    os.environ["GENIA_HOME"] = os.path.join(site.getsitepackages()[0], "")
    main = os.path.join(site.getsitepackages()[0], "genia", "main.py")
    subprocess.run(["python3", "-m", "streamlit", "run", main])
