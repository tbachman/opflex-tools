import re

METADATA_FILE='metadata.cpp'
CI_OPEN='ClassInfo\('
LIST_OF="list_of"

OPEN_PAREN="("
CLOSE_PAREN=")"
WS=' '
NL='\n'

# This is the regular expression that can be used to
# extract a string of items from the PropertyInfo object
PROPERTIES_RE='\(PropertyInfo\(([^\)]*).*'

# This is the regular expression that can be used to
# extract a string of items from the ClassInfo object
CLASS_RE='ClassInfo\((.*)'

class PropertyInfo:
    def __init__(self, propstring):
        '''Constructor passes in a string of properties.
           We have to figure out how many there are, strip
           out any whitespace, and put them into their
           appropriate fields'''
        proplist=[prop.strip() for prop in propstring.split(',')]
        if len(proplist) == 4:
            self.pid, self.name, self.type, self.cardinality = proplist
        elif len(proplist) == 5:
            self.pid, self.name, self.type, self.cid, self.cardinality = proplist
        else:
            # This case handles EnumInfo's. We can't split it because
            # it splits up the EnumInfo properties. Instead, we have
            # to parse it, knowing what an EnumInfo format looks like


class ClassInfo:
    self.properties=[]
    def __init__(self, class_string, prop_array):

        field_list=[field.strip() for field in class_string.split(',')]
        self.cid, self.ctype, self.name, self.owner = field_list[0:-1]

        for prop in prop_array:
            self.properties.append(PropertyInfo(prop))

def open_metadata(filename):
    '''Open the metadata file for reading'''
    return open(filename, "r");

def find_token(haystack, needle):
    '''Find the needle in the haystack'''
    count=0
    for hay in haystack:
        count = count + 1
        sl=hay.strip()
        if re.match(needle, sl):
            break
    if hay == haystack[-1]:
        return None
    return haystack[count-1:-1]

def match_parenthesis(ll, count, pos):
    '''Scan lines until a matching set of open/close parenthesis
       is found.  It retunns a tuple of the starting line and index
       where the outer open parenthesis was found and ending line
       and index where the outer close parenthesis was found.
       This requires there to be an open parenthesis on the 
       first line provided.'''
    paren_list=[]
    pos=ll[count].find(OPEN_PAREN, pos)
    # If no open parenthesis in first line, quit
    if pos == -1:
        return count
    paren_list.append((count,pos))
    pos = pos + 1
    startcnt, startpos, endcnt, endpos = 0,0,0,0
    while 1 == 1:
        popos=ll[count].find(OPEN_PAREN, pos)
        pcpos=ll[count].find(CLOSE_PAREN, pos)
        # If nothing more on this line, go
        # to the next one
        if popos == -1 and pcpos == -1:
            pos = 0
            count = count + 1
            continue
        # either both positive, or one is -1
        if popos < pcpos:
            if popos > 0:
                paren_list.append((count,popos))
                pos=popos+1
            else:
                startcnt, startpos = paren_list.pop()
                endcnt, endpos = count, pcpos
                pos=pcpos+1
        elif pcpos < popos:
            if pcpos > 0:
                startcnt, startpos = paren_list.pop()
                endcnt, endpos = count, pcpos
                pos=pcpos+1
            else:
                paren_list.append((count,popos))
                pos=popos+1
        # If empty stack, we're done
        if len(paren_list) == 0:
            return (startcnt, startpos, endcnt, endpos)

      

def get_properties(subset, prop_array):
    '''Get the properties associated with this class. Properties
       may span multiple lines'''
    count=0
    # This finds the first instance of a property
    while re.match(PROPERTIES_RE, subset[count].strip()):
        # Properties can span multiple lines (we see this
        # with enums). Collect lines into a single string
        # until we have a full property. We do this by 
        # matching the closing brace
        index=count
        pos=0
        fullstring=''
        startcnt, startpos, count, endpos = match_parenthesis(subset, index, pos)
        while index <= count:
            # The split is used to remove any single line comments
            # that  may appear at the end of the line, as those have
            # parenthesis too
            fullstring = fullstring + subset[index].split('//')[0]
            index = index + 1
        # Properties are grouped by parenthesis, and their members
        # are also grouped by parenthesis. Use the inner parenthesis
        # as the mechanism for getting the string of members
        #propstring=re.match(PROPERTIES_RE, fullstring.strip())
        pos = startpos + 1
        tmparray=[]
        tmparray.append(fullstring)
        a, startpos, b, endpos = match_parenthesis(tmparray, 0, pos)
        startpos = startpos + 1
        prop_array.append(fullstring[startpos:endpos].replace(WS, '').replace(NL,''))
        count = count + 1
    return subset[count:-1]

f=open_metadata(METADATA_FILE)
if f == None:
    print "Couldn't open " . METADATA_FILE
    exit

lines=f.readlines()
class_list=[]

# do this until we break out
while 1 == 1:
    # Find the beginning of a new ClassInfo
    lines=find_token(lines, CI_OPEN)
    if lines == None:
        break
    
    # Get the class fields string
    class_string=re.match(CLASS_RE, lines[0].strip()).group(1)

    # Start with a clean prop array
    prop_array=[]
    classlist=[prop.strip() for prop in class_string.split(',')]

    # Get the class properties

    # we know the next line is always a "list_of", so
    # skip it and get all the properties
    lines=get_properties(lines[2:-1], prop_array)

    # See if there are any keys associated with this class.
    # If there are, set the "is_key" field in the associated
    # property.
    if re.match(LIST_OF_RE, lines[1:-1]):
        

    # We have a new class -- create the object
    c=ClassInfo(class_string, prop_array)

    class_list.append(c)
