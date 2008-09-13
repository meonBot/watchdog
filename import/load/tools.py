#!/usr/bin/env python
"""
common tools for load scripts
"""
import os
import re
import string
import unicodedata

import simplejson
import web

from settings import db

STATE_TABLE = 'load/manual/states.json'
DISTRICT_TABLE = 'load/manual/states.json'

_stripterms = ['the', 'corporation', 'corp', 'incorporated', 'inc']
r_plain = re.compile(r'[a-z ]+')
def stemcorpname(name):
    """
    >>> stemcorpname('The Boeing Corp.')
    'boeing'
    >>> stemcorpname('SAIC Inc.')
    'saic'
    """
    if not name: return name
    name = name.lower()
    name = ''.join(r_plain.findall(name))
    name = ' '.join(x for x in name.split() if x not in _stripterms)
    return name

_unfipscache = {}
def unfips(fipscode):
    if not _unfipscache:
        states = simplejson.load(file(STATE_TABLE))
        for stateid, state in states.iteritems():
            _unfipscache[state['fipscode']] = stateid
        
    return _unfipscache.get(fipscode)

def fixdist(dist):
    districts = simplejson.load(file(DISTRICT_TABLE))
    if dist.endswith('-01') and dist[:-1] + '0' in districts:
        return dist[:-1] + '0'
    else:
        return dist
    

_districtcache = {}
def districtp(district):
    """
    Return the watchdog ID for the represenative of `district`.
    """
    if not _districtcache:
        reps = simplejson.load(file('../data/load/politicians/index.json'))
        for repid, rep in reps.iteritems():
            if rep['district_id'] in _districtcache:
                _districtcache[rep['district_id']].append(repid)
            else:
                _districtcache[rep['district_id']] = [repid]
    
    return _districtcache.get(district) or []

def id_ify(text):
    """Take a string and convert it to a suitable watchdog id."""
    text = text.strip()
    # replace accented characters with non-accented ones
    text = unicodedata.normalize('NFKD',text).encode('ascii','ignore')
    P = set(string.punctuation)
    P.remove('_')
    # Remove punctuation (except '_') and replace spaces with '_' and lower case.
    text = ''.join(filter(lambda y: y not in P, text)).lower().replace(' ','_')
    return text

def getWatchdogID(district, lastname):
    # Filter out accented characters.
    #lastname = unicodedata.normalize('NFKD',lastname).encode('ascii','ignore')
    watchdog_ids = filter(lambda x: lastname.lower().replace(' ', '_') in x, districtp(district))
    if len(watchdog_ids) == 1:
        return watchdog_ids[0]
    return None


def fix_district_name(name):
    name=name.replace("-SEN1","").replace("-SEN2","").strip()
    if name in ['DC','GU','PR']:
        name += '-00'
    return name
    


_govtrackcache = {}
_opensecretscache = {}
def _fill():
    for pol in db.select('politician', what='id, govtrackid, opensecretsid'):
        _govtrackcache[pol.govtrackid] = str(pol.id)
        _opensecretscache[pol.opensecretsid] = str(pol.id)
        
def govtrackp(govtrack_id):
    """
    Return the watchdog ID for a person's `govtrack_id`.
    
        >>> govtrackp('400114')
        'michael_f._doyle'
        >>> print govtrackp('aosijdoisad') # ID we don't have
        None
    """
    if not _govtrackcache: _fill()
    return _govtrackcache.get(govtrack_id)

def opensecretsp(opensecrets_id):
    """
    Returns the watchdog ID for a person's `opensecrets_id`.
    """
    if not _opensecretscache: _fill()
    return _opensecretscache.get(opensecrets_id)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
