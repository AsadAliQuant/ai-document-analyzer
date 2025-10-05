# Lock System Guide

## Overview
A simple remote lock system that allows you to remotely disable the application by updating a Google Sheet.

## How It Works

1. **Google Sheet Control**
   - The app checks your public Google Sheet CSV every 60 seconds
   - Cell A1 controls the lock state:
     - `0` = Application unlocked (normal operation)
     - `1` = Application locked (blocked with overlay)

2. **Your Control URL**
   - Edit your sheet here: [Your Google Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vRaSrw4NtfrP1soUfYrAVGv7WtJp8jEaG77LNgOGyW9pBNE4xyqioEvDMKDQDcvseJLnjHUYiCITng7/pub?output=csv)
   - Simply change cell A1 to `1` to lock, or `0` to unlock
   - Changes take effect within 60 seconds

3. **Offline Behavior**
   - The app stores the last known state locally in `lock_state.txt`
   - If the client goes offline, the app continues using the last known state
   - When online again, it will check for updates every 60 seconds

4. **User Experience When Locked**
   - A full-screen overlay appears with the message:
     > "This application is temporarily disabled.  
     > Please contact the developer."
   - The overlay blocks all access to the application
   - The client cannot use any features while locked

## Files Created

- **lock_manager.py**: Handles CSV checking and state management
- **lock_overlay.py**: Creates the blocking overlay widget
- **lock_state.txt**: Stores the last known lock state (auto-generated)

## Testing

1. Open the Google Sheet
2. Set cell A1 to `1`
3. Wait up to 60 seconds
4. The app should show the lock overlay
5. Change A1 back to `0`
6. Wait up to 60 seconds
7. The overlay should disappear

## Customization

To change the lock URL, edit `main_window.py` line 91-93:
```python
self.lock_manager = LockManager(
    csv_url="YOUR_NEW_URL_HERE"
)
```

To change the message, edit `lock_overlay.py` line 25:
```python
message = QLabel("Your custom message here")
```

To change the check interval (currently 60 seconds), edit `lock_manager.py` line 26:
```python
self.timer.start(60000)  # milliseconds
```
