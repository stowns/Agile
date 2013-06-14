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
    STORY_PATH = sublime.packages_path() + '/StoryManager/stories'

    def run(self):
        self.story_names = []
        self.story_paths = []
        # get stories
        stories = os.listdir(self.STORY_PATH)
        for story in stories:
            if not story.startswith('.'): # ignore . system files (.DS_Store)
                with open(self.STORY_PATH + '/' + story, 'rb') as story_file:
                    story_json = json.load(story_file)

                    self.story_paths.append(self.STORY_PATH + '/' + story)
                    self.story_names.append(story_json['title']) # the name given by the user is the first entry in the csv, thats all we need to display in the dropdown
        
        self.window.show_quick_panel(self.story_names, self.story_selected) 

    def story_selected(self, index):
        if index != -1:
            self.story_path = self.story_paths[index]
            current_views = self.window.views
            url = 'https://iseatz.jira.com/browse/' + str(self.story_names[index]).strip('[]').strip("'")
            open_url(url)
            
            with open(self.story_path, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                reader.next() #throw away the first line (name)
                for row in reader:
                    self.window.open_file(row[0])