Agile
======

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
- refactor python code
- support for ST3?
- error handling here and there
- Package up for Package Control