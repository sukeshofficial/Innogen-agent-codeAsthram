import { JSDOM } from "jsdom";
import Blockly from "blockly/core";
import "blockly/blocks";
import "blockly/python";

export function runBlocklyXML(xmlText) {
  try {
    const dom = new JSDOM("<html><body></body></html>");
    global.window = dom.window;
    global.document = dom.window.document;

    const workspace = new Blockly.Workspace();

    const xmlDom = Blockly.Xml.textToDom(xmlText);
    Blockly.Xml.domToWorkspace(xmlDom, workspace);

    const python = Blockly.Python.workspaceToCode(workspace);

    return { python, error: "" };
  } catch (err) {
    return { python: "", error: err.message };
  }
}
