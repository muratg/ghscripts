import github
from auth import get_github
import sys
import csv


def monkey_patch_github_library():
    """ Monkey patching to enable Label descriptions """ 
    @property
    def my_description(self):
        self._completeIfNotSet(self._description)
        return self._description.value
    def my_edit(self, name, color, description):
        post_parameters = {
            "name": name,
            "color": color,
            "description": description,
        }
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH",
            self.url,
            input=post_parameters,
            headers={'Accept': 'application/vnd.github.symmetra-preview+json'}  ## required, since the api is still in beta
        )
        self._useAttributes(data)
    def my_initAttributes(self):
        self._initAttributes_orig()
        self._description = github.GithubObject.NotSet
    def my_useAttributes(self, attributes):
        self._useAttributes_orig(attributes)
        if "description" in attributes: 
            self._description = self._makeStringAttribute(attributes["description"])
    def my_create_label(self, name, color, description):
        post_parameters = {
            "name": name,
            "color": color,
            "description": description,
        }
        headers, data = self._requester.requestJsonAndCheck(
            "POST",
            self.url + "/labels",
            input=post_parameters,
            headers={'Accept': 'application/vnd.github.symmetra-preview+json'} 
        )
        return github.Label.Label(self._requester, headers, data, completed=True)

    github.Label.Label.description = my_description
    github.Label.Label.edit = my_edit
    github.Label.Label._initAttributes_orig = github.Label.Label._initAttributes
    github.Label.Label._initAttributes = my_initAttributes
    github.Label.Label._useAttributes_orig  = github.Label.Label._useAttributes
    github.Label.Label._useAttributes =  my_useAttributes
    github.Repository.Repository.create_label = my_create_label

def labelize(repos, label_names, label_descs, label_colors):
    
    G = get_github()
    
    for repo_name in repos:
        print(f"Processing '{repo_name}'...") 
        repo = G.get_repo(repo_name)

        for idx, label_name in enumerate(label_names):
            try:
                label = repo.get_label(label_name)
                print(f"  - Label '{label_name}':\tUpdating.")
                label.edit(label.name, label_colors[idx], label_descs[idx])
            except:
                print(f"  - Label '{label_name}':\tCreating. ")
                repo.create_label(label_name, label_colors[idx], label_descs[idx])


UPDATE='update'
COMMANDS = [UPDATE]

def main():
    monkey_patch_github_library()

    if len(sys.argv) == 1:
        usage()
    elif sys.argv[1] not in COMMANDS:
        print(f"Error: Unknown command '{sys.argv[1]}'\n")
        usage()

    ## update command
    elif sys.argv[1] == UPDATE:
        if len(sys.argv) != 4:
            print(f"Error. Too little, or too many parameters. Should be 4 instead of {len(sys.argv)} ")
            usage()
        else:
            with open(sys.argv[2]) as repos_f, open(sys.argv[3]) as labels_f:
                repos = repos_f.read().splitlines()
                labels = csv.reader(labels_f)
                labels = [[cell.strip() for cell in line] for line in labels]  # [name * description * color]
                labels = list(zip(*labels))  #     [name] * [description] * [color list]
 
                labelize(repos, labels[0], labels[1], labels[2])

def usage():
    print(f"""
  Usage: python labelize.py <command> <repofile> [<labelfile>]
  
  Commands:
    {UPDATE}: Updates given repos with the given labels 

  Sample repofile: 
    aspnet/signalr
    aspnet/kestrelhttpserver
    aspnet/iisintegration

  Sample labelfile:
    cost: 0,Will take no time. This is a tracking issue,#ffeeee
    cost: S,Will take up to 2 days to complete,#ffcccc
    cost: M,Will take from 3 - 5 days to complete,#ff9999
    cost: L,Will take from 6 - 10 days to complete,#ff5555
    cost: XL,Will take more than 10 days to complete,#ff0000
  """)

## entry point
if __name__ == '__main__':
    main()
