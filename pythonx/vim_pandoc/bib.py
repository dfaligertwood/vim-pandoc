import vim
import re
import os
import os.path
import operator
from glob import glob
import json
import subprocess as sp

def find_bibfiles():

    try:
        local_bib_extensions = vim.vars["pandoc#biblio#bib_extensions"]
    except:
        local_bib_extensions = []

    bib_extensions = ["bib",
                      "bibtex",
                      "ris",
                      "json", 
                      "enl", 
                      "wos", 
                      "medline", 
                      "copac", 
                      "xml"]

    search_methods = {"b": b_search(),
                      "c": c_search(),
                      "l": l_search(),
                      "t": t_search(),
                      "g": g_search()}

    sources = vim.vars["pandoc#biblio#sources"]
    
    def b_search():
        # Search for bibiographies with the same name as the current file in the
        # current dir.

        if vim.current.buffer.name in (None, ""): return []

        file_name = os.path.splitext(vim.current.buffer.name)[0]
        search_paths = [file_name + "." + f for f in local_bib_extensions]

        bibfiles = [os.path.abspath(f) for f in search_paths if os.path.exists(f)]
        return bibfiles

    def c_search():
        # Search for any other bibliographies in the current dir. N.B. this does
        # not currently stop bibliographies picked up in b_search() from being found.
        # Is this an issue?

        relative_bibfiles = [glob("*." + f) for f in local_bib_extensions]
        bibfiles = [os.path.abspath(f) for f in relative_bibfiles]
        return bibfiles

    def l_search():
        # Search for bibliographies in the pandoc data dirs.

        if os.path.exists(os.path.expandvars("$HOME/.pandoc/")):
            b = os.path.expandvars("$HOME/.pandoc/")
        elif os.path.exists(os.path.expandvars("%APPDATA%/pandoc/")):
            b = os.path.expandvars("%APPDATA%/pandoc/")
        else:
            return []
        
        search_paths = [b + "default." + f for f in bib_extensions]
        bibfiles = [os.path.abspath(f) for f in search_paths if os.path.exists(f)]
        return bibfiles

    def t_search():
        # Search for bibliographies in the texmf data dirs.

        if vim.eval("executable('kpsewhich')") == '0': return []

        texmf = sp.Popen(["kpsewhich", "-var-value", "TEXMFHOME"], stdout=sp.PIPE, stderr=sp.PIPE).\
                communicate()[0].strip()
        
        if os.path.exists(texmf):
            search_paths = [texmf + "/*." + f for f in bib_extensions]
            relative_bibfiles = [glob(f) for f in search_paths]
            bibfiles = [os.path.abspath(f) for f in relative_bibfiles]
            return bibfiles

        return []

    def g_search():
        # Search for bibliographies in the directories defined in pandoc#biblio#bibs

        return [f for f in vim.vars["pandoc#biblio#bibs"]]

    bibfiles = []
    for f in sources:
        bibfiles.extend(search_methods.get(f))

    return bibfiles



def bibliography_to_json(bibliography):
    # Calls pandoc-citeproc to convert a bibliography to JSON.
    #
    # Expects bibliography to be a file path.
    #
    # Returns an Array of CSL formatted Dicts, corresponding to bibliography
    # entries.
    # If this does not work, returns empty Array. Should probably raise an error
    # something. Will let someone who understands this better deal with that....

    # Also probably needs to be rewritten so this parsing occurs at file load time,
    # and the bibliography is stored elsewhere. Not sure how best to do this offhand.

    # Additional query: If we are to support YAML frontmatter, perhaps change this to import yaml?

    command = ["pandoc-citeproc", "-j", bibliography]

    try:
        raw_bib = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE).communicate()[0]
        bibliography = json.loads(raw_bib)
    except:
        bibliography = []

    return bibliography

def csl_variable_parse(entry, variable_name):

    def plain(variable_contents):
        # Currently a placeholder. Will parse 'plain' CSL variables and return an array of
        # strings for matching.
        return variable_contents

    def number(variable_contents):
        # Returns plain. Exists in case we decide to treat number variables seperately in
        # future.
        return plain(variable_contents)

    def name(variable_contents):
        # Currently a placeholder. Will parse 'name' CSL variables and return an array of
        # strings for matching.
        if not variable_contents: return []

    def date(variable_contents):
        # Currently a placeholder. Will parse 'date' CSL variables and return an array of
        # strings for matching.
        False

    variable_type = {
            "abstract": plain,
            "annote": plain,
            "archive": plain,
            "archive_location": plain,
            "archive-place": plain,
            "authority": plain,
            "call-number": plain,
            "citation-label": plain,
            "citation-number": plain,
            "collection-title": plain,
            "container-title": plain,
            "container-title-short": plain,
            "dimensions": plain,
            "doi": plain,
            "event": plain,
            "event-place": plain,
            "first-reference-note-number": plain,
            "genre": plain,
            "isbn": plain,
            "issn": plain,
            "jurisdiction": plain,
            "keyword": plain,
            "locator": plain,
            "medium": plain,
            "note": plain,
            "original-publisher": plain,
            "original-publisher-place": plain,
            "original-title": plain,
            "page": plain,
            "page-first": plain,
            "pmcid": plain,
            "pmid": plain,
            "publisher": plain,
            "publisher-place": plain,
            "references": plain,
            "reviewed-title": plain,
            "scale": plain,
            "section": plain,
            "source": plain,
            "status": plain,
            "title": plain,
            "title-short": plain,
            "url": plain,
            "version": plain,
            "year-suffix": plain,

            "chapter-number": number,
            "collection-number": number,
            "edition": number,
            "issue": number,
            "number": number,
            "number-of-pages": number,
            "number-of-volumes": number,
            "volume": number,

            "accessed": date,
            "container": date,
            "event-date": date,
            "issued": date,
            "original-date": date,
            "submitted": date,

            "author": name,
            "collection-editor": name,
            "composer": name,
            "container-author": name,
            "director": name,
            "editor": name,
            "editorial-director": name,
            "illustrator": name,
            "interviewer": name,
            "original-author": name,
            "recipient": name,
            "reviewed-author": name,
            "translator": name,
            }

    return variable_type[variable_name](entry.get(variable_name, False))


def match(entry, query):
    # Matching engine. Basic 'fuzzy' match: break query into strings based on spaces &c.
    # Then compare with chosen matching variables. If a match is found, return true.
    # Maybe have matching variables configurable?

    # Expects entry to be CSL-formatted dict. Query to be a string.

    False

def get_bibliography_suggestions(bibliography_path, query):
    bibliography = bibliography_to_json(bibliography_path)
    suggestions = [entry_to_completion(entry) for entry in bibliography if match(entry, query)]
    return suggestions

def entry_to_completion(entry):
    False

def get_suggestions():
    bibs = vim.eval("b:pandoc_biblio_bibs")
    if len(bibs) < 1:
        bibs = find_bibfiles()
    query = vim.eval("a:partkey")

    for bib in bibs:
        matches.extend(get_bibliography_suggestions(bib, query))

    if len(matches) > 0:
        matches = sorted(matches, key=operator.itemgetter("word"))

    return matches
