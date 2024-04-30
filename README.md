***WARNING: THIS SOFTWARE IS IN ITS BETA PHASE, EXPECT ISSUES/INCONVENIENCES UNTIL THE FIRST RELEASE HAS BEEN MADE. I"M AIMING TO CREATE THE FIRST RELEASE BY MAY 5TH 2024***

That said, you *can* use the software currently (it is usable), just beware it still needs to be modified for easy use on all distros and devices.


This software was started as a project for personal use but adapted to be easy(ish) to use by others, so not everything will be as easy as it is in the official Elgatio software.

# Installation
Download the latest release, unzip it, and inside the folder, and install all necessary packages (use ``pip install -r requirements.txt``)
Run streamdeck.py
When it asks if you want to download icon and background packs, you can choose not to download any.

# Usage
Once you've finished the installation process, you're good to go.
Configuring a button, the screen, or a dial is as simple as clicking on it in the GUI and entering whatever you'd like.

# Objects

## screen
### Events
- touchShort: short touch, triggered when the screen is touched for a short amount of time
- touchLong: long touch, triggered when the screen is touched for a longer amount of time
- up: upwards swipe, triggered when you swipe up on the screen
- down: downwards swipe, triggered when you swipe down on the screen
- left: left swipe, triggered when you swipe left on the screen, sets to ``page.previous`` on page creation
- right: right swipe, triggered when you swipe right on the screen, sets to ``page.next`` on page creation
### Properties
- text: the text to display on the screen
- image: the background to use. will be resized to 800x100 (the size of the touchscreen)

## button
### Events
- press: triggered when you press a button
- release: triggered when you release a button
- pushShort: triggered when you push a button for a short time (in most cases, you should avoid using press and pushShort at the same time)
- pushLong: triggered when you push a button for a longer time (in most cases, you should avoid using press and pushLong at the same time)
### Properties
- iconOn: the image/icon to use on this button (iconOff was never implemented). will be resized to 120x120 (the size of buttons)
- text: the text to display on the button

## dial
### Events
- press: triggered when you push a dial
- release: triggered when you release a dial
- clockwise: triggered when you rotate a dial clockwise
- counterclockwise: triggered when you rotate a dial counterclockwise
- up: triggered when you swipe up over a dial's icon, blocks screen's up event if set
- down: triggered when you swipe down over a dial's icon, blocks screen's down event if set
- left: triggered when you swipe left over a dial's icon, blocks screen's left event if set
- right: triggered when you swipe right over a dial's icon, blocks screen's right event if set
- pus

### Events


# Actions
