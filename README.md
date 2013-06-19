Agile
======
ST2 allows users to create projects but offers no mechanism for saving a particular workspace with-in that project.  This can become a problem if you find yourself working on multiple stories involving dozens of files at once.  Agile allows you to save a window and associate its state with a Sprint and Story name that can then be retrieved at a later date.  That's about it.

Installation
----------
- Easy: via [Package Control](http://wbond.net/sublime_packages/package_control) 
- Super-hard: clone repo to your /Sublime Text 2/Packages directory

Basic Flow
----------
- shift+super+p -> 'Agile: Create New Sprint' -> save sprint
- ctrl+super+s -> save story
- ctrl+super+o -> select sprint -> select story

Shortcuts
----------
- ctrl+super+s - save story
- crtl+super+o - open story
- shift+super+p - all remaining commands available under 'Agile' prefix

### Jira Support
Agile can automatically open the jira ticket associated with your story if 2 criteria are met
- configure a root url via shift+super+p -> 'Agile: Configure Jira'
- You must name your jira story identically to its jira url slug.  ie) https://example.jira.com/browse/my-story would need to be saved as 'my-story'

### TODO:
- support for ST3
- error handling here and there