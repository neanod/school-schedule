# school-schedule
<h1>What does it do?</h1>
This is a program that check's AGL's schedule vk group for the photos of the new schedules and if needed add's it to you google calendar. It checks only for the current day and 10 days ahead, everything else is not edited by a program.
<h1>How to use</h1>
You have to create the following files in the project's directory:
* `credentials.json` - credentials from your google console project with the access to your calendar
* `VK_TOKEN` - admin token from vk, can be obtained here: https://vkhost.github.io/
* `GEMINI_TOKEN` - google ai token (no billing information needed, everything used in this program is free)
* `token.json` - will be created automatically at the first launch. Be aware that you will need to sign in you Google Account to create this file and use this program
