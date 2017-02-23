If installing Rundeck on Windows, do this to smooth the edges a bit.

To set Powershell as the default shell/script executor, add this to the resources.xml for the node in the project
```
local-node-executor="script-exec" 
script-exec-shell="bash -c" 
script-exec="${exec.command}"/>
```

