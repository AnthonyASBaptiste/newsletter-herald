# Newsletter Herald — Admin User Manual
Welcome to Newsletter Herald! This guide explains how to manage the parish bulletin summarization, archives, and email subscription lists.

---

## 📌 Executive Summary

Newsletter Herald is an automated liturgical newsletter pipeline. It parses weekly parish bulletins, extracts theological and calendar metadata, generates warm summaries using Groq Cloud AI, and distributes the email newsletter directly to your active parish subscriber database.

---

## 📤 1. Manual Bulletin Ingestion
To upload a new bulletin (when the automated pipeline is bypassed or for manual entries):
1. Navigate to the **Console Dashboard**.
2. Click **Upload Bulletin** (or drag a file into the upload zone).
3. Select a weekly parish bulletin (`.pdf` or `.docx` format).
4. The system will automatically:
   - Compress the document for fast web loading.
   - Run AI summarization to extract the **Target Sunday**, **Liturgical Season**, **Calendar Year**, and **Liturgical Summary**.
5. Once processed, it will appear in the main feed or redirect to the audit logs if a validation error occurs.

---

## ⚠️ 2. Ingestion Auditing & Metadata Overrides
To prevent AI hallucination or incorrect dates, the pipeline performs strict **Validation Checks** (e.g., verifying if the extracted Target Sunday is correct).

If a file fails validation, it enters the **System Errors & Audit Log**:
1. Click **System Errors** from the navigation bar.
2. Under **Ingestion Errors**, locate the failed document.
3. Click **Edit & Resolve** to open the metadata correction dialog.
4. Correct any fields (e.g. adjust the target Sunday date).
5. Choose one of two action buttons:
   *   **Save & Schedule Email**: Saves the corrections and queues the newsletter for weekly email delivery to all subscribers.
   *   **Archive Only (No Email)**: Publishes the newsletter directly to the public feed archives. It will mark the bulletin as "delivered" without queueing any emails (perfect for adding missing historic editions).

---

## 👥 3. Subscriber Directory Management
To view or update your parish mailing list, navigate to the **Subscribers** view:

### Add Single Subscriber:
1. Click **Add Subscriber**.
2. Enter the **Email**, **First Name**, **Last Name**, and **Phone Number**.
3. Click **Save** to insert the record.

### Sync from Google Contacts (CSV Batch Import):
1. Export your contact list from Gmail/Google Contacts as a **Google CSV** file.
2. In SALLTO Herald, click **Sync from Google Contacts** in the Subscribers panel.
3. Upload the exported `contacts.csv` file.
4. The import script will automatically parse and map the complex Gmail columns, extracting names, email addresses, and phone numbers to keep your database synchronized.

---

## 🔒 4. Access Control & Troubleshooting
*   **Whitelisted Administrators**: Only users logged in via Clerk with the emails `anthony.as.baptiste@gmail.com` or `sallto.newsletter@gmail.com` are granted access to the console and subscriber directories.
*   **Access Denied Screen**: If you sign in with an unauthorized personal account, you will see a restricted access card. Click **Sign Out** to switch accounts or **View Public Feed** to browse the public bulletin archive.
