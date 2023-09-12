

Happy hacking!
(base) PS C:\Code\texttrek\web> ls


    Directory: C:\Code\texttrek\web


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        12/09/2023     19:27                node_modules
d-----        12/09/2023     19:27                public
d-----        12/09/2023     19:27                src
d-----        12/09/2023     19:27                text-trek
-a----        12/09/2023     19:27            310 .gitignore
-a----        12/09/2023     19:27         696810 package-lock.json
-a----        12/09/2023     19:27            812 package.json
-a----        12/09/2023     19:27           3359 README.md


(base) PS C:\Code\texttrek\web> npx create-react-appcd^C
(base) PS C:\Code\texttrek\web> cd ..
(base) PS C:\Code\texttrek> python .\main.py
C:\Users\yusuf\anaconda3\python.exe: can't open file 'C:\Code\texttrek\main.py': [Errno 2] No such file or directory
(base) PS C:\Code\texttrek> .venv\Scripts\activate
.venv\Scripts\activate : The module '.venv' could not be loaded. For more information, run 'Import-Module .venv'.
At line:1 char:1
+ .venv\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (.venv\Scripts\activate:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CouldNotAutoLoadModule

(base) PS C:\Code\texttrek> cd .\scripts\
(base) PS C:\Code\texttrek\scripts> .venv\Scripts\activate
(.venv) (base) PS C:\Code\texttrek\scripts> python .\main.py
Traceback (most recent call last):
  File "C:\Code\texttrek\scripts\main.py", line 6, in <module>
    openai.organization = os.environ["OPEN_AI_ORGANIZATION"]
                          ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen os>", line 679, in __getitem__
KeyError: 'OPEN_AI_ORGANIZATION'
(.venv) (base) PS C:\Code\texttrek\scripts> $Env:OPEN_AI_ORGANIZATION="org-mGjZuZi63BzqHJjxjN0mVXrF"
(.venv) (base) PS C:\Code\texttrek\scripts> python manage.py startapp images^C                                                                              
(.venv) (base) PS C:\Code\texttrek\scripts> conda install -c conda-forge gcc^C                                                                              
(.venv) (base) PS C:\Code\texttrek\scripts> $Env:OPEN_AI_KEY="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"       
(.venv) (base) PS C:\Code\texttrek\scripts> cd adnext_index^C                                                                                               
(.venv) (base) PS C:\Code\texttrek\scripts> $Env:BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=texttrek;AccountKey=UgwvYEd935HB7A/CVUSnincX1HvKQzW5cvsf/t6fmEscE1yXT10PBECpNQ7+cNrBKlHjVautmxmM+ASt21SK3A==;EndpointSuffix=core.windows.net"