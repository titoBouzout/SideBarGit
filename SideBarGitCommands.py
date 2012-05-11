# coding=utf8
import sublime_plugin, sublime
import os
import re

from sidebar.SideBarSelection import SideBarSelection
from sidebar.SideBarGit import SideBarGit

try:
	from BufferScroll import BufferScrollAPI
except:
	BufferScrollAPI = False

class Object():
	pass

#run last command again on a focused tab when pressing F5

class SideBarGitRefreshTabContentsByRunningCommandAgain(sublime_plugin.WindowCommand):
	def run(self):
		window = sublime.active_window()
		if not window:
			return
		view 	 =  window.active_view()
		if view is None:
			return
		if view.settings().has('SideBarGitIsASideBarGitTab'):
			SideBarGit().run(
												[],
												view.settings().get('SideBarGitModal'),
												view.settings().get('SideBarGitBackground'),
												view,
												view.settings().get('SideBarGitCommand'),
												view.settings().get('SideBarGitItem'),
												view.settings().get('SideBarGitToStatusBar'),
												view.settings().get('SideBarGitTitle'),
												view.settings().get('SideBarGitNoResults'),
												view.settings().get('SideBarGitSyntaxFile')
												)
		elif view.file_name():
			if BufferScrollAPI:
				BufferScrollAPI.save(view, 'sidebar-git');
			view.run_command("revert")
			if BufferScrollAPI:
				BufferScrollAPI.restore(view, 'sidebar-git');

	def is_enabled(self):
		window = sublime.active_window()
		if not window:
			return False
		view 	 =  window.active_view()
		if view is None:
			return False
		if view.settings().has('SideBarGitIsASideBarGitTab') or view.file_name():
			return True


def closed_affected_items(items):
	closed_items = []
	for item in items:
		if not item.isDirectory():
			closed_items += item.close_associated_buffers()
	return closed_items

def reopen_affected_items(closed_items):
	for item in closed_items:
		file_name, window, view_index = item
		if window and os.path.exists(file_name):
			view = window.open_file(file_name)
			window.set_view_index(view, view_index[0], view_index[1])
#Following code for selected files or folders

class SideBarGitDiffAllChangesSinceLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', 'HEAD', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffAllChangesSinceLastCommitIgnoreWhiteSpaceCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', 'HEAD', '--no-color', '-w', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffChangesNotStagedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffChangesStagedNotCommitedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', '--no-color', '--staged', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenIndexAndLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', '--no-color', '--cached', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenRemoteAndLastLocalCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', '--no-color', 'origin/master..', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenLastLocalCommitAndRemoteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'diff', '--no-color', '..origin/master', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolAllChangesSinceLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', 'HEAD', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolChangesNotStagedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolChangesStagedNotCommitedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', '--staged', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolBetweenIndexAndLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', '--cached', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolBetweenRemoteAndLastLocalCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', 'origin/master..', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDifftoolBetweenLastLocalCommitAndRemoteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'difftool', '..origin/master', '--', item.forCwdSystemName()]
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatShortLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '--pretty=short', '--decorate', '--graph', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatShortFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '--pretty=short', '--decorate', '--graph', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatListLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import sys
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-n', '50', '--pretty=format:%s'.encode(sys.getfilesystemencoding()),  '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatListCommitLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import sys
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-n', '50', '--pretty=format:%h %s'.encode(sys.getfilesystemencoding()), '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogExtendedLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '-p', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogExtendedFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', '-p', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogSinceLatestPushCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'log', 'origin/master..', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitReflogCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'reflog', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Reflog: '+item.name()
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBlameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'blame', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Blame: '+item.name()
			object.word_wrap = False
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

class SideBarGitStatusCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = Object()
			object.item = item
			object.command = ['git', 'status', '--untracked-files=all', '--ignored', '--', item.forCwdSystemName()]
			object.title = 'Status: '+item.name()
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked on selected items? ', self.run, paths)
		else:
			items = SideBarSelection(paths).getSelectedItems()
			closed_items = closed_affected_items(items)
			for item in items:
				object = Object()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Discarded changes to tracked on selected items')
			reopen_affected_items(closed_items)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedCleanUntrackedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked and clean untracked on selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = Object()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = Object()
				object.item = item
				object.command = ['git', 'clean', '-f', '-d', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Discarded changes to tracked and cleaned untracked on selected items')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedCleanUntrackedUnstageCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked, clean untracked and unstage on selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = Object()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = Object()
				object.item = item
				object.command = ['git', 'clean', '-f', '-d', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = Object()
				object.item = item
				object.command = ['git', 'reset', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Discarded changes to tracked, cleaned untracked and unstage on selected items')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedUnstageCleanUntrackedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked, unstage and clean untracked on selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = Object()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = Object()
				object.item = item
				object.command = ['git', 'reset', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = Object()
				object.item = item
				object.command = ['git', 'clean', '-f', '-d', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Discarded changes to tracked, unstage and cleaned untracked on selected items')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertUnstageCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Unstage selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = Object()
				object.item = item
				object.command = ['git', 'reset', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Unstage selected items')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitCheckoutToCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		failed = False
		if input == False:
			SideBarGit().prompt('Checkout selected items to object: ', '', self.run, paths)
		elif content != '':
			import sys
			for item in SideBarSelection(paths).getSelectedItems():
				object = Object()
				object.item = item
				object.command = ['git', 'checkout', content.encode(sys.getfilesystemencoding()), '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Checkout selected items to "'+content+'"')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitIgnoreOpenCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			item.path(item.dirname())
			while not os.path.exists(item.join('.git')):
				if os.path.exists(item.join('.gitignore')):
					break;
				if item.dirname() == item.path():
					break;
				item.path(item.dirname())

			if os.path.exists(item.join('.gitignore')):
				item.path(item.join('.gitignore'))
			else:
				item.path(item.join('.gitignore'))
				item.create()
			item.edit()

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitIgnoreAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			original = item.path()
			originalIsDirectory = item.isDirectory()
			item.path(item.dirname())
			while not os.path.exists(item.join('.git')):
				if os.path.exists(item.join('.gitignore')):
					break;
				if item.dirname() == item.path():
					break;
				item.path(item.dirname())

			if os.path.exists(item.join('.gitignore')):
				item.path(item.join('.gitignore'))
			else:
				if os.path.exists(item.join('.git')):
					item.path(item.join('.gitignore'))
					item.create()
				else:
					SideBarGit().status('Unable to found repository for "'+original.encode('utf-8')+'"')
					continue
			ignore_entry = re.sub('^/+', '', original.replace(item.dirname(), '').replace('\\', '/'))
			if originalIsDirectory:
				ignore_entry = '/'+ignore_entry
			content = item.contentUTF8().strip()+'\n'+ignore_entry
			content = content.replace('\r\n', '\n')
			content = "\n".join(list(set(content.split('\n'))))

			item.write(content.strip())
			SideBarGit().status('Ignored file "'+ignore_entry+'" on '+item.path())

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

# Following code for selected folders. Dirname for when a file is selected.

class SideBarGitInitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			object = Object()
			object.item = item
			object.command = ['git', 'init']
			object.to_status_bar = True
			SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitCloneCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		failed = False
		if input == False:
			SideBarGit().prompt('Enter URL to clone: ', sublime.get_clipboard(), self.run, paths)
		elif content != '':
			import sys
			for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
				object = Object()
				object.item = item
				object.command = ['git', 'clone', '--recursive', content.encode(sys.getfilesystemencoding())]
				object.to_status_bar = True
				if not SideBarGit().run(object, True):
					failed = True
			if not failed:
				SideBarGit().status('Cloned URL "'+content+'"')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitGuiCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			object = Object()
			object.item = item
			object.command = ['git','gui']
			SideBarGit().run(object, False, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitGitkCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			object = Object()
			object.item = item
			object.command = ['gitk']
			SideBarGit().run(object, False, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

# Following code for unique selected repos found on items selected

class SideBarGitCheckoutRepositoryToCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		failed = False
		if input == False:
			SideBarGit().prompt('Checkout repository to object: ', '', self.run, paths)
		elif content != '':
			import sys
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = ['git', 'checkout', content.encode(sys.getfilesystemencoding())]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Checkout repository to "'+content+'"')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = item.repository
			object.command = ['git','push']
			object.to_status_bar = True
			SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushWithOptionsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Push with options: ', "git push aRemoteName aLocalBranch:aRemoteBranch", self.run, paths)
		elif content != '':
			import sys
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = content.encode(sys.getfilesystemencoding()).split(' ')
				object.to_status_bar = True
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushAndPushTagsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = item.repository
			object.command = ['git','push','&&','git','push','--tags']
			object.to_status_bar = True
			SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushAllBranchesCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = item.repository
			object.command = ['git','push','origin','*:*']
			object.to_status_bar = True
			SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushTagsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = item.repository
			object.command = ['git','push','--tags']
			object.to_status_bar = True
			SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		if confirm == False:
			SideBarGit().confirm('Pull from default? ', self.run, paths)
		else:
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = ['git','pull']
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPullWithOptionsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Pull with options: ', "git pull", self.run, paths)
		elif content != '':
			import sys
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = content.encode(sys.getfilesystemencoding()).split(' ')
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitFetchCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		if confirm == False:
			SideBarGit().confirm('Fetch from default? ', self.run, paths)
		else:
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = ['git','fetch']
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitFetchWithOptionsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Fetch with options: ', "git fetch aRemoteName aRemoteBranch:aLocalBranch", self.run, paths)
		elif content != '':
			import sys
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = content.encode(sys.getfilesystemencoding()).split(' ')
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitCommitUndoCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		if confirm == False:
			SideBarGit().confirm('Undo Commit? ', self.run, paths)
		else:
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.command = ['git', 'reset', '--soft', 'HEAD^']
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

# Following code for files and folders for each unique selected repos

class SideBarGitCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Enter a commit message: ', '', self.run, paths)
			sublime.active_window().run_command('toggle_setting', {"setting": "spell_check"})
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommand = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommand.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = Object()
				object.item = repo.repository
				object.to_status_bar = True
				object.command = commitCommand
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitCommitAllCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Enter a commit message: ', '', self.run, paths)
			sublime.active_window().run_command('toggle_setting', {"setting": "spell_check"})
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = item.repository
				object.to_status_bar = True
				object.command = ['git', 'commit', '-a', '-m', content]
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitCommitAmendCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			commitCommand = ['git', 'commit', '--amend', '-C', 'HEAD', '--']
			for item in repo.items:
				commitCommand.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
			object = Object()
			object.item = repo.repository
			object.to_status_bar = True
			object.command = commitCommand
			SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitAddCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Enter a commit message: ', '', self.run, paths)
			sublime.active_window().run_command('toggle_setting', {"setting": "spell_check"})
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommandAdd = ['git', 'add', '--']
				commitCommandCommit = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommandAdd.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
					commitCommandCommit.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = Object()
				object.item = repo.repository
				object.command = commitCommandAdd
				SideBarGit().run(object)
				object = Object()
				object.item = repo.repository
				object.to_status_bar = True
				object.command = commitCommandCommit
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitAddCommitPushCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Enter a commit message: ', '', self.run, paths)
			sublime.active_window().run_command('toggle_setting', {"setting": "spell_check"})
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommandAdd = ['git', 'add', '--']
				commitCommandCommit = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommandAdd.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
					commitCommandCommit.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = Object()
				object.item = repo.repository
				object.command = commitCommandAdd
				SideBarGit().run(object)
				object = Object()
				object.item = repo.repository
				object.to_status_bar = True
				object.command = commitCommandCommit
				SideBarGit().run(object)
				object = Object()
				object.item = repo.repository
				object.command = ['git','push']
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			command = ['git', 'add', '--']
			for item in repo.items:
				command.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
			object = Object()
			object.item = repo.repository
			object.command = command
			SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRemoveKeepLocalCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		if confirm == False:
			SideBarGit().confirm('Remove from repository, keep local copies? ', self.run, paths)
		else:
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				command = ['git', 'rm', '-r', '--cached', '--']
				for item in repo.items:
					command.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = Object()
				object.item = repo.repository
				object.command = command
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRemoveCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		if confirm == False:
			SideBarGit().confirm('Remove from repository, and remove local copies? ', self.run, paths)
		else:
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				command = ['git', 'rm', '-r', '-f', '--']
				for item in repo.items:
					command.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = Object()
				object.item = repo.repository
				object.command = command
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLiberalCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('[SideBarGit@SublimeText ./]:', 'git ', self.run, paths)
		elif content != '':
			import sys
			for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
				object = Object()
				object.item = item
				object.command = content.encode(sys.getfilesystemencoding()).split(' ')
				object.title = content
				object.no_results = 'No output'
				object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRemoteAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('Remote add: ', "git remote add aRemoteName "+sublime.get_clipboard(), self.run, paths)
		elif content != '':
			import sys
			content = content.encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = repo.repository
				object.command = content.split(' ')
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchNewFromCurrentCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('New branch: ', "", self.run, paths)
		elif content != '':
			import sys
			content = content.encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', '-b', content]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchNewFromMasterCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('New branch: ', "", self.run, paths)
		elif content != '':
			import sys
			content = content.encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', 'master']
				SideBarGit().run(object)

				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', '-b', content]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchNewFromCleanCurrentCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('New branch: ', "", self.run, paths)
		elif content != '':
			import sys
			content = content.encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):

				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', '-B', content]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchNewFromCleanMasterCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False, content = ''):
		if input == False:
			SideBarGit().prompt('New branch: ', "", self.run, paths)
		elif content != '':
			import sys
			content = content.encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):

				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', 'master']
				SideBarGit().run(object)

				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', '-B', content]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchSwitchToMasterCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = Object()
				object.item = repo.repository
				object.command = ['git', 'checkout', 'master']
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchSwitchToCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'branch', '-v']
			object.silent = True
			SideBarGit().run(object)
			SideBarGit().quickPanel(self.on_done, repo.repository, (SideBarGit.last_stdout.decode('utf-8')).split('\n'))

	def on_done(self, extra, data, result):
			result = data[result].strip()
			if result.startswith("*"):
				return
			else:
				import sys
				branch = result.split(' ')[0]
				object = Object()
				object.item = extra
				object.command = ['git', 'checkout', branch.encode(sys.getfilesystemencoding())]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchDeleteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'branch', '-v']
			object.silent = True
			SideBarGit().run(object)
			SideBarGit().quickPanel(self.on_done, repo.repository, (SideBarGit.last_stdout.decode('utf-8')).split('\n'))

	def on_done(self, extra, data, result):
			result = data[result].strip()
			if result.startswith("*"):
				return
			else:
				import sys
				branch = result.split(' ')[0]
				object = Object()
				object.item = extra
				object.command = ['git', 'branch', '-d', branch.encode(sys.getfilesystemencoding())]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBranchDeleteForceCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'branch', '-v']
			object.silent = True
			SideBarGit().run(object)
			SideBarGit().quickPanel(self.on_done, repo.repository, (SideBarGit.last_stdout.decode('utf-8')).split('\n'))

	def on_done(self, extra, data, result):
			result = data[result].strip()
			if result.startswith("*"):
				return
			else:
				import sys
				branch = result.split(' ')[0]
				object = Object()
				object.item = extra
				object.command = ['git', 'branch', '-D', branch.encode(sys.getfilesystemencoding())]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitMergeToCurrentFromCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'branch', '-v']
			object.silent = True
			SideBarGit().run(object)
			SideBarGit().quickPanel(self.on_done, repo.repository, (SideBarGit.last_stdout.decode('utf-8')).split('\n'))

	def on_done(self, extra, data, result):
			result = data[result].strip()
			if result.startswith("*"):
				return
			else:
				import sys
				branch = result.split(' ')[0]
				object = Object()
				object.item = extra
				object.command = ['git', 'merge', branch.encode(sys.getfilesystemencoding())]
				object.to_status_bar = True
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRebaseCurrentIntoMasterCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'rebase', 'master']
			SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

 #  }
 #  this.tagAdd = function(event)
 #  {
	# var aMsg = this.s.prompt('Enter tag name to add…', '');
	# if(aMsg != '')
	# {
	#   var repos = this.getSelectedRepos(event);
	#   var commands = '';
	#   for(var id in repos.r)
	#   {
	# 	commands += 'cd '+repos.r[id].cwd+'';
	# 	commands += '\n';
	# 	commands += 'git tag "'+this.s.filePathEscape(aMsg)+'" >>'+repos.obj.output+' 2>&1';
	# 	commands += '\n';
	#   }
	#   this.s.fileWrite(repos.obj.sh, commands);
	#   this.run(repos.obj.sh, repos.obj.outputFile, 'Tag "'+aMsg+'" added', false, true);
	# }
 #  }
 #  this.tagRemove = function(event)
 #  {
	# var aMsg = this.s.prompt('Enter tag name to remove…', '');
	# if(aMsg != '')
	# {
	#   var repos = this.getSelectedRepos(event);
	#   var commands = '';
	#   for(var id in repos.r)
	#   {
	# 	commands += 'cd '+repos.r[id].cwd+'';
	# 	commands += '\n';
	# 	commands += 'git tag -d "'+this.s.filePathEscape(aMsg)+'" >>'+repos.obj.output+' 2>&1';
	# 	commands += '\n';
	#   }
	#   this.s.fileWrite(repos.obj.sh, commands);
	#   this.run(repos.obj.sh, repos.obj.outputFile, '', false, true);
	# }
 #  }
 #  this.tagAuto = function(event)
 #  {
	# var repos = this.getSelectedRepos(event);
	# var commands = '';
	# for(var id in repos.r)
	# {
	#   var version = this.repositoryPreference(id, 'version') || 0;
	# 	  version++;
	#   this.repositoryPreference(id, 'version', version);

	#   commands += 'cd '+repos.r[id].cwd+'';
	#   commands += '\n';
	#   commands += 'git tag "'+this.s.filePathEscape(this.s.now().replace(/-/g, '').substr(2, 6)+'.'+version)+'" >>'+repos.obj.output+' 2>&1';
	#   commands += '\n';
	# }
	# this.s.fileWrite(repos.obj.sh, commands);
	# this.run(repos.obj.sh, repos.obj.outputFile, 'Tag '+this.s.now().replace(/-/g, '').substr(2, 6)+' added', false, true);
 #  }
 #  this.tagList = function(event)
 #  {
	# var repos = this.getSelectedRepos(event);
	# var commands = '';
	# for(var id in repos.r)
	# {
	#   commands += 'cd '+repos.r[id].cwd+'';
	#   commands += '\n';
	#   commands += 'git tag -l >>'+repos.obj.output+' 2>&1';
	#   commands += '\n';
	# }
	# this.s.fileWrite(repos.obj.sh, commands);
	# this.run(repos.obj.sh, repos.obj.outputFile, '', true, false);
 #  }
 #  this.tagsGetFromRepo = function(aObj)
 #  {
	# var sh = this.s.fileCreateTemporal('kGit.sh', '');

	# this.s.fileWrite(sh, 'cd '+aObj.cwd+' \n echo `git for-each-ref refs/tags --sort=-authordate` \n');

	# var tags = this.run(sh, sh+'.diff', '', false, false, true).split('\n');
	# 	tags.shift();
	# 	tags.shift();
	# 	tags.shift();
	# 	tags.shift();
	# 	tags.shift();
	# 	tags = tags.join('');
	# 	tags = tags.split('refs/tags/');
	# 	tags.shift();
	# 	for(var id in tags)
	# 	  tags[id] = tags[id].split(' ')[0];
	# 	tags.reverse();
	# return tags;
 #  }


#  //TODO: hardcoded branch name

 #  }
 #  this.diffBetweenLatestTagAndLastCommit = function(event)
 #  {
	# var selected = this.getSelectedPaths(event);
	# for(var id in selected)
	# {
	#   var obj = this.getPaths(selected[id]);
	#   var tags = this.tagsGetFromRepo(obj);
	#   this.s.fileWrite(obj.sh, 'cd '+obj.cwd+'\ngit diff "'+(tags.pop() || '')+'"... -- '+obj.selected+' >>'+obj.output+' 2>&1\n');
	#   this.run(obj.sh, obj.outputFile, 'No difference found', true);
	# }
 #  }
 #  this.diffBetweenTheTwoLatestTags = function(event)
 #  {
	# var selected = this.getSelectedPaths(event);
	# for(var id in selected)
	# {
	#   var obj = this.getPaths(selected[id]);
	#   var tags = this.tagsGetFromRepo(obj);
	#   this.s.fileWrite(obj.sh, 'cd '+obj.cwd+'\ngit diff "'+(tags[tags.length-2] || '')+'".."'+(tags[tags.length-1] || '')+'" -- '+obj.selected+' >>'+obj.output+' 2>&1\n');
	#   this.run(obj.sh, obj.outputFile, 'No difference found', true);
	# }
 #  }
 #  this.logSinceLatestTag = function(event)
 #  {
	# var selected = this.getSelectedPaths(event);
	# for(var id in selected)
	# {
	#   var obj = this.getPaths(selected[id]);
	#   var tags = this.tagsGetFromRepo(obj);
	#   this.s.fileWrite(obj.sh, 'cd '+obj.cwd+'\n echo "log:'+this.s.filePathEscape(this.s.pathToNix(obj.selectedFile))+'" >> '+obj.output+' \n git log "'+(tags.pop() || '')+'"... --stat --graph -- '+obj.selected+' >>'+obj.output+' 2>&1\n');
	#   this.run(obj.sh, obj.outputFile, 'No log to show', true);
	# }

 #  this.logBetweenTheTwoLatestTags = function(event)
 #  {
	# var selected = this.getSelectedPaths(event);
	# for(var id in selected)
	# {
	#   var obj = this.getPaths(selected[id]);
	#   var tags = this.tagsGetFromRepo(obj);
	#   this.s.fileWrite(obj.sh, 'cd '+obj.cwd+' echo "log:'+this.s.filePathEscape(this.s.pathToNix(obj.selectedFile))+'" >> '+obj.output+' \n git log "'+(tags[tags.length-2] || '')+'".."'+(tags[tags.length-1] || '')+'" --stat --graph -- '+obj.selected+' >>'+obj.output+' 2>&1\n');
	#   this.run(obj.sh, obj.outputFile, 'No log to show', true);
	# }
 #  }