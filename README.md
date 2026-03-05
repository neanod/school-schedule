# school-schedule
<h1>What does it do?</h1>
This is a program that check's AGL's schedule vk group for the photos of the new schedules and if needed add's it to you google calendar. It checks only for the current day and 10 days ahead, everything else is not edited by a program.
<h1>How to use</h1>
<h2>Tokens</h2>
You have to create the following files in the project's directory:
<p>* <code>credentials.json</code> - credentials from your google console project with the access to your calendar</p>
<p>* <code>VK_TOKEN</code> - admin token from vk, can be obtained here: https://vkhost.github.io/</p>
<p>* <code>GEMINI_TOKEN</code> - google ai token (no billing information needed, everything used in this program is free)</p>
<p>* <code>token.json</code> - will be created automatically at the first launch. Be aware that you will need to sign in you Google Account to create this file and use this program</p>
<h2>Dependencies</h2>
<p>You may want to create a venv (optional)</p>
<p><code>python -m venv venv</code></p> 
<p>Install the requirements</p>
<p><code>pip install -r requirements.txt</code></p>
<p>Launch the program</p>
<p><code>python main.py</code></p>
<p>It's recommended to use autostart for this program as it updates your calendar only when executed. Use crontab for example.</p>
