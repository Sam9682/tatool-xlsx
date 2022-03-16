import zipfile
import os

class Zipper:
    def __init__(self, input_args):
        self.input_args = input_args

    def zipfolder(self):
        temp_zipfile = self.input_args.tempdirzip + 'tempzip.zip'
        zipobj = zipfile.ZipFile(temp_zipfile, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        rootlen = len(os.path.dirname(self.input_args.output_dir)) + 1
        for base, dirs, files in os.walk(os.path.dirname(self.input_args.output_dir)):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])
        return temp_zipfile