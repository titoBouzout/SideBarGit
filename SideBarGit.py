# coding=utf8
import sublime
import os
import subprocess

from SideBarItem import SideBarItem
from Utils import Object

class SideBarGit:

	last_stdout = ''

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
			object = Object()
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
			SideBarGit.last_stdout = str(stdout).rstrip()
			self.last_stdout = str(stdout).rstrip()

			stdout = stdout.strip()

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
			SideBarGit.last_stdout = ''
			self.last_stdout = ''
		except IOError as (errno, strerror):
			print 'FAILED'
			failed = True
			print errno
			print strerror
			SideBarGit.last_stdout = ''
			self.last_stdout = ''
		if debug:
			print '----------------------------------------------------------'

		try:
			object.to_status_bar
		except:
			object.to_status_bar = False

		try:
			object.silent
			return
		except:
			pass

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
				try:
					object.word_wrap
					view.settings().set('word_wrap', False)
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

				content = "[SideBarGit@SublimeText "
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

	def quickPanel(self, function, extra, data):
		import functools
		window = sublime.active_window()
		window.show_input_panel("BUG!", '', '', None, None)
		window.run_command('hide_panel');
		window.show_quick_panel(data, functools.partial(self.quickPanelDone, function, extra, data))

	def quickPanelDone(self, function, extra, data, result):
		if result != -1:
			function(extra, data, result)

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
					repos.append(Object())
					repos[index].repository = item
					repos[index].items = []
				repos[index].items.append(SideBarItem(original, os.path.isdir(original)))
		return repos

	def escapeCMDWindows(self, string):
		return string.replace('^', '^^')