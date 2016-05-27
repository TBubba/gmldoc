import sys, os, shutil, xml, re
import xml.etree.ElementTree as ET
from jinja2 import Environment, PackageLoader
JINJA_ENV = Environment(loader=PackageLoader('gmdoc', 'templates'))

# Templates
METHOD_TEMPLATE = JINJA_ENV.get_template('method.html')
INDEX_TEMPLATE = JINJA_ENV.get_template('index.html')

# Basic types
TYPE_REAL = 'real'
TYPE_STRING = 'string'

class Extension(object):
	def __init__(self, name, description):
		self.name = name
		self.description = description

# Represents the entire project the documentation is generated for
class Project(object):
    def __init__(self):
    	super(Project, self).__init__() # Run parent constructor
    	self.name = ''          # Name of the project        (string)
    	self.directory = ''     # Path to the project        (string)
        self.methods = []         # Collection of scripts      (Method[])
        self.methodsFolder = ScriptFolder("scripts", self) # Folder tree of scripts     (ScriptFolder)
       #self.objects = []
        self.help    = ''         # Text from the help file    (string)

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

# Represents a folder in the project (for scripts, objects etc.)
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

# Represents a method parameter in the source code
class MethodParam():
	def __init__(self, name, type, desc):
		self.name = name         # Name of the parameter       (string)
		self.type = type         # Type of the parameter       (not sure - currently string)
		self.description = desc  # Description of the paramter (string)

# Represents a method return value/type in the source code
class MethodReturn():
	def __init__(self, type, desc):
		self.type = type         # Type of returned value      (not sure - currently string)
		self.description = desc  # Description of the return   (string)

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
def extract_rtf_text(text):
	#
	depth = 0
	last = ''
	result = ''
	for char in text:
		# Only reads text one layer of "{ }"
		# (curly brackets) deep
		if last != '\\':
			if char == '{': # 
				depth += 1
				last = char
				continue
			elif char == '}': # 
				depth -= 1
				last = char
				continue
		if depth == 1: # 
			result += char
		last = char # Update last
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
	is_private = False # If the script is private (and should be not be included)
	for comment in comments:
		the_param = strip_token("@param", comment)
		the_return = strip_token("@return", comment)
		the_flags = strip_token("@flags", comment)
		if the_flags: # This line is a flag line
			the_flags = the_flags.split()
			for flag in the_flags:
				if (flag == "private"): # Private, hides the script from the documentation
					is_private = True
				#elif (flag == ""): # Some other flag, doe something else
					#
		elif the_param: # This line is about a parameter
			the_param = the_param.split(' ',1)
			method.params.append(MethodParam(the_param[0], TYPE_REAL, the_param[1]))
		elif the_return: # This line is about the return value
			method.return_value = the_return
		else: # This line is part of the description
			desc += strip_leading_comment_markup(comment)
	method.description = desc
	print(method.description)

	# Add script to project script collection
	if is_private != True: # Check if script was flagged as private
		script_folder.add_child(method) # Add script to the project script collection
	else:
		print('Skipping private script ' + script_name)

# Loops through a folder and it's sub-folders and extracts
# any script it finds and creates a folder structure from it
def extract_scripts_folder(script_folder, parent_element):
	folder_children = parent_element.getchildren() # Get all children in folder
	if folder_children is None: # Return if empty
		return

	#
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
	help_file = open(os.path.join(project_dir, help_filename), 'r')
	help_data = help_file.read()
	help_file.close()
	project.help = extract_rtf_text(help_data) # Add help to the project
	print(">> Successfully read project help file")

	# Read all the project scripts and extract
	# doc information from them
	print("Reading scripts...")
	project_scripts = project_xml.find("scripts") # Get scripts root element
	extract_scripts_folder(project.methodsFolder, project_scripts)
	print(">> Successfully read scripts")

	# Return project
	return project;

# Documents the given project file
def doc(project_file, outdir):
	# TODO normalize outdir - remove trailing /
	# and remove any leading dots and / 

	# Extract the project from the project file
	# and all files listed in it (scripts, objects etc.)
	project = exctract_project(project_file)

	# TODO create a proper extension
	extension = Extension('TODO Title','TODO Description')

	# Write the HTML files
	# Creating the output directory if it doesn't exist
	# Then generated the index.html file
	# Then finally creating another html for each method
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	index_html = INDEX_TEMPLATE.render({
		'extension': extension,
		'all_methods': project.methods,
	})
	index_file = open(os.path.join(outdir,'index.html'), 'w')
	index_file.write(index_html)
	index_file.close()
	for method in project.methods:
		print("Rendering file %s", method.name)
		render_params = {
			'extension': extension,
			'all_methods': project.methods,
			'method': method,
			# Uncomment these lines when testing locally
			# 'stylesheet_url': '../styles/all.css',
		}
		the_html = METHOD_TEMPLATE.render(render_params)
		text_file = open(os.path.join(outdir,method.name + '.html'), "w")
		text_file.write(the_html)
		text_file.close()

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
