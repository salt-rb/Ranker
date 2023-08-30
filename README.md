# Ranker

## Overview

Ranker is a tool that allows you to create ranked lists of your favorite movies, songs, books, or pretty much anything else using head-to-head matches to generate ELO scores to assign to each item in your list. The more you run the Ranker, the more accurate your list will be.

## To Run

To run, simply run the ranker.py file. You may need to install some packages if you don't have them already. This can be done by running ```pip install -r requirements.txt```

As the names suggest, do not delete files with the "rankerDoNotDelete" prefix. If you do delete these, previously saved workspaces will be lost.

## To use

If this is your first time running Ranker, you will need to create a new workspace. To do this, follow these steps:
1. Copy and paste your items from Excel (or another spreadsheet founction like Google Sheets) into the entry box
2. Click the "Create New Workspace" button in the top left
3. When prompted, enter a unique name for your workspace

These steps also work for adding more items into your loaded workspace, but in this case use the "Add More to Workspace" button.

If you have already created a workspace, you can load it with the "Load Existing Workspace" button and then selecting the workspace you'd like to use.
Once you have a workspace, you can start comparing by clicking the button in the bottom left. You will now then be given two options from your inputed list. You should select to item that you prefer between the two (you also have the option to skip the match if you can't decide). If you make an incorrect selection, you also have the option to undo it and choose again (top right).

You can see what your list currently looks like at any time with the "See Rankings" button. The results can be copied and pasted into Excel or another spreadsheet function.
