#!/bin/python3

from lxml import etree
import os


tree = etree.parse('docs-xml/manpages/smb.conf.5.xml')
root = tree.getroot()

def pathSplit(path):
    dirlist = path.split('/')
    return dirlist

############### common command #################
def get_debuglevel():
    return "_comp_compgen -- -W \'{0..10}\'\n"

def get_directory():
    return "_comp_compgen_filedir -d \n"

def get_configfile():
    return get_directory()

def get_logbasename():
    return get_directory()

def get_OptionArgCommands():
    return ""

def get_list():
    #rabi check this function it should return something from smbtree
    return None

def get_nameresolve():
    #you need to read smb.conf file to update data
    return None


def get_netbiosname():
    return None

def get_netbiosscope():
    return None

def get_workgroup():
    #rabi you need to retrive data from smbtree
    return None

def get_realm():
    return None

def get_chown():
    return None

def get_chgrp():
    return None

def get_inherit():
    return None

def get_save():
    return None

def get_restore():
    return None

def get_querysecurityinfo():
    return None

def get_authenticationfile():
    return get_directory()

def get_usekerberos():
    return "_comp_compgen -- -W 'desired required off'\n"

def get_simplebinddn():
    return None

def get_usekrb5ccache():
    return None

def get_clientprotection():
    return "_comp_compgen -- -W 'sign encrypt off'\n"



def getSigningOption():
    return "_comp_compgen -- -W 'on off required'\n"

def getHost():
    return None


def getSectionfromAnchor(anchorAttrib):
    if (root == '' or root == None):
        parseSmbConf()
    sectionLists = root.xpath('//section')
    for section in sectionLists:
        if ((section == None) or (section == '')):
            continue
        anchorList = section.xpath('./anchor')
        for anchor in anchorList:
            if (anchor.attrib['id'] == anchorAttrib):
                return section

def getValListFromSectionPath(section, path, listItemsPath):
    pathList = section.xpath(path)
    optionStr = ""
    for plist in pathList:
        if (plist == None):
            continue
        itemList = plist.xpath(listItemsPath)
        for item in itemList:
            optionStr = optionStr + ' ' + item.text.split(' ')[0]
        break
    return optionStr
def get_socketoptions():
#you need to read smb.conf file to update data
    section = getSectionfromAnchor('SOCKETOPTIONS')
    sockOption = getValListFromSectionPath(section,'./variablelist/varlistentry/listitem/itemizedlist', './listitem/para')
    return f"_comp_compgen -- -W \'{sockOption}\' \n"
