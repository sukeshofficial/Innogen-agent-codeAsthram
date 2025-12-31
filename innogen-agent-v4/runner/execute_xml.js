window.executeXML = function (xmlText) {
  try {
    if (!window.Blockly || !window.Python) {
      return {
        status: "environment_error",
        error: "Blockly or Python generator not found"
      };
    }

    const workspace = Blockly.getMainWorkspace();
    if (!workspace) {
      return {
        status: "workspace_error",
        error: "Blockly workspace not available"
      };
    }

    // 1️⃣ Clear workspace
    workspace.clear();

    // 2️⃣ Load XML
    let dom;
    try {
      dom = Blockly.utils.xml.textToDom(xmlText);
    } catch (e) {
      return {
        status: "xml_parse_error",
        error: String(e)
      };
    }

    try {
      Blockly.Xml.domToWorkspace(dom, workspace);
    } catch (e) {
      return {
        status: "xml_injection_error",
        error: String(e)
      };
    }

    // 3️⃣ Generate Python
    let pythonCode;
    try {
      pythonCode = Python.workspaceToCode(workspace);
    } catch (e) {
      return {
        status: "python_generation_error",
        error: String(e)
      };
    }

    return {
      status: "success",
      python: pythonCode
    };

  } catch (fatal) {
    return {
      status: "fatal_error",
      error: String(fatal)
    };
  }
};
