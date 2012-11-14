# EXTRACTED FROM 
#https://github.com/luqman/SublimeText2RailsRelatedFiles


import sublime, sublime_plugin, os, glob, re
from vendor.inflector import *


class RailsRelatedFilesHelper:

  @staticmethod
  def get_directory_listing_without_folders(path):

    files = []
    result = glob.glob(path)

    for _file in result:

      if not os.path.isdir(_file):
        files.append(_file)

    return files

  @staticmethod
  def for_controllers(app_folder, working_directory, base_file_name):

    controller = base_file_name.replace('_controller', '')
    model = Inflector(English).singularize(controller).lower()

    namespace_directory    = RailsRelatedFilesHelper.get_namespace_directory(working_directory)
    working_directory_base = os.path.basename(working_directory)

    if namespace_directory:

      controller = os.path.join(working_directory_base, controller)

    walkers = [
      'app/models/'          + model      + '*',
      'app/models/**/'       + model      + '*',
      'app/helpers/'         + controller + '**',
      'app/helpers/**/'      + controller + '**',
      'app/views/'           + controller + '/**',
      'app/views/**/'        + controller + '/**',
      'test/'                + controller + '**',
      'test/**/'             + controller + '**',
      'spec/'                + controller + '**',
      'spec/**/'             + controller + '**'
    ]

    return RailsRelatedFilesHelper.get_files_while_walking(app_folder, walkers)

  @staticmethod
  def for_views(app_folder, working_directory):

    working_directory_base = os.path.basename(working_directory) #if app/views/posts it should return "posts"
    model                  = Inflector(English).singularize(os.path.basename(working_directory_base)).lower() # should return "post"
    namespace_directory    = RailsRelatedFilesHelper.get_namespace_directory(working_directory) #should return none
    controller = model

    if namespace_directory:
      working_directory_base = namespace_directory

      controller = os.path.join(os.path.split(working_directory_base)[0], controller)

    walkers = [
      'app/models/'             + model      + '**',
      'app/models/**/'          + model      + '**',
      'app/views/'              + working_directory_base + '/**',
      'app/helpers/'            + controller + '**',
      'app/helpers/**/'         + controller + '**',
      'app/assets/javascripts/' + model      + '**',
      'app/assets/stylesheets/' + model      + '**',
      'app/controllers/'        + controller + '**'
      'app/controllers/**/'     + controller + '**'
      'test/'                   + controller + '**'
      'test/**/'                + controller + '**'
      'spec/'                   + controller + '**'
      'spec/**/'                + controller + '**'
    ]

    return RailsRelatedFilesHelper.get_files_while_walking(app_folder, walkers)

  @staticmethod
  def for_models(app_folder, working_directory, file_name_base_no_ext):

    model = Inflector(English).singularize(file_name_base_no_ext).lower()
    controller = Inflector(English).pluralize(file_name_base_no_ext).lower()

    walkers = [
      'app/models/'         + model      + '**',
      'app/models/**/'      + model      + '**',
      'app/helpers/'        + controller + '**',
      'app/helpers/**/'     + controller + '**',
      'app/views/'          + controller + '/**',
      'app/views/**/'       + controller + '/**',
      'app/controllers/'    + controller + '**',
      'app/controllers/**/' + controller + '**',
      'test/'               + model      + '**',
      'test/**/'            + model      + '**',
      'spec/'               + model      + '**',
      'spec/**/'            + model      + '**'
    ]

    return RailsRelatedFilesHelper.get_files_while_walking(app_folder, walkers)

  @staticmethod
  def for_tests(app_folder, working_directory, base_file_name):

    if '_controller' in base_file_name:
      controller = base_file_name.replace('_controller', '').replace('_spec', '').replace('_test', '').replace('test_', '')
      model = Inflector(English).singularize(controller).lower()
    else:
      model = base_file_name.replace('_spec', '').replace('test_', '')
      controller = Inflector(English).pluralize(model).lower()

    namespace_directory    = RailsRelatedFilesHelper.get_namespace_directory(working_directory)
    working_directory_base = os.path.basename(working_directory)

    if namespace_directory:

      controller = os.path.join(working_directory_base, controller)
      model = os.path.join(working_directory_base, model)

    walkers = [
      'app/controllers/'    + controller + '**',
      'app/controllers/**/' + controller + '**',
      'app/models/'         + model      + '**',
      'app/models/**/'      + model      + '**',
      'app/helpers/'        + controller + '**',
      'app/helpers/**/'     + controller + '**',
      'app/views/'          + controller + '/**',
      'app/views/**/'       + controller + '/**'
    ]

    return RailsRelatedFilesHelper.get_files_while_walking(app_folder, walkers)


  @staticmethod
  def get_app_sub_directory(filename):

    regex = re.compile('(app\/views|app\/controllers|app\/helpers|app\/models|app\/assets|test|spec)')
    match = regex.findall(filename)

    if match:

      return match[0]

    else:

      return

  @staticmethod
  def get_namespace_directory(directory):

    regex = re.compile('(\/app\/views|controllers|test|spec)\/(.*)') #amazing regex skills...
    match = regex.findall(directory)

    if match:

      return match[0][1]

    else:

      return

  @staticmethod
  def get_files_while_walking(app_folder, walkers):

    files = []

    for walker in walkers:

      files += (
        RailsRelatedFilesHelper().get_directory_listing_without_folders(app_folder + '/' + walker)
      )

    files_without_full_path = []
    for _file in files:

      files_without_full_path += [_file.replace(app_folder + '/', '')]

    return files_without_full_path



class RailsFindCommand(sublime_plugin.TextCommand):

  APP_FOLDERS = ['app/controllers', 'app/models', 'app/views', 'test', 'spec'] #assets, helpers

  def run(self, edit):

    self.build_files()

    for region in self.view.sel():  
      current_line = self.view.substr(self.view.line(region))
      current_word = self.view.substr(self.view.word(region))
      path = ''
      if current_line.find('has_many') != -1 or current_line.find('has_and_belongs_to_many') != -1:
        path = (self.rails_root_directory + "/app/models/" + Inflector(English).singularize(current_word) + ".rb")
      elif current_line.find('belongs_to') != -1:
        path = (self.rails_root_directory + "/app/models/" + current_word + ".rb")
      elif current_line.find('render') != -1:
        regexp = 'render\s(:{0,1}(partial|template|file):{0,1}\s*(\=\>){0,1}\s*|)[\'|\"]([_\/a-z]*)[\'|\"]'
        path = self.rails_root_directory + '/app/views/' + re.search(regexp, current_line).group(4) + '.html.haml'
        path = re.sub(r'(.*\/)([_a-z]*\..*)', r'\1_\2', path)

        if not os.path.isfile(path):
          path = self.get_working_dir() + '/' + re.search(regexp, current_line).group(4) + '.html.haml'
          path = re.sub(r'(.*\/)([_a-z]*\..*)', r'\1_\2', path)
      
      if path != '' and os.path.isfile(path): 
        self.view.window().open_file(path)
    
  def build_files(self):

    self.files = []
    self.rails_root_directory = rails_root(self.get_working_dir())

    if self.rails_root_directory:

      self.show_context_menu = sublime.load_settings("Rails.sublime-settings").get('show_context_menu')

      current_file_name      = self._active_file_name()
      working_directory      = self.get_working_dir().replace("\\",'/')
      working_directory_base = os.path.basename(working_directory)

      file_name_base         = os.path.basename(current_file_name)
      file_name_base_no_ext  = os.path.splitext(file_name_base)[0]

      app_sub_directory      = RailsRelatedFilesHelper.get_app_sub_directory(working_directory)

      if app_sub_directory in self.APP_FOLDERS:

        func, args = {
          'app/controllers': (RailsRelatedFilesHelper.for_controllers, (self.rails_root_directory, working_directory, file_name_base_no_ext,)),
          'app/views'      : (RailsRelatedFilesHelper.for_views,       (self.rails_root_directory, working_directory,)),
          'app/models'     : (RailsRelatedFilesHelper.for_models,      (self.rails_root_directory, working_directory, file_name_base_no_ext,)),
          'test'           : (RailsRelatedFilesHelper.for_tests,       (self.rails_root_directory, working_directory, file_name_base_no_ext,)),
          'spec'           : (RailsRelatedFilesHelper.for_tests,       (self.rails_root_directory, working_directory, file_name_base_no_ext,))
        }.get(app_sub_directory)

        self.files = func(*args)

        if not self.files:
          self.files = ['Rails Related Files: Nothing found...']


  def get_working_dir(self):
    file_name = self._active_file_name()
    if file_name:
      return os.path.dirname(file_name)
    else:
			return self.window.folders()[0]

  def _active_file_name(self):
    view = self.view;
    if view and view.file_name() and len(view.file_name()) > 0:
      return view.file_name()

def rails_root(directory):
  while directory:
    if os.path.exists(os.path.join(directory, 'Rakefile')):
      return directory
    parent = os.path.realpath(os.path.join(directory, os.path.pardir))
    if parent == directory:
      # /.. == /
      return False
    directory = parent
  return False
