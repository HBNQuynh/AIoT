# Guide to Importing and Running the AI Translation Plugin on Google Docs (Using App Script)

This guide will help you import your completed App Script code and run it to create an AI translation add-in directly within Google Docs.

## 1. Prerequisites

Before you begin, ensure you have the following:

* **Google Account:** You will need a Google account to access Google Docs and Google Apps Script.
* **Completed App Script Code:** You should have your App Script code file for the translation plugin ready.

## 2. Steps to Import Code into Google Apps Script

Follow these steps to import your code into the App Script editor:

1.  **Open Google Docs:** Go to Google Docs ([https://docs.google.com/](https://docs.google.com/)) and open any document.
2.  **Access the Script Editor:**
    * In your Google Docs document, select **Tools** from the menu bar.
    * Choose **Script editor**. A new browser tab or window will open, displaying the Google Apps Script editor.
3.  **Delete Default Code (If Any):** If this is your first time using the script editor for this document, there might be a default `myFunction()` function. You can delete this.
4.  **Copy and Paste Code:**
    * Open your App Script code file.
    * Select all the code content and copy it (Ctrl+A or Cmd+A, then Ctrl+C or Cmd+C).
    * Go back to the Google Apps Script editor.
    * Paste the copied code into the editor window (Ctrl+V or Cmd+V). Make sure you overwrite or delete any existing code before pasting.
5.  **Save the Project:**
    * Click the **Save project** icon (floppy disk icon) in the top left corner.
    * Give your project a name (e.g., "AI Translation Plugin").
    * Click **OK**.

## 3. Steps to Run the Code and Obtain the Add-on in Google Docs

After importing the code, you need to deploy it as an add-on to use it in Google Docs:

1.  **Refresh Google Docs:** After saving the code in the script editor, return to your Google Docs document and refresh the page (F5 or Cmd+R).
2.  **Check for the Add-on:**
    * After refreshing, an **Add-ons** menu will appear in the Google Docs menu bar (usually located between "Tools" and "Help").
    * Hover over the **Add-ons** menu. You should see the name of your add-on project (e.g., "AI Translation Plugin").
    * Click on the add-on name. If this is the first time you are running this add-on, Google might ask you for authorization.
3.  **Authorize the Add-on (If Required):**
    * An authorization dialog will appear. Click **Continue**.
    * Select the Google account you are using.
    * Google will display a notification about the permissions the add-on requires (e.g., view and manage documents, connect to external services if you are using translation APIs).
    * Click **Allow** to grant the add-on the necessary permissions.
4.  **Use the Add-on:** Once the authorization is successful (if needed), go back to the **Add-ons** menu, select your add-on's name, and choose the function you want to use (e.g., "Open Translation Sidebar").
5.  **Sidebar Appears:** A sidebar should appear on the right side of your Google Docs screen, allowing you to set translation preferences such as source language, target language, LLM model, and temperature.
6.  **Perform Translation:** Follow the instructions in the sidebar to select text for translation or translate the entire document based on your settings.

## 4. Important Notes

* **Access Permissions:** Ensure that your code does not request unnecessary sensitive access permissions. Clearly explain the permissions your add-on requires when sharing it with others.
* **API Keys (If Applicable):** If your plugin uses external translation APIs (e.g., from Google Cloud, OpenAI), make sure you have set up and are managing your API keys securely within your App Script code (e.g., using the Properties Service to store keys).
* **Testing and Debugging:** After importing and running, thoroughly test all the plugin's functionalities to ensure it works as expected. Use the logging function (`Logger.log()`) in App Script to track and debug if necessary. You can view the logs by selecting **View** > **Logs** in the script editor.
* **Google Apps Script Version:** Occasionally, different versions of Google Apps Script might have minor changes. Ensure your code is compatible with the current version.
* **Usage Limits:** Be aware of the usage limits for Google Apps Script and any translation APIs you might be using (e.g., the number of translation requests per day).
* **Sharing the Add-on (Optional):** If you want to share this add-on with others, you can deploy it from the script editor as a Google Workspace Add-on. This process involves creating a manifest file and might require verification from Google.

## 5. System Requirements to Run the Code

* **Web Browser:** Google Apps Script and Google Docs run in a web browser. You should use modern and supported web browsers such as Google Chrome, Mozilla Firefox, Safari, or Microsoft Edge.
* **Internet Connection:** A stable internet connection is required to access Google Docs, Google Apps Script, and use AI translation services.
* **Device:** You can use desktop computers, laptops, or mobile devices with a web browser to access and use this plugin. However, editing and importing code is usually more convenient on a computer.

Good luck with submitting your project! If you have any further questions, don't hesitate to ask.
