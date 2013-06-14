import sublime, sublime_plugin
import os
import csv

def open_url(url):
        sublime.active_window().run_command('open_url', {"url": url})

class SaveStoryCommand(sublime_plugin.WindowCommand):
    STORY_PATH = sublime.packages_path() + '/StoryManager/stories'

    def run(self):
        if not os.path.exists(self.STORY_PATH):
            os.makedirs(self.STORY_PATH)

        self.window.show_input_panel('Story Name: ', '', self.save_story, None, None)

    def save_story(self, story_title):
        tabs = self.window.views()
        filename = self.STORY_PATH + '/' + story_title + '.csv'

        with open(filename, 'wb') as csvfile:
            storywriter = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            storywriter.writerow([story_title])  # write the story title to csv
            for tab in tabs:    # write filepaths
                if (tab.file_name() == None ): #skip empty tabs
                    continue
                storywriter.writerow([tab.file_name()])

class OpenStoryCommand(sublime_plugin.WindowCommand):
    STORY_PATH = sublime.packages_path() + '/StoryManager/stories'

    def run(self):
        self.story_names = []
        self.story_paths = []

        # get stories
        stories = os.listdir(self.STORY_PATH)
        for story in stories:
            if not story.startswith('.'): # ignore . system files (.DS_Store)
                with open(self.STORY_PATH + '/' + story, 'rb') as csvfile:
                    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                    self.story_paths.append(self.STORY_PATH + '/' + story)
                    self.story_names.append(reader.next()) # the name given by the user is the first entry in the csv, thats all we need to display in the dropdown
        
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