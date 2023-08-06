# GitList
_Displays the state of your local git repos_

If you've ever wanted a quick and easy overview of your git repos from the
command line - **GitList** - is for you.

![](images/gitlist-output.jpg)

## Installing

```
    pip install gitlist
```


## Usage

`gitlist [DIRECTORY_TO_SEARCH]`

If you omit the optional DIRECTORY\_TO\_SEARCH `gitlist` will report on the tree
starting at the current directory. Running `gitlist` will show relative paths to
each git repository in green. If there are uncommitted changes or unpushed local
changes that are committed, then relevant messages will be displayed in yellow.

## Testing

Run the following commands:

```
    git clone --recurse-submodules git@github.com:craigiansmith/gitlist.git
    pipenv install --dev
    pipenv shell
    python -m pytest
```
