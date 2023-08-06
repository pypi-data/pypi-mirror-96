from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from pathlib import Path
from precipy.analytics_function import AnalyticsFunction
from precipy.identifiers import FileType
from precipy.identifiers import GeneratedFile
from precipy.identifiers import hash_for_document
from precipy.identifiers import hash_for_template_file
from precipy.identifiers import hash_for_template_text
from uuid import uuid4
import datetime
import glob
import itertools
import json
import logging
import os
import precipy.jinja_filters as jinja_filters
import precipy.output_filters as output_filters
import shutil
import tempfile

def generate_range_key(range_env):
    if range_env:
        return "__".join("%s_%s" % (k, range_env[k]) for k in sorted(range_env))
    else:
        return ""

class Batch(object):
    def __init__(self, config):
        self.orig_dir = os.getcwd()
        self.config = config
        self.h = str(uuid4())
        self.setup_logging()
        self.setup_work_dirs()
        self.setup_template_environment()
        self.setup_document_templates()
        self.setup_storages()
        self.functions = {}
        self.function_meta = {}
        self.documents = {}

        # set specific options
        if self.config.get('opts', False):
            self.config['reset'] = self.config['opts'].reset
            self.config['forcedelete'] = self.config['opts'].forcedelete

    def setup_logging(self):
        self.logger = logging.getLogger(name="precipy")

        if "logfile" in self.config:
            handler = logging.FileHandler(self.config['logfile'])
        else:
            # log to stderr if no logfile specified
            handler = logging.StreamHandler()

        level = self.config.get('loglevel', "INFO")
        handler.setLevel(level)
        self.logger.setLevel(level)

        FORMAT = '%(asctime)-15s %(levelname)-6s %(message)s'
        formatter = logging.Formatter(fmt=FORMAT)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.info("")
        self.logger.info("***** BEGIN LOGGING BATCH %s" % self.h)
        self.logger.info("")
        self.logger.debug("Config:")
        for k, v in self.config.items():
            self.logger.debug("%s: %r" % (k, v))

    def setup_work_dirs(self):
        self.cache_bucket_name = self.config.get('cache_bucket_name', "cache")
        self.output_bucket_name = self.config.get('output_bucket_name', "output")
        self.tempdir = Path(self.config.get('tempdir', tempfile.gettempdir())) / "precipy"

        self.logger.info("tempdir is %s" % self.tempdir)

        self.cachePath = self.tempdir / self.cache_bucket_name
        self.outputPath = self.tempdir / self.output_bucket_name
        self.localOutputPath = Path(self.output_bucket_name)

        os.makedirs(self.cachePath, exist_ok=True)
        shutil.rmtree(self.outputPath, ignore_errors=True)
        os.makedirs(self.outputPath, exist_ok=True)

    def rangeOutputPath(self):
        path = self.outputPath / self.current_range_key
        os.makedirs(path, exist_ok=True)
        return path

    def setup_template_environment(self):
        self.template_dir = self.config.get('template_dir', "templates")

        self.jinja_env = Environment(
            loader = FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']))

        self.jinja_env.filters['highlight'] = jinja_filters.highlight

        self.template_data = {}

    def setup_storages(self):
        self.storages = self.config.get('storages', [])
        for storage in self.storages:
            storage.init(self)
            storage.connect()
            if self.config.get('reset'):
                self.logger.debug("resetting cache for %r" % storage)
                storage.reset_cache()

    def upload_to_storages_cache(self, f):
        for storage in self.storages:
            public_url = storage.upload_cache(f.cache_filepath)
            f.public_urls.append(public_url)

    def upload_to_storages_output(self, f):
        for storage in self.storages:
            public_url = storage.upload_output(f.canonical_filename, f.cache_filepath)
            f.public_urls.append(public_url)

    def setup_document_templates(self):
        self.logger.debug("in setup_document_templates")
        self.logger.info("collecting list of document templates to process...")
        self.template_filenames = []

        for key in ['templates', 'template_file', 'template_files']:
            self.logger.info("looking for templates specified under config key '%s'" % key)
            entries = self.config.get(key, [])
            if isinstance(entries, str):
                entries = [entries]
            if entries:
                self.logger.info("  found template(s): %s" % ", ".join(str(e) for e in entries))
            self.template_filenames += entries

        if "template" in self.config:
            # template content is embedded in config - mostly used for testing
            self.template_filenames += ["%s.md" % self.h]

        if len(self.template_filenames) == 0:
            self.logger.info("no specified templates found, will add all in %s directory" % self.template_dir)
            raw_template_files = glob.glob("%s/*" % self.template_dir)
            if raw_template_files:
                self.logger.info("  found template(s): %s" % ", ".join(raw_template_files))
            self.template_filenames += [f.split("/")[1] for f in raw_template_files]

    def init_range(self, range_env):
        self.current_range_env = range_env
        self.current_range_key = generate_range_key(range_env)
        self.functions[self.current_range_key] = {}
        self.documents[self.current_range_key] = {}

    def run(self, analytics_modules):
        for range_env in self.range_environments():
            self.logger.debug("")

            self.logger.debug("now processing range env %s" % str(range_env))
            self.init_range(range_env)
            self.logger.debug("range key is %s" % self.current_range_key)

            self.logger.debug("")
            self.logger.debug("***** ANALYTICS")
            self.logger.debug("")
            self.generate_analytics(analytics_modules)

            self.logger.debug("")
            self.logger.debug("***** DOCUMENTS")
            self.logger.debug("")
            self.generate_documents()

            self.logger.debug("")
            self.logger.debug("***** PUBLISH")
            self.logger.debug("")
            self.publish_documents()

    def range_environments(self):
        """
        Generates a list of dictionaries containing variable names and values
        for every combination of the specified ranges.
        """
        if not 'ranges' in self.config:
            return [{}]

        var_names = sorted(self.config['ranges'])
        var_ranges = []
        for var_name in var_names:
            range_spec = self.config['ranges'][var_name]

            if isinstance(range_spec, dict):
                rng = range(range_spec.get('start'), range_spec.get('stop'), range_spec.get('step'))
            else:
                rng = range_spec

            var_ranges.append(rng)

        return [dict(zip(var_names, var_values)) for var_values in itertools.product(*var_ranges)]

    ## Analytics
    def generate_analytics(self, analytics_modules):
        self.analytics_modules = analytics_modules

        self.logger.debug("in generate_analytics with available modules:")
        for m in analytics_modules:
            self.logger.debug("     %r" % m)

        self.current_function_name = None
        self.current_function_data = None

        previous_functions = {}
        for key, kwargs in self.config.copy().get('analytics', []):
            for k, v in self.current_range_env.items():
                if k not in kwargs:
                    continue
                self.logger.debug("updating value for %s to %s" % (k, str(v)))
                kwargs[k] = v
            h = self.process_analytics_entry(key, kwargs, previous_functions)
            previous_functions[key] = h

        self.current_function_name = None
        self.current_function_data = None

    def process_analytics_entry(self, key, kwargs, previous_functions):
        af = self.resolve_function(key, kwargs, previous_functions)

        self.logger.debug("checking for cached metadata from a prior run")
        self.logger.debug("  in %s" % af.metadata_cache_filepath())

        if af.metadata_path_exists():
            self.logger.debug("    success!")
            af.load_metadata()

        if not af.metadata_path_exists():
            self.logger.debug("    not found, checking remote storages...")
            if af.download_from_storages(af.metadata_cache_filepath()):
                af.load_metadata()
                for sf in af.files.values():
                    self.logger.debug("    downloading supplemental file %s" % sf.canonical_filename)
                    filepath = af.supplemental_file_cache_filepath(sf.canonical_filename)
                    if not af.download_from_storages(filepath):
                        raise Exception("couldn't download storage for %s" % filepath)

        if not af.metadata_path_exists():
            self.logger.debug("cached metadata not found locally or remotely, running the function")
            af.run_function()
            af.is_populated = True
            af.from_cache = False
            self.logger.debug("  run function complete")
        else:
            if not af.is_populated:
                af.load_metadata()

        self.functions[self.current_range_key][key] = af
        return af.h

    def resolve_function(self, key, kwargs, previous_functions):
        """
        Determines which function is to be run. Function name is generally the
        key, but if a function_name parameter is passed this is used instead
        (useful if you want to call the same function more than once).
        """

        if 'function_name' in kwargs:
            qual_function_name = kwargs['function_name']
        else:
            qual_function_name = key

        if "." in qual_function_name:
            module_name, function_name = qual_function_name.split(".")
        else:
            module_name, function_name = [None, qual_function_name]

        # get function object from function name
        fn = self.get_fn_object(module_name, function_name)
        if fn is None:
            errmsg_raw = "couldn't find a function %s in modules %s"
            errmsg = errmsg_raw % (function_name, ", ".join(str(m) for m in self.analytics_modules))
            raise Exception(errmsg)
        self.logger.info("matched '%s' to fn %r" % (qual_function_name, fn))

        return AnalyticsFunction(fn, kwargs,
            previous_functions=previous_functions, 
            storages=self.storages,
            cachePath=self.cachePath,
            constants=self.config.get('constants', None),
            logger=self.logger,
            key=key
            )

    def get_fn_object(self, module_name, function_name):
        for mod in self.analytics_modules:
            if module_name != None and mod.__name__ != module_name:
                pass
            else:
                fn = getattr(mod, function_name)
                if fn is not None:
                    return fn

    def populate_template_data(self):
        def read_file_contents(path):
            with open(self.rangeOutputPath() / path, 'r') as f:
                return f.read()
        def load_json(path):
            with open(self.rangeOutputPath() / path, 'r') as f:
                return json.load(f)
        def fn_params(qual_fn_name, param_name):
            return self.config['analytics'][qual_fn_name][param_name]

        self.template_data['batch'] = self
        self.template_data['keys'] = self.functions.keys()

        functions = self.functions[self.current_range_key]
        self.template_data['functions'] = functions
        self.template_data.update(functions)

        constants = self.config.get('constants', {})
        self.template_data.update(constants)
        self.template_data['constants'] = constants

        # functions/modules for use within templates
        self.template_data['read_file_contents'] = read_file_contents
        self.template_data['load_json'] = load_json
        self.template_data['fn_params'] = fn_params
        self.template_data['datetime'] = datetime

    def copy_all_supplemental_files(self):
        """
        Copies all supplemental files to the current working directory.
        """
        for af in self.functions[self.current_range_key].values():
            for gf in af.files.values():
                self.logger.debug("  copying supp file %s" % gf.canonical_filename)
                shutil.copyfile(gf.cache_filepath, gf.canonical_filename)

    def upload_all_supplemental_files(self, mode='cache'):
        """
        Uploads all supplemental files
        """
        for item in self.functions.values():
            for af in item.values():
                for gf in af.files.values():
                    if mode == 'cache':
                        self.upload_to_storages_cache(gf)
                    elif mode == 'output':
                        self.upload_to_storages_output(gf)
                    else:
                        raise Exception("unexpected mode '%s'" % mode)

    def create_and_populate_work_dir(self, prev_doc):
        workPath = self.cachePath / "docs" / prev_doc.h
        self.logger.debug("populating work dir %s" % workPath)
        os.makedirs(workPath, exist_ok=True)
        os.chdir(workPath)

        # write the previous document
        shutil.copyfile(prev_doc.cache_filepath, prev_doc.canonical_filename)
        self.copy_all_supplemental_files()

        return workPath

    def render_and_save_template(self, template_file, document_basename=None):
        if document_basename:
            pretty_name = self.render_text(document_basename)
        else:
            pretty_name = None

        if template_file == "%s.md" % self.h:
            pretty_name = pretty_name or "template.md"
            h, text = self.render_text_template()
        else:
            pretty_name = pretty_name or template_file
            h, text = self.render_file_template(template_file)

        with open(self.cachePath / template_file, 'w') as f:
            f.write(text)

        doc = GeneratedFile(pretty_name, h, file_type=FileType.TEMPLATE,
                cache_filepath=self.cachePath / template_file)
        self.documents[self.current_range_key][pretty_name] = doc

        return doc

    def generate_documents(self):
        """
        Render all the templates and apply all the document filters on them.
        """
        self.populate_template_data()

        for template_info in self.template_filenames:
            if isinstance(template_info, str):
                template_file = template_info
                template_name = None
            elif isinstance(template_info, dict):
                template_file = template_info['file']
                template_name = template_info.get('name')
            template_doc = self.render_and_save_template(template_file, template_name)
            doc = template_doc

            for filter_opts in self.config.get('filters', []):
                workPath = self.create_and_populate_work_dir(doc)

                if len(filter_opts) == 2:
                    filter_name, output_ext = filter_opts
                    filter_args = {}
                else:
                    filter_name, output_ext, filter_args = filter_opts

                filter_doc_hash = hash_for_document(template_doc.h, filter_name, output_ext, filter_args)
                result_filename = "%s.%s" % (os.path.splitext(doc.canonical_filename)[0], output_ext)
                filter_fn = output_filters.__dict__["do_%s" % filter_name]
                filter_fn(doc.canonical_filename, result_filename, output_ext, filter_args)
                
                doc = GeneratedFile(result_filename, filter_doc_hash, file_type=FileType.DOCUMENT, 
                    cache_filepath = workPath / result_filename)
                self.documents[self.current_range_key][result_filename] = doc
    
                self.upload_to_storages_cache(doc)

            # change back to original working directory
            os.chdir(self.orig_dir)

    def rewrite_local_output(self):
        if os.path.exists(self.localOutputPath):
            if os.path.exists(self.localOutputPath / (".%s" % self.h)):
                pass
            elif os.path.exists(self.localOutputPath / '.precipy'):
                self.logger.debug("  removing old %s" % self.localOutputPath)
                shutil.rmtree(self.localOutputPath)
            else:
                self.logger.debug("  can't remove old %s" % self.localOutputPath)
                return False

        self.logger.debug("  copying files to %s" % (self.localOutputPath / self.current_range_key))
        shutil.copytree(self.rangeOutputPath(), self.localOutputPath / self.current_range_key)
        with open(self.localOutputPath / ".precipy", 'w') as f:
            f.write("Keep this here so precipy knows it's okay to delete this dir.")
        with open(self.localOutputPath / (".%s" % self.h), 'w') as f:
            f.write("Track which batch this is for.")
        with open(self.localOutputPath / "PrecipyREADME.txt", 'w') as f:
            f.write("""This folder will be deleted and recreated with each run. 
            Copy this folder elsewhere if you want to keep it permanently.""")
        return True

    def publish_documents(self):
        self.logger.debug("in publish_documents with range key %s" % self.current_range_key)

        curdir = os.getcwd()
        self.logger.debug("changing dir to %s" % self.rangeOutputPath())
        os.chdir(self.rangeOutputPath())

        for doc in self.documents[self.current_range_key].values():
            self.logger.debug("  copying file to %s" % doc.canonical_filename)
            shutil.copyfile(doc.cache_filepath, doc.canonical_filename)
        self.copy_all_supplemental_files()

        os.chdir(curdir)

        self.logger.debug("copying output to local output directory %s" % self.localOutputPath)
        if self.rewrite_local_output():
            for storage in self.storages:
                self.logger.debug("copying output to storage %r" % storage)
                storage.reset_output()
                for docs in self.documents.values():
                    for doc in docs.values():
                        self.logger.debug("      processing doc %r" % doc)
                        url = storage.upload_output(doc.canonical_filename, doc.cache_filepath)
                        doc.public_urls.append(url)
                        self.logger.debug("        uploaded to url %s" % url)
                self.upload_all_supplemental_files(mode='output')

    def render_text(self, text):
        template = self.jinja_env.from_string(text)
        return template.render(self.template_data)

    def render_text_template(self):
        template_text = self.config['template']
        h = hash_for_template_text(template_text)
        return h, self.render_text(template_text)

    def render_file_template(self, template_file):
        template = self.jinja_env.get_template(template_file)
        h = hash_for_template_file(self.template_dir + "/%s" % template_file)
        return h, template.render(self.template_data)
