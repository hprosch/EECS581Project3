# EECS581: Software Engineering II

## Project 3: Wordle

### Description
Our Wordle program works just like the fun puzzle game you are familiar with, in addition to new features designed by our team. For more information on these, please see the `How to Play` section. 

### Installation
First, `git clone` this project’s repository onto your local machine.  Next, navigate to where you have the application on your machine, and install Flask by running on the command line `pip3 install flask`.  Then, start up the python file with the command `python3 app.py`, and note the IP address that specifies where the application is running.  For example, the output may be `Running on http://127.0.0.1:5000`.  Enter the HTTP address you see into the browser of your choice to view the application.

### How to Play
Upon launching the game, select the mode of gameplay that you prefer:

* `Start`
    * Classic Mode: the World gameplay you know and love.
    * Easy Mode: the `Free Letter` button allows you to request up to 5 free letters.
    * Hard Mode: when a yellow tile appears, each successive guess must contain that letter in any position.  When a green tile appears, each successive guess must use the green letter in the same index position.
* `Multiplayer`: coming soon.
* `Adventure`: coming soon.

For all modes, users have a series of 6 attempts to guess a 5-letter word correctly.  If a letter tile turns yellow, that means that letter is present in the target word, just not at that index position.  Similarly, if a letter tile turns green, that letter is present in that index position in the target word.  Any grey letter tiles on the game grid are not present in the target word.  

At any point, a new game can be started, or a new mode can be selected from the main menu.  `Hint` button feature coming soon.

To win the game, you must correctly guess the word before running out of attempts.  If you run out of attempts, the game ends and the target word is displayed.

### Documentation
See the `Project3ArchitectureDocument.docx` document within the Document folder for more information on the structure and use cases for this project.  All Team Meeting Logs and other documentation, along with all diagrams and sprint artifacts, are also included there for reference.
