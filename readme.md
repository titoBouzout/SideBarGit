Description
------------------

Provides git commands on Side Bar of Files and Folders for Sublime Text 2. For sublime text see: http://www.sublimetext.com/

It should work with files names in any language.

This plugin is a port of the "Komodin" extension for komodo edit. See: https://github.com/titoBouzout/komodo-komodin-git


Usage
------------------

* Right click on "multiple/single" "files/folders" of the "tree" sidebar to apply commands on selected files which maybe are from different repositories.

* To apply commands to focused document use the document context menu.

* Tip: If a command sends output to a tab ( example a diff ), pressing F5 on that tab: will execute the command again and refresh the tab with the new contents ( example the new computed diff )

Provides the following commands
------------------

<pre>
Add & Commit
  o git add -- "/selected/paths/files/or/and/folders"
  o git commit -m "promptMessage" -- "/selected/paths/files/or/and/folders"
Add & Commit & Push
  o git add -- "/selected/paths/files/or/and/folders"
  o git commit -m "promptMessage" -- "/selected/paths/files/or/and/folders"
  o git push

Commit
  o git commit -m "promptMessage" -- "/selected/paths/files/or/and/folders"
Commit Undo
  o git reset --soft HEAD~1

Commit Amend
  o git commit --amend -C HEAD -- "/selected/paths/files/or/and/folders"
Commit All
  o git commit -a -m "promptMessage"

Status
  o git status --untracked-files=all -- "/selected/paths/files/or/and/folders"

Diff

	all changes since the last commit
	  o git diff HEAD -- "/selected/paths/files/or/and/folders"
	changes that have not been staged
	  o git diff  -- "/selected/paths/files/or/and/folders"
	changes that are staged but not committed
	  o git diff --staged -- "/selected/paths/files/or/and/folders"
	between the index and last commit
	  o git diff --cached -- "/selected/paths/files/or/and/folders"
	between remote and last local commit (origin/master..)
	  o git diff origin/master.. -- "/selected/paths/files/or/and/folders"
	between last local commit and remote (..origin/master)
	  o git diff ..origin/master -- "/selected/paths/files/or/and/folders"
	between the two latest tags
	  o git diff "previousTag".."lastTag" -- "/selected/paths/files/or/and/folders"

Log stat last 30
  o git log -n 30 --stat --graph -- "/selected/paths/files/or/and/folders"

	Log stat full
	  o git log --stat --graph -- "/selected/paths/files/or/and/folders"
	Log extended last 30
	  o git log -n 30 -p -- "/selected/paths/files/or/and/folders"
	Log extended full
	  o git log -p -- "/selected/paths/files/or/and/folders"
	Log since last tag
	  o git log "lastTag"... --stat --graph --  "/selected/paths/files/or/and/folders"
	Log since last push
	  o git log origin/master... --stat --graph -- "/selected/paths/files/or/and/folders"
	Log between the two latest tags
	  o git log "prevToLastTag".."lastTag" --stat --graph -- "/selected/paths/files/or/and/folders"

Blame
  o git blame -- "/selected/paths/files/NOT/folders"

Auto-Tag
  o git tag "YYMMDD.Version"

	Tag Add
	  o git tag "promptMessage"
	Tag Remove
	  o git tag -d "promptMessage"
	Tag List
	  o git tag -l

Revert Discard changes to tracked
  o git checkout HEAD -- "/selected/paths/files/or/and/folders"

	Revert Discard changes to tracked, clean untracked
	  o git checkout HEAD -- "/selected/paths/files/or/and/folders"
	  o git clean -f -d -- "/selected/paths/files/or/and/folders"
	Revert Discard changes to tracked, clean untracked, unstage
	  o git checkout HEAD -- "/selected/paths/files/or/and/folders"
	  o git clean -f -d -- "/selected/paths/files/or/and/folders"
	  o git reset HEAD -- "/selected/paths/files/or/and/folders"
	Revert Discard changes to tracked, unstage, clean untracked
	  o git checkout HEAD -- "/selected/paths/files/or/and/folders"
	  o git reset HEAD -- "/selected/paths/files/or/and/folders"
	  o git clean -f -d -- "/selected/paths/files/or/and/folders"
	Revert Unstage
	  o git reset HEAD -- "/selected/paths/files/or/and/folders"

Checkout to
  o git checkout promptMessage -- "/selected/paths/files/or/and/folders"
Checkout repo to
  o cd repoPath
  o git checkout promptMessage

Push
  o git push

	Push, Push Tags
	  o git push && git push --tags
	Push Tags
	  o git push --tags
	Push with options…
	  o promptMessage

	Pull
	  o git pull
	Pull with options…
	  o promptMessage

	Fetch
	  o git fetch
	Fetch with options…
	  o promptMessage

	Remote add
	  o git remote add promptMessage
	Configure default remote
	  o git config branch.promptBranch.remote promptRemoteName

Clone
  o git clone promptMessage
Init
  o git init

Add
  o git add -- "/selected/paths/files/or/and/folders"
Remove
  o git rm -r -f -- "/selected/paths/files/or/and/folders"
Remove Keep Local
  o git rm -r --cached -- "/selected/paths/files/or/and/folders"

Open Git Ignore
Add to Git Ignore

Git GUI
Gitk
Liberal Git Command
</pre>

Installation
------------------

 * Install this repository via "Package Control" http://wbond.net/sublime_packages/package_control

Todo
------------------

 * Tag commands not yet ported

Source-code
------------------

https://github.com/SublimeText/SideBarGit

Forum Thread
------------------

http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3405

Contribute
------------------

[Consider make a contribution](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=extensiondevelopment%40gmail%2ecom&lc=UY&item_name=Tito&item_number=sublime%2dtext%2dside%2dbar%2dplugin&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted )