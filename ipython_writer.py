import glob
import io
import sys

from IPython.nbconvert.exporters.export import exporter_map
from IPython.nbconvert.utils.exceptions import ConversionException
from IPython.nbconvert.writers import FilesWriter

from _ipython_config import *


class KeepDirStructureFileWriter(FilesWriter):
    def __init__(self, *args, **kwargs):
        super(KeepDirStructureFileWriter, self).__init__(*args, **kwargs)
        self.parent.convert_notebooks = self.convert_notebooks

    def write(self, output, resources, notebook_name=None, **kw):
        old_build_directory = self.build_directory
        self.build_directory = resources.get('build_directory', old_build_directory)
        res = super(KeepDirStructureFileWriter, self).write(
            output, resources, notebook_name, **kw)
        self.build_directory = old_build_directory
        return res

    def convert_notebooks(self):
        return self._convert_notebooks(self.parent)

    @staticmethod
    def _convert_notebooks(self):
        """
        Convert the notebooks in the self.notebook traitlet

        NOTE: this is a direct copy from IPython's NbConvertApp, but it retains
              directory structure of globbed notebooks.
        """
        # Export each notebook
        conversion_success = 0

        if self.output_base != '' and len(self.notebooks) > 1:
            self.log.error(
            """UsageError: --output flag or `NbConvertApp.output_base` config option
            cannot be used when converting multiple notebooks.
            """)
            self.exit(1)

        exporter = exporter_map[self.export_format](config=self.config)

        for notebook_filename in self.notebooks:
            self.log.info("Converting notebook %s to %s", notebook_filename, self.export_format)

            # Get a unique key for the notebook and set it in the resources object.
            abs_nb_root = os.path.dirname(notebook_filename)
            nb_root = os.path.relpath(abs_nb_root, ROOT)
            notebook_name, _ = os.path.splitext(os.path.basename(notebook_filename))
            resources = {}
            resources['unique_key'] = notebook_name
            resources['output_files_dir'] = notebook_name
            self.log.info("Support files will be in %s", os.path.join(resources['output_files_dir'], ''))

            # Copy over other files in the notebook directory
            outputs = {}
            for filename in glob.glob(os.path.join(abs_nb_root, '*')):
                if not filename.endswith('.ipynb') and os.path.isfile(filename):
                    with io.open(filename, mode='rb') as fp:
                        outputs[os.path.basename(filename)] = fp.read()
            resources['outputs'] = outputs

            # Ensure our exporter uses the correct directory in output
            resources['build_directory'] = os.path.join(OUTPUT_DIR, nb_root)

            # Try to export
            try:
                output, resources = exporter.from_filename(notebook_filename, resources=resources)
            except ConversionException as e:
                self.log.error("Error while converting '%s'", notebook_filename,
                      exc_info=True)
                self.exit(1)
            else:
                write_resultes = self.writer.write(output, resources, notebook_name=notebook_name)

                #Post-process if post processor has been defined.
                if hasattr(self, 'postprocessor') and self.postprocessor:
                    self.postprocessor(write_resultes)
                conversion_success += 1

        # If nothing was converted successfully, help the user.
        if conversion_success == 0:
            self.print_help()
            sys.exit(-1)
