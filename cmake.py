#!/usr/bin/env python
# vim:set fileencoding=utf-8 sw=4 ts=8 et:vim
# Author:  Marko Mahnič
# Created: apr 2010 
# License: GPL (http://www.gnu.org/copyleft/gpl.html)
# This program comes with ABSOLUTELY NO WARRANTY. USE AT YOUR OWN RISK.

import subprocess as subp
import re

parts = ['cmake-commands', 'cmake-modules', 'cmake-properties', 'cmake-variables', 'cmake-policies']
copyright = ""

def partList(curpart):
    lst = []
    if curpart.strip() != "": lst.append(curpart)
    for p in parts:
        if p != curpart:
            lst.append(p)
    return lst

def tocLinks(curpart, lead, maxwidth=78):
    lst = partList(curpart)
    lst = [ '|%s|' % p for p in lst]
    line = lead
    lines = []
    for p in lst:
        if len(line) + 1 + len(p) < maxwidth:
            line = line + " " + p
        else:
            lines.append(line)
            line = lead + " " + p
    if len(line) > len(lead): lines.append(line)
    return lines

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
    links = tocLinks('', 'CMake ')
    for l in links: f.write("%s\n" % (l))
    f.write("\n")
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
    print part
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
        text.extend(tocLinks(part, "    "))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    return (index, ["CMake Commands"], part, "cmakecmds.txt")

def processModules():
    part = 'cmake-modules'
    print part
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
        text.extend(tocLinks(part, "    "))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    return (index, ["CMake Modules"], part, "cmakemods.txt")

def processProperties():
    part = 'cmake-properties'
    print part
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
        text.extend(tocLinks(part, "    "))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    return (index, ["CMake Properties"], part, "cmakeprops.txt")

def processVariables():
    part = 'cmake-variables'
    print part
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
        text.extend(tocLinks(part, "    "))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    return (index, ["CMake Variables"], part, "cmakevars.txt")

def processPolicies():
    part = 'cmake-policies'
    print part
    modules  = [ "CMP%04d" % d for d in xrange(20) ]
    index = []
    for cmd in modules:
        cmd = cmd.strip()
        if cmd.startswith("cmake version"): continue
        if cmd == "": continue
        text = capshell('cmake --help-policy "' + cmd + '"')
        text = cleanup(text)
        if len(text) < 3: continue
        if text[0].startswith("cmake version"): text = text[1:]
        text = unindent(text)

        text[0] = "%-40s *%s*" % (text[0].rstrip(), cmd)

        text.append("")
        text.extend(tocLinks(part, "    "))
        text.append("")
        # print "\n".join(text)
        idxentry = (cmd, text[1].strip(), text)
        index.append(idxentry)

    return (index, ["CMake Policies"], part, "cmakeplcs.txt")


def cmpSizeAlpha(a, b):
    if len(a) < len(b): return 1
    if len(a) > len(b): return -1
    if a < b: return -1
    if a > b: return 1
    return 0

def crossreference(parts):
    print "Cross-referencing"
    words = []
    for p in parts:
        for entry in p[0]:
            words.append(entry[0]) # part.index.cmd
    # print words
    ambwords = [w for w in words if re.search(r"[<_0-9]", w) == None] # no special chars
    keep = [ w for w in ambwords if re.match(r"^[A-Z]+$", w) != None] # all caps
    ambwords = [ w for w in ambwords if not w in keep ]
    keep = [ w for w in ambwords if re.match(r"[A-Z]+[a-z]+[A-Z]", w) != None] # camel case
    ambwords = [ w for w in ambwords if not w in keep ]
    keep = ['elseif', 'endforeach', 'endfunction', 'endif', 'endmacro', 'endwhile',
            'foreach', 'CPack', 'CTest', 'Dart', 'Findosg']
    ambwords = [ w for w in ambwords if not w in keep ]
    # What's left:
    # ['break', 'else', 'export', 'file', 'function', 'if', 'include', 'install',
    # 'list', 'macro', 'math', 'message', 'option', 'project', 'return', 'set',
    # 'string', 'unset', 'while', 'remove', 'subdirs', 'Documentation']
    print "These words won't be cross-referenced:"
    print ambwords

    words.sort(cmpSizeAlpha) # longest words first
    rew = [ re.escape(w) for w in words if not w in ambwords ]
    rx = re.compile(r"(^|[^*|'_a-zA-Z0-9<>])(" + ("|".join(rew)) + r")([^*|'_a-zA-Z0-9<>]|$)")

    count = 0
    for p in parts:
        for entry in p[0]:
            text = entry[2]
            for iln in range(1, len(text)):
                ln = text[iln]
                if ln.strip().startswith("Defined in"): continue
                (text[iln], n) = rx.subn(r'\1|\2|\3', text[iln])
                count += n
    print "Found", count, "cross-references"

def run():
    processCopyright()
    parts = []
    parts.append(processCommands())
    parts.append(processModules())
    parts.append(processProperties())
    parts.append(processVariables())
    parts.append(processPolicies())

    crossreference(parts)

    for p in parts: dump(*p)

run()
