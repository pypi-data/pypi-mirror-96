# lookfor

```lookfor``` is a simple command line tool to find things: files, directories, and files by extension. `lookfor` consists of only two commands (besides `--version` and `--help`), and aims to replace two Unix commands by being simpler to use and return results faster.

### Installation

```
git clone https://github.com/breakthatbass/lookfor.git

cd lookfor

pip install .
```


### Usage

`lf <flag> <file/ext>`

#### Commands:
```
--file, -f file/dir          searches for file/dir and prints all paths. Starts in cwd.
--ext, -e extension          searches for extension and prints all paths. Starts in cwd.
--version, -V                prints version info.
--help, -h                   prints usage
```

| unix command                    | lookfor command   | what is does                     |
| ------------------------------- | ----------------- | -------------------------------- |
| `find . \| grep file/dir`       | `lf -f file/dir`  | prints all paths that match      |
| `find . -type f -name "*.ext"`  | `lf -e ext`       | prints all paths that have `ext` |

