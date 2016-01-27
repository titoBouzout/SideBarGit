# coding=utf8
import sublime
import os, re
import subprocess
from .SideBarAPI import SideBarItem

import threading

class Object():
	pass

class Content():
	pass

s = {}

def plugin_loaded():
	global s
	s = sublime.load_settings('SideBarGit.sublime-settings')

def write_to_view(view, content):
	view.run_command('write_to_view', {"content": content});

class SideBarGitQueue:
	def __init__(self):
		self.queue = []
		self.running = False;

SideBarGitQueue = SideBarGitQueue();

class SideBarGitThread(threading.Thread):
		def __init__(self):
			SideBarGitQueue.running = True
			threading.Thread.__init__(self)

		def run(self):
			if len(SideBarGitQueue.queue) > 0:
				object = SideBarGitQueue.queue.pop(0)
				# print(object);
				SideBarGit().run2(
					object[0],
					object[1],
					object[2],
					object[3],
					object[4],
					object[5],
					object[6],
					object[7],
					object[8],
					object[9]
				);
				SideBarGitThread().start();
			SideBarGitQueue.running = False

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
					refresh_funct_syntax_file = False,
					blocking=False
					):
		if not blocking:
			SideBarGitQueue.queue.append([
			                       	object,
			                       	modal,
			                       	background,
			                       	refresh_funct_view,
			                       	refresh_funct_command,
			                       	refresh_funct_item,
			                       	refresh_funct_to_status_bar,
			                       	refresh_funct_title,
			                       	refresh_funct_no_results,
			                       	refresh_funct_syntax_file
			                       ]);
			if not SideBarGitQueue.running:
				SideBarGitThread().start();
		else:
			self.run2(
			    object,
					modal,
					background,
					refresh_funct_view,
					refresh_funct_command,
					refresh_funct_item,
					refresh_funct_to_status_bar,
					refresh_funct_title,
					refresh_funct_no_results,
					refresh_funct_syntax_file)

	def run2(
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
			print ('----------------------------------------------------------')
			print ('GIT:')
			print (object.command)
			print ('CWD:')
			print (object.item.forCwdSystemPath())
			print ('PATH:')
			print (object.item.forCwdSystemName())

		failed = False

		if sublime.platform() == 'windows':
			object.command = list(map(self.escapeCMDWindows, object.command))

		if sublime.platform() is not 'windows' and object.command[0] == 'git':
			if s.get('path_to_git_unixes') != '':
				object.command[0] = s.get('path_to_git_unixes')
			elif os.path.exists('/usr/local/git/bin'):
				object.command[0] = '/usr/local/git/bin/git'

		cwd = object.item.forCwdSystemPath()

		try:
			if sublime.platform() == 'windows':
				if 'push' in object.command or 'pull' in object.command or 'clone' in object.command or 'fetch' in object.command:
					object.command.insert(0, '/C')
					object.command.insert(0, 'cmd')
					shell = False
				else:
					shell = True
				process = subprocess.Popen(
																	#" ".join(object.command),
																	object.command,
																	cwd=cwd,
																	stdout=subprocess.PIPE,
																	stderr=subprocess.STDOUT,
																	shell=shell)
			else:
				process = subprocess.Popen(
																	object.command,
																	cwd=cwd,
																	stdout=subprocess.PIPE,
																	stderr=subprocess.STDOUT,
																	shell=False)

			if background:
				if debug:
					print ('SUCCESS')
					print ('----------------------------------------------------------')
				return True

			stdout, stderr = process.communicate()
			try:
				process.kill()
			except:
				pass
			stdout = stdout.decode('utf-8', 'ignore');
			SideBarGit.last_stdout = str(stdout).rstrip()
			self.last_stdout = str(stdout).rstrip()

			stdout = stdout.strip()

			if stdout.find('fatal:') == 0 or stdout.find('error:') == 0 or stdout.find('Permission denied') == 0 or stderr:
				if debug:
					print ('FAILED')
				failed = True
			else:
				if debug:
					print ('SUCCESS')
			if stdout:
				if debug:
					print ('STDOUT')
					print (stdout)
			if stderr:
				print ('STDERR')
				print (stderr)
		except (OSError, IOError) as e:
			print ('FAILED')
			failed = True
			print (e.errno)
			print (e.strerror)
			SideBarGit.last_stdout = ''
			self.last_stdout = ''
		if debug:
			print ('----------------------------------------------------------')

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
					view.set_name(object.title)
				except:
					view.set_name('No Title')
				try:
					if object.syntax_file:
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
				content += object.item.name()
				content += "/] "
				content += (" ".join(object.command))
				content += "\n\n"
				content += "# Improve this command, the output or the tab title by posting here:"
				content += "\n"
				content += "# http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3405"
				content += "\n"
				content += "# Tip: F5 will run the command again and refresh the contents of this tab"
				content += "\n\n"
				content += stdout

				write_to_view(view, content);

		return True

	def confirm(self, message, function, arg1):
		if int(sublime.version()) >= 2186:
			if sublime.ok_cancel_dialog('Side Bar Git : '+message):
				function(arg1, True)
		else:
			import functools
			sublime.active_window().run_command('hide_panel');
			sublime.active_window().show_input_panel("Confirmation Required:", message, functools.partial(function, arg1, True), None, None)

	def prompt(self, message, default, function, arg1):
		import functools
		sublime.active_window().run_command('hide_panel');
		sublime.active_window().show_input_panel(message, default, functools.partial(function, arg1, True), None, None)

	def alert(self, message):
		try:
			sublime.error_message('Git : '+(message))
		except:
			try:
				sublime.error_message('Git : '+message)
			except:
				print (message)

	def status(self, message):
		if len(message) > 250:
			view = sublime.active_window().new_file()
			view.settings().set('word_wrap', False)
			view.set_scratch(True)
			content = "[SideBarGit@SublimeText] "
			write_to_view(view, content+"\n"+message);
		else:
			message = message.replace('\n', ' ')
			try:
				v = sublime.active_window().active_view()
				v.set_status('SideBarGit', 'Git : '+(message))
				sublime.set_timeout(lambda: SideBarGit().statusRemove(v), 16000)
			except:#there is no tabs opened
				sublime.status_message('Git : '+(message))

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
		data = [item[:70] for item in data]
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
