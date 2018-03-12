import platform
import os
import subprocess
import inspect
import urllib
import base64

APPLICATIONS_PREFIX = "/applications/scripts"

NAME = L('Title')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SH = ICON
ICON_BAT = ICON

OS = platform.system()

scriptFileName = inspect.getframeinfo(inspect.currentframe()).filename
scriptsDirectory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(scriptFileName)))), "Scripts")

####################################################################################################

def Start():
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = "List"
    ObjectContainer.art = R(ART)

@handler(APPLICATIONS_PREFIX, NAME, thumb=ICON, art=ART)
@route(APPLICATIONS_PREFIX)
def ApplicationsMainMenu():
    scriptsMenuItems = ObjectContainer(view_group="InfoList")

    Log.Debug("Looking in " + scriptsDirectory + " for .bat or .sh files")
    for filename in os.listdir(scriptsDirectory):
        if filename.endswith(".bat") or filename.endswith(".sh"): 
            scriptsMenuItems.add(
                PopupDirectoryObject(
                    key=Callback(RunScript,scriptFile=filename),
                    title=filename,
                    thumb=R(ICON_SH if filename.endswith(".sh") else ICON_BAT if filename.endswith(".bat") else ICON),
                    art=R(ART)
                )
            )
    return scriptsMenuItems

@route(APPLICATIONS_PREFIX + "/runscript")
def RunScript(scriptFile=None):
    scriptFilePath = os.path.join(scriptsDirectory, scriptFile)
    Log.Debug("running " + scriptFilePath)
    try:
        p = subprocess.Popen([scriptFilePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = p.communicate()
        Log.Debug("finished running " + scriptFilePath + " with exit code: " + str(p.returncode))
        result = ObjectContainer(header="script", message="Exit Code: " + str(p.returncode) + "\r\nDo not navigate back or the script will run again!")
        result.add(
            DirectoryObject(
                key=Callback(BackToStartMessage),
                title="STDOUT:"
            )
        )
        for line in stderr.splitlines():
            if line != "":
                result.add(
                    DirectoryObject(
                        key=Callback(BackToStartMessage),
                        title=line
                    )
                )
        result.add(
            DirectoryObject(
                key=Callback(BackToStartMessage),
                title="STDERR:"
            )
        )
        for line in stdout.splitlines():
            if line != "":
                result.add(
                    DirectoryObject(
                        key=Callback(BackToStartMessage),
                        title=line
                    )
                )
    except Exception as ex:
        result = ObjectContainer(header="script", message="Error starting the script.")
        for line in str(ex).splitlines():
            result.add(
                DirectoryObject(
                    key=Callback(BackToStartMessage),
                    title=line
                )
            )

    return result

@route(APPLICATIONS_PREFIX + "/backtostartmessage")
def BackToStartMessage():
        return ObjectContainer(header="warning", message="Do not navigate back, or the script will run again!")