When developing FortiusANT, the following guidelines were followed.
If code is proposed through PR's it would be nice to maintain these same guidelines.

## Editor

- Convert tabs to spaces
- One tab = 4-spaces

It depends what editor you use how this is set.

In Visual Studio Code:
- File, Preferences, Settings
- tab Workspace
- search for tabSize
- Detect indentation = true
- tabSize = 4

## Comment

Comment serves to explain **what and why**, where the code itself details the **how**.

Separating comment from the code, makes it possible to read either the comment (what is happening and why) or the code itself (how is it implemented).

The currently available code serves as an example about the intention.

## Code complexity

Even though following code may be perfectly correct,
without comment and because of multiple nesting it's difficult to understand.

At first, comment is required to explain the what/why of the code (see above).

Also, since the purpose of the code is not explained, it is impossible to detect an error without reverse engineering the code and the context.

    def f(val,bits):
        if val>>(bits-1) == 1: 
            return 0-(val^(2**bits-1))-1 
        else:
            return val

    value = f((data[39]<<8)|data[38],16)

And if constructs are repeatably used, make a function to encapsulate complexity.

    value1 = f((data[39]<<8)|data[38],16)
    value2 = f((data[13]<<8)|data[14],16)
    value3 = f((data[11]<<8)|data[10],16)

this kind of code makes it difficult to find the error as present in the previous example.

## Do not use constants in code
Instead of:

    array[1]

The code should be

    sunday=1 
    array[sunday]

Because `array[sunday]` is not the same as `array[1]` (in the eye of the reader):

## New lines

newlines are an issue when working on windows (CR-LF) and unix (LF) and this can be resolved as described in https://git-scm.com/docs/gitattributes#_text

The .gitattributes text-file in the root of your working-directory takes care of the normalization:

    # Set the default behavior, in case people don't have core.autocrlf set.
    * text=auto

    # Declare files that will always have CRLF line endings on checkout.
    *.bat text eol=crlf

**2020-12-23 This .gitattributes file is not yet published on github to avoid issues with active branches.**

Click [here](https://github.com/WouterJD/FortiusANT/blob/master/.gitattributes) to see the file in the master branch.

If this .gitattributes file DOES NOT exist in your branch, proceed as follows (see https://git-scm.com/docs/gitattributes#_effects paragraph 'From a clean working directory:'):
- Check-in all code to github, so that you have a clean working directory
- Create .gitattributes in your working-directory with the contents as described above

From a clean working directory:

    $ git add --renormalize .
    $ git status        # Show files that will be normalized
    $ git commit -m "Introduce end-of-line normalization"
after this, your branch is normalized and you can proceed development.

**Note**:
If you have a branch that is created before .gitattributes was added to master
AND If .gitattributes is created on master, but not on your branch or vice-versa,
there will be many changes where the newlines are not equal.
