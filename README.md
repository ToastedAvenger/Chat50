# Chat50
Chat50 (CS50's Final project)
#### Video demo <https://youtu.be/zLACk7mx4a8>
#### Description: A website which allows users to create rooms for chatting with others.

## Installation
Inside the projects forlder run
```bash
pip install requirements.txt
```

## Run and Host
Add --debug to make it reload after any change is made to code.
Add --host=0.0.0.0 to make this available in your local network
```python
python -m flask run
```

## Working
Project is a website made with the help of Flask and Socket-io module.
In this website users can register and create their accounts that will be used to login and access the features of websites.

This website basically allows users to create rooms which other users can join and then they can chat. There are two types of rooms:

1) Public (Anyone can join)
2) Private (Requires password to join)

Any user who has joined the room will remain part of the room until(they will be part of the room even if they close their browser, just like whatsapp groups) manually clicked they click the LEAVE button in the room.

Socket-io is used to handle the sending receiving of messages to all clients.

Information about all the users and rooms are stored in database made in sql.

PS: I indeed have plans to make it much better in the future. There are many things that I still want to implement.

This is my Final Project.

THIS WAS CS50.
