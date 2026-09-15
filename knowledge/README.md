# Knowledge roots for the bot (relative to project).

On the Black Fox Windows workspace these folders are junction links to:

- `../AI_Knowledge_Base_Multilingual`
- `../AI_BOT_DATABASE`
- `../Support_Decision_Tree`

On a Linux deploy host, either copy those trees here or replace with symlinks:

```bash
ln -s /path/to/AI_Knowledge_Base_Multilingual knowledge/AI_Knowledge_Base_Multilingual
ln -s /path/to/AI_BOT_DATABASE knowledge/AI_BOT_DATABASE
ln -s /path/to/Support_Decision_Tree knowledge/Support_Decision_Tree
```
