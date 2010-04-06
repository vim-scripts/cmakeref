#!/usr/bin/env python
# vim:set fileencoding=utf-8 sw=4 ts=8 et:vim
# Author:  Marko Mahnič
# Created: apr 2010 
# License: GPL (http://www.gnu.org/copyleft/gpl.html)
# This program comes with ABSOLUTELY NO WARRANTY.

import subprocess as subp
import re

parts = ['cmake-commands', 'cmake-modules', 'cmake-properties', 'cmake-variables']
copyright = ""

def partList(curpart):
    lst = []
    if curpart.strip() != "": lst.append(curpart)
    for p in parts:
        if p != curpart:
            lst.append(p)
    return lst

def tocLinks(curpart):
    lst = partList(curpart)
    lst = [ '|%s|' % p for p in lst]
    return "  ".join(lst)

def capshell(cmd):
    acmd = []
    quote = 0
    for p in cmd.split():
        if not quote:
            if p.startswith('"') and not p.endswith('"'): quote = 1
            acmd.append(p)
        else:
            acmd[-1] = acmd[-1] + " " + p
            if p.endswith('"'): quote = 0

    acmd = [ p.strip('"') for p in acmd ]

    p = subp.Popen(acmd, stdout=subp.PIPE)
    cap = p.communicate()
    return cap[0].split("\n")

def unique(items):
    items.sort()
    pitem = ""
    uitems = []
    for i in items:
        if i == pitem: continue
        uitems.append(i)
        pitem = i

    return uitems


def dump(index, preamble, indextag, filename):
    global copyright
    f = open(filename, 'w')
    # preamble
    for line in preamble:
        f.write(line); f.write("\n")
    f.write("\n" * 2)

    # index
    f.write("%s %s\n\n" %   ('CMake', tocLinks('')))
    f.write("%-30s *%s*\n" % ("INDEX", indextag))
    f.write("\n" * 1)
    for entry in index:
        f.write("    %*s %s\n" % (-30, "|%s|" % entry[0], entry[1]))

    # text
    for entry in index:
        f.write("\n" * 2)
        for line in entry[2]:
            f.write(line); f.write("\n")

    f.write("\n%s\n" % ("-" * len(copyright[0])))
    for line in copyright:
        f.write(line); f.write("\n")
    f.write("\n\n## vim:ft=help:isk=!-~,^*,^\\|,^\\\":ts=8\n")

def unindent(text):
    minindent = 999
    for line in text:
        if line.strip() == "": continue
        indent = len(line) - len(line.lstrip())
        if indent < minindent: minindent = indent

    if minindent > 0:
        text = [line[minindent:] for line in text]

    return text

def cleanup(text):
    while len(text) > 2 and text[-1].strip() == "": text = text[:-1]
    pline = ""
    newtext = []
    for line in text:
        if line.strip() == "" and pline == "": continue
        newtext.append(line)
        pline = line.strip()
    return newtext

def processCopyright():
    global copyright
    text = capshell('cmake --copyright')
    copyright = text[:3]
    text[0] = "%-40s%s" % (text[0], "*cmake-copyright*")
    copyright[0] = "%-40s%s" % (copyright[0], "|cmake-copyright|")
    f = open("cmakecopyright.txt", "w")
    for line in text:
        f.write(line)
        f.write("\n")
    f.close()

def processCommands():
    part = 'cmake-commands'
    commands = capshell('cmake --help-command-list')
    index = []
    for cmd in commands:
        cmd = cmd.strip()
        if cmd.startswith("cmake version"): continue
        if cmd == "": continue
        text = capshell('cmake --help-command ' + cmd)
        text = cleanup(text)
        if len(text) < 2: continue
        if text[0].startswith("cmake version"): text = text[1:]
        text = unindent(text)
        text[0] = "%-40s *%s*" % (text[0].rstrip(), cmd)
        #if cmd == "find_package":
        #    text.insert(2, "%*sList of packages   |cmake-pindex|" % (7, ""))

        text.append("")
        text.append("    " +tocLinks(part))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    dump(index, ["CMake Commands"], part, "cmakecmds.txt")

def processModules():
    part = 'cmake-modules'
    modules  = capshell('cmake --help-module-list')
    index = []
    for cmd in modules:
        cmd = cmd.strip()
        if cmd.startswith("cmake version"): continue
        if cmd == "": continue
        text = capshell('cmake --help-module ' + cmd)
        text = cleanup(text)
        if len(text) < 2: continue
        if text[0].startswith("cmake version"): text = text[1:]
        text = unindent(text)
        if cmd.startswith("Find"): extra = " *%s*" % cmd[4:]
        else: extra = ""
        text[0] = "%-40s *%s*%s" % (text[0].rstrip(), cmd, extra)

        text.append("")
        if cmd.startswith("Find"):
            text.append("%*sSee also |find_package|" % (5, ""))
        text.append("    " + tocLinks(part))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    dump(index, ["CMake Modules"], part, "cmakemods.txt")

def processProperties():
    part = 'cmake-properties'
    modules  = unique(capshell('cmake --help-property-list'))
    index = []
    for cmd in modules:
        cmd = cmd.strip()
        if cmd.startswith("cmake version"): continue
        if cmd == "": continue
        text = capshell('cmake --help-property ' + cmd)
        text = cleanup(text)
        if len(text) < 2: continue
        if text[0].startswith("cmake version"): text = text[1:]
        text = unindent(text)

        text[0] = "%-40s *%s*" % (text[0].rstrip(), cmd)

        text.append("")
        text.append("    " + tocLinks(part))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    dump(index, ["CMake Properties"], part, "cmakeprops.txt")

def processVariables():
    part = 'cmake-variables'
    modules  = unique(capshell('cmake --help-variable-list'))
    index = []
    for cmd in modules:
        cmd = cmd.strip()
        if cmd.startswith("cmake version"): continue
        if cmd == "": continue
        text = capshell('cmake --help-variable "' + cmd + '"')
        text = cleanup(text)
        if len(text) < 2: continue
        if text[0].startswith("cmake version"): text = text[1:]
        text = unindent(text)

        if cmd.find("[") >= 0:
            cmd = cmd.replace("[", "<").replace("]", ">").replace(" ", "_")
            text[0] = text[0].replace("[", "<").replace("]", ">").replace(" ", "_")
        extra = ""
        if cmd.startswith("CMAKE_<LANG>"): extra += " *%s*" % cmd[12:]
        text[0] = "%-40s *%s*%s" % (text[0].rstrip(), cmd, extra)

        text.append("")
        text.append("    " + tocLinks(part))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    dump(index, ["CMake Variables"], part, "cmakevars.txt")

def run():
    processCopyright()
    processCommands()
    processModules()
    processProperties()
    processVariables()

run()
