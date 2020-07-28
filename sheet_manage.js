function getCellColor() {
	var ss = SpreadsheetApp.getActiveSpreadsheet();
	var sheet = ss.getSheets()[0];

	var cell = sheet.getRange("B5");
	sheet.appendRow([cell.getBackground()]);
}
