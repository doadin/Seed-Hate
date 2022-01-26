# deluge-seedhate
Automates the removal of torrents when they are completed to preventing seeding.

# Build instructions
1. Clone the repo
1. From the command line, navagate to repo directory
1. Run command `python setup.py bdist_egg`
  * note: If your default python version is different from the deluge python version (2.7), then you will have to change `python` to reference the correct binary.
1. check the `dist` folder, you should see a `SeedHate*.egg`, this is file to choose when installing the plugin from deluge

# Install instructions
1. Open SeedHate
1. Open Preferences
1. Select `Plugings` from the Categories on the left
1. Press the `Install Plugin` button
![Installing SeedHate]
1. Choose the SeedHate*.egg plugin file
1. Check the box in front of the SeedHate plugin to enable it
![Enabling SeedHate]