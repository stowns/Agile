import sublime, sublime_plugin
import os
import json

def open_url(url):
        sublime.active_window().run_command('open_url', {"url": url})

class SaveStoryCommand(sublime_plugin.WindowCommand):
    STORY_PATH = sublime.packages_path() + '/StoryManager/stories'

    def run(self):
        if not os.path.exists(self.STORY_PATH):
            os.makedirs(self.STORY_PATH)

        self.window.show_input_panel('Story Name: ', '', self.save_story, None, None)

    def save_story(self, story_title):
        filename = self.STORY_PATH + '/' + story_title + '.json'
        w = self.window
        with open(filename, 'wb') as json_file:
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


class OpenStoryCommand(sublime_plugin.WindowCommand):
    STORIES_PATH = sublime.packages_path() + '/StoryManager/stories'
    

    def run(self):
        self.story_names = []
        self.story_paths = []
        w = self.window

        # get story files
        stories_directory = os.listdir(self.STORIES_PATH)
        for file_path in stories_directory:
            if not file_path.startswith('.'): # ignore . system files (.DS_Store)
                with open(self.STORIES_PATH + '/' + file_path, 'rb') as story_file:
                    story_json = json.load(story_file)

                    self.story_paths.append(self.STORIES_PATH + '/' + file_path)
                    self.story_names.append(story_json['title'])  # used for the dropdown display name
        
        self.window.show_quick_panel(self.story_names, self.story_selected)

    def story_selected(self, index):
        w = self.window
        if index != -1:
            self.story_path = self.story_paths[index]
            current_views = self.window.views
            #TODO: refactor this
            url = 'https://iseatz.jira.com/browse/' + str(self.story_names[index]).strip('[]').strip("'")
            open_url(url)
            
            with open(self.story_path, 'rb') as json_file:
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


