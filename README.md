# COALI Discord Bot
The **COALI Discord Bot** is the official all-in-one bot for the official [COALI Discord Community](https://discord.gg/PAEACCZDgq) of the world's largest student-led Facebook group for [Cambridge O/A Level and IGCSE (COALI)](https://www.facebook.com/groups/COALIOfficial). 

The bot is currently under development and is pending a major rewrite since a myriad of Discord framework updates and newly introduced features and restrictions. Migration to Discord slash commands and Discord UI facilities are one of the to-do list items for this project's development. 

This project is currently private and not open for collaboration, however, very soon it will be for sure. This repository has only been made public for showcase of work to the **Google Developers Student Club (GDSC) FAST-NUCES Lahore**. Authorization tokens and sensitive auth content has been replaced with placeholder text, as the original directory remains integrated with the [Heroku Hosting Service](https://heroku.com).  

## Packages Used
The project has been developed completely in the Python programming language and makes use of the following packages (can also be found inside requirements.txt). 

```txt
psutil
jishaku
requests
discord.py
git+https://github.com/nhorvath/Pyrebase4
git+https://github.com/dateutil/dateutil/
```
All these packages can be installed using
```bash
pip install requirements.txt
```
within the main directory. 

Main third-party packages used in the development for this project are [Discord.py](https://github.com/Rapptz/discord.py), the Python Discord API Wrapper, and [Pyrebase](https://github.com/nhorvath/Pyrebase4), the Python Google Firebase API Wrapper.

## Google Firebase Usage
The [Pyrebase](https://github.com/nhorvath/Pyrebase4) API wrapper library has been used to manage database transactions and storage for the client by using [Google Firebase](https://firebase.google.com). The project can be explored for how the Firebase has been integrated into the project by viewing files such as `cogs/AutoMod.py`, `cogs/Utilities.py` and `cogs/Warnings.py`. 

Firebase authorization values are stored under `json/FirebaseCreds.json` in the json format instead as an environment variable due to personal preference. Authorization values have been replaced with placeholder text. 

## Contributing
The project is currently private and not open for collaboration or contribution at the moment. However, in the upcoming future it will be. 

Call for collaboration would be announced over all COALI Platforms and collaborators would be welcomed. For now, the whole project has been developed from scratch by the project owner alone. 

## License
No licensing exists for this project as of now as this project is not available for commercial display or use and is private. This project has been made public solely for showcase of work in Firebase to the GDSC Technical Team heads. It will be recommended to not copy or download code without the project owner's permission. 