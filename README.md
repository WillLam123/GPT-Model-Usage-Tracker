### **GPT-Model-Usage-Tracker: A Python Application to Track GPT Model Usage**

This Python code provides a utility to track the usage of GPT models over time. It features a GUI built with PyQt5 and includes options for tracking usage, system tray integration, and automatic updates based on time. Below is a breakdown of the key functionalities and logic.

#### **Features of the Application:**

1. **Always on Top Window**:
   - The application window is designed to stay on top of other windows 
   
2. **System Tray Integration**:
   - The application minimizes to the system tray instead of closing, ensuring it's always running in the background. You can bring it back to the foreground with a double-click or via the tray menu.
   - A system tray icon provides quick access to features like showing the window or exiting the application.

3. **Right-Side Docking with Hide/Show Animation**:
   - The window is initially placed on the right side of the screen, and when you hover over it, the window reveals itself. When the mouse leaves, it hides back to the side with a smooth animation.
   - This functionality is controlled by `enterEvent` and `leaveEvent`, which trigger a sliding animation using `QPropertyAnimation`.

4. **Model Usage Counter**:
   - The application tracks the usage of different GPT models (e.g., '4', '4o', '01 preview', '01 mini'). For each model, a label displays the current count of how many times that model has been used.
   - The user can manually increase or decrease the count using the '+' and '-' buttons for each model.

5. **Automated Count Expiry**:
   - Each model has an associated refresh period. For example:
     - Model `4` and `4o` reset every 3 hours (10800 seconds).
     - Model `01p` resets every 7 days (604800 seconds).
     - Model `01m` resets daily (86400 seconds).
   - Every minute, the program checks if any recorded usage timestamps have expired. If a timestamp is older than the model's refresh period, it is removed from the count. The counts automatically update without user intervention, ensuring that the usage data reflects the recent activity.

6. **Data Persistence**:
   - Usage data is stored in a JSON file (`count_data.json`) so that it can be loaded and updated between application sessions. The `loadData()` and `saveData()` functions handle the reading and writing of this file, ensuring that the state is maintained across launches.
   - If there’s an issue loading or saving the data, an error message is displayed, ensuring the user knows if there’s a problem.

7. **User-Friendly Interface**:
   - The GUI layout is simple, with a label and two buttons (`+` and `-`) for each model to easily track usage manually.
   - The window also includes a close button ('X'), which hides the window instead of terminating the application, keeping it running in the system tray.

#### **Counting and Expiry Logic**:
- **Increment and Decrement**: 
   - When you press the `+` button for a model, the current timestamp is recorded in the model's list of timestamps. This represents one use of the model.
   - If the `-` button is pressed, the earliest timestamp (oldest usage) is removed from the list.
- **Automated Expiry**:
   - The application checks every minute if any timestamps are older than the model's refresh period. Expired timestamps are removed, and the count is adjusted accordingly.
   - This ensures that the displayed usage count reflects the most recent activity within the specified time window for each model.

---

### **How to Use This Application:**
1. Launch the application and you'll see a window displaying the models along with their current usage count.
2. Use the `+` and `-` buttons to manually track model usage.
3. The usage count will automatically update over time as older counts expire based on the refresh period for each model.
4. Minimize the window to the system tray where you can easily access it when needed.

---

### **Installation and Setup:**
To use this script, ensure you have the following dependencies installed:
```bash
pip install PyQt5
```

Make sure to replace `"path_to_icon.png"` with the actual path to an icon for the system tray.

---

This utility is particularly useful for anyone needing to track their GPT model usage over time, simplifying the management of limits or quotas. I developed it primarily to monitor the usage of the o1-preview model, as it has a one-week time window, making it challenging to track the usage of it.

