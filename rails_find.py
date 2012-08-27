import sublime, sublime_plugin, os

class RailsFindCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    #self.rails_root_directory = rails_root(self.get_working_dir())
    self.view.insert(edit, 1, self._active_file_name())
 
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