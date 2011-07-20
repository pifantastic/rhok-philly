""" HTML content generator."""

'''
# Refactor code so a generator object can return the whole page at once
# We'll append '\t'*self.tabs before all rows and adjust self.tabs when entering or leaving blocks of code.
class htmlGenerator():

    tabs = 0 
    content = ""

    def __init__(self,tabs=0):
        self.tabs = tabs

    def exportToFile(self, fileName):
        """Saves content to a file. Name should be without extension."""
        # Consider rewriting to check whether input fileName has extension.
        exportFile = open(fileName+'.html', 'w')
        exportFile.write(self.content)
        exportFile.close()
'''    

def httpHeader(cookieList=[]):
    """ Generates the top of the html file. 
    Optional parameter: List of cookies."""
    myStr = "Content-Type: text/html"
    for cookie in cookieList:
        myStr += cookie.output()
    return myStr

def header(myTitle):
    return "<html><head><title>%s</title></head>\n\n<body>" % myTitle

def footer():
    """ Generates the bottom of the html file."""
    return "</body></html>"

# GENERAL HTML ELEMENTS ########################################

def ul(myList):
    """ Generates HTML list from a given list."""
    myStr = ""
    myStr += "<ul>"
    for item in myList:
        myStr += "\t<li>%s</li>" %item 
    myStr += "</ul>"
    return myStr

# FORM ELEMENTS ################################################

def inputHidden(name,val):
    myStr = ""
    myStr += '<input type="hidden" name="%s" value="%s">' %(name,val)
    return myStr

def inputText(name,val,size,max=50):
    return '<input type="text" name="%s" value="%s" size="%s" maxlength="%s">' %(name,val,size,max)

def inputPassword(name,size=20,val=''):
    return '<input type="password" name="%s" value="%s" size="%s">' %(name,val,size)

def inputTextArea(name,numrows,numcols,initvalue="",wrapstyle="virtual"):
    return '<textarea name="%s" rows="%s" cols="%s" wrap="%s">%s</textarea>' %(name,numrows,numcols,wrapstyle,initvalue)

def inputOption(valSubmitted,valShown):
    """ For use within a "select" type of input."""
    return '<option value="%s">%s</option>' %(valSubmitted,valShown)

def inputSelectFromList(name,optionList):
    """ Used when we want the visible option names to be the same as submitted values."""
    myStr = ""
    myStr += '<select name="%s">' %name
    for item in optionList:
        myStr += inputOption(item,item)
    myStr += '</select>'
    return myStr

def inputSelectFromDict(name, optionDict):
    """ The values shown to the user in the form will be the keys.
    The values submitted to the form are associated values in dictionary."""
    myStr = ""
    myStr += '<select name="%s">' %name
    for key,value in optionDict.items():
        myStr += inputOption(key,value)
    myStr += '</select>'
    return myStr

def inputSelectTuples(name,tupleList):
    """ Tuples should be (value to submit, label shown in form)."""
    myStr = ""
    myStr += '<select name="%s">' %name
    for opt in tupleList:
        myStr += inputOption(opt[0],opt[1])
    myStr += '</select>'
    return myStr

def inputMultSelect(name,optionDict,numselect):
    """The MULTIPLE option allows selecting multiple elements."""
    myStr = '<select name="%s" multiple size="%s">' %(name,numselect)
    for key,value in optionDict.items():
        myStr += inputOption(value,key)
    myStr += '</select>'
    return myStr

def inputCheckbox(name,value,check=False):
    # If check is False, multiplying "checked" by it yields an empty string.
    # Multiplying by True would give us one repetition of the string.
    return '<input type=checkbox name="%s" value="%s"%s>' %(name,value,("checked"*check))
    
def inputFile(name):
    return '<input type=file name="%s">' %name
    
def inputSubmit(name,val):
    return '<input type="submit" name="%s" value="%s">' %(name,val)

def startForm(id,name,action):
    """ Insert start tag for form. 
    Assumes method is "post" and enctype is multipart/form-data."""
    return '<form id="%s" name="%s" action="%s" method="post" enctype="multipart/form-data">' %(id,name,action)

def endForm():
    return '</form>'
    
def inputRadioButton(name,value,check=False):
    if check:
        return '<input type="radio" name="%s" value="%s" checked>' %(name,value)
    else:
        return '<input type="radio" name="%s" value="%s">' %(name,value)

