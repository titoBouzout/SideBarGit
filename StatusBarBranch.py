import sublime, sublime_plugin
from SideBarGit import SideBarGit
from SideBarSelection import SideBarSelection
from Utils import Object
import threading

s = sublime.load_settings('SideBarGit.sublime-settings')

class StatusBarBranch(sublime_plugin.EventListener):

	def on_load(self, v):
		if s.get('statusbar_branch') and v.file_name():
			StatusBarBranchGet(v.file_name(), v).start()

	def on_activated(self, v):
		if s.get('statusbar_branch') and v.file_name():
			StatusBarBranchGet(v.file_name(), v).start()

class StatusBarBranchGet(threading.Thread):

	def __init__(self, file_name, v):
		threading.Thread.__init__(self)
		self.file_name = file_name
		self.v = v

	def run(self):
		for repo in SideBarGit().getSelectedRepos(SideBarSelection([self.file_name]).getSelectedItems()):
			object = Object()
			object.item = repo.repository
			object.command = ['git', 'branch']
			object.silent = True
			SideBarGit().run(object)
			sublime.set_timeout(lambda:self.on_done(SideBarGit.last_stdout.decode('utf-8')), 0)
			return

	def on_done(self, branches):
			branches = branches.split('\n')
			for branch in branches:
				if branch.startswith("*"):
					self.v.set_status('statusbar_sidebargit_branch', branch)
					return