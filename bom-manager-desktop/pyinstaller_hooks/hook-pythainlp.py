"""Bundle only what Thai PDF word breaking needs: the newmm tokenizer and the
word lists it reads. Overrides the contrib hook, which copies the ~60 MB corpus.
qt_launcher's smoke test fails the build if word breaking falls back."""
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files(
    "pythainlp", includes=["corpus/words_th.txt", "corpus/stopwords_th.txt"])
hiddenimports = ["pythainlp.tokenize.newmm"]
