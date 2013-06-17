import sublime, sublime_plugin
import os
import json

def open_url(url):
    sublime.active_window().run_command('open_url', {"url": url})

def open_sprint_folders():
    SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'
    sprint_folders = []
    sprint_titles = []
    
    if not os.path.exists(SPRINTS_PATH):
        os.makedirs(SPRINTS_PATH)

    # get existing sprint folders
    sprint_folders = os.listdir(SPRINTS_PATH)
    # kill system files
    sprint_folders[:] = [x for x in sprint_folders if not x.startswith('.')]
    return sprint_folders, sprint_titles, SPRINTS_PATH

# prompt user with list of existing sprint titles to choose from
# give the story a title
# save story
class SaveStoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.sprint_folders, self.sprint_titles, sprints_path = open_sprint_folders()

        if len(self.sprint_folders) == 0:
            sublime.error_message('No Sprints currently exist. Please create one')
            return

        # read the metadata file from each directory to get sprint titles for displaying in the quick_panel
        for folder in self.sprint_folders:
            with open(sprints_path + folder + '/metadata.json', 'rb') as metadata_file:
                json_data = json.load(metadata_file)
                self.sprint_titles.append(json_data['title'])

        self.window.show_quick_panel(self.sprint_titles, self.sprint_selected)

    # hold reference to sprint folder
    # prompt user to give the story a title
    def sprint_selected(self, index):
        SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'

        w = self.window
        if index != -1:
            self.sprint_path = sublime.packages_path() + '/Agile/sprints/' + self.sprint_folders[index]
            'sprint path ' + self.sprint_path
            w.show_input_panel('Story Title: ', '', self.save_story, None, None)
      
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
    SPRINTS_PATH = sublime.packages_path() + '/Agile/sprints/'

    def run(self):
        w = self.window

        # get sprint folders,files
        self.sprint_folders, self.sprint_titles, sprints_path = open_sprint_folders()
       
        if len(self.sprint_folders) == 0:
            sublime.error_message('No Sprints currently exist. Please create one')
            return

        # read the metadata file from each directory to get sprint titles for displaying in the quick_panel
        for folder in self.sprint_folders:
            with open(sprints_path + folder + '/metadata.json', 'rb') as metadata_file:
                json_data = json.load(metadata_file)
                self.sprint_titles.append(json_data['title'])

        self.window.show_quick_panel(self.sprint_titles, self.sprint_selected)

    # hold reference to sprint folder
    # show stories in sprint
    def sprint_selected(self, index):
        w = self.window
        self.story_titles = []

        if index != -1:
            self.sprint_path = sublime.packages_path() + '/Agile/sprints/' + self.sprint_folders[index]

            # get all files from sprint folder
            all_paths = os.listdir(self.sprint_path)

            # kill system files
            # TODO: do this better
            all_paths[:] = [x for x in all_paths if not x.startswith('.')]
            all_paths[:] = [x for x in all_paths if not x.startswith('metadata.json')]
            self.story_paths = all_paths
            # read the metadata file from each directory to get sprint titles for displaying in the quick_panel
            for story_path in self.story_paths:
                with open(self.sprint_path + '/' + story_path, 'rb') as story_file:
                    json_data = json.load(story_file)
                    self.story_titles.append(json_data['title'])

            self.window.show_quick_panel(self.story_titles, self.story_selected)

    def story_selected(self, index):
        w = self.window
        if index != -1:
            self.story_path = self.story_paths[index]
            current_views = self.window.views
            #TODO: refactor this
            url = 'https://iseatz.jira.com/browse/' + str(self.story_titles[index]).strip('[]').strip("'")
            open_url(url)
            
            with open(self.sprint_path + '/' + self.story_path, 'rb') as json_file:
                json_data = json.load(json_file)
                print json_data
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
