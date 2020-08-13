current=[]
import os

def bar(n):
    global current
    new=[c+1 for c in range(n)]
    if len(current)>len(new):
        for i in range(len(new)):
            print('{0} updated with content from {1}'.format(current[i], new[i]))

        for i in range(len(current)-len(new)):
            print('{0} unpinned'.format(current[len(new)+i]))

    if len(current)<len(new):
        for i in range(len(current)):
            print('{0} updated with content from {1}'.format(current[i], new[i]))
        for i in range(len(new)-len(current)):
            print('{0} created and pinned'.format(new[len(current)+i]))

    if len(current)==len(new):
        for i in range(len(new)):
            print('{0} updated with content from {1}'.format(current[i], new[i]))

    current=new
    return

script_path=os.path.dirname(os.path.abspath(__file__))
