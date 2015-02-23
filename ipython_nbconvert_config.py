from _ipython_config import *

c = get_config()
c.NbConvertApp.writer_class = 'ipython_writer.KeepDirStructureFileWriter'
c.FilesWriter.build_directory = OUTPUT_DIR
