# Paper-Downloader

- [Paper-Downloader](#paper-downloader)
  - [JNM-Downloader](#jnm-downloader)
  - [Download PKU Paper](#download-pku-paper)
  - [Remove pdf password](#remove-pdf-password)

## JNM-Downloader

down all journal of nuclear material from sci-hub

`python jnm_downloader.py start_year end_year`

for example: `python jnm_downloader.py 1959 1960`

Don't use `jnm_multithreadd_downloader.py`, your ip will be banned quickly.

## Download PKU Paper

Download Peking University Paper

`python jnm_downloader.py`

## Remove pdf password

1. pip install pikepdf
2. put this file out of directory, which contains pdf files
3. run this file, `python Unlock_pdf.py`