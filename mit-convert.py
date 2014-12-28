#
# This isn't the prettiest python code, but it achieves
# what I need -- convert the metadata.cpp file output by
# the Genie code generator into a java file that creates
# the equivalent schema
import re

METADATA_FILE='metadata.cpp'
CI_OPEN='ClassInfo\('
LIST_OF="list_of"

OPEN_PAREN="("
CLOSE_PAREN=")"
WS=' '
NL='\n'
LIST_SEP=','
CSEP='::'
COMPOSITE_PROP='PropertyInfo::COMPOSITE'

# This is the regular expression that can be used to
# extract a string of items from the PropertyInfo object
PROPERTIES_RE='\(PropertyInfo\(([^\)]*).*'

# This is the regular expression that can be used to
# extract a string of items from the ClassInfo object
CLASS_RE='ClassInfo\((.*)'
PROPID_RE='\(([0-9]*)\)'

class PropertyInfo:
    def extract_tokens(self, enum_token):
        '''Get the EnumInfo tokens'''
        count = 0
        startpos = 0
        while 1 == 1:
            a,startpos,b,endpos=match_parenthesis(enum_token,count,startpos)
            if startpos == -1:
                break
            startpos += 1
            end_token = endpos + 1
            a,startpos,b,endpos=match_parenthesis(enum_token,count,startpos)
            startpos += 1
            self.token_array.append(enum_token[a][startpos:endpos])
            startpos = end_token
    def __init__(self, propstring):
        '''Constructor passes in a string of properties.
           We have to figure out how many there are, strip
           out any whitespace, and put them into their
           appropriate fields'''
        self.pid = ''
        self.cid = ''
        self.name = ''
        self.type = ''
        self.is_key = False
        self.cardinality = ''
        self.enum_name = ''
        self.token_array = []
        proplist=[prop.strip() for prop in propstring.split(LIST_SEP)]
        if len(proplist) == 4:
            self.pid, self.name, self.type, self.cardinality = proplist
        elif len(proplist) == 5:
            self.pid, self.name, self.type, self.cid, self.cardinality = proplist
        else:
            self.pid, self.name, self.type, self.cardinality = proplist[0:4]
            # This case handles EnumInfo's. We can't split it because
            # it splits up the EnumInfo properties. Instead, we have
            # to parse it, knowing what an EnumInfo format looks like
            pos = 0
            count = 0
            tmparray=[]
            tmparray.append(propstring)
            a,startpos,b,endpos=match_parenthesis(tmparray,count, pos)
            startpos += 1
            enum_token = propstring[startpos:endpos]
            # EnumInfo name is first item in remaining comma-sep list
            self.enum_name=enum_token.split(LIST_SEP)[0]
            enum_array=[]
            enum_array.append(enum_token)
            # Now get the enum tokens
            self.extract_tokens(enum_array)
        # remove the 'ul'
        self.pid = self.pid[0:-2]
    def set_key(self):
        self.is_key = True


class ClassInfo:
    def __init__(self, class_string, prop_array):
        '''Initialize the class, using the class info string
           and the list of properties.'''
        self.cid = ''
        self.ctype = ''
        self.name = ''
        self.owner = ''
        self.properties = []
        field_list=[field.strip() for field in class_string.split(LIST_SEP)]
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
    return haystack[count-1:]

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
        return -1,-1,-1,-1
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
            if popos >= 0:
                paren_list.append((count,popos))
                pos=popos+1
            else:
                startcnt, startpos = paren_list.pop()
                endcnt, endpos = count, pcpos
                pos=pcpos+1
        elif pcpos < popos:
            if pcpos >= 0:
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
    return subset[count:]

def dump_classes(class_list):
    for c in class_list:
        print "Class Name: " + c.name
        for prop_obj in c.properties:
            print "\tPropertyName: " + prop_obj.name
            if prop_obj.is_key:
                print "\t\tIs a Key"
            if prop_obj.enum_name:
                print "\t\tEnumInfo: " + prop_obj.enum_name
                for enum_val in prop_obj.token_array:
                    name,val = enum_val.split(',')
                    print "\t\t\tname: " + name + ", val: " + val
        print "----------------------------------"

def add_java_property(propinfo):
    print "        ppib = new PolicyPropertyInfoBuilder();"
    print "        ppil = new ArrayList<PolicyPropertyInfo>();"
    print "        classKeys = new ArrayList<PolicyPropertyId>();"
    print "        ppib.setPropId(new PolicyPropertyId(" + propinfo.pid + "l))."
    print "             setPropName(" + propinfo.name + ")."
    print "             setType(PolicyPropertyInfo.PropertyType." + propinfo.type.split(CSEP)[1] + ")."
    if propinfo.type == COMPOSITE_PROP: 
        print "             setClassId(" + propinfo.cid + "l)."
    print "             setPropCardinality(PolicyPropertyInfo.PropertyCardinality." + propinfo.cardinality.split(CSEP)[1] + ");"
    print "        ppi = ppib.build();"
    print "        ppil.add(ppi);"
    if propinfo.is_key:
        print "        classKeys.add(ppi.getPropId());"

def add_java_class(java_class):
    print "        pcib = new PolicyClassInfoBuilder();"
    print "        pcib.setClassId(" + java_class.cid + ")."
    print "             setClassName(" + java_class.name + ")."
    print "             setPolicyType(PolicyClassInfo.PolicyClassType." + java_class.ctype.split(CSEP)[1] + ");"
    print "             setProperty(ppil)."
    print "             setKey(classKeys);"
    print "        pci = pcib.build();"
    print ""

def create_java_data(class_list):
    for c in class_list:
        for prop_obj in c.properties:
            add_java_property(prop_obj)
        add_java_class(c)
            
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
    classlist=[prop.strip() for prop in class_string.split(LIST_SEP)]
    # we know the next line is always a "list_of", so
    # skip it and get all the properties
    lines=get_properties(lines[2:], prop_array)
    # See if there are any keys associated with this class.
    # If there are, set the "is_key" field in the associated
    # property.
    c=ClassInfo(class_string, prop_array)
    class_list.append(c)
    # Now go find any properties used as keys.  We can always
    # skip the next line, as it's a comma in the ClassInfo 
    # parameter list. If the line after it has list_of, then
    # we need to extract lines as long as they have an open
    # parenthesis
    if lines[1].find(LIST_OF) != -1:
        index=2
        while 1 == 1:
            prop_id=re.match(PROPID_RE, lines[index].strip())
            if prop_id == None:
                break
            for prop in c.properties:
                if prop_id.group(1) == prop.pid:
                    prop.set_key()
            index += 1
create_java_data(class_list)
