# 🤖 AI Assistant Context Prompt for LineDrive
**Copy and paste this entire prompt at the start of a new conversation**

---

## 📚 CRITICAL: Read the Documentation FIRST

Before making ANY suggestions, code changes, or answering questions about LineDrive:

**READ THIS FILE**: `DOCUMENTATION.md` in the project root

This 1,000+ line comprehensive document contains:
- Complete system architecture
- All module descriptions and purposes
- Working code patterns and critical design decisions
- What NOT to break
- Development best practices
- API references
- Troubleshooting guides

---

## 🎯 LineDrive System Overview

LineDrive is a **multi-module platform** with several distinct systems:

### 🎬 **Primary Module: ScriptCraft (YouTube Script Creation)**
- **4-agent AI workflow**: Topic enhancement → Script writing → Review → Assembly & Polish
- **3 interfaces**: Console UI (baseline), Web GUI (local), Azure Container (cloud)
- **Current state**: ✅ ALL THREE WORKING - DO NOT BREAK ANY
- **Completion time**: 3-4 minutes per full workflow
- **New in v2.0**: Emotional thumbnail generation with 6 AI-powered variations

### ⚾ **Secondary Module: Baseball Tournament Management**
- Batch scrapers for Perfect Game, Little League, USA Baseball
- Azure Data Lake storage integration
- Tournament data analysis and search

### 📱 **Tertiary Module: Social Media Integration**
- X/Twitter posting functionality
- Content distribution automation

---

## 🚨 CRITICAL RULES - NEVER BREAK THESE

### 1. **Module Isolation - Golden Rule**
```
Console UI = Golden Baseline (NEVER break)
Web GUI = Independent (don't break when working on container)
Container = Independent (don't break when working on web GUI)
```

**Each module MUST remain functional** even when others are being modified.

### 2. **Git Operations - ALWAYS ASK FIRST**
```
❌ NEVER run: git commit (without asking)
❌ NEVER run: git push (without asking)
✅ ALWAYS: Show what will be committed and ASK for permission
✅ ALWAYS: Wait for explicit "yes" before any git operation
```

### 3. **Working Code - DO NOT MODIFY Without Permission**
These files are WORKING and critical:
- `console_launcher_modular.py` - Primary console entry point
- `console_ui/workflows.py` - Core 4-agent workflow
- `scriptcraft-app/web_gui.py` - Web interface with SSE streaming
- `tools/media/emotional_thumbnail_generator.py` - Thumbnail generation

**Before modifying ANY of these, ASK the user for permission and explain why.**

### 4. **SSE Streaming Pattern - DO NOT CHANGE**
```python
# ⚠️ CRITICAL: This exact pattern prevents hanging
while True:  # Process messages BEFORE checking done
    if not streamer.message_queue.empty():
        message = streamer.message_queue.get()
        yield f"data: {json.dumps(message)}\n\n"
    if streamer.done and streamer.message_queue.empty():
        break

# ❌ WRONG: This causes hanging
while not streamer.done:  # DON'T DO THIS
```

### 5. **Progress Bar Pattern - CRITICAL**
```python
# ⚠️ CORRECT: Only send updates with explicit progress values
progress = self._extract_progress(message)
if progress is not None and self.streamer:
    self.streamer.send_update(message.strip(), progress)
# Don't send messages without progress

# ⚠️ CORRECT: send_update() must return early if no progress
def send_update(self, message: str, progress: int = None):
    if progress is None:
        return  # Don't send - prevents default 50% jump
        
# ⚠️ CORRECT: Filter chapter START messages (return None)
elif "Writing Chapter" in message and "/" in message:
    return None  # Don't update progress while starting
elif "Reviewing Chapter" in message and "/" in message:
    return None  # Don't update progress while starting
    
# ✅ CORRECT: Only update on COMPLETION
elif "Chapter" in message and "completed" in message:
    # Calculate and return percentage
```

### 6. **Thread Management Pattern - CRITICAL**
```python
# ⚠️ CORRECT: Handle "already has an active run" errors
try:
    run = self.project.agents.runs.create_and_process(...)
except Exception as e:
    if "already has an active run" in str(e).lower():
        # List and cancel existing runs
        existing_runs = self.project.agents.runs.list(thread_id)
        for run in existing_runs:
            if run.status not in ["completed", "failed", ...]:
                self.project.agents.runs.cancel(thread_id, run.id)
                time.sleep(5)  # Wait for cancellation
        # Retry after cleanup
```

### 7. **Console UI Entry Point**
```bash
# ✅ CORRECT (from project root)
python console_launcher_modular.py

# ❌ WRONG (creates import errors)
cd console_ui && python main.py
```

---

## 🔧 Development Workflow

### Before Making Changes:
1. **Read DOCUMENTATION.md** - Understand the full system
2. **Identify which module** you're working on (Console/Web/Container)
3. **Test the baseline first** - Run console UI to establish working state
4. **Create isolated tests** - Don't run full 3-4 minute workflows for debugging
5. **ASK before modifying working code** - Explain the necessity
6. **Check for thread management issues** - Azure agents can have "active run" conflicts
7. **Verify progress bar behavior** - Ensure monotonically increasing progress (never decreases)

### Testing Strategy:
```bash
# 1. Test Console UI (baseline - 3 minutes)
printf "2\n3\nAI test topic\n\ngeneral\nconversational\nminimal\nshort\n" | python console_launcher_modular.py

# 2. Test Web GUI (3-4 minutes)
cd scriptcraft-app && python web_gui.py
# Navigate to http://localhost:8080

# 3. Test Thumbnails (< 1 minute)
python tools/test_emotional_thumbnails.py
```

### After Making Changes:
1. **Test the module you modified** - Verify it still works
2. **Test dependent modules** - Ensure nothing broke
3. **Clean up test files** - Remove debug/temporary files
4. **Show changes** - Use `git diff` or `git status`
5. **ASK before committing** - Show what will be committed and wait for approval

---

## ✅ Good Development Practices

### DO:
- ✅ Read `DOCUMENTATION.md` before making suggestions
- ✅ Test console UI first (it's the baseline)
- ✅ Create isolated tests (avoid long workflows)
- ✅ Ask before modifying working code
- ✅ Keep modules independent
- ✅ Show git changes before committing
- ✅ Wait for explicit permission to commit/push
- ✅ Suggest refactoring AFTER stability
- ✅ Clean up test files when functionality works

### DON'T:
- ❌ Auto-commit without asking
- ❌ Auto-push without asking
- ❌ Break console UI (golden baseline)
- ❌ Break one module while working on another
- ❌ Change SSE streaming pattern
- ❌ Modify `console_launcher_modular.py` without permission
- ❌ Remove Azure SDK filtering
- ❌ Alter threading/async code without understanding
- ❌ Create alternative entry points in `console_ui/`

---

## 📁 Key Files Reference

### Entry Points
- `console_launcher_modular.py` - Console UI (PRIMARY - golden baseline)
- `scriptcraft-app/web_gui.py` - Web GUI
- `batch_scrapers/batch_scraper_ui.py` - Baseball data scrapers

### Core Workflow
- `console_ui/workflows.py` - 4-agent script creation system
- `linedrive_azure/agents/enhanced_autogen_system.py` - AutoGen agent framework

### AI Agents
- `linedrive_azure/agents/script_writer_agent_client.py`
- `linedrive_azure/agents/script_review_agent_client.py`
- `linedrive_azure/agents/youtube_upload_details_agent_client.py`

### Media Generation
- `tools/media/emotional_thumbnail_generator.py` - NEW v2.0 (6 variations)
- `tools/media/thumbnail_generator.py` - Legacy

### Testing
- `tools/test_emotional_thumbnails.py` - 5-stage thumbnail diagnostic (KEEP)
- `tools/test_thumbnail_generator.py` - Legacy thumbnail test (KEEP)

---

## 🏗️ Architecture Patterns

### 1. Lazy Loading (Import Performance)
```python
_genai = None

def _ensure_genai():
    global _genai
    if _genai is None:
        import google.generativeai as genai
        _genai = genai
    return _genai
```

### 2. Console Capture (Web GUI Progress)
```python
class ConsoleCapture:
    def write(self, text):
        self.original_stdout.write(text)  # Terminal
        self.streamer.add_message(text)   # Web client
```

### 3. Server-Sent Events (SSE)
```python
# Process queue BEFORE checking done status
while True:
    if not streamer.message_queue.empty():
        message = streamer.message_queue.get()
        yield f"data: {json.dumps(message)}\n\n"
    if streamer.done and streamer.message_queue.empty():
        break
```

---

## 🎯 Current Working State (v2.0.0)

### ✅ What's Working:
- **Console UI**: Full script creation + thumbnails (Step 4.8)
- **Web GUI**: SSE streaming + progress + thumbnails
- **Azure Container**: Cloud deployment with managed identity
- **Emotional Thumbnails**: 6 AI-powered variations with Gemini Flash Image
- **Baseball Scrapers**: Multi-league data collection
- **Azure Storage**: Data Lake integration

### 🏷️ Git Tags:
- `v2.0.0-emotional-thumbnails` - Current release
- `working-web-gui-v1.0` - Baseline before thumbnails

### 🔄 Recovery if Broken:
```bash
# Restore to last working version
git reset --hard v2.0.0-emotional-thumbnails

# Or restore web GUI baseline
git reset --hard working-web-gui-v1.0
```

---

## 🐛 Common Issues & Solutions

### Issue: Import Error `google.generativeai`
**Solution**: 
```bash
venv314/bin/pip install google-generativeai
```

### Issue: Console UI import errors
**Cause**: Running from wrong directory
**Solution**: Always run from project root
```bash
cd /Users/christhi/Dev/Github/linedrive
python console_launcher_modular.py
```

### Issue: Web GUI hangs at completion
**Cause**: SSE completion logic bug (already fixed in v2.0)
**Solution**: Ensure using correct `while True:` pattern (see documentation)

### Issue: Thumbnail generation timeout
**Solution**: Timeout already increased to 15 minutes in v2.0

### Issue: Progress bar jumps to 50% immediately
**Cause**: Default progress value in `send_update()` method ✅ **FIXED Oct 27, 2025**
**Solution**: Already fixed - removed default 50% and background updater thread
```python
# ✅ CORRECT (post-fix):
if progress is None:
    return  # Don't send updates without explicit progress
```

### Issue: Progress bar jumps backward during chapter work
**Cause**: Chapter START messages triggering progress updates ✅ **FIXED Oct 27, 2025**
**Solution**: Already fixed - filtered "Writing Chapter X/Y" and "Reviewing Chapter X/Y" messages
```python
# ✅ CORRECT (post-fix):
elif "Writing Chapter" in message and "/" in message:
    return None  # Don't update progress when starting
```

### Issue: Thread already has an active run error
**Cause**: Azure agent thread not cleaned up before retry ✅ **FIXED Oct 27, 2025**
**Solution**: Already fixed - added thread cleanup logic with cancellation and wait
```python
# ✅ CORRECT (post-fix):
# Cancel existing runs before creating new one
existing_runs = self.project.agents.runs.list(thread_id)
for run in existing_runs:
    if run.status not in ["completed", "failed", "cancelled", "expired"]:
        self.project.agents.runs.cancel(thread_id, run.id)
        time.sleep(5)  # Wait for cancellation
```

---

## 📞 When You Need More Information

If you need more details about:
- **Architecture**: See DOCUMENTATION.md - Architecture section
- **API Reference**: See DOCUMENTATION.md - API Reference section
- **Deployment**: See DOCUMENTATION.md - Deployment section
- **Troubleshooting**: See DOCUMENTATION.md - Troubleshooting section
- **Code patterns**: See DOCUMENTATION.md - Development Guide section

---

## 💡 Your Role as AI Assistant

### Your Responsibilities:
1. **Understand the full system** before making suggestions
2. **Respect working code** - Don't break what works
3. **Test thoroughly** - Console UI baseline first, then others
4. **Ask permission** - For code modifications and git operations
5. **Maintain module isolation** - Keep console/web/container independent
6. **Provide context** - Explain WHY changes are needed
7. **Suggest rollback plans** - If something might break

### Your Interaction Protocol:
```
BEFORE modifying working code:
"I need to modify [file] to [reason]. This might affect [modules]. 
 Should I proceed? Here's what I'll change: [explanation]"

BEFORE committing:
"I've made these changes: [list changes]
 Here's the git diff: [show diff]
 Should I commit these changes?"

BEFORE pushing:
"Ready to push to GitHub. Confirm?"

AFTER creating test code:
"Should I clean up these test files now?"

WHEN code gets complex:
"This is getting complex. Should we refactor for modularity?"
```

### Remember:
- **READ DOCUMENTATION.MD FIRST** before answering questions
- **ASK BEFORE GIT OPERATIONS** (commit/push)
- **TEST CONSOLE UI FIRST** (golden baseline)
- **KEEP MODULES INDEPENDENT** (don't break one while fixing another)
- **EXPLAIN YOUR REASONING** (why is this change necessary?)

---

## 🎓 Quick Reference Card

| Situation | Action |
|-----------|--------|
| Before ANY change | Read DOCUMENTATION.md |
| Before modifying working code | Ask user for permission |
| Before git commit | Show diff and ASK |
| Before git push | ASK for confirmation |
| Testing changes | Console UI baseline first |
| Debugging | Create isolated test (not full workflow) |
| After test files created | Ask about cleanup |
| Code gets complex | Suggest refactoring after stability |
| Unsure about something | Read docs or ASK user |
| Breaking change possible | STOP and ASK first |

---

**Remember: This is a complex, working system with multiple interfaces. Your job is to help improve it WITHOUT breaking what already works. Always maintain the console UI as the golden baseline that must never break.**

---

## 🚀 Ready to Start

Now that you have this context:
1. **Acknowledge** you've read this prompt
2. **Confirm** you understand the rules (especially git operations)
3. **Ask** what the user wants to work on
4. **Read DOCUMENTATION.md** if you need more details about any module

**Always start by confirming which module we're working on (Console/Web/Container/Baseball/Social) and whether it's a new feature or fixing existing code.**
