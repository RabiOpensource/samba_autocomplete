#!/bin/python3

import sys
from lxml import etree
from autocompletehelper import *


#               Creating Function of subcommand                                 #
def makeSubCmdList(arg, cmdInfo):
    if (arg.text.find('|') > 0):
        command = arg.text.split('|')
        for cmd in command:
            if ((cmd.find('--') >= 0) and (cmd.find('=') > 0)):
                cmdInfo["argStr"] = cmdInfo["argStr"] + ' ' + cmd[:cmd.find('=') + 1]
    else:
        if ((arg.text.find('--') > 0) or (arg.text.find('=') > 0)):
            cmdInfo["argStr"] = cmdInfo["argStr"] + ' ' + arg.text[:arg.text.find('=') + 1]

def createFunctionName(command, fName):
    if (fName.find('--') >= 0):
        fName = (fName.split('--')[1])
    if (fName.find('=') >= 0):
        fName = ((fName.split('='))[0])
    fName = fName.replace("-","")
    str =  '_comp_cmd_' + command + '_' + fName
    return str

def findCommandName(arg):
    subcmd = None
    if (arg.text.find('|') > 0):
        command = arg.text.split('|')
        for cmd in command:
            if ((cmd.find('--') >= 0) and (cmd.find('=') > 0)):
                subcmd = cmd.split('=')[0]
    else:
        if (arg.text.find('=') > 0):
            subcmd = arg.text.split('=')[0]
    return subcmd
    
def createFunction(command, fName):
    fName = fName.replace("-","")
    getFName = f"get_{fName}"
    try:
        getFunctionData = globals()[getFName]
        fdData = getFunctionData()
        if (fdData == None):
            return None
        else:
            fDefination =  '_comp_cmd_' + command + '_' + fName + '() \n{ \n'
            fDefination = fDefination + "   " + getFunctionData()
            fDefination = fDefination + '}\n'
            return fDefination
    except KeyError:
        return None

def findRootAndTree(cmdInfo):
    if (cmdInfo is not None):
        cmdInfo["tree"] = etree.parse(cmdInfo["xmlFile"])
        cmdInfo["root"] = cmdInfo["tree"].getroot()


#               Parsing XML data                                                #
def usage():
    print( sys.argv[0] + " --output <output directory> <manpages/smbcommand.xml> ")
    sys.exit(1)

def deInitAutoComplete(cmdInfo):
    cmdInfo.clear()

def initAutoComplete():
    cmdInfo = {}
    if len(sys.argv) != 4:
        usage()
    if ((sys.argv[1] == "--output") and (sys.argv[3] != None)):
        cmdInfo["outputdir"] = sys.argv[2]
        cmdInfo["xmlFile"] = sys.argv[3]
        cmdInfo["option"] = "--output"
        cmdInfo["argStr"] = ""
        cmdInfo["functionStr"] = ""
        cmdInfo["subNoArgCommands"] = []
        cmdInfo["subcommands"] = []
        cmdInfo["autoCompletionCode"] = ""
        cmdInfo["command"] = ""
        return cmdInfo
    else:
        usage()
        
def findListofSubCommandFromXml(cmdInfo):
    for refsynopsisdiv in cmdInfo["root"].xpath('//refsynopsisdiv'):
        cmdsynopsis = refsynopsisdiv.find('cmdsynopsis')
        cmdInfo["command"] = cmdsynopsis.find('literal').text
        args = cmdsynopsis.findall('arg')

        for arg in args:
            if 'choice' in arg.attrib:
                makeSubCmdList(arg, cmdInfo)
                subcmd = findCommandName(arg)
                if (subcmd == None):
                    continue

                fName = subcmd.split('--')[1]
                fData = createFunction(cmdInfo["command"], fName)
                if (fData == None): 
                    cmdInfo["subNoArgCommands"].append(subcmd)
                else:
                    cmdInfo["subcommands"].append(subcmd)
                    cmdInfo["functionStr"] = cmdInfo["functionStr"] + fData


#               Building auto complete script           
def buildAutoCompleteScript(cmdInfo):
    cmdInfo["autoCompletionCode"] += f'_comp_cmd_{cmdInfo["command"]}() \n{{\n'
    cmdInfo["autoCompletionCode"] += f'    local cur prev words cword was_split comp_args\n'

    cmdInfo["autoCompletionCode"] += f'    _comp_initialize -s -- "$@" || return \n'
    cmdInfo["autoCompletionCode"] += f'    case $prev in\n'

    for subcmd in cmdInfo["subcommands"]:
        functionData = createFunctionName(cmdInfo["command"], subcmd)
        cmdInfo["autoCompletionCode"] += f'        {subcmd})\n'
        cmdInfo["autoCompletionCode"] += f'            {functionData}\n'
        cmdInfo["autoCompletionCode"] += f'            return\n'
        cmdInfo["autoCompletionCode"] += f'            ;;\n'

    cmdInfo["autoCompletionCode"] += f'        '
    for noargcmd in cmdInfo["subNoArgCommands"]:
        cmdInfo["autoCompletionCode"] += f'{noargcmd}'
        if (noargcmd != cmdInfo["subNoArgCommands"][-1]):
            cmdInfo["autoCompletionCode"] += f' | '

    if cmdInfo["subNoArgCommands"]:
        cmdInfo["autoCompletionCode"] += f' )\n'
        cmdInfo["autoCompletionCode"] += f'            return\n'
        cmdInfo["autoCompletionCode"] += f'            ;;\n\n'

    cmdInfo["autoCompletionCode"] += f'    esac\n'
    cmdInfo["autoCompletionCode"] += f'    [[ $was_split ]] && return \n\n'

    cmdInfo["autoCompletionCode"] += f'     if [[ $cur == -* ]]; then \n'
    cmdInfo["autoCompletionCode"] += f'        _comp_compgen_help\n'
    cmdInfo["autoCompletionCode"] += "        [[ ${COMPREPLY-} == *= ]] && compopt -o nospace\n"
    cmdInfo["autoCompletionCode"] += f'    fi\n\n'

    cmdInfo["autoCompletionCode"] += f'}}&& \n'
    cmdInfo["autoCompletionCode"] += f'  complete -F _comp_cmd_{cmdInfo["command"]} {cmdInfo["command"]}'

def writeAutoCompletionCodeToFile(cmdInfo):
    autoCompletionFile = f'{cmdInfo["outputdir"]}'
    with open(autoCompletionFile, 'w') as f:
        f.write(cmdInfo["functionStr"])
        f.write(cmdInfo["autoCompletionCode"])


def main():
    cmdInfo = initAutoComplete() 
    findRootAndTree(cmdInfo)
    findListofSubCommandFromXml(cmdInfo)
    buildAutoCompleteScript(cmdInfo)  
    writeAutoCompletionCodeToFile(cmdInfo)
    deInitAutoComplete(cmdInfo)

if __name__ == "__main__":
    main()
