# UX Writing Examples

Practical examples for common UI scenarios. Use alongside SKILL.md guidelines.

---

## Form Validation Errors

### Required Fields
- "Email is required"
- "Please enter your name"

### Format Errors
- "Enter a valid email address (e.g., name@example.com)"
- "Password must be at least 8 characters"
- "Phone number should contain only digits"

### Range Errors
- "Value must be between 1 and 100"
- "Date must be in the future"
- "File size cannot exceed 10 MB"

---

## Network/API Errors

### Connection Issues
- "Unable to connect. Check your internet connection and try again."
- "Server is temporarily unavailable. Please try again in a few minutes."

### Timeout Errors
- "Request timed out. The server is taking longer than expected."

### Authentication Errors
- "Session expired. Please sign in again."
- "You don't have permission to access this resource."

### Data Errors
- "Unable to load data. Refresh the page to try again."
- "Changes couldn't be saved. Please try again."

---

## Empty States

### First-Time User
- "No datasets yet. Upload your first dataset to get started."
- "Your dashboard is empty. Add widgets to customize your view."

### No Results
- "No results found for '[query]'. Try adjusting your filters."
- "No matching records. Check your search terms or clear filters."

### Completed State
- "All tasks complete. Great work!"
- "No pending items. You're all caught up."

---

## Success Messages

### Create Operations
- "Dataset created successfully."
- "Pipeline saved."

### Update Operations
- "Changes saved."
- "Settings updated."

### Delete Operations
- "Dataset deleted."
- "Item removed."

### Process Completion
- "Pipeline completed successfully."
- "Export finished. Download ready."

---

## Loading States

### Generic Loading
- "Loading..."
- "Loading dashboard..."

### Specific Operations
- "Uploading file... (45%)"
- "Processing data..."
- "Generating report..."

### Long Operations
- "This may take a few minutes..."
- "Analyzing large dataset. Please wait..."

---

## Confirmation Dialogs

### Delete Confirmations
**Title:** "Delete dataset?"
**Body:** "This will permanently delete 'Customer Data Q4' and all associated pipelines. This action cannot be undone."
**Primary:** "Delete"
**Secondary:** "Cancel"

### Discard Changes
**Title:** "Discard unsaved changes?"
**Body:** "You have unsaved changes that will be lost."
**Primary:** "Discard"
**Secondary:** "Keep Editing"

### Irreversible Actions
**Title:** "Reset all settings?"
**Body:** "This will restore all settings to their defaults. Your custom configurations will be lost."
**Primary:** "Reset Settings"
**Secondary:** "Cancel"

---

## Tooltips and Help Text

### Feature Explanations
- "Refresh rate: How often data is updated from the source."
- "Retention period: How long data is stored before automatic deletion."

### Input Guidance
- "Enter a unique name for this pipeline. Letters, numbers, and hyphens only."
- "Select the timezone for scheduled reports."

### Status Indicators
- "Last synced: 5 minutes ago"
- "Processing: 3 of 10 files complete"

---

## Progress Indicators

### Step Progress
- "Step 1 of 4: Configure source"
- "Step 2 of 4: Map fields"

### Percentage Progress
- "Uploading... 45%"
- "Processing: 8 of 20 records"

### Time Estimates
- "About 2 minutes remaining"
- "Completing shortly..."

---

## Notification Messages

### Info
- "New version available. Refresh to update."
- "Scheduled maintenance tonight at 11 PM UTC."

### Warning
- "Your session will expire in 5 minutes."
- "Storage is 90% full. Consider archiving old data."

### Error
- "Failed to sync. Will retry automatically."
- "Some features may be unavailable."

---

**Version:** 2.1.0
