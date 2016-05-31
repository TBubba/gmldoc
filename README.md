# GMLDoc

***The missing documentation tool for GameMaker Extensions.***

Generates documentation files in HTML format from a given GameMaker project. The tool allows implicit documentation simply
by adding comments to your scripts and objects. You can document your scripts as follows;

```
/// my_cool_script(arg0,arg1)
/// Simply adds the two arguments together.
/// @param arg0 The first argument to the function
/// @param arg1 The second argument to the function
/// @return An awesome value that you probably want to deal with

// This comment will be ignored
return argument0 + argument1
```

Each script has four components;

- **Sytnax** eg. `my_cool_script(arg0,arg1)`
- **Description** eg. `Simply adds the two arguments together.`
- **Parameters** in the format <name> <description> eg. `arg0 The first argument to the function`
- **Return Statement** eg. `An awesome value that you probably want to deal with`

You can comment any way you like, the tool will stop reading your comments once a break in
leading comment is found.

You can also use markup in your comments to give headings, bold text and code examples like so;

```
/// my_super_well_documented_function()
/// <p>We can add some extra spacing using line breaks and paragraph tags.<p>
///	</br>
/// <h5>And headers</h5>
/// <p>And even code:</p>
/// <pre>
/// var greeting = my_super_well_documented_function();
/// show_debug_message(greeting);
/// </pre>
/// <b>This will be bold</b>

return "Hello World";
```

Documentation like this is useful because it easy to do and your users can simply look at your
scripts to get all the information that's available in the API reference. It's about not
having to make documentation a separate, pain-staking task, it should all just come together.

### Installation

The installation only takes minutes, and the guide is very beginner friendly. You can find it at the **[installation wiki page](../../wiki/installation)**.

### Usage

You can find the usage guide on the **[usage wiki page](../../wiki/usage)**.

### TODO 

The todo-list can be found at the **[todo wiki page](../../wiki/todo)**.

### License

> This is free and unencumbered software released into the public domain.

> Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

> In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

> For more information, please refer to <http://unlicense.org/>
