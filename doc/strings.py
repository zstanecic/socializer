# -*- coding: utf-8 -*-
documentation = [
_(u"""socializer's manual """),
_(u""""""),
_(u"""## Introduction"""),
_(u""""""),
_(u"""Socializer is an application to use [VK.com](https://vk.com) in an easy and accessible way with minimal CPU resource usage. Socializer will allow you to interact with the VK social network by giving you access to the most relevant features such as:"""),
_(u""""""),
_(u"""* Basic post creation in your wall (including photos)."""),
_(u"""* Audio addition, removal, download and search."""),
_(u"""* audio albums management (create, delete and add audios)."""),
_(u"""* Post comments."""),
_(u"""* like, unlike and repost other's posts."""),
_(u"""* Open other's timelines so you could track someone's friends, posts or audio files."""),
_(u"""* Basic chat features."""),
_(u""""""),
_(u"""Note: When new features are added to socializer they will be added to this section."""),
_(u""""""),
_(u"""## Running"""),
_(u""""""),
_(u"""If you are using a built version, unzip the file in a new directory with no special characters, and open the socializer.exe file. If you haven't configured your VK account, you will see a dialogue, just press yes and a new dialogue will  prompt for an user email or phone number and the password for your account.  Take into account that the provided information will be saved in a config file as plain text. This application will need your information  for renegotiating the access token when it expires."""),
_(u""""""),
_(u"""Note: Every time you grant access to socializer, probably You will receive an email from VK by telling you that someone has accessed to your account. It means that a new token has been negotiated between VK and socializer by using an authomatic process, you should ignore  those advices, unless you receive an email when you are not logged in VK with socializer or other application. You can see your authorised  applications in the configuration section in the VK website. New tokens are renegotiated every 24 hours."""),
_(u""""""),
_(u"""## Main interface"""),
_(u""""""),
_(u"""If you have used [TWBlue](https://github.com/manuelcortez/twblue) before, the socializer's interface is quite similar. Once you have authorised your account, you will see a window with the following elements:"""),
_(u""""""),
_(u"""* A tree view at the left of the window, where you will see the list of buffers. These buffers are divided in three categories, posts, music and people. You could expand each category for seeing the child buffers. There are some additional buffers, timelines and chats, wich will be filled with timelines for your friends or with chats, when you  start or receive a chat session."""),
_(u"""* A button for making a post to your wall."""),
_(u"""* In audio buffers, Two buttons: Play and play all."""),
_(u"""* In audio album buffers, a button for loading music. By default, albums are empty, you have to press  the load button for getting the album's items."""),
_(u"""* A list where you will see the posts for the currently selected buffer."""),
_(u"""* In people buffers, like the friends buffer, a button for sending a message to your friends. Pressing that button will cause a chat buffer to be created."""),
_(u"""* A status bar where the program will put some useful information about what it's doing at the moment."""),
_(u"""* And a menu bar."""),
_(u""""""),
_(u"""When socializer starts, it will try to load your news items, wall, audios (your audios, recommended and populars) and friends. At the moment there are only a few supported actions for   these items:"""),
_(u""""""),
_(u"""* Audio files: You can play the currently selected song, view the song's details (including lyrics, if available), add or remove from your library, and download it to a desired place in your hard drive. You can find audio files in your news feed or in your own audios buffers. You can find audios as post's attachments. You can create an audios timeline for displaying other's audios."""),
_(u"""* News feed's post: In your news feed buffer, you can press return in any post and socializer will open a new dialogue which can be different, depending in the kind of post you are when the return key was pressed. For example it will open the post if you are focusing a "normal" post, a list of people if you are in a post wich indicates that someone has added friends, an audio displayer if you are in a post wich indicates that someone has added an audio, etc."""),
_(u"""* Wall posts: It will show the post in a dialogue so you could interact with its attachments, view and post comments, or like/unlike/share the post."""),
_(u"""* You can send a message to someone by pressing the send message button in the buffer where you are, if available. Deactivated accounts cannot receive messages."""),
_(u""""""),
_(u"""### Making a post"""),
_(u""""""),
_(u"""When you press the post button, a new dialogue will show up. This dialogue allows you to post something in your wall. In this dialogue you have to write a message. You can translate your message and fix your spelling mistakes. Also you can post an URL address, socializer will try to add it as an attachment, so you will not have to worry about this. When you're ready, just press the send button and it'll be done."""),
_(u""""""),
_(u"""If you want to add some photos, you can press the attach button, then press the kind of attachment you want to add. After this, select the file you want to add and you will see it in the list, once processed. When you are done with attachments, press the OK button, and continue with your post. When you are ready, press the send button. Your post could take some time to be published, depending in the amount of files you have added, but it should be displayed in your wall and newsfeed as soon as it is posted."""),
_(u""""""),
_(u"""### Working with posts in news feed"""),
_(u""""""),
_(u"""You can press the return key in any post in your news feed for opening a new dialogue with some information. The information and dialogue will be different if you are viewing a friendship's notification  (when someone has added some friends), an audio file, or a regular post."""),
_(u""""""),
_(u"""If you open a regular post in your newsfeed, you will be able to see the comments in a list, indicate if you do like or dislike the post, repost or add a new comment. If the post has some attachments, you'll find a list populated with them, you can press return in an attachment to execute its default action, wich will be different depending on the kind of attachment that you are viewing."""),
_(u""""""),
_(u"""For friend notifications, you can only view the new added friends in a list and  there are some kind of posts that aren't handled. It should be improved."""),
_(u""""""),
_(u"""Additionally, you can press the menu Key or the right click  for displaying a menu with some quick actions available for the post you are focusing. These actions are different for every post type."""),
_(u""""""),
_(u"""### Working with songs"""),
_(u""""""),
_(u"""Note: the following applies to audio timelines too."""),
_(u""""""),
_(u"""If you want to play or view  audio's details, you'll have to navigate to the tree view, and, using the down arrow, look for "my audios", "populars" or "Recommendations". You will see two more buttons, play and play all. The play button will play the currently selected audio, and the play all button will play audios in the current buffer, starting with the current selected item. You can go to the song's list, look for a desired song and press the play button, or Ctrl+return, which is a keyboard shorcut. Take in to account that there are some keyboard shorcuts that only work in the list of items."""),
_(u""""""),
_(u"""You can play audio from any buffer, just press ctrl+return for making the audio playback possible."""),
_(u""""""),
_(u"""If someone has added multiple audios at once to his library, you will see something like this in your newsfeed: "(friend) has added 4 audios: audio 1, audio2, audio3 and audio4". You can press return in the  post for opening the audio's details dialogue, where you will be able to see a list with these audios. By default the first detected song is selected, which means that you could read its details by pressing tab, download or add it to your library. If you change the audio in the list, the information will be updated and you will see details and actions will take effect in the new selected audio."""),
_(u""""""),
_(u"""When an  audio file is playing, you can press f5 and f6 for decreasing and increasing volume, respectively, or control+shift+return for play/pause."""),
_(u""""""),
_(u"""If you want to see  some details for the selected audio file, you can do it by pressing the return key. You will be able to read some useful information  (title, artist, duration and the lyric, if available). Also you will be able to download the song to your hard drive, you have to press the download button in the details' dialogue."""),
_(u""""""),
_(u"""When the download starts, you can close the details dialogue and check the status bar in the main window for seeing the current progress."""),
_(u""""""),
_(u"""Additionally, you can search for audios by using the menu bar, in the buffer menu, select search, then audio. It will display a dialog where you have to set your search preferences."""),
_(u""""""),
_(u"""If you press the menu key, you will see a menu where you will be able to do some actions, for example, add the audio to an album, or add/remove the song from your library."""),
_(u""""""),
_(u"""## menu Bar"""),
_(u""""""),
_(u"""You can go to the menu bar by pressing ALT. Right now, there are  three  menus, application, buffer and help:"""),
_(u""""""),
_(u"""### Application menu"""),
_(u""""""),
_(u"""* Create. Here you can create some things in VK. The only supported item at this moment is the audio album."""),
_(u"""* Delete: Removes items from the VK servers. The only supported item here is the audio album."""),
_(u"""* you can set your preferences by opening the preferences dialog located in this menu."""),
_(u""""""),
_(u"""### Buffer menu"""),
_(u""""""),
_(u"""* new timeline: This option allows you to create a new timeline. This kind of buffers is capable of download all posts in an user's profile."""),
_(u"""* search: This submenu  allows you to create a new buffer, at the moment, you can create only a kind of buffer, an audio search. The audio search will be located in the music category and will have the last 299 results of your query."""),
_(u"""* Update current buffer: perform an update operation in the selected buffer, which will retrieve the new items."""),
_(u"""* Load previous items: Get the previous items for the currently  focused buffer."""),
_(u"""* Remove buffer: Tries to remove the current buffer. Default buffers can't  be removed."""),
_(u""""""),
_(u"""The help menu is self explanatory."""),
_(u""""""),
_(u"""## Contributing"""),
_(u""""""),
_(u"""If you notice some errors in this document, or features that are not documented yet, you can suggest those changes by contacting me (more information can be find in the following section)."""),
_(u""""""),
_(u"""## contact"""),
_(u""""""),
_(u"""If you have questions, don't esitate to contact me in [Twitter,](https://twitter.com/manuelcortez00) or sending me an email to manuel(at)manuelcortez(dot)net. Just replace the words in parentheses with the original signs."""),
]