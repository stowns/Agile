import sublime, sublime_plugin
import os, shutil, errno
import json


SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'
PREFS_PATH = sublime.packages_path() + '/Agile/preferences.json'

def open_url(url):
    sublime.active_window().run_command('open_url', {"url": url})

def init_prefs():
    with open(PREFS_PATH, 'wb') as json_file:
        prefs = { 'jira_root' : 'https://example.jira.com' }
        json.dump(prefs, json_file)

def load_prefs():
    ensure_path(PREFS_PATH)

    with open(PREFS_PATH, 'r+') as json_file:
        try:
            json_data = json.load(json_file)
            return json_data
        except ValueError as exc:
            #enters if there is no data in the file yet`
            init_prefs()
            load_prefs()

def ensure_path(path, is_folder=False):
    if not os.path.exists(path):
        if is_folder:
            os.makedirs(path)
        else:
            open(path, 'wb').close()

def open_sprint_folders(origin):
    SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'
    sprint_folders = []
    sprint_titles = []
    
    ensure_path(SPRINTS_PATH, True)

    # get existing sprint folders
    sprint_folders = os.listdir(SPRINTS_PATH)
    # kill system files
    sprint_folders[:] = [x for x in sprint_folders if not x.startswith('.')]

    if len(sprint_folders) == 0:
            sublime.error_message('No Sprints currently exist. Please create one')
            return

    # read the metadata file from each directory to get sprint titles for displaying in the quick_panel
    for folder in sprint_folders:
        with open(SPRINTS_PATH + folder + '/metadata.json', 'rb') as metadata_file:
            json_data = json.load(metadata_file)
            sprint_titles.append(json_data['title'])

    origin.window.show_quick_panel(sprint_titles, origin.sprint_selected)
    
    return sprint_folders

# hold reference to sprint folder
# show stories in sprint
def select_story(origin, sprint_path, index):
    story_titles = []

    if index != -1:
        # get all files from sprint folder
        story_paths = os.listdir(sprint_path)

        # filter out sprint metadata and system files
        # TODO: do this better
        story_paths[:] = [x for x in story_paths if not x.startswith('.')]
        story_paths[:] = [x for x in story_paths if not x.startswith('metadata.json')]
        
        # read the title from each story.json, stuff it into the story_titles for the dispay with a quick_panel
        for story_path in story_paths:
            with open(sprint_path + '/' + story_path, 'rb') as story_file:
                json_data = json.load(story_file)
                story_titles.append(json_data['title'])

        origin.window.show_quick_panel(story_titles, origin.story_selected)

        # return paths to reference by index after selection
        return story_titles, story_paths



# prompt user with list of existing sprint titles to choose from
# give the story a title
# save story
class SaveStoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.sprint_folders  = open_sprint_folders(self)

    # hold reference to sprint folder
    # prompt user to give the story a title
    def sprint_selected(self, index):
        self.sprint_path = SPRINTS_PATH + self.sprint_folders[index]
        self.window.show_input_panel('Story Title: ', '', self.save_story, None, None)
      
    def save_story(self, story_title):
        w = self.window

        # make the title safe to save as a file
        keepcharacters = (' ','.','_')
        story_path = self.sprint_path + '/' + "".join(c for c in story_title if c.isalnum() or c in keepcharacters).rstrip() + '.json'
        
        with open(story_path, 'wb') as json_file:
            data = { 'title' : story_title, 'groups' : [] }
            
            num_groups = w.num_groups()
            if num_groups > 0:
                for i in range(num_groups):
                    # iterate groups
                    w.run_command('focus_group', { 'group' : i }) # only way I know how to access the views of each group
                    # get views in the group we just focused to
                    views = w.views_in_group(w.active_group())
                    # store views in json
                    data['groups'].append([])
                    for view in views:
                        if (view.file_name() == None ): #skip empty tabs
                            continue
                        data['groups'][i].append(view.file_name())
            else:
                data['groups'][0] = []
                views = w.views()
                for view in views:
                    if (tab.file_name() == None ): #skip empty tabs
                        continue
                    data['groups'][0].append(view.file_name())
            # save the file
            json.dump(data, json_file)

# display sprint folders via quick panel
# display stories associated w/ a sprint
class OpenStoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.prefs = load_prefs()
        self.sprint_folders  = open_sprint_folders(self)

    def sprint_selected(self, index):
        self.sprint_path = SPRINTS_PATH + self.sprint_folders[index]
        self.story_titles, self.story_paths = select_story(self, self.sprint_path, index)

    # open the story json file
    # iterate the groups, if any
    # open the views
    def story_selected(self, index):
        w = self.window
        if index != -1:
            self.story_path = self.story_paths[index]
            if self.prefs['jira_root']:
                url = self.prefs['jira_root'] + '/browse/' + str(self.story_titles[index]).strip('[]').strip("'")
                print url
                open_url(url)
            
            with open(self.sprint_path + '/' + self.story_path, 'rb') as json_file:
                json_data = json.load(json_file)

                # create the view groups
                num_groups = len(json_data['groups'])
                if num_groups > 1:
                    self.set_layout(num_groups)
                    #iterate the groups
                    for i in range(num_groups):
                        w.run_command('focus_group', { 'group' : i })
                        #iterate and open the files in the group
                        for index, j in enumerate(json_data['groups'][i]):
                            view = self.window.open_file(j)
                            w.set_view_index(view, w.active_group(), index)
                else:
                    for index, i in enumerate(json_data['groups'][0]):
                        view = self.window.open_file(i)
                        w.set_view_index(view, w.active_group(), index)

    # redefined layouts for 2,3,4 columns
    def set_layout(self, num_columns):
        layouts = [{
                        "cols": [0.0, 0.5, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                    },
                    {
                        "cols": [0.0, 0.33, 0.66, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1]]
                    },
                    {
                        "cols": [0.0, 0.25, 0.5, 0.75, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1], [1, 0, 2, 1], [2, 0, 3, 1], [3, 0, 4, 1]]
                    }
                  ]
        self.window.run_command('set_layout', layouts[num_columns - 2])

# open sprint folders
class DeleteStoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.sprint_folders  = open_sprint_folders(self)

    def sprint_selected(self, index):
        self.sprint_path = SPRINTS_PATH + self.sprint_folders[index]
        self.story_titles, self.story_paths = select_story(self, self.sprint_path, index)

    def story_selected(self, index):
        if index != -1:
            self.story_path = self.story_paths[index]
            self.window.show_quick_panel(['nevermind', 'really delete this story'], self.you_sure_brah)

    def you_sure_brah(self, index):
        if index == 1:
            os.remove(self.sprint_path + '/' + self.story_path)
        else:
            return
            

# prompt user with input panel
# create sprint folder
# save metadata file with-in sprint folder
class CreateSprintCommand(sublime_plugin.WindowCommand):
    SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'

    def run(self):
        self.window.show_input_panel('Sprint Title: ', '', self.create_sprint, None, None)

    def create_sprint(self, sprint_title):
        # make the title safe to save as a directory
        keepcharacters = (' ','.','_')
        sprint_path = self.SPRINTS_PATH + "".join(c for c in sprint_title if c.isalnum() or c in keepcharacters).rstrip()
        
        try:
            os.mkdir(sprint_path)
            
            # save a metadata json file
            metadata_path = sprint_path + '/metadata.json'
            
            with open(metadata_path, 'wb') as metadata_file:
                data = { 'title' : sprint_title }
                json.dump(data, metadata_file)
        except OSError as exc: 
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                # TODO: show error
                pass

# open sprint folders
class DeleteSprintCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.sprint_folders  = open_sprint_folders(self)

    def sprint_selected(self, index):
        self.sprint_path = SPRINTS_PATH + self.sprint_folders[index]
        self.window.show_quick_panel(['nevermind', 'really delete this sprint'], self.you_sure_brah)

    def you_sure_brah(self, index):
        if index == 1:
            shutil.rmtree(self.sprint_path)
        else:
            return

class ConfigureJiraCommand(sublime_plugin.WindowCommand):

    def run(self):
      ensure_path(PREFS_PATH)
      json_data = load_prefs()
      self.window.show_input_panel('Enter Jira Root Url: ', json_data['jira_root'], self.jira_added, None, None)

    def jira_added(self, jira_root):        
        with open(PREFS_PATH, 'r+') as json_file:
            data = json.load(json_file)
            data['jira_root'] = jira_root
            json_file.seek(0)  # write to the start of the file
            json_file.write(json.dumps(data))
            json_file.truncate()  # remove the old stuff
