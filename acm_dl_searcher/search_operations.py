from fuzzysearch import find_near_matches


class GenericSearchFunction:
    """A generic search function which returns if there is a fuzzy search match"""
    def __init__(self, pattern, max_l_dist=2):
        self.pattern = pattern
        self.max_l_dist = max_l_dist

    def __call__(self, content):
        return _generic_fuzzy_filter(content, self.pattern, self.max_l_dist)


class GenericVenueFilter:
    """ If any of short_name, title or doi matches a given input, the callable will return true"""
    def __init__(self, short_name_filter, title_filter, doi_filter):
        self.short_name_filter = short_name_filter
        self.title_filter = title_filter
        self.doi_filter = doi_filter
        
        if short_name_filter is None and title_filter is None and doi_filter is None:
            self._all_none = True
        else:
            self._all_none = False
            
    def  __call__(self, short_name, title, doi):
        if self._all_none:
            return True
        elif self.short_name_filter is not None and _generic_fuzzy_filter(short_name, self.short_name_filter, 0):
            return True
        elif self.title_filter is not None and _generic_fuzzy_filter(title, self.title_filter, 0):
            return True
        elif self.doi_filter is not None and _generic_fuzzy_filter(doi, self.doi_filter, 0):
            return True
        return False


def _generic_fuzzy_filter(string, pattern, max_l_dist=2):
    return len (find_near_matches(pattern, string, max_l_dist=max_l_dist)) > 0
    
