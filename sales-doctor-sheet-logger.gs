/*
 * Sales Doctor -> Google Sheet logger
 * Logs each anonymized diagnosis (no names, no emails) so you get a monthly
 * read on what founders are actually struggling with.
 *
 * SETUP (about 5 minutes, one time):
 * 1. Go to https://sheets.google.com and create a new sheet. Name it
 *    "Sales Doctor Log". In row 1 put headers: Timestamp | Problem | Diagnosis
 * 2. In that sheet, menu: Extensions -> Apps Script. Delete whatever is there.
 * 3. Paste this whole file. Save.
 * 4. Click Deploy -> New deployment -> type "Web app".
 *      Description: Sales Doctor logger
 *      Execute as:  Me
 *      Who has access: Anyone
 *    Click Deploy, authorize when prompted, and COPY the Web app URL
 *    (it looks like https://script.google.com/macros/s/AKfy.../exec).
 * 5. In Vercel -> talpaperin.com -> Settings -> Environment Variables, add:
 *      Name:  SHEET_WEBHOOK_URL
 *      Value: the Web app URL you copied
 *    Save, then redeploy the site.
 *
 * That's it. Every diagnosis now appends a row. If you ever change the script,
 * use Deploy -> Manage deployments -> edit -> New version so the URL stays the same.
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    sheet.appendRow([
      data.ts || new Date().toISOString(),
      data.problem || "",
      data.diagnosis || ""
    ]);
    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
