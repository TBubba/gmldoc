import sys, os, shutil, xml, re
import xml.etree.ElementTree as ET
from jinja2 import Environment, PackageLoader
JINJA_ENV = Environment(loader=PackageLoader('gmdoc', 'templates'))

# Templates
METHOD_TEMPLATE = JINJA_ENV.get_template('method.html')
INDEX_TEMPLATE = JINJA_ENV.get_template('index.html')
SIDEBAR_TEMPLATE = JINJA_ENV.get_template('sidebar.html')

# Basic types
TYPE_REAL = 'real'
TYPE_STRING = 'string'

#
class FlagSource(object):
    def __init__(self):
    	super(FlagSource, self).__init__() # Run parent constructor
    	self.flags_def = {} # Default flag values            (dict[string:string])
    	self.flags_setdef = {} # Default flag vales when changed (but no value entered) (dict[string:string])

    # Set (a flag)
    def set(self, flag, def_value, setdef_value): # Sets both
    	self.flags_def[flag] = def_value
    	self.flags_setdef[flag] = setdef_value
    def set_def(self, flag, value): # Sets "flags_def" (default)
    	self.flags_def[flag] = value
    def set_setdef(self, flag, value): # Sets "flags_setdef" (set-def)
    	self.flags_setdef[flag] = value

    # Get (a flags value)
    def get_def(self, flag, value): # Gets "flags_def" (default)
    	return self.flags_def.get(flag, value)
    def get_setdef(self, flag, value): # Gets "flags_setdef" (set-def)
    	return self.flags_setdef.get(flag, value)

    # Factory
    @staticmethod
    def factory_method():
    	source = FlagSource()
    	source.set('private',   '0', '1') # If it should not be in the compiled docs (number)
    	source.set('nosidebar', '0', '1') # If it should not be in the sidebar       (number)
    	return source

#
class FlagCollection(object):
    def __init__(self, source):
    	super(FlagCollection, self).__init__() # Run parent constructor
    	self.flags = {} # Flags and their current value     (dict[string:string])
    	self.source = source # Object that handels defaults (FlagSource)
    	self.flags = dict(source.flags_def) # Copy default flags from source

    # Set a flag (creates one if it doesn't exist)
    def set(self, flag, value):
    	self.flags[flag] = value

    # Set a flag to it's set-def value (creates one if it doesn't exist)
    def set_setdef(self, flag):
    	setdef = source.get_setdef(flag, None)
    	if (setdef == None):
    		raise Exception("Could not find set-def value of flag " + flag)
    	self.flags[flag] = setdef

    # Returns value of a flag (or default if not found)
    def get(self, flag, default):
    	return self.flags.get(flag, default)

    # Resets to default flags (copies the default)
    def reset(self):
    	self.flags = dict(self.source.flags_def)

# Represents the entire Game Maker project that the documentation
# will be generated for. It is not the documenatation itself.
class Project(object):
    def __init__(self):
    	super(Project, self).__init__() # Run parent constructor
    	self.name = ''          # Name of the project        (string)
    	self.directory = ''     # Path to the project        (string)
        self.methods = []         # Collection of scripts    (Method[])
        self.methodsFolder = ScriptFolder("scripts", self) # Folder tree of scripts     (ScriptFolder)
       #self.objects = []
        self.help    = ProjectHelp() # Projects help file    (ProjectHelp)

# Represents an item inside the project (Folder, script, object etc.)
class ProjectItem(object):
    def __init__(self):
    	super(ProjectItem, self).__init__() # Run parent constructor
    	self.parent = None        # Parent item                  (ProjectItem)
    	self.children = []        # Collection on children items (ProjectItem[])

    def set_parent(self, parent): # Sets the parent of this item
    	if isinstance(parent, ProjectItem) or parent is None:
    		self.parent = parent
    	else:
    		raise Exception("Only ProjectItems can be the parent to another (or None)")

    def add_child(self, child): # Adds a child to this item
    	if isinstance(child, ProjectItem):
    		self.children.append(child)
    		child.set_parent(self)
    	else:
    		raise Exception("Only ProjectItems can be added as children to one another")

# Represents a folder in the project (for scripts, objects etc.)
class ProjectFolder(ProjectItem):
    def __init__(self, name):
    	super(ProjectFolder, self).__init__() # Run parent constructor
    	self.name = name          # Name of the folder          (string)

# Represents a folder in the project for scripts specifically
class ScriptFolder(ProjectFolder):
    def __init__(self, name, project):
    	super(ScriptFolder, self).__init__(name) # Run parent constructor
    	self.project = project    # Referece to a project       (Project)

    def add_child(self, child): # Adds a child to this item
    	if isinstance(child, ProjectItem): # If child is a valid type
    		self.children.append(child)
    		child.set_parent(self)
    		if isinstance(child, Method): # If child is a script
    			self.project.methods.append(child)
    	else:
    		raise Exception("Only ProjectItems can be added as children to one another")

# Represents a method in the source code
class Method(ProjectItem):
    def __init__(self, name, syntax):
    	super(Method, self).__init__() # Run parent constructor
    	self.name = name         # Name of the script          (string)
        self.params = []         # Collection of parameters    (MethodParam[])
        self.syntax = syntax     # Syntax of the script        (string)
        self.description = ''    # Description                 (string)
        self.ret = None          # Return value/type           (MethodReturn)
        self.flags = FlagCollection(Method.flag_source) # All flags from doc comments (FlagCollection)

    #
    flag_source = FlagSource.factory_method()

# Represents a method parameter in the source code
class MethodParam(object):
	def __init__(self, name, type, desc):
    	#super(MethodParam, self).__init__() # Run parent constructor
		self.name = name         # Name of the parameter       (string)
		self.type = type         # Type of the parameter       (not sure - currently string)
		self.description = desc  # Description of the paramter (string)

# Represents a method return value/type in the source code
class MethodReturn(object):
	def __init__(self, type, desc):
    	#super(MethodReturn, self).__init__() # Run parent constructor
		self.type = type         # Type of returned value      (not sure - currently string)
		self.description = desc  # Description of the return   (string)

# Respresents the "Game Information" or "help file" of the project
class ProjectHelp(object):
    def __init__(self):
    	#super(ProjectHelp, self).__init__() # Run parent constructor
    	self.plaintext = ''      # All text from the help file               (string)
    	self.docs = ''           # The documentation from the help file      (string)
    	self.docs_split = ''     # Same as "docs" but split on each new line (string[])

# Represents the documentation for the project. This will be what
# keeps the settings for how the documentation will be and look.
class Docs(object):
    def __init__(self):
    	#super(Docs, self).__init__() # Run parent constructor
    	self.project = None          # The project the documentation will be about  (Project)
    	self.settings = DocsSettings() # The settings for the documentation         (DocsSettings)
    	self.title = ''              # The title of all outputted doc pages         (string)
    	self.description = ''        # The description of the project (header data) (string)

# The settings for the documentation
class DocsSettings(object):
    def __init__(self):
    	#super(DocsSettings, self).__init__() # Run parent constructor
    	self.allowjavascript = 0 # If JavaScript will be allowed in the docs (0/1 or True/False)

# Kills the program and prints the given message
def die(message):
	print(message)
	sys.exit()

# Print the intended usage of the program
def usage():
	die("usage: "+sys.argv[0]+" <target.project.gmx>")

# Reads an xml file and returns the root node
def read_xml(the_dir):
	the_file = open(the_dir,"r")
	contents = the_file.read()
	the_file.close()
	return ET.fromstring(contents)

# Exctracts plain text from given RTF formatted text
# Note: Only ASCII characters and almost all RTF is discarded
# TODO make HTML tags out of the RTF (bold, font, size, color etc.)
def extract_rtf_text(text):
	depth = 0 # How many layers deep in "{}" (curly brackets) we are
	escape_finishers = {'\\', ' ', '\n', ';', '{', '}'}
	escaped = 0 # 0 = Not escaped | 1 = Escped | 2 = Escape just ended
	slash_tail = '' #
	last = '' # Last char from last run of the loop
	result = '' # The text that will be returned when we are done
	for char in text:
		# Take care of escaped characters
		if escaped == 1:
			# Keep adding escaped chars to slash_tail
			if char == '\\' and slash_tail != '': # End of escape
				escaped = 0 # It ended with '\' after one or more escaped chars
			elif char not in escape_finishers: # End escape characters
				slash_tail += char # Continue escape (keep adding chars to slash_tail)
				last = char
				continue
			else: # End of escape
				escaped = 2
			# Do stuff depeding on slash_tail
			if slash_tail == "line": # New line
				result += '\n'
			# TODO handle non-ASCII characters in some way
			slash_tail = '' # Reset slash_tail
		if escaped == 0: #
			if char == '\\': # Start escape characters
				escaped = 1
				last = char
				continue
		else:
			escaped = 0

		# Change level if char is a non-escaped curly bracket
		#if last != '\\': # Check if escaped
		if char == '{': # Go down one level
			depth += 1
			last = char
			continue
		elif char == '}': # Go up one level
			depth -= 1
			last = char
			continue

		# Check if we are at the right curly bracket depth
		if depth == 1: # Only reads text at "{}" depth 1
			result += char

		last = char # Update last (char to current)
	return result

# Extracts all comments from the given code
def extract_special_comment_text(code):
	state = 0
	last = ''
	result = ''
	for char in code:
		# Once we have read the entire first comment
		# section and we hit code, we are done. Return
		# the result
		if state == -1: ## New line after new line
			if char == '/' or char == '*':
				state = 0
			elif char != ' ':
				return result

		if state == 0: # New line after non-new line or first char
			if char == '\n':
				state = -1
			elif last == '/':
				if char == '*':
					result += last + char
					state = 2
				elif char == '/':
					result += last + char
					state = 1
		elif state == 1:
			if char == '\n':
				state = 0
			result += char
		elif state == 2:
			if last == '*' and char == '/':
				state = 0
			result += char
		last = char
	return result

# Removes any / * and spaces from the start of the given string
def strip_leading_comment_markup(code):
	i = 0
	for char in code:
		if char != ' ' and char != '/' and char != '*':
			return code[i:]
		else:
			i += 1
	return ''

# 
def strip_token(token, code):
	i = code.find(token)
	if i >= 0:
		return code[i+len(token):].strip()

# Splits flags
# Returns a dictionary with flag names as keys and their values as values
# (The flags will have None as their value if '=' was entered - use set-def instead)
def split_flags(code):
	# Split the flag-value pairs from each others
	flags = code.split() # Split on space (' ')
	split_flags = {}
	for flag in flags:
		# Split the flag from their value and add them to the dictionary
		flag = flag.split('=', 1) # Split at the first equals sign ('=')
		if 1 < len(list): # If at last one '=' was entered
			split_flags[flag[0]] = flag[1]
		else: # No value was eneterd
			split_flags[flag[0]] = None

	return flags

# Extracts one script from a script xml element
# and creates and returns a Method instance from it
def extract_script(script, script_folder):
	# Get script path, name and file extenstion
	script_path = script.text.replace("\\", "/")
	script_path = os.path.join(script_folder.project.directory, script_path)
	script_name_and_ext = os.path.basename(script_path)
	script_name = os.path.splitext(script_name_and_ext)[0]

	# Skip scripts that start with an underscore
	if script_name[0] == '_': 
		print('Skipping private script ' + script_name)
		return
	else:
		print("Reading script " + script_name + "...")

	# Read the script file
	script_file = open(script_path,"r")
	code = script_file.read()
	script_file.close()
	comments = extract_special_comment_text(code).split('\n')
	syntax = strip_leading_comment_markup(comments[0])
	comments = comments[1:]

	# Generate a method object from the script file
	method = Method(script_name, syntax)
	desc = ''
	for comment in comments:
		# Check for any (script compatible) token
		the_param  = strip_token("@param",  comment) # TODO make some sort of "switch"-
		the_return = strip_token("@return", comment) #      like replacement for this
		the_flags  = strip_token("@flags",  comment)

		# 
		if the_flags: # This line is a flag line
			flags = split_flags(the_flags)
			for flag, value in flags.iteritems():
				if (value == None): # No values was entered
					method.flags.setdef(flag)
				else:
					method.flags.set(flag, value)
		elif the_param: # This line is about a parameter
			the_param = the_param.split(' ',1)
			method.params.append(MethodParam(the_param[0], TYPE_REAL, the_param[1]))
		elif the_return: # This line is about the return value
			method.return_value = the_return
		else: # This line is part of the description
			desc += strip_leading_comment_markup(comment)
	
	# Add description to script
	method.description = desc
	print(method.description)

	# Add script to project script collection
	if method.flags.get('private', 0) != 1: # Check if script was flagged as private
		script_folder.add_child(method) # Add script to the project script collection
	else:
		print('Skipping private script ' + script_name)

# Loops through a folder and it's sub-folders and extracts
# any script it finds and creates a folder structure from it
def extract_scripts_folder(script_folder, parent_element):
	folder_children = parent_element.getchildren() # Get all children in folder
	if folder_children is None: # Return if folder is empty
		return

	# Go through all folder items (children)
	for script_element in parent_element:
		# Get elements name tag (only folders have name tags)
		script_folder_name = script_element.get("name")

		# Check if it is a script or a folder
		if script_folder_name is None: # It's a script
			extract_script(script_element, script_folder) # Extract script from element to folder
		else: # It's a folder
			new_folder = ScriptFolder(script_folder_name, script_folder.project) # Create new folder
			script_folder.add_child(new_folder) # Add it to current folder
			extract_scripts_folder(new_folder, script_element) # Loop through it

# Reads and extracts all relevant information from the projects help file
def extract_help(help_filepath, project):
	# Create and add project help to project
	project_help = ProjectHelp()
	project.help = project_help

	# Open and read the entire help file
	help_file = open(help_filepath, 'r')
	help_data = help_file.read()
	help_file.close()

	# Extract all relevant data from the help file
	help_text = extract_rtf_text(help_data)
	help_docs = extract_special_comment_text(help_data)
	help_docs_split = help_docs.split('\n')

	# Add the relevant data to the projects help
	project_help.plaintext = help_text
	project_help.docs = help_docs
	project_help.docs_split = help_docs_split

	# 
	for comment in help_docs_split:
		token_ignore = strip_token("@ignore", comment)
		token_inojs = strip_token("@nojs", comment)

		if token_ignore: # This line is the "ignore" token
			s = 2 # Do something?
		elif token_inojs: #
			s = 2 #

	# Do something more with the tokens maybe?

# Extracts all the relevant information from the given project
# and creates (and returns) a Project instance with that information
def exctract_project(project_filename):
	project_dir = os.path.dirname(project_filename)

	# Create a project instance
	project = Project()
	project.directory = project_dir; # Set project directory

	# Read the project file (to find all project files)
	print("Reading project file...")
	# TODO check if file is valid xml or if it exists
	project_xml = read_xml(project_filename)
	print(">> Successfully read project file")

	# Read the projects "Game Information" (default help.rtf)
	# TODO check if the XML element exists before taking it?
	print("Reading project help file...")
	help_filename = project_xml.find("help").find("rtf").text
	help_filepath = os.path.join(project_dir, help_filename)
	extract_help(help_filepath, project)
	print(">> Successfully read project help file")

	# Read all the project scripts and extract
	# doc information from them
	print("Reading scripts...")
	project_scripts = project_xml.find("scripts") # Get scripts root element
	extract_scripts_folder(project.methodsFolder, project_scripts)
	print(">> Successfully read scripts")

	# Return project
	return project;

# Generates/Renders the HTML for the final documentation
def generate_documentation(docs, outdir):

	# Write the HTML files
	# Create output directory if it doesn't exist
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	# Generate the sidebar HTML (doesn't have to be a file)
	sidebar_html = SIDEBAR_TEMPLATE.render({
		'docs': docs
	})

	# Generate the index.html file
	index_html = INDEX_TEMPLATE.render({
		'docs': docs
	})
	index_file = open(os.path.join(outdir,'index.html'), 'w')
	index_file.write(index_html)
	index_file.close()

	# Then finally creating another html for each method
	for method in docs.project.methods:
		print("Rendering file %s", method.name)
		render_params = {
			'docs': docs,
			'method': method,
			# Uncomment these lines when testing locally
			# 'stylesheet_url': '../styles/all.css',
		}
		the_html = METHOD_TEMPLATE.render(render_params)
		text_file = open(os.path.join(outdir,method.name + '.html'), "w")
		text_file.write(the_html)
		text_file.close()

# Documents the given project file
def doc(project_file, outdir):
	# TODO normalize outdir - remove trailing /
	# and remove any leading dots and / 

	#
	docs = Docs()

	# Extract the project from the project file
	# and all files listed in it (scripts, objects etc.)
	project = exctract_project(project_file)
	docs.project = project

	# Generate / Render the HTML
	generate_documentation(docs, outdir)

# Check command line args
if len(sys.argv) < 2:
	print("Must supply a project file")
	usage()

# Set and validate the target project file
TARGET_FILE = sys.argv[1]
print("Project target: "+TARGET_FILE)
if not os.path.isfile(TARGET_FILE):
	die("Project file doesn't exist!")

# Check optional command line arg (output directory)
OUTPUT_DIRECTORY = 'output' # Default output directory name
if len(sys.argv) > 2:
	OUTPUT_DIRECTORY = sys.argv[2]
print("Output directory: "+OUTPUT_DIRECTORY)

# Start documenting the given file
doc(TARGET_FILE, OUTPUT_DIRECTORY)
