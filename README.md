Sublime KRL Validator
=====================

This Sublime Text 3 plugin sends KRL rulesets through the online validator (http://cs.kobj.net/manage/validate/) and reports any errors.

![Screenshot](http://i.imgur.com/8ZnvHfT.png)

Usage
=====
Invoke by pressing super+shift+k (super is command on a Mac and the "windows key" on Windows or Linux), or by selecting Validate KRL from the Command Palette.

The status message will read "Validating KRL..." while waiting for a response from the server. When the validator indicates that the ruleset is valid, the status message will read, "Valid KRL". If the ruleset isn't valid, the quick panel will show error details.