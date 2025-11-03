: # 
: # 
:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL

#!/bin/bash
for file in *; do 
  if [[ "$file" == *.plantuml ]]; then
    echo Generating plantuml image from $file
    plantuml -v -tpng -charset UTF-8 $file
  fi
done

exit $?

:CMDSCRIPT
ECHO Windows is currently not supported
