# coding=utf8
import sublime, sublime_plugin
import os
import re
import subprocess

class SideBarGit:

	def run(
					self,
					object,
					modal = False,
					background = False,

					refresh_funct_view = False,
					refresh_funct_command = False,
					refresh_funct_item = False,
					refresh_funct_to_status_bar = False,
					refresh_funct_title = False,
					refresh_funct_no_results = False,
					refresh_funct_syntax_file = False
					):

		if not refresh_funct_view:
			pass
		else:
			object = SideBarGitItem()
			object.command = refresh_funct_command
			object.item = SideBarItem(refresh_funct_item, os.path.isdir(refresh_funct_item))
			object.to_status_bar = refresh_funct_to_status_bar
			object.title = refresh_funct_title
			object.no_results = refresh_funct_no_results
			object.syntax_file = refresh_funct_syntax_file

		debug = False
		if debug:
			print '----------------------------------------------------------'
			print 'GIT:'
			print object.command
			print 'CWD:'
			print object.item.forCwdSystemPath()
			print 'PATH:'
			print object.item.forCwdSystemName()

		failed = False

		import sys
		if sys.platform == 'win32':
			object.command = map(self.escapeCMDWindows, object.command)

		cwd = object.item.forCwdSystemPath()

		try:
			if not modal :
				process = subprocess.Popen(
																	object.command,
																	cwd=cwd,
																	stdout=subprocess.PIPE,
																	stderr=subprocess.STDOUT,
																	shell= sys.platform == 'win32',
																	universal_newlines=True)
			else:
				if sys.platform == 'win32':
					process = subprocess.Popen(
																		#" ".join(object.command),
																		object.command,
																		cwd=cwd,
																		stdout=subprocess.PIPE,
																		stderr=subprocess.STDOUT,
																		shell=True,
																		universal_newlines=True)
				else:
					process = subprocess.Popen(
																		object.command,
																		cwd=cwd,
																		stdout=subprocess.PIPE,
																		stderr=subprocess.STDOUT,
																		shell=False,
																		universal_newlines=True)

			if background:
				if debug:
					print 'SUCCESS'
					print '----------------------------------------------------------'
				return True

			stdout, stderr = process.communicate()

			if stdout.find('fatal:') == 0 or stdout.find('error:') == 0 or stdout.find('Permission denied') == 0 or stderr:
				print 'FAILED'
				failed = True
			else:
				if debug:
					print 'SUCCESS'
			if stdout:
				if debug:
					print 'STDOUT'
					print stdout
			if stderr:
				print 'STDERR'
				print stderr
		except OSError as (errno, strerror):
			print 'FAILED'
			failed = True
			print errno
			print strerror
		except IOError as (errno, strerror):
			print 'FAILED'
			failed = True
			print errno
			print strerror
		if debug:
			print '----------------------------------------------------------'

		try:
			object.to_status_bar
		except:
			object.to_status_bar = False

		if failed:
			try:
				strerror
				if errno == 2:
					self.alert(strerror+'\nPossible error:\n'+object.command[0]+' not found on $PATH')
				else:
					self.alert(strerror)
				return False
			except:
				if not stdout and not stderr:
					return False
				if stdout.find('Permission denied') == 0 or stdout.find('fatal: The remote end hung up unexpectedly') == 0:
					self.alert((stdout or '')+'\n'+(stderr or '')+'\nPossible error:\nssh keys not in .ssh/ directory or keys not opened')
				else:
					self.alert((stdout or '')+'\n'+(stderr or ''))
				return False
		else:
			if stdout != '' and refresh_funct_view == False and (object.to_status_bar or " ".join(object.command).find('git push') == 0 or stdout.find('nothing to commit') == 0):
				self.status(stdout)
			else:
				if stdout == '' and refresh_funct_view == False:
					try:
						self.status(object.no_results)
					except:
						self.status('No output to show')
					return True
				if stdout == '' and refresh_funct_view != False:
					try:
						stdout = object.no_results
					except:
						stdout = 'No output to show'
				if stdout == '':
					return True

				if refresh_funct_view == False:
					view = sublime.active_window().new_file()
				else:
					view = refresh_funct_view
				try:
					view.set_name(object.title.decode('utf-8'))
				except:
					view.set_name('No Title')
				try:
					if object.syntax_file != False:
						view.set_syntax_file(object.syntax_file)
				except:
					pass
				view.settings().set('fallback_encoding', 'UTF-8')
				view.settings().set('encoding', 'UTF-8')
				view.settings().set('default_dir', object.item.dirname())
				view.set_scratch(True)

				if refresh_funct_view == False:
					view.settings().set('SideBarGitIsASideBarGitTab', True)
					view.settings().set('SideBarGitCommand', object.command)
					view.settings().set('SideBarGitModal', modal)
					view.settings().set('SideBarGitBackground', background)
					view.settings().set('SideBarGitItem', object.item.path())
					try:
						view.settings().set('SideBarGitToStatusBar', object.to_status_bar)
					except:
						view.settings().set('SideBarGitToStatusBar', False)
					try:
						view.settings().set('SideBarGitTitle', object.title)
					except:
						view.settings().set('SideBarGitTitle', 'No Title')
					try:
						view.settings().set('SideBarGitNoResults', object.no_results)
					except:
						view.settings().set('SideBarGitNoResults', 'No output to show')
					try:
						view.settings().set('SideBarGitSyntaxFile', object.syntax_file)
					except:
						view.settings().set('SideBarGitSyntaxFile', False)

				content = "[SideBarGit@sublime "
				content += object.item.name().decode('utf-8')
				content += "/] "
				content += (" ".join(object.command)).decode('utf-8')
				content += "\n\n"
				content += "# Improve this command, the output or the tab title by posting here:"
				content += "\n"
				content += "# http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3405"
				content += "\n"
				content += "# Tip: F5 will run the command again and refresh the contents of this tab"
				content += "\n\n"

				content += stdout.decode('utf-8')
				edit = view.begin_edit()
				view.replace(edit, sublime.Region(0, view.size()), content);
				view.sel().clear()
				view.sel().add(sublime.Region(0))
				view.end_edit(edit)
		return True

	def confirm(self, message, function, arg1):
		import functools
		sublime.active_window().run_command('hide_panel');
		sublime.active_window().show_input_panel("Confirmation Required:", message.decode('utf-8'), functools.partial(function, arg1, True), None, None)

	def prompt(self, message, default, function, arg1):
		import functools
		sublime.active_window().run_command('hide_panel');
		sublime.active_window().show_input_panel(message.decode('utf-8'), default.decode('utf-8'), functools.partial(function, arg1, True), None, None)

	def alert(self, message):
		try:
			sublime.error_message('Git : '+(message.decode('utf-8')))
		except:
			try:
				sublime.error_message('Git : '+message)
			except:
				print message

	def status(self, message):
		message = message[:200] + (message[200:] and '…')
		message = message.replace('\n', ' ')
		try:
			v = sublime.active_window().active_view()
			v.set_status('SideBarGit', 'Git : '+(message.decode('utf-8')))
			sublime.set_timeout(lambda: SideBarGit().statusRemove(v), 16000)
		except:#there is no tabs opened
			sublime.status_message('Git : '+(message.decode('utf-8')))

	def statusRemove(self, v):
		try:
			v.erase_status('SideBarGit')
		except:#this view is not there
			pass


	def getSelectedRepos(self, items):
		repos = []
		reposTemp = []
		for item in items:
			original = item.path()
			while not os.path.exists(item.join('.git')):
				if item.dirname() == item.path():
					break;
				item.path(item.dirname())

			if os.path.exists(item.join('.git')):
				try:
					index = reposTemp.index(item.path())
				except ValueError:
					reposTemp.append(item.path())
					index = reposTemp.index(item.path())
					repos.append(SideBarGitItem())
					repos[index].repository = item
					repos[index].items = []
				repos[index].items.append(SideBarItem(original, os.path.isdir(original)))
		return repos

	def escapeCMDWindows(self, string):
		return string.replace('^', '^^')


class SideBarGitRefreshTabContentsByRunningCommandAgain(sublime_plugin.TextCommand):
	def run(self, edit):
		if self.view.settings().has('SideBarGitIsASideBarGitTab'):
			SideBarGit().run(
												[],
												self.view.settings().get('SideBarGitModal'),
												self.view.settings().get('SideBarGitBackground'),
												self.view,
												self.view.settings().get('SideBarGitCommand'),
												self.view.settings().get('SideBarGitItem'),
												self.view.settings().get('SideBarGitToStatusBar'),
												self.view.settings().get('SideBarGitTitle'),
												self.view.settings().get('SideBarGitNoResults'),
												self.view.settings().get('SideBarGitSyntaxFile')
												)

class SideBarGitItem:
	pass

#Following code for selected files or folders

class SideBarGitDiffAllChangesSinceLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', 'HEAD', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffChangesNotStagedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffChangesStagedNotCommitedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', '--staged', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenIndexAndLastCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', '--cached', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenRemoteAndLastLocalCommitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', 'origin/master..', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitDiffBetweenLastLocalCommitAndRemoteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'diff', '..origin/master', '--', item.forCwdSystemName()]
			object.title = 'Diff: '+item.name()+'.diff'
			object.no_results = 'No differences to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatShortLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '--pretty=short', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatShortFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '--pretty=short', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatListLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import sys
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-n', '50', '--pretty=format:%s'.encode(sys.getfilesystemencoding()),  '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogStatListCommitLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import sys
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-n', '50', '--pretty=format:%h %s'.encode(sys.getfilesystemencoding()), '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogExtendedLatestCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-n', '30', '-p', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogExtendedFullCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', '-p', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Diff/Diff.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitLogSinceLatestPushCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'log', 'origin/master..', '--stat', '--graph', '--decorate', '--no-color', '--', item.forCwdSystemName()]
			object.title = 'Log: '+item.name()
			object.no_results = 'No log to show'
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitBlameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'blame', '--', item.forCwdSystemName()]
			object.title = 'Blame: '+item.name()
			object.syntax_file = 'Packages/Git/Git Blame.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitStatusCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			object = SideBarGitItem()
			object.item = item
			object.command = ['git', 'status', '--untracked-files=all','--ignored', '--', item.forCwdSystemName()]
			object.title = 'Status: '+item.name()
			object.syntax_file = 'Packages/Git/Git Graph.tmLanguage'
			SideBarGit().run(object)
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked on selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
			if not failed:
				SideBarGit().status('Discarded changes to tracked on selected items')
	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitRevertTrackedCleanUntrackedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirm = False, drop_me = ''):
		failed = False
		if confirm == False:
			SideBarGit().confirm('Discard changes to tracked and clean untracked on selected items? ', self.run, paths)
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = SideBarGitItem()
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
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'clean', '-f', '-d', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = SideBarGitItem()
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
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'checkout', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = SideBarGitItem()
				object.item = item
				object.command = ['git', 'reset', 'HEAD', '--', item.forCwdSystemName()]
				if not SideBarGit().run(object):
					failed = True
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				ignore_entry += '/*'
			item.write(item.contentUTF8().strip()+'\n'+ignore_entry)
			SideBarGit().status('Ignored file "'+ignore_entry+'" on '+item.path())

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

# Following code for selected folders. Dirname for when a file is selected.

class SideBarGitInitCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			object = SideBarGitItem()
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
			SideBarGit().prompt('Enter URL to clone: ', '', self.run, paths)
		elif content != '':
			import sys
			for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
				object = SideBarGitItem()
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
			object = SideBarGitItem()
			object.item = item
			object.command = ['git','gui']
			SideBarGit().run(object, False, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitGitkCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], input = False):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			object = SideBarGitItem()
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
				object = SideBarGitItem()
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
			object = SideBarGitItem()
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
				object = SideBarGitItem()
				object.item = item.repository
				object.command = content.encode(sys.getfilesystemencoding()).split(' ')
				SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushAndPushTagsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = SideBarGitItem()
			object.item = item.repository
			object.command = ['git','push','&&','git','push','--tags']
			SideBarGit().run(object, True)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarGitPushTagsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
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
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommand = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommand.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = SideBarGitItem()
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
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for item in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				object = SideBarGitItem()
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
			object = SideBarGitItem()
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
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommandAdd = ['git', 'add', '--']
				commitCommandCommit = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommandAdd.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
					commitCommandCommit.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = SideBarGitItem()
				object.item = repo.repository
				object.command = commitCommandAdd
				SideBarGit().run(object)
				object = SideBarGitItem()
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
		elif content != '':
			import sys
			content = (content[0].upper() + content[1:]).encode(sys.getfilesystemencoding())
			for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
				commitCommandAdd = ['git', 'add', '--']
				commitCommandCommit = ['git', 'commit', '-m', content, '--']
				for item in repo.items:
					commitCommandAdd.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
					commitCommandCommit.append(item.forCwdSystemPathRelativeFrom(repo.repository.path()))
				object = SideBarGitItem()
				object.item = repo.repository
				object.command = commitCommandAdd
				SideBarGit().run(object)
				object = SideBarGitItem()
				object.item = repo.repository
				object.to_status_bar = True
				object.command = commitCommandCommit
				SideBarGit().run(object)
				object = SideBarGitItem()
				object.item = repo.repository
				object.command = ['git','push']
				SideBarGit().run(object, True)

class SideBarGitAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection(paths).getSelectedItems()):
			command = ['git', 'add', '--']
			for item in repo.items:
				command.append(item.forCwdSystemPathRelativeFromRecursive(repo.repository.path()))
			object = SideBarGitItem()
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
				object = SideBarGitItem()
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
				object = SideBarGitItem()
				object.item = repo.repository
				object.command = command
				SideBarGit().run(object)

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

 #  }
 #  this.remoteAdd = function(event)
 #  {
	# var aMsg = this.s.prompt('Enter name and URL of remote…');
	# if(aMsg != '')
	# {
	#   var repos = this.getSelectedRepos(event);
	#   var commands = '';
	#   for(var id in repos.r)
	#   {
	# 	commands += 'cd '+repos.r[id].cwd+'';
	# 	commands += '\n';
	# 	commands += 'git remote add '+aMsg+' >>'+repos.obj.output+' 2>&1';
	# 	commands += '\n';
	#   }
	#   this.s.fileWrite(repos.obj.sh, commands);
	#   this.run(repos.obj.sh, repos.obj.outputFile, '', false, true);
	# }
 #  }
 #  this.configDefaultRemote = function(event)
 #  {
	# var aBranch = this.s.prompt('Enter the name of your local branch…');
	# if(aBranch != '')
	#   var aRemote = this.s.prompt('Enter the name of the remote…');
	# if(aBranch != '' && aRemote != '')
	# {
	#   var repos = this.getSelectedRepos(event);
	#   var commands = '';
	#   for(var id in repos.r)
	#   {
	# 	commands += 'cd '+repos.r[id].cwd+'';
	# 	commands += '\n';
	# 	commands += 'git config branch.'+aBranch+'.remote '+aRemote+' >>'+repos.obj.output+' 2>&1';
	# 	commands += '\n';
	#   }
	#   this.s.fileWrite(repos.obj.sh, commands);
	#   this.run(repos.obj.sh, repos.obj.outputFile, '', false, true);
	# }
 #  }
 #  this.command = function(event)
 #  {
	# var selected = this.getSelectedPathFolder(event);
	# var obj = this.getPaths(selected);

	# var aMsg = this.s.prompt('[komodin@komodo '+obj.cwdSelected+'] $ ', 'git ');
	# if(aMsg != '')
	# {
	#   this.s.fileWrite(obj.sh, 'cd '+obj.cwdSelected+' \n'+aMsg+' >>'+obj.output+' 2>&1');
	#   this.loadingSet();
	#   this.s.execute(this.gitPath, obj.sh, obj.outputFile, function(a,b){ kgit.executeObserver(a,b,true)});
	# }
 #  }

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


class SideBarSelection:

	def __init__(self, paths = []):

		if len(paths) < 1:
			try:
				path = sublime.active_window().active_view().file_name()
				if path != '' and path != '.' and path != '..' and path != './' and path != '/' and path != '//' and path != '\\' and path != '\\\\':
					paths = [path]
				else:
					paths = []
			except:
				paths = []
		self._paths = paths

		self._obtained_selection_information_basic = False
		self._obtained_selection_information_extended = False

	def len(self):
		return len(self._paths)

	def hasDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._has_directories

	def hasFiles(self):
		self._obtainSelectionInformationBasic()
		return self._has_files

	def hasOnlyDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._only_directories

	def hasOnlyFiles(self):
		self._obtainSelectionInformationBasic()
		return self._only_files

	def hasImages(self):
		return self.hasFilesWithExtension('gif|jpg|jpeg|png')

	def hasFilesWithExtension(self, extensions):
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				return True;
		return False

	def getSelectedItems(self):
		self._obtainSelectionInformationExtended()
		return self._files + self._directories;

	def getSelectedDirectories(self):
		self._obtainSelectionInformationExtended()
		return self._directories;

	def getSelectedFiles(self):
		self._obtainSelectionInformationExtended()
		return self._files;

	def getSelectedDirectoriesOrDirnames(self):
		self._obtainSelectionInformationExtended()
		return self._directories_or_dirnames;

	def getSelectedImages(self):
		return self.getSelectedFilesWithExtension('gif|jpg|jpeg|png')

	def getSelectedFilesWithExtension(self, extensions):
		items = []
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				items.append(item)
		return items

	def _obtainSelectionInformationBasic(self):
		if not self._obtained_selection_information_basic:
			self._obtained_selection_information_basic = True

			self._has_directories = False
			self._has_files = False
			self._only_directories = False
			self._only_files = False

			for path in self._paths:
				if self._has_directories == False and os.path.isdir(path):
					self._has_directories = True
				if self._has_files == False and os.path.isdir(path) == False:
					self._has_files = True
				if self._has_files and self._has_directories:
					break

			if self._has_files and self._has_directories:
				self._only_directories = False
				self._only_files 	= False
			elif self._has_files:
				self._only_files 	= True
			elif self._has_directories:
				self._only_directories = True

	def _obtainSelectionInformationExtended(self):
		if not self._obtained_selection_information_extended:
			self._obtained_selection_information_extended = True

			self._directories = []
			self._files = []
			#selected directories and/or the dirname of selected files if any
			self._directories_or_dirnames = []

			for path in self._paths:
				if os.path.isdir(path):
					item = SideBarItem(path, True)
					if item not in self._directories:
						self._directories.append(item)
					if item not in self._directories_or_dirnames:
						self._directories_or_dirnames.append(item)
				else:
					item = SideBarItem(path, False)
					if item not in self._files:
						self._files.append(item)
					item = SideBarItem(os.path.dirname(path), True)
					if item not in self._directories_or_dirnames:
						self._directories_or_dirnames.append(item)

class SideBarItem:

	def __init__(self, path, is_directory):
		self._path = path
		self._is_directory = is_directory

	def path(self, path = ''):
		if path == '':
			return self._path
		else:
			self._path = path
			self._is_directory = os.path.isdir(path)
			return path

	def pathSystem(self):
		import sys
		return self.path().encode(sys.getfilesystemencoding())

	def pathWithoutProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path = re.sub('^'+re.escape(directory), '', path)
		return path.replace('\\', '/')

	def pathRelativeFromProject(self):
		return re.sub('^/+', '', self.pathWithoutProject())

	def pathRelativeFromProjectEncoded(self):
		import urllib
		return urllib.quote(self.pathRelativeFromProject().encode('utf-8'))

	def pathRelativeFromView(self):
		return os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/')

	def pathRelativeFromViewEncoded(self):
		import urllib
		return urllib.quote(os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/').encode('utf-8'))

	def pathAbsoluteFromProject(self):
		return self.pathWithoutProject()

	def pathAbsoluteFromProjectEncoded(self):
		import urllib
		return urllib.quote(self.pathAbsoluteFromProject().encode('utf-8'))

	def uri(self):
		import urllib
		return 'file:'+urllib.pathname2url(self.path().encode('utf-8'));

	def join(self, name):
		return os.path.join(self.path(), name)

	def dirname(self):
		branch, leaf = os.path.split(self.path())
		return branch;

	def forCwdSystemPath(self):
		if self.isDirectory():
			return self.pathSystem()
		else:
			return self.dirnameSystem()

	def forCwdSystemName(self):
		if self.isDirectory():
			return './'
		else:
			path = self.pathSystem()
			branch = self.dirnameSystem()
			leaf = path.replace(branch, '').replace('\\', '').replace('/', '')
			return leaf

	def forCwdSystemPathRelativeFrom(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.pathSystem().replace(relative.pathSystem(), '').replace('\\', '/')
		if path == '':
			return './'
		else:
			return './'+re.sub('^/+', '', path)

	def forCwdSystemPathRelativeFromRecursive(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.pathSystem().replace(relative.pathSystem(), '').replace('\\', '/')
		if path == '':
			return './'
		else:
			if self.isDirectory():
				return './'+re.sub('^/+', '', path)+'/'
			else:
				return './'+re.sub('^/+', '', path)

	def dirnameSystem(self):
		import sys
		return self.dirname().encode(sys.getfilesystemencoding())

	def dirnameCreate(self):
		try:
			os.makedirs(self.dirname())
		except:
			pass

	def name(self):
		branch, leaf = os.path.split(self.path())
		return leaf;

	def nameSystem(self):
		import sys
		return self.name().encode(sys.getfilesystemencoding())

	def nameEncoded(self):
		import urllib
		return urllib.quote(self.name().encode('utf-8'));

	def namePretty(self):
		return self.name().replace(self.extension(), '').replace('-', ' ').replace('_', ' ').strip();

	def open(self):
		import sys
		if sys.platform == 'darwin':
			import subprocess
			subprocess.Popen(['open', '-a', self.path()], shell=True)
		elif sys.platform == 'win32':
			import subprocess
			subprocess.Popen([self.nameSystem()], cwd=self.dirnameSystem(), shell=True)
		else:
			sys.path.append(os.path.join(sublime.packages_path(), 'SideBarEnhancements'))
			import desktop
			desktop.open(self.path())

	def edit(self):
		sublime.active_window().open_file(self.path())

	def isDirectory(self):
		return self._is_directory

	def isFile(self):
		return self.isDirectory() == False

	def contentUTF8(self):
		import codecs
		return codecs.open(self.path(), 'r', 'utf-8').read()

	def contentBinary(self):
		return file(self.path(), "rb").read()

	def contentBase64(self):
		return 'data:'+self.mime()+';base64,'+(file(self.path(), "rb").read().encode("base64").replace('\n', ''))

	def reveal(self):
		sublime.active_window().run_command("open_dir", {"dir": self.dirname(), "file": self.name()} )

	def write(self, content):
		file(self.path(), 'w+').write(content)

	def mime(self):
		import mimetypes
		return mimetypes.guess_type(self.path())[0] or 'application/octet-stream'

	def extension(self):
		return os.path.splitext('name'+self.name())[1].lower()

	def exists(self):
		return os.path.isdir(self.path()) or os.path.isfile(self.path())

	def create(self):
		if self.isDirectory():
			self.dirnameCreate()
			os.makedirs(self.path())
		else:
			self.dirnameCreate()
			self.write('')

	def move(self, location):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists():
			return False
		else:
			location.dirnameCreate();
			os.rename(self.path(), location.path())
			return True

	def copy(self, location):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists():
			return False
		else:
			location.dirnameCreate();
			import shutil
			if self.isDirectory():
				shutil.copytree(self.path(), location.path())
			else:
				shutil.copy2(self.path(), location.path())
			return True

