from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from rich import print
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
load_dotenv("../.env")  # Ensure correct path
GroqAPIKey = os.getenv("GroqAPIKey")

# User agent for web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# System configuration
SystemChatBot = [{
    "role": "system", 
    "content": f"Hello, I am {os.getenv('Username', 'User')}, You're a content writer."
}]
messages = []

def GoogleSearch(Topic):
    """Perform Google search"""
    search(Topic)
    return True

def Content(Topic):
    """Generate content using AI"""
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        messages.append({"role": "assistant", "content": Answer})
        return Answer.replace("</s>", "")

    clean_topic = Topic.lower().replace("content ", "").strip()
    content = ContentWriterAI(clean_topic)
    
    filename = f"Data/{clean_topic.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    OpenNotepad(filename)
    return True

def YouTubeSearch(Topic):
    """Search YouTube"""
    query = Topic.replace("youtube search ", "")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return True

def PlayYoutube(query):
    """Play YouTube video"""
    playonyt(query.replace("play ", ""))
    return True

def OpenApp(app_name, sess=requests.Session()):
    """Open application with fallback to web search"""
    if "youtube" in app_name.lower():
        webbrowser.open("https://www.youtube.com")
        return True
    
    try:
        appopen(app_name, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"[AppOpener Error] {e} - Falling back to web search")
        
        try:
            url = f"https://www.google.com/search?q={app_name}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for selector in ['a[href^="http"]', 'a[jsname="UWckNb"]']:
                    links = [a['href'] for a in soup.select(selector) if 'http' in a.get('href', '')]
                    if links:
                        webbrowser.open(links[0])
                        return True
        except Exception as e:
            print(f"[Web Search Error] {e}")
    
    print(f"Failed to open {app_name}")
    return False

def CloseApp(app_name):
    """Close application"""
    try:
        close(app_name, match_closest=True, output=False, throw_error=True)
        return True
    except:
        return False

def System(command):
    """System controls"""
    key_actions = {
        "mute": "volume mute",
        "unmute": "volume mute",
        "volume up": "volume up",
        "volume down": "volume down"
    }
    
    if command in key_actions:
        keyboard.press_and_release(key_actions[command])
        return True
    return False

async def TranslateAndExecute(commands):
    """Async command processor"""
    funcs = []
    
    for cmd in commands:
        if cmd.startswith("open "):
            app = cmd[5:].strip()
            if app.lower() != "it":
                funcs.append(asyncio.to_thread(OpenApp, app))
                
        elif cmd.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd[6:].strip()))
            
        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd[5:].strip()))
            
        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd[8:].strip()))
            
        elif cmd.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd[14:].strip()))
            
        elif cmd.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd[15:].strip()))
            
        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd[7:].strip()))
    
    await asyncio.gather(*funcs)
    return True

async def Automation(commands):
    """Main automation interface"""
    await TranslateAndExecute(commands)
    return True
